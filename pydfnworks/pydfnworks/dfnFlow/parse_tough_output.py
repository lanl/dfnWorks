import os
import re
import numpy as np
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape


# ---------------------------------------------------------------------------
# INP mesh cell types (AVS/UCD → VTK type codes)
# ---------------------------------------------------------------------------

_VTK_CELL_TYPES = {
    "line":    3,
    "tri":     5,
    "quad":    9,
    "tet":    10,
    "hex":    12,
    "prism":  13,
    "pyramid":14,
}

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


def _sanitize_vtk_name(name: str) -> str:
    """Return a VTK-safe scalar field name (alphanumeric + underscores only)."""
    cleaned = re.sub(r'[^0-9A-Za-z_]+', '_', name.strip()).strip('_') or 'field'
    return f'_{cleaned}' if cleaned[0].isdigit() else cleaned


# ---------------------------------------------------------------------------
# INP mesh reader (AVS/UCD format produced by DFNWorks/LaGriT)
# ---------------------------------------------------------------------------

def _parse_inp_mesh(inp_file: Path) -> dict:
    """Read mesh topology and material IDs from an AVS/UCD INP file.

    Parameters
    ----------
    inp_file:
        Path to ``full_mesh.inp`` produced by LaGriT.

    Returns
    -------
    dict with keys:
        ``points``      – list of (x, y, z) tuples
        ``cells``       – list of 0-based node-index lists, one per cell
        ``cell_types``  – list of VTK type codes, one per cell
        ``material_ids``– list of integer material IDs, one per cell
    """
    with inp_file.open('r', encoding='utf-8') as f:
        header = f.readline().split()
        if len(header) < 2:
            raise ValueError(f"{inp_file} does not start with a valid AVS/UCD header")
        num_nodes = int(header[0])
        num_cells = int(header[1])

        points = []
        for i in range(num_nodes):
            fields = f.readline().split()
            if len(fields) < 4:
                raise ValueError(f"Node line {i + 2} has fewer than 4 fields")
            points.append((float(fields[1]), float(fields[2]), float(fields[3])))

        cells, cell_types, material_ids = [], [], []
        for i in range(num_cells):
            fields = f.readline().split()
            if len(fields) < 4:
                raise ValueError(f"Cell line {num_nodes + 2 + i} has fewer than 4 fields")
            material_ids.append(int(fields[1]))
            cell_type = fields[2].lower()
            if cell_type not in _VTK_CELL_TYPES:
                raise ValueError(f"Unsupported INP cell type '{fields[2]}'")
            cells.append([int(n) - 1 for n in fields[3:]])  # INP is 1-based
            cell_types.append(_VTK_CELL_TYPES[cell_type])

    return dict(points=points, cells=cells, cell_types=cell_types, material_ids=material_ids)


# ---------------------------------------------------------------------------
# VTU / PVD writers
# ---------------------------------------------------------------------------

def _write_vtu(
    vtu_file: Path,
    mesh: dict,
    variables: list[str],
    data: np.ndarray,
    coord_indices: set[int],
) -> None:
    """Write one XML VTK unstructured-grid (.vtu) file.

    Parameters
    ----------
    vtu_file:
        Destination path.
    mesh:
        Dict returned by ``_parse_inp_mesh``.
    variables:
        Full variable list from the Tecplot header.
    data:
        Array of shape ``(n_points, n_vars)`` for this zone.
    coord_indices:
        Column indices of X/Y/Z variables to skip.
    """
    connectivity = ' '.join(str(n) for cell in mesh['cells'] for n in cell)
    offsets, offset = [], 0
    for cell in mesh['cells']:
        offset += len(cell)
        offsets.append(offset)

    with vtu_file.open('w', encoding='utf-8', newline='\n') as f:
        f.write('<?xml version="1.0"?>\n')
        f.write('<VTKFile type="UnstructuredGrid" version="0.1" byte_order="LittleEndian">\n')
        f.write('  <UnstructuredGrid>\n')
        f.write(f'    <Piece NumberOfPoints="{len(mesh["points"])}" '
                f'NumberOfCells="{len(mesh["cells"])}">\n')

        # ---- solution variables as POINT_DATA --------------------------- #
        f.write('      <PointData Scalars="Scalars">\n')
        for var_idx, var_name in enumerate(variables):
            if var_idx in coord_indices:
                continue
            field_name = escape(_sanitize_vtk_name(var_name))
            values = data[:, var_idx]
            f.write(f'        <DataArray type="Float64" Name="{field_name}" format="ascii">\n')
            f.write('          ' + ' '.join(f'{v:.8e}' for v in values) + '\n')
            f.write('        </DataArray>\n')
        f.write('      </PointData>\n')

        # ---- material IDs as CELL_DATA ---------------------------------- #
        f.write('      <CellData Scalars="material_id">\n')
        f.write('        <DataArray type="Int32" Name="material_id" format="ascii">\n')
        f.write('          ' + ' '.join(str(m) for m in mesh['material_ids']) + '\n')
        f.write('        </DataArray>\n')
        f.write('      </CellData>\n')

        # ---- node coordinates ------------------------------------------- #
        f.write('      <Points>\n')
        f.write('        <DataArray type="Float64" NumberOfComponents="3" format="ascii">\n')
        f.write('          ' + ' '.join(f'{c:.12e}' for pt in mesh['points'] for c in pt) + '\n')
        f.write('        </DataArray>\n')
        f.write('      </Points>\n')

        # ---- cell topology ---------------------------------------------- #
        f.write('      <Cells>\n')
        f.write('        <DataArray type="Int32" Name="connectivity" format="ascii">\n')
        f.write(f'          {connectivity}\n')
        f.write('        </DataArray>\n')
        f.write('        <DataArray type="Int32" Name="offsets" format="ascii">\n')
        f.write('          ' + ' '.join(str(o) for o in offsets) + '\n')
        f.write('        </DataArray>\n')
        f.write('        <DataArray type="UInt8" Name="types" format="ascii">\n')
        f.write('          ' + ' '.join(str(ct) for ct in mesh['cell_types']) + '\n')
        f.write('        </DataArray>\n')
        f.write('      </Cells>\n')

        f.write('    </Piece>\n')
        f.write('  </UnstructuredGrid>\n')
        f.write('</VTKFile>\n')


def _write_pvd(pvd_file: Path, datasets: list[tuple[float, str]]) -> None:
    """Write a ParaView collection (.pvd) file for a VTU time series.

    Parameters
    ----------
    pvd_file:
        Destination path (e.g. ``tough_vtk_outputs/tough.pvd``).
    datasets:
        List of ``(time, vtu_filename)`` pairs in chronological order.
        ``vtu_filename`` should be relative to ``pvd_file``'s directory.
    """
    vtkfile = ET.Element(
        'VTKFile', type='Collection', version='0.1', byte_order='LittleEndian'
    )
    collection = ET.SubElement(vtkfile, 'Collection')
    for time, vtu_path in datasets:
        ET.SubElement(collection, 'DataSet',
                      timestep=f'{time:.8e}', group='', part='0', file=vtu_path)
    ET.indent(vtkfile, space='  ')
    ET.ElementTree(vtkfile).write(pvd_file, encoding='utf-8', xml_declaration=True)


# ---------------------------------------------------------------------------
# Main class method
# ---------------------------------------------------------------------------

def parse_tough_output(self, tecplot_file: str = '', inp_file: str = '') -> None:
    """Parse TOUGH3 Tecplot output into a per-timestep VTU/PVD time series.

    Reads all ``ZONE`` blocks from a TOUGH3 (or TOUGH+) Tecplot output file
    — one zone per output time — and writes:

    - ``tough_vtk_outputs/<base>-NNNN.vtu`` for each timestep
    - ``tough_vtk_outputs/tough.pvd`` ParaView collection with correct time values

    Mesh geometry and topology are read from ``full_mesh.inp`` (AVS/UCD
    format produced by LaGriT).  Only solution fields (all variables except
    X, Y, Z) are written as ``PointData``; element material IDs are written
    as ``CellData``.

    Parameters
    ----------
    self:
        The parent DFNWorks object.
    tecplot_file:
        Path to the TOUGH Tecplot output file.  Defaults to
        ``<local_dfnFlow_file stem>.dat``.
    inp_file:
        Path to the AVS/UCD mesh file.  Defaults to ``self.inp_file``
        (``full_mesh.inp``).

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
    mesh = _parse_inp_mesh(inp_path)

    # ------------------------------------------------------------------ #
    # Resolve the Tecplot file
    # ------------------------------------------------------------------ #
    if not tecplot_file:
        tecplot_file = 'Plot_Data_Elem'
    if not os.path.exists(tecplot_file):
        self.print_log(f"TOUGH Tecplot file not found: {tecplot_file}", 'error')
    self.print_log(f"--> Reading Tecplot data from {tecplot_file}")

    # ------------------------------------------------------------------ #
    # Output directory
    # ------------------------------------------------------------------ #
    out_dir = Path('tough_vtk_outputs')
    out_dir.mkdir(parents=True, exist_ok=True)
    base = Path(tecplot_file).stem

    # ------------------------------------------------------------------ #
    # Parse the Tecplot file
    # ------------------------------------------------------------------ #
    variables: list[str] = []
    coord_indices: set[int] = set()
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
            coord_indices = {
                j for j, v in enumerate(variables)
                if v.split('(')[0].strip().upper() in ('X', 'Y', 'Z')
            }
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

    if not zones:
        self.print_log(f"No zones found in {tecplot_file}", 'error')

    # ------------------------------------------------------------------ #
    # Write one VTU per zone and collect PVD entries
    # ------------------------------------------------------------------ #
    pvd_datasets: list[tuple[float, str]] = []

    for zone_idx, (zone_time, data) in enumerate(zones, start=1):
        if data.shape[0] != len(mesh['points']):
            self.print_log(
                f"Zone {zone_idx} at time {zone_time:g} has {data.shape[0]} rows "
                f"but mesh has {len(mesh['points'])} nodes — skipping", 'warning')
            continue

        vtu_name = f"{base}-{zone_idx:04d}.vtu"
        vtu_path = out_dir / vtu_name
        self.print_log(f"--> Writing {vtu_path}")
        _write_vtu(vtu_path, mesh, variables, data, coord_indices)
        pvd_datasets.append((zone_time, vtu_name))

    pvd_path = out_dir / 'tough.pvd'
    _write_pvd(pvd_path, pvd_datasets)
    self.print_log(f"--> Wrote {len(pvd_datasets)} VTU files and {pvd_path}")
    self.print_log('--> Parsing TOUGH output complete')
