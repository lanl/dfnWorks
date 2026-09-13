"""UGE-correction utilities for dfnWorks / PFLOTRAN.

All functions that read, validate, and correct an explicit-unstructured-grid
``.uge`` mesh file live in this module. The shared validity rule is: a value is
replaced by its absolute value if negative, by a fill value if it is ``NaN`` or
``+/-inf``, and otherwise left unchanged.

Correcting a bad value is only defensible when the mesh is *almost* conforming.
Degenerate cells are an artifact of the relaxed meshing constraints used by rFram
(see :mod:`pydfnworks.dfnGen.meshing.mesh_dfn`), and they show up mostly in dense
networks and around triple intersections. So the module enforces a policy before
it corrects anything:

    * rFram off and any invalid value  -> hard error. A conforming mesh has no
      business producing negative or non-finite coefficients; that is a meshing
      failure, not an artifact to paper over.
    * more than ``BAD_FRACTION_LIMIT`` of the cells *or* of the connections
      invalid -> hard error, regardless of rFram. The two fractions are tested
      independently against their own totals.
    * otherwise -> correct, and log every offending cell and connection.

Contents
--------
    classify_fix, scan_uge, scan_fills
        Low-level helpers implementing the validity rule, the mesh-wide scan,
        and the fill estimate.
    fix_uge_volumes, fix_stream
        Byte-faithful fixer: a clean file round-trips unchanged, and only the
        corrected lines are rewritten.
    correct_uge_file
        dfnWorks method. ``dim=3`` aperture-converts ``full_mesh.uge`` into
        ``full_mesh_vol_area.uge``; ``dim=2`` keeps ``full_mesh.uge``. The mesh
        is always scanned and the policy above is always enforced.
    lagrit2pflotran
        dfnWorks method. Forwards ``dim`` to :func:`correct_uge_file`.
"""
import math
import os
import tempfile
from time import time
from collections import namedtuple

CELL_FMT = "%10d  % .12E  % .12E  % .12E  % .12E"          # id  x y z  volume
CONN_FMT = "%10d %10d  % .12E  % .12E  % .12E  % .12E"     # id1 id2  fx fy fz  area

#: Largest fraction of invalid cells (or of invalid connections) that may be
#: corrected. Above this the mesh is rejected instead of repaired.
BAD_FRACTION_LIMIT = 0.01

Result = namedtuple("Result", ["cell_negative", "cell_nonfinite",
                               "conn_negative", "conn_nonfinite",
                               "vol_fill", "area_fill"])

#: Outcome of :func:`scan_uge`. ``bad_cells`` holds ``(id, x, y, z, volume,
#: kind)`` tuples and ``bad_conns`` holds ``(id1, id2, area, kind)`` tuples, with
#: ``kind`` as returned by :func:`classify_fix`.
ScanResult = namedtuple("ScanResult", ["path", "vol_fill", "area_fill",
                                       "n_cells", "n_conns",
                                       "bad_cells", "bad_conns"])


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


def scan_uge(input_path, strategy="min"):
    """Scan a ``.uge`` file for invalid values and estimate per-column fills.

    Makes a single sequential pass, tracking the running minimum, sum, and count
    of the valid volumes (CELLS) and areas (CONNECTIONS), and recording every
    entry that :func:`classify_fix` flags. Memory is O(number of invalid
    entries), not O(mesh).

    Every offending entry is recorded rather than only the first few: the caller
    reports them all, and the policy decisions downstream (see
    :func:`correct_uge_file`) only ever let a small fraction through.

    Parameters
    ----------
        input_path : str
            Path to the ``.uge`` file.
        strategy : str
            ``'min'`` (default) uses the smallest finite positive value in each
            column; ``'mean'`` uses the mean of the finite positive values.

    Returns
    -------
        ScanResult
            ``(path, vol_fill, area_fill, n_cells, n_conns, bad_cells,
            bad_conns)``. A fill is ``None`` when its column holds no finite
            positive value to derive one from (an empty or wholly invalid
            column); it is the caller's job to reject such a mesh.

    Raises
    ------
        ValueError
            If ``strategy`` is not recognised.

    Notes
    -----
        A volume or area of exactly ``0.0`` is neither flagged nor used as a
        fill candidate, matching :func:`classify_fix`, which passes it through
        unchanged.
    """
    v_min = a_min = math.inf
    v_tot = a_tot = 0.0
    v_cnt = a_cnt = 0
    n_conns = 0
    bad_cells = []
    bad_conns = []
    with open(input_path) as f:
        n_cells = int(f.readline().split()[-1])
        for _ in range(n_cells):
            cols = f.readline().split()
            v = float(cols[4])
            _, kind = classify_fix(v, 0.0)
            if kind is not None:
                bad_cells.append((int(cols[0]), float(cols[1]), float(cols[2]),
                                  float(cols[3]), v, kind))
            elif v > 0.0:
                v_min = min(v_min, v); v_tot += v; v_cnt += 1
        conn = f.readline().split()
        if conn and conn[0].upper() == "CONNECTIONS":
            n_conns = int(conn[-1])
            for _ in range(n_conns):
                cols = f.readline().split()
                a = float(cols[5])
                _, kind = classify_fix(a, 0.0)
                if kind is not None:
                    bad_conns.append((int(cols[0]), int(cols[1]), a, kind))
                elif a > 0.0:
                    a_min = min(a_min, a); a_tot += a; a_cnt += 1

    def pick(mn, tot, cnt):
        if cnt == 0:
            return None
        if strategy == "min":
            return mn
        if strategy == "mean":
            return tot / cnt
        raise ValueError(f"unknown strategy {strategy!r} (use 'min', 'mean', or a number)")

    return ScanResult(input_path, pick(v_min, v_tot, v_cnt),
                      pick(a_min, a_tot, a_cnt), n_cells, n_conns,
                      bad_cells, bad_conns)


def scan_fills(input_path, strategy="min"):
    """Estimate per-column fill values from the finite, positive entries.

    Thin wrapper on :func:`scan_uge` for callers that only need the fills.

    Parameters
    ----------
        input_path : str
            Path to the ``.uge`` file.
        strategy : str
            ``'min'`` (default) or ``'mean'``.

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
    res = scan_uge(input_path, strategy)
    if res.vol_fill is None:
        raise ValueError("no finite positive volumes to derive a fill value from")
    return res.vol_fill, res.area_fill


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
        nan_fill : str, float, or tuple
            Fill strategy for NaN/inf entries: ``'min'`` (default), ``'mean'``,
            an explicit number applied to both columns, or an explicit
            ``(vol_fill, area_fill)`` pair. Passing a pair skips the scan, for
            callers that have already run :func:`scan_uge`.

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
    if isinstance(nan_fill, (tuple, list)):
        vol_fill, area_fill = nan_fill
    else:
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
def _fracture_of(self, cell_id):
    """Fracture (material) id for a cell, or ``None`` when unavailable.

    Parameters
    ----------
        self : object
            DFN Class.
        cell_id : int
            One-based cell id from the ``.uge`` file.

    Returns
    -------
        int or None
    """
    try:
        return int(self.material_ids[cell_id - 1])
    except (AttributeError, IndexError, TypeError, ValueError):
        return None


def _report_scan(self, res):
    """Log every invalid coefficient and enforce the correction policy.

    Writes one line per offending cell and per offending connection to both the
    screen and the log (``print_log`` at ``info`` level does both), then decides
    whether the mesh may be corrected:

      * rFram off and anything invalid -> hard error.
      * invalid cells or invalid connections above :data:`BAD_FRACTION_LIMIT` of
        their own total -> hard error, regardless of rFram.
      * otherwise -> return, and let the caller apply the correction.

    Parameters
    ----------
        self : object
            DFN Class. Uses ``self.r_fram``, ``self.print_log``, and (when
            available) ``self.material_ids`` to name the fracture a cell is on.
        res : ScanResult
            Output of :func:`scan_uge`.

    Returns
    -------
        bool
            True if a correction must be applied, False if the mesh is clean.

    Notes
    -----
        Exits the run via ``print_log(..., 'error')`` when the mesh is rejected.
        The offending entries are dumped *before* that decision, so the listing
        is available in both the pass and the fail case.
    """
    n_bad_cells = len(res.bad_cells)
    n_bad_conns = len(res.bad_conns)
    if not n_bad_cells and not n_bad_conns:
        return False

    cell_frac = n_bad_cells / res.n_cells if res.n_cells else 0.0
    conn_frac = n_bad_conns / res.n_conns if res.n_conns else 0.0

    self.print_log(
        f"--> Invalid geometric coefficients in {res.path}: "
        f"{n_bad_cells} of {res.n_cells} cells ({100 * cell_frac:0.4f}%), "
        f"{n_bad_conns} of {res.n_conns} connections ({100 * conn_frac:0.4f}%)",
        "warning")

    if n_bad_cells:
        self.print_log("--> Invalid cells:")
        for cid, x, y, z, vol, kind in res.bad_cells:
            frac = _fracture_of(self, cid)
            self.print_log(
                f"      cell {cid:>10d}  fracture {frac if frac is not None else '?':>6}"
                f"  x {x: .12e}  y {y: .12e}  z {z: .12e}"
                f"  volume {vol: .12e}  [{kind}]")

    if n_bad_conns:
        self.print_log("--> Invalid connections:")
        for id1, id2, area, kind in res.bad_conns:
            f1 = _fracture_of(self, id1)
            f2 = _fracture_of(self, id2)
            self.print_log(
                f"      cells {id1:>10d} -> {id2:>10d}"
                f"  fractures {f1 if f1 is not None else '?'} -> "
                f"{f2 if f2 is not None else '?'}"
                f"  area {area: .12e}  [{kind}]")

    if not self.r_fram:
        self.print_log(
            "Error. Invalid geometric coefficients in the UGE file with rFram "
            "turned off.\nWith rFram off the mesh is expected to conform, so "
            "negative or non-finite volumes and areas indicate a meshing "
            "failure rather than a relaxed-constraint artifact, and are not "
            "corrected. See the listing above for the offending cells and "
            "connections.\nExiting\n", "error")

    over = []
    if cell_frac > BAD_FRACTION_LIMIT:
        over.append(f"cells {100 * cell_frac:0.4f}%")
    if conn_frac > BAD_FRACTION_LIMIT:
        over.append(f"connections {100 * conn_frac:0.4f}%")
    if over:
        self.print_log(
            f"Error. Invalid geometric coefficients exceed the "
            f"{100 * BAD_FRACTION_LIMIT:0.2f}% limit ({'; '.join(over)}).\n"
            "The correction is only defensible for a handful of degenerate "
            "cells; at this level the flow solution would not be trustworthy. "
            "Remesh (smaller h, or a less dense network) rather than "
            "correcting. This is common in dense networks and around triple "
            "intersections.\nExiting\n", "error")

    self.print_log(
        f"--> rFram is on and both fractions are below "
        f"{100 * BAD_FRACTION_LIMIT:0.2f}%; correcting "
        "(negative -> absolute value, NaN/inf -> smallest positive value).")
    return True


def correct_uge_file(self, dim=3):
    """Correct the LaGriT ``.uge`` file for the PFLOTRAN flow solver.

    Always runs. The behaviour splits on two independent axes:

      * ``dim`` controls the aperture conversion and the output target. ``dim=3``
        multiplies cell volumes by aperture and connection areas by the mean
        aperture, writing ``<inp>_vol_area.uge``. ``dim=2`` keeps the raw
        ``<inp>.uge`` as the active mesh (no aperture conversion).
      * the mesh is *always* scanned for invalid coefficients first, and
        :func:`_report_scan` decides what happens. Every offending cell and
        connection is written to the screen and the log. A correction (negative
        -> abs, NaN/inf -> smallest positive fill, applied *before* any aperture
        scaling) is only made when ``self.r_fram`` is True and fewer than
        :data:`BAD_FRACTION_LIMIT` of the cells *and* of the connections are
        invalid. Otherwise the run exits with an error.

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

    # Scan before writing anything: the policy below can reject the mesh, and
    # the dim=3 branch streams its output as it reads, so the counts have to be
    # in hand first.
    scan = scan_uge(raw_uge, "min")
    fix = _report_scan(self, scan)      # exits the run if the mesh is rejected

    if fix and scan.vol_fill is None and any(k == "nonfinite"
                                             for *_, k in scan.bad_cells):
        self.print_log(
            "Error. NaN or inf cell volumes but no finite positive volume to "
            "derive a fill value from.\nExiting\n", "error")
    if fix and scan.area_fill is None and any(k == "nonfinite"
                                              for *_, k in scan.bad_conns):
        self.print_log(
            "Error. NaN or inf connection areas but no finite positive area to "
            "derive a fill value from.\nExiting\n", "error")

    if dim == 3:
        out_uge = self.inp_file[:-4] + "_vol_area.uge"
        aperture = self.aperture
        material_ids = self.material_ids
        cell_based = self.cell_based_aperture

        with open(raw_uge, "r") as fin, open(out_uge, "w") as fout:
            cell_header = fin.readline(); fout.write(cell_header)
            cell_lines = []
            for _ in range(int(cell_header.split()[-1])):
                parts = fin.readline().split(None, 5)
                cid = int(parts[0]); vol = float(parts[4])
                if fix:
                    vol, _ = classify_fix(vol, scan.vol_fill)
                idx = cid - 1 if cell_based else material_ids[cid - 1] - 1
                vol *= aperture[idx]
                cell_lines.append(f"{cid}\t{parts[1]}\t{parts[2]}\t{parts[3]}\t{vol:0.12e}\n")
            fout.writelines(cell_lines)

            conn_header = fin.readline(); fout.write(conn_header)
            conn_lines = []
            for _ in range(int(conn_header.split()[-1])):
                parts = fin.readline().split(None, 6)
                id1 = int(parts[0]); id2 = int(parts[1]); area = float(parts[5])
                if fix:
                    area, _ = classify_fix(area, scan.area_fill)
                avg_ap = 0.5 * (aperture[material_ids[id1 - 1] - 1] +
                                aperture[material_ids[id2 - 1] - 1])
                area *= avg_ap
                conn_lines.append(f"{id1}\t{id2}\t{parts[2]}\t{parts[3]}\t{parts[4]}\t{area:0.12e}\n")
            fout.writelines(conn_lines)
        self.uge_file = out_uge
    else:
        if fix:
            # atomic in-place; reuse the fills already found by the scan
            fix_uge_volumes(raw_uge,
                            nan_fill=(scan.vol_fill, scan.area_fill))
        self.uge_file = raw_uge

    self.print_log(f"--> Complete: UGE file -> {self.uge_file} ({time() - t:0.3f} s)")

