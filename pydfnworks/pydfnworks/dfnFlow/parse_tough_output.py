import os
import re
import numpy as np
from pathlib import Path

from pydfnworks.general.vtu_io import read_inp_mesh, write_vtu, write_pvd

# Output directory for the .vtu/.pvd time series (mirrors pflotran_vtu_outputs).
TOUGH_VTU_DIR = 'tough_vtu_outputs'

# Maps Tecplot ZONETYPE to nodes-per-element (for skipping connectivity blocks).
_ZONETYPE_NODES = {
    'FELINESEG':        2,
    'FETRIANGLE':       3,
    'FEQUADRILATERAL':  4,
    'FETETRAHEDRON':    4,
    'FEBRICK':          8,
}


# ---------------------------------------------------------------------------
# Tecplot parsing helpers
# ---------------------------------------------------------------------------

def _parse_tecplot_variables(line: str) -> list[str]:
    """Return variable names from a Tecplot VARIABLES line.

    Handles both quoted names (TOUGH3)::

        VARIABLES = "X(m)" "Y(m)" "Z(m)" "P(Pa)"

    and unquoted names (TOUGH+)::

        VARIABLES = x y z P T SG SW

    Parameters
    ----------
    line:
        The raw VARIABLES line from the Tecplot file.

    Returns
    -------
    list[str]
        Ordered variable names. Units (if present) are kept attached;
        coordinate detection in the caller strips them before comparison.
    """
    _, _, rhs = line.partition('=')
    quoted = re.findall(r'"([^"]*)"', rhs)
    return quoted if quoted else rhs.split()


def _parse_tecplot_zone_header(line: str) -> dict:
    """Parse a Tecplot ZONE header into a plain dict.

    Handles both ordered zones (TOUGH+)::

        ZONE T="1.09854E+05" I=8800

    and unstructured FE zones (TOUGH3)::

        ZONE T="Time  1.09854E+05 s", N=8800, E=25120,
             DATAPACKING=POINT, ZONETYPE=FEBRICK

    Parameters
    ----------
    line:
        The raw ZONE header line.

    Returns
    -------
    dict
        Populated keys from: ``T`` (str), ``I`` (int), ``N`` (int),
        ``E`` (int), ``DATAPACKING`` (str), ``ZONETYPE`` (str).
        Missing keys are absent from the dict.
    """
    result = {}
    t_match = re.search(r'\bT\s*=\s*"([^"]*)"', line, re.IGNORECASE)
    if t_match:
        result['T'] = t_match.group(1)
    # I= is the ordered-zone row count; N= and E= are the unstructured equivalents.
    for key in ('I', 'N', 'E'):
        m = re.search(rf'\b{key}\s*=\s*(\d+)', line)
        if m:
            result[key] = int(m.group(1))
    for key in ('DATAPACKING', 'ZONETYPE'):
        m = re.search(rf'\b{key}\s*=\s*(\w+)', line, re.IGNORECASE)
        if m:
            result[key] = m.group(1).upper()
    return result


def _extract_zone_time(zone_title: str) -> float:
    """Extract the first floating-point number from a zone title string.

    Handles both bare floats (TOUGH+: ``"1.09854E+05"``) and prefixed
    strings (TOUGH3: ``"Time  1.09854E+05 s"``).

    Returns 0.0 if no number is found.
    """
    match = re.search(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', zone_title)
    return float(match.group()) if match else 0.0


# ---------------------------------------------------------------------------
# TOUGH output readers
# ---------------------------------------------------------------------------

def _parse_tough_tecplot(tecplot_file) -> tuple[list[str], list[tuple[float, np.ndarray]]]:
    """Read all ZONE blocks from a TOUGH3 / TOUGH+ Tecplot file.

    Returns
    -------
    tuple
        ``(variables, zones)`` where ``zones`` is a list of
        ``(simulation_time, data)`` with ``data`` of shape ``(n_pts, n_vars)``.
    """
    variables: list[str] = []
    # Each entry: (simulation_time, data_array shape (n_pts, n_vars))
    zones: list[tuple[float, np.ndarray]] = []

    with open(tecplot_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        upper = stripped.upper()

        # ---- VARIABLES header ---------------------------------------- #
        if upper.startswith('VARIABLES'):
            variables = _parse_tecplot_variables(stripped)
            i += 1
            continue

        # ---- ZONE block ---------------------------------------------- #
        if upper.startswith('ZONE'):
            header = _parse_tecplot_zone_header(stripped)
            zone_time = _extract_zone_time(header.get('T', '0'))

            # I= (ordered) takes priority; fall back to N= (unstructured).
            n_pts = header.get('I') or header.get('N', 0)
            n_ele = header.get('E', 0)  # 0 for ordered zones
            zonetype = header.get('ZONETYPE', 'FEBRICK')
            nodes_per_ele = _ZONETYPE_NODES.get(zonetype, 8)
            n_vars = len(variables)
            i += 1

            # Accumulate data tokens regardless of line wrapping.
            tokens: list[str] = []
            while len(tokens) < n_pts * n_vars and i < len(lines):
                tokens.extend(lines[i].split())
                i += 1
            data = np.array(tokens[:n_pts * n_vars], dtype=float).reshape(n_pts, n_vars)

            # Skip connectivity block (unstructured zones only).
            if n_ele > 0:
                conn_needed = n_ele * nodes_per_ele
                conn_tokens: list[str] = []
                while len(conn_tokens) < conn_needed and i < len(lines):
                    conn_tokens.extend(lines[i].split())
                    i += 1

            zones.append((zone_time, data))
            continue

        i += 1

    return variables, zones


def _is_tough_csv(tough_file) -> bool:
    """Return True if ``tough_file`` looks like TOUGH3 CSV output (``OUTPUT_ELEME.csv``)."""
    if Path(tough_file).suffix.lower() == '.csv':
        return True
    with open(tough_file, 'r', encoding='utf-8') as f:
        first = f.readline().strip()
    return first.startswith('"') and ',' in first


def _parse_tough_csv(csv_file) -> tuple[list[str], list[tuple[float, np.ndarray]]]:
    """Read TOUGH3 CSV element output (``OUTPUT_ELEME.csv``).

    Expected layout::

        "ELEM","X","Y","Z","ROCK","PRES",...     <- variable names
        "","(M)","(M)","(M)","","(PA)",...      <- units
        "TIME [sec]  0.18884456E+08"            <- starts each timestep
        "AAA 1", -0.25E+003, ..., 0.10E-001     <- one row per element

    The leading ``ELEM`` column (element name) is dropped.

    Returns
    -------
    tuple
        ``(variables, zones)`` where ``zones`` is a list of
        ``(simulation_time, data)`` with ``data`` of shape ``(n_rows, n_vars)``.
    """
    variables: list[str] = []
    zones: list[tuple[float, np.ndarray]] = []
    zone_time = None
    rows: list[list[float]] = []

    with open(csv_file, 'r', encoding='utf-8') as f:
        names = [v.strip().strip('"').strip() for v in f.readline().split(',')]
        variables = names[1:]  # drop ELEM
        f.readline()  # units line
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.upper().startswith('"TIME'):
                if zone_time is not None:
                    zones.append((zone_time, np.array(rows, dtype=float)))
                zone_time = _extract_zone_time(stripped.split(']', 1)[-1])
                rows = []
                continue
            fields = stripped.split(',')
            rows.append([float(v) for v in fields[1:]])

    if zone_time is not None:
        zones.append((zone_time, np.array(rows, dtype=float)))
    return variables, zones


# ---------------------------------------------------------------------------
# Main class method
# ---------------------------------------------------------------------------

def parse_tough_output(self, tecplot_file: str = '', inp_file: str = '', binary: bool = True) -> None:
    """Parse TOUGH3 Tecplot or CSV output into a per-timestep VTU/PVD time series.

    Reads all ``ZONE`` blocks from a TOUGH3 (or TOUGH+) Tecplot output file,
    or all ``"TIME [sec] ..."`` blocks from a TOUGH3 CSV file
    (``OUTPUT_ELEME.csv``) — one block per output time — and writes:

    - ``tough_vtu_outputs/<base>-NNNN.vtu`` for each timestep
    - ``tough_vtu_outputs/<base>.pvd`` ParaView collection with correct time values

    where ``<base>`` is the stem of the TOUGH output file (e.g. ``OUTPUT_ELEME``).

    Mesh geometry and topology are read from ``full_mesh.inp`` (AVS/UCD
    format produced by LaGriT).  Only solution fields (all variables except
    X, Y, Z) are written as ``PointData``; element material IDs are written
    as ``CellData``.

    Parameters
    ----------
    self:
        The parent DFNWorks object.
    tecplot_file:
        Path to the TOUGH Tecplot or CSV output file.  Files ending in
        ``.csv`` (or whose first line is quoted, comma-separated names) are
        read as TOUGH3 CSV.  Defaults to ``Plot_Data_Elem``.
    inp_file:
        Path to the AVS/UCD mesh file.  Defaults to ``self.inp_file``
        (``full_mesh.inp``).
    binary:
        If True (default), data arrays are base64-encoded binary. If False,
        they are written as ASCII text (larger, but human-readable).

    Returns
    -------
    None

    Notes
    -----
    - Both quoted variable names (TOUGH3: ``"X(m)"``) and unquoted names
      (TOUGH+: ``x``) are handled automatically.
    - Both ordered zones (``I=``, TOUGH+) and unstructured FE zones
      (``N=`` / ``E=``, TOUGH3) are supported.  Connectivity blocks are
      skipped by token count when present.
    - Tecplot allows multiple values per line; data is accumulated by
      token count rather than line count.
    - The PVD file encodes actual simulation times so ParaView's time
      slider maps to physical time rather than sequential file indices.
    - Files are written with ``pydfnworks.general.vtu_io``, the same writer
      used by ``parse_pflotran_vtk`` and ``parse_pflotran_h5``.
    """
    self.print_log('--> Parsing TOUGH output with Python')

    # ------------------------------------------------------------------ #
    # Resolve the INP mesh file
    # ------------------------------------------------------------------ #
    if not inp_file:
        inp_file = getattr(self, 'inp_file', 'full_mesh.inp')
    inp_path = Path(inp_file)
    if not inp_path.is_file():
        self.print_log(f"INP mesh file not found: {inp_path}", 'error')
    self.print_log(f"--> Reading mesh from {inp_path}")
    mesh = read_inp_mesh(inp_path)

    # ------------------------------------------------------------------ #
    # Resolve the Tecplot file
    # ------------------------------------------------------------------ #
    if not tecplot_file:
        tecplot_file = 'Plot_Data_Elem'
    if not os.path.exists(tecplot_file):
        self.print_log(f"TOUGH Tecplot file not found: {tecplot_file}", 'error')
    self.print_log(f"--> Reading TOUGH output from {tecplot_file}")

    # ------------------------------------------------------------------ #
    # Output directory
    # ------------------------------------------------------------------ #
    out_dir = Path(TOUGH_VTU_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = Path(tecplot_file).stem

    # ------------------------------------------------------------------ #
    # Parse the TOUGH output (Tecplot or CSV)
    # ------------------------------------------------------------------ #
    if _is_tough_csv(tecplot_file):
        variables, zones = _parse_tough_csv(tecplot_file)
    else:
        variables, zones = _parse_tough_tecplot(tecplot_file)
    coord_indices = {
        j for j, v in enumerate(variables)
        if v.split('(')[0].strip().upper() in ('X', 'Y', 'Z')
    }

    if not zones:
        self.print_log(f"No zones found in {tecplot_file}", 'error')

    # Check that output rows follow the INP node ordering.
    xyz_idx = sorted(coord_indices)
    first = zones[0][1]
    if len(xyz_idx) == 3 and first.shape[0] == mesh['points'].shape[0]:
        pts = mesh['points']
        # TOUGH MESH coordinates are written at reduced precision.
        tol = 1e-3 * max(np.ptp(pts, axis=0).max(), 1.0)
        if not np.allclose(first[:, xyz_idx], pts, atol=tol):
            self.print_log("TOUGH output coordinates do not match INP node "
                           "coordinates; element order may differ from node order",
                           'warning')

    # ------------------------------------------------------------------ #
    # Write one VTU per zone and collect PVD entries
    # ------------------------------------------------------------------ #
    pvd_datasets: list[tuple[float, str]] = []
    n_points = mesh['points'].shape[0]
    fields = [(j, v) for j, v in enumerate(variables) if j not in coord_indices]

    for zone_idx, (zone_time, data) in enumerate(zones, start=1):
        if data.shape[0] != n_points:
            self.print_log(
                f"Zone {zone_idx} at time {zone_time:g} has {data.shape[0]} rows "
                f"but mesh has {n_points} nodes — skipping", 'warning')
            continue

        vtu_name = f"{base}-{zone_idx:04d}.vtu"
        vtu_path = out_dir / vtu_name
        self.print_log(f"--> Writing {vtu_path}")
        point_data = {name: data[:, j] for j, name in fields}
        write_vtu(vtu_path, mesh, point_data=point_data, binary=binary)
        pvd_datasets.append((zone_time, vtu_name))

    pvd_path = out_dir / f'{base}.pvd'
    write_pvd(pvd_path, pvd_datasets)
    self.print_log(f"--> Wrote {len(pvd_datasets)} snapshots to {out_dir}/; open {pvd_path} in ParaView")
    self.print_log('--> Parsing TOUGH output complete')
