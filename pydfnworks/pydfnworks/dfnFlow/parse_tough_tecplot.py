import os
import re
import numpy as np
from pathlib import Path

from .pflotran import _sanitize_vtk_field_name

# ---------------------------------------------------------------------------
# Tecplot parsing helpers
# ---------------------------------------------------------------------------

# Maps Tecplot ZONETYPE keyword to the number of nodes per element.
# Used to skip the connectivity block without reading it into memory.
_ZONETYPE_NODES = {
    'FELINESEG':       2,
    'FETRIANGLE':      3,
    'FEQUADRILATERAL': 4,
    'FETETRAHEDRON':   4,
    'FEBRICK':         8,
}


def _parse_tecplot_variables(line: str) -> list[str]:
    """Return the list of variable names from a Tecplot VARIABLES line.

    Tecplot encloses each name in double quotes, e.g.::

        VARIABLES = "X(m)" "Y(m)" "Z(m)" "P(Pa)" "T(degC)"

    Parameters
    ----------
    line:
        The raw VARIABLES line from the Tecplot file.

    Returns
    -------
    list[str]
        Ordered variable names with their units still attached
        (e.g. ``"X(m)"``). Coordinate detection in the caller
        strips the units before comparison.
    """
    return re.findall(r'"([^"]*)"', line)


def _parse_tecplot_zone_header(line: str) -> dict:
    """Parse a Tecplot ZONE header line into a plain dict.

    Handles the subset of keys written by TOUGH3::

        ZONE T="Time  1.09854E+05 s", N=8800, E=25120,
             DATAPACKING=POINT, ZONETYPE=FEBRICK

    Parameters
    ----------
    line:
        The raw ZONE header line.

    Returns
    -------
    dict
        Keys present in the header: ``T`` (str), ``N`` (int),
        ``E`` (int), ``DATAPACKING`` (str), ``ZONETYPE`` (str).
        Missing keys are simply absent from the dict.
    """
    result = {}
    t_match = re.search(r'\bT\s*=\s*"([^"]*)"', line, re.IGNORECASE)
    if t_match:
        result['T'] = t_match.group(1)
    for key in ('N', 'E'):
        m = re.search(rf'\b{key}\s*=\s*(\d+)', line)
        if m:
            result[key] = int(m.group(1))
    for key in ('DATAPACKING', 'ZONETYPE'):
        m = re.search(rf'\b{key}\s*=\s*(\w+)', line, re.IGNORECASE)
        if m:
            result[key] = m.group(1).upper()
    return result


# ---------------------------------------------------------------------------
# Main conversion routine
# ---------------------------------------------------------------------------

def parse_tough_tecplot(self, tecplot_file: str = '', grid_vtk_file: str = '') -> None:
    """Parse TOUGH3 Tecplot output into per-time-step legacy VTK files.

    Reads all ``ZONE`` blocks from a TOUGH3 Tecplot ``.dat`` file — one
    zone per output time — and writes a corresponding
    ``tough_vtk_outputs/<base>-NNN.vtk`` file for each.  The mesh
    geometry is taken from the existing DFNWorks VTK file; only the
    solution fields (everything except X, Y, Z) are extracted from the
    Tecplot data and written as ``POINT_DATA`` scalars.

    Parameters
    ----------
    self:
        The parent DFNWorks object.
    tecplot_file:
        Path to the TOUGH3 Tecplot output file.  If empty, defaults to
        ``<local_dfnFlow_file stem>.dat`` in the current directory.
    grid_vtk_file:
        Path to a VTK file containing the mesh geometry.  If empty,
        ``inp2vtk_python`` is called to produce one from ``self.inp_file``.

    Returns
    -------
    None

    Notes
    -----
    - Variable names are sanitized for legacy VTK compatibility via
      ``_sanitize_vtk_field_name`` (spaces and brackets → underscores).
    - Tecplot allows multiple values per line; data is read by token
      count rather than line count, so non-standard line wrapping is
      handled correctly.
    - The connectivity block present in each Tecplot zone is skipped;
      element topology is taken from the VTK mesh file instead.
    - Output files mirror the naming convention of
      ``parse_pflotran_h5``: ``tough_vtk_outputs/<base>-NNN.vtk``.
    """
    self.print_log('--> Parsing TOUGH3 Tecplot output with Python')

    # ------------------------------------------------------------------ #
    # Resolve the mesh VTK
    # ------------------------------------------------------------------ #
    if grid_vtk_file:
        self.vtk_file = grid_vtk_file
    elif not getattr(self, 'vtk_file', None) or not os.path.exists(self.vtk_file):
        self.inp2vtk_python()
    grid_file = self.vtk_file

    # ------------------------------------------------------------------ #
    # Resolve the Tecplot file
    # ------------------------------------------------------------------ #
    if not tecplot_file:
        tecplot_file = f"{Path(self.local_dfnFlow_file).stem}.dat"
    if not os.path.exists(tecplot_file):
        self.print_log(f"TOUGH3 Tecplot file not found: {tecplot_file}", 'error')
    self.print_log(f"--> Reading Tecplot data from {tecplot_file}")

    # ------------------------------------------------------------------ #
    # Read mesh block from the existing VTK (skip the 3 header lines so
    # we can write our own header, matching parse_pflotran_h5).
    # ------------------------------------------------------------------ #
    with open(grid_file, 'r') as f:
        grid = f.readlines()[3:]

    num_points = None
    for line in grid:
        if 'POINTS' in line:
            num_points = line.strip().split()[1]
            break
    if num_points is None:
        self.print_log(f"Could not find POINTS line in {grid_file}", 'error')

    # ------------------------------------------------------------------ #
    # Output directory
    # ------------------------------------------------------------------ #
    out_dir = 'tough_vtk_outputs'
    os.makedirs(out_dir, exist_ok=True)

    base = Path(self.local_dfnFlow_file).stem
    header_lines = [
        '# vtk DataFile Version 2.0\n',
        'TOUGH3 output\n',
        'ASCII\n',
    ]

    # ------------------------------------------------------------------ #
    # Parse the Tecplot file
    # ------------------------------------------------------------------ #
    variables: list[str] = []
    # Indices of X/Y/Z columns — skipped when writing VTK POINT_DATA.
    coord_indices: set[int] = set()
    # Accumulated zones: list of (zone_title, np.ndarray shape (N, n_vars))
    zones: list[tuple[str, np.ndarray]] = []

    with open(tecplot_file, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        # ---- VARIABLES header ---------------------------------------- #
        if stripped.upper().startswith('VARIABLES'):
            variables = _parse_tecplot_variables(stripped)
            # Identify coordinate columns by stripping units before
            # comparison, e.g. "X(m)" → "X".
            coord_indices = {
                j for j, v in enumerate(variables)
                if v.split('(')[0].strip().upper() in ('X', 'Y', 'Z')
            }
            i += 1
            continue

        # ---- ZONE block ---------------------------------------------- #
        if stripped.upper().startswith('ZONE'):
            header = _parse_tecplot_zone_header(stripped)
            n_pts = header.get('N', 0)
            n_ele = header.get('E', 0)
            zonetype = header.get('ZONETYPE', 'FEBRICK')
            nodes_per_ele = _ZONETYPE_NODES.get(zonetype, 8)
            n_vars = len(variables)
            i += 1

            # Read n_pts * n_vars floats.  Tecplot allows multiple values
            # per line, so accumulate tokens until the count is satisfied
            # rather than assuming one point per line.
            tokens: list[str] = []
            while len(tokens) < n_pts * n_vars and i < len(lines):
                tokens.extend(lines[i].split())
                i += 1
            data = np.array(tokens[:n_pts * n_vars], dtype=float).reshape(n_pts, n_vars)

            # Skip the connectivity block the same way — count tokens
            # rather than lines, since line wrapping is not guaranteed.
            conn_needed = n_ele * nodes_per_ele
            conn_tokens: list[str] = []
            while len(conn_tokens) < conn_needed and i < len(lines):
                conn_tokens.extend(lines[i].split())
                i += 1

            zones.append((header.get('T', f'Zone {len(zones) + 1}'), data))
            continue

        i += 1

    if not zones:
        self.print_log(f"No zones found in {tecplot_file}", 'error')

    # ------------------------------------------------------------------ #
    # Write one VTK file per zone
    # ------------------------------------------------------------------ #
    for zone_idx, (zone_title, data) in enumerate(zones, start=1):
        out_path = os.path.join(out_dir, f"{base}-{zone_idx:03d}.vtk")
        self.print_log(f"--> Writing {out_path}")

        with open(out_path, 'w') as f:
            for line in header_lines:
                f.write(line)
            for line in grid:
                f.write(line)
            f.write('\n')
            f.write(f"POINT_DATA {num_points}\n")

            for var_idx, var_name in enumerate(variables):
                if var_idx in coord_indices:
                    continue

                values = data[:, var_idx]
                field = _sanitize_vtk_field_name(var_name)

                if np.issubdtype(values.dtype, np.integer):
                    scalar_type = 'int'
                    fmt = '%d'
                else:
                    scalar_type = 'float'
                    fmt = '%.8e'

                f.write(f"SCALARS {field} {scalar_type} 1\n")
                f.write("LOOKUP_TABLE default\n")
                for v in values:
                    f.write(fmt % v)
                    f.write('\n')

    self.print_log('--> Parsing TOUGH3 Tecplot output complete')
