#!/usr/bin/env python3
"""UGE-correction utilities for dfnWorks / PFLOTRAN.

All functions that read, validate, and correct an explicit-unstructured-grid
``.uge`` mesh file live in this module. The shared validity rule is: a value is
replaced by its absolute value if negative, by a fill value if it is ``NaN`` or
``+/-inf``, and otherwise left unchanged.

Contents
--------
    classify_fix, scan_fills
        Low-level helpers implementing the validity rule and the fill estimate.
    fix_uge_volumes, fix_stream
        Standalone, byte-faithful fixer usable as a function or from the CLI.
    correct_uge_file
        dfnWorks method. ``dim=3`` aperture-converts ``full_mesh.uge`` into
        ``full_mesh_vol_area.uge``; ``dim=2`` keeps ``full_mesh.uge``. When
        ``self.r_fram`` is True the raw values are sanitized first.
    lagrit2pflotran
        dfnWorks method. Forwards ``dim`` to :func:`correct_uge_file`.

Command line
------------
    python3.11 uge_tools.py full_mesh.uge --in-place
"""
import argparse
import math
import os
import sys
import tempfile
from time import time
from collections import namedtuple

CELL_FMT = "%10d  % .12E  % .12E  % .12E  % .12E"          # id  x y z  volume
CONN_FMT = "%10d %10d  % .12E  % .12E  % .12E  % .12E"     # id1 id2  fx fy fz  area

Result = namedtuple("Result", ["cell_negative", "cell_nonfinite",
                               "conn_negative", "conn_nonfinite",
                               "vol_fill", "area_fill"])


def classify_fix(x, fill):
    """Apply the validity rule to a single value and report what was done.

    Parameters
    ----------
        x : float
            The raw value (cell volume or connection area).
        fill : float
            Replacement value used when ``x`` is NaN or infinite.

    Returns
    -------
        tuple (float, str or None)
            The corrected value and a tag describing the action: ``None`` if the
            value was already valid, ``'negative'`` if it was negated, or
            ``'nonfinite'`` if it was replaced by ``fill``.

    Notes
    -----
        Negative -> ``abs(x)``; NaN/inf -> ``fill``; otherwise unchanged.
    """
    if not math.isfinite(x):
        return fill, "nonfinite"
    if x < 0.0:
        return -x, "negative"
    return x, None


def scan_fills(input_path, strategy="min"):
    """Estimate per-column fill values from the finite, positive entries.

    Makes a single sequential pass with O(1) memory, tracking the running
    minimum, sum, and count of valid volumes (CELLS) and areas (CONNECTIONS).

    Parameters
    ----------
        input_path : str
            Path to the ``.uge`` file.
        strategy : str
            ``'min'`` (default) uses the smallest finite positive value in each
            column; ``'mean'`` uses the mean of the finite positive values.

    Returns
    -------
        tuple (float, float or None)
            ``(vol_fill, area_fill)``. ``area_fill`` is ``None`` when the file
            has no CONNECTIONS section.

    Raises
    ------
        ValueError
            If no finite positive volume exists to derive a fill from, or if
            ``strategy`` is not recognised.
    """
    v_min = a_min = math.inf
    v_tot = a_tot = 0.0
    v_cnt = a_cnt = 0
    with open(input_path) as f:
        n = int(f.readline().split()[-1])
        for _ in range(n):
            v = float(f.readline().split()[4])
            if math.isfinite(v) and v > 0.0:
                v_min = min(v_min, v); v_tot += v; v_cnt += 1
        conn = f.readline().split()
        if conn and conn[0].upper() == "CONNECTIONS":
            for _ in range(int(conn[-1])):
                a = float(f.readline().split()[5])
                if math.isfinite(a) and a > 0.0:
                    a_min = min(a_min, a); a_tot += a; a_cnt += 1
    if v_cnt == 0:
        raise ValueError("no finite positive volumes to derive a fill value from")

    def pick(mn, tot, cnt):
        if cnt == 0:
            return None
        if strategy == "min":
            return mn
        if strategy == "mean":
            return tot / cnt
        raise ValueError(f"unknown strategy {strategy!r} (use 'min', 'mean', or a number)")

    return pick(v_min, v_tot, v_cnt), pick(a_min, a_tot, a_cnt)


def fix_stream(fin, fout, vol_fill, area_fill):
    """Stream-copy a ``.uge`` file from ``fin`` to ``fout``, correcting bad values.

    Cell volumes (column 5) and connection areas (column 6) are passed through
    :func:`classify_fix`. Lines that need no change are written verbatim; only
    corrected lines are reformatted (byte-faithfully, in LaGriT's format).

    Parameters
    ----------
        fin : file object
            Open, readable handle on the source ``.uge`` file.
        fout : file object
            Open, writable handle for the corrected output.
        vol_fill : float
            Fill value for NaN/inf cell volumes.
        area_fill : float or None
            Fill value for NaN/inf connection areas.

    Returns
    -------
        tuple (int, int, int, int)
            ``(cell_negative, cell_nonfinite, conn_negative, conn_nonfinite)``.

    Raises
    ------
        ValueError
            If a section header is malformed, the file is truncated, or a NaN/inf
            area is encountered while ``area_fill`` is ``None``.
    """
    header = fin.readline()
    parts = header.split()
    if not parts or parts[0].upper() != "CELLS":
        raise ValueError(f"expected 'CELLS <n>' header, got: {header!r}")
    fout.write(header)

    c_neg = c_bad = 0
    for _ in range(int(parts[-1])):
        line = fin.readline()
        if not line:
            raise ValueError("file ended before all CELLS lines were read")
        cols = line.split()
        fixed, kind = classify_fix(float(cols[4]), vol_fill)
        if kind is None:
            fout.write(line)
        else:
            fout.write(CELL_FMT % (int(cols[0]), float(cols[1]), float(cols[2]),
                                   float(cols[3]), fixed) + "\n")
            c_neg += kind == "negative"; c_bad += kind == "nonfinite"

    k_neg = k_bad = 0
    conn_header = fin.readline()
    if conn_header:
        fout.write(conn_header)
        cparts = conn_header.split()
        if cparts and cparts[0].upper() == "CONNECTIONS":
            for _ in range(int(cparts[-1])):
                line = fin.readline()
                if not line:
                    raise ValueError("file ended before all CONNECTIONS lines were read")
                cols = line.split()
                if area_fill is None and not math.isfinite(float(cols[5])):
                    raise ValueError("NaN/inf area but no positive area to fill from; pass a number")
                fixed, kind = classify_fix(float(cols[5]), area_fill)
                if kind is None:
                    fout.write(line)
                else:
                    fout.write(CONN_FMT % (int(cols[0]), int(cols[1]), float(cols[2]),
                                           float(cols[3]), float(cols[4]), fixed) + "\n")
                    k_neg += kind == "negative"; k_bad += kind == "nonfinite"

    for line in fin:
        fout.write(line)
    return c_neg, c_bad, k_neg, k_bad


def fix_uge_volumes(input_path, output_path=None, nan_fill="min"):
    """Make every CELLS volume and CONNECTIONS area in a ``.uge`` file valid and positive.

    Parameters
    ----------
        input_path : str
            Path to the ``.uge`` file to correct.
        output_path : str, optional
            Destination path. If ``None`` (default) the file is corrected in
            place via an atomic temp-file-then-replace.
        nan_fill : str or float
            Fill strategy for NaN/inf entries: ``'min'`` (default), ``'mean'``,
            or an explicit number applied to both columns.

    Returns
    -------
        Result
            Namedtuple with the per-section correction counts and the fill
            values used: ``(cell_negative, cell_nonfinite, conn_negative,
            conn_nonfinite, vol_fill, area_fill)``.

    Notes
    -----
        A clean file is returned byte-for-byte identical; only corrected lines
        are rewritten.
    """
    try:
        vol_fill = area_fill = float(nan_fill)
    except (TypeError, ValueError):
        vol_fill, area_fill = scan_fills(input_path, nan_fill)

    if output_path is None:
        d = os.path.dirname(os.path.abspath(input_path))
        with open(input_path) as fin, \
             tempfile.NamedTemporaryFile("w", dir=d, delete=False) as ftmp:
            tmp = ftmp.name
            counts = fix_stream(fin, ftmp, vol_fill, area_fill)
        os.replace(tmp, input_path)
    else:
        with open(input_path) as fin, open(output_path, "w") as fout:
            counts = fix_stream(fin, fout, vol_fill, area_fill)
    return Result(*counts, vol_fill, area_fill)


# --------------------------------------------------------------------------- #
# dfnWorks methods
# --------------------------------------------------------------------------- #
def correct_uge_file(self, dim=3):
    """Correct the LaGriT ``.uge`` file for the PFLOTRAN flow solver.

    Always runs. The behaviour splits on two independent axes:

      * ``dim`` controls the aperture conversion and the output target. ``dim=3``
        multiplies cell volumes by aperture and connection areas by the mean
        aperture, writing ``<inp>_vol_area.uge``. ``dim=2`` keeps the raw
        ``<inp>.uge`` as the active mesh (no aperture conversion).
      * ``self.r_fram`` controls validity sanitization. When True, raw values are
        passed through :func:`classify_fix` (negative -> abs, NaN/inf -> smallest
        positive fill) *before* any aperture scaling. This is where the
        degenerate cells produced by relaxed meshing constraints are repaired.

    In all cases ``self.uge_file`` is set to the file PFLOTRAN should read.

    Parameters
    ----------
        self : object
            DFN Class.
        dim : int
            Problem dimension, ``3`` (default) or ``2``.

    Returns
    -------
        None

    Notes
    -----
        Assumes the following instance variables exist:
          - ``self.flow_solver`` (str): must be ``"PFLOTRAN"``.
          - ``self.inp_file`` (str): used to derive the ``.uge`` file name.
          - ``self.r_fram`` (bool): whether the feature-rejection mesher was used.
          - ``self.material_ids`` (list[int]): material id per cell.
          - ``self.aperture`` (list[float]): aperture per cell or material.
          - ``self.cell_based_aperture`` (bool): aperture indexing mode.
          - ``self.print_log`` (callable): logging method.
    """
    self.print_log("--> Starting: Correcting UGE file")
    if self.flow_solver != "PFLOTRAN":
        self.print_log("Error. Wrong flow solver requested\n", "error")

    raw_uge = self.inp_file[:-4] + ".uge"
    if not os.path.isfile(raw_uge):
        self.print_log("Error. Cannot find uge file\nExiting\n", "error")

    t = time()
    c_neg = c_bad = k_neg = k_bad = 0

    if dim == 3:
        out_uge = self.inp_file[:-4] + "_vol_area.uge"
        aperture = self.aperture
        material_ids = self.material_ids
        cell_based = self.cell_based_aperture

        vol_fill = area_fill = None
        if self.r_fram:
            vol_fill, area_fill = scan_fills(raw_uge, "min")

        with open(raw_uge, "r") as fin, open(out_uge, "w") as fout:
            cell_header = fin.readline(); fout.write(cell_header)
            cell_lines = []
            for _ in range(int(cell_header.split()[-1])):
                parts = fin.readline().split(None, 5)
                cid = int(parts[0]); vol = float(parts[4])
                if self.r_fram:
                    vol, kind = classify_fix(vol, vol_fill)
                    c_neg += kind == "negative"; c_bad += kind == "nonfinite"
                idx = cid - 1 if cell_based else material_ids[cid - 1] - 1
                vol *= aperture[idx]
                cell_lines.append(f"{cid}\t{parts[1]}\t{parts[2]}\t{parts[3]}\t{vol:0.12e}\n")
            fout.writelines(cell_lines)

            conn_header = fin.readline(); fout.write(conn_header)
            conn_lines = []
            for _ in range(int(conn_header.split()[-1])):
                parts = fin.readline().split(None, 6)
                id1 = int(parts[0]); id2 = int(parts[1]); area = float(parts[5])
                if self.r_fram:
                    area, kind = classify_fix(area, area_fill)
                    k_neg += kind == "negative"; k_bad += kind == "nonfinite"
                avg_ap = 0.5 * (aperture[material_ids[id1 - 1] - 1] +
                                aperture[material_ids[id2 - 1] - 1])
                area *= avg_ap
                conn_lines.append(f"{id1}\t{id2}\t{parts[2]}\t{parts[3]}\t{parts[4]}\t{area:0.12e}\n")
            fout.writelines(conn_lines)
        self.uge_file = out_uge
    else:
        if self.r_fram:
            res = fix_uge_volumes(raw_uge, nan_fill="min")     # atomic in-place
            c_neg, c_bad, k_neg, k_bad = (res.cell_negative, res.cell_nonfinite,
                                          res.conn_negative, res.conn_nonfinite)
        self.uge_file = raw_uge

    if self.r_fram:
        self.print_log(f"--> rFram sanitize: cells {c_neg} neg / {c_bad} NaN-inf, "
                       f"conns {k_neg} neg / {k_bad} NaN-inf")
    self.print_log(f"--> Complete: UGE file -> {self.uge_file} ({time() - t:0.3f} s)")

