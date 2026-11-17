"""
.. module:: vtu_io.py
   :synopsis: Read AVS/UCD (.inp) meshes and write XML VTK unstructured-grid
              (.vtu) files and ParaView collection (.pvd) time series.

The writers use only the standard library and numpy. Data arrays are written
either as inline base64-encoded binary (the default, compact and fast to load)
or as ASCII (human-readable, for debugging and small tests).

Adapted from the VTU/PVD writer in the TOUGH output parser so that all
dfnWorks flow parsers share one implementation.
"""

import base64
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np

# AVS/UCD cell type -> VTK cell type code
VTK_CELL_TYPES = {
    "line": 3,
    "tri": 5,
    "quad": 9,
    "tet": 10,
    "hex": 12,
    "prism": 13,
    "pyramid": 14,
}

# numpy dtype kind/size -> VTK DataArray type name
_VTK_TYPE_NAMES = {
    ("f", 4): "Float32",
    ("f", 8): "Float64",
    ("i", 1): "Int8",
    ("i", 2): "Int16",
    ("i", 4): "Int32",
    ("i", 8): "Int64",
    ("u", 1): "UInt8",
    ("u", 2): "UInt16",
    ("u", 4): "UInt32",
    ("u", 8): "UInt64",
}


def sanitize_name(name):
    """Return a VTK-safe array name (letters, digits and underscores only).

    Parameters
    ----------
        name : str
            Original field name, e.g. ``'Liquid Pressure [Pa]'``.

    Returns
    -------
        str
            Sanitized name, e.g. ``'Liquid_Pressure_Pa'``. Names that would
            start with a digit get a leading underscore.
    """
    cleaned = re.sub(r"[^0-9A-Za-z_]+", "_", str(name).strip()).strip("_") or "field"
    return f"_{cleaned}" if cleaned[0].isdigit() else cleaned


def read_inp_mesh(inp_file):
    """Read mesh topology and material IDs from an AVS/UCD (.inp) file.

    Parameters
    ----------
        inp_file : str or Path
            Path to an AVS/UCD mesh such as ``full_mesh.inp`` written by LaGriT.

    Returns
    -------
        mesh : dict
            ``points`` (n_points, 3) float64 array,
            ``connectivity`` 1-D int64 array of 0-based node indices,
            ``offsets`` 1-D int64 array (end offset of each cell in connectivity),
            ``cell_types`` 1-D uint8 array of VTK cell type codes,
            ``material_ids`` 1-D int32 array, one per cell.

    Notes
    -----
        Supported cell types: line, tri, quad, tet, hex, prism, pyramid.
        Node and cell attribute blocks after the topology are ignored.
    """
    inp_file = Path(inp_file)
    with inp_file.open("r") as f:
        header = f.readline().split()
        if len(header) < 2:
            raise ValueError(f"{inp_file} does not start with a valid AVS/UCD header")
        num_nodes, num_cells = int(header[0]), int(header[1])

        node_lines = [f.readline() for _ in range(num_nodes)]
        points = np.loadtxt(node_lines, usecols=(1, 2, 3), ndmin=2, dtype=np.float64)
        if points.shape[0] != num_nodes:
            raise ValueError(f"{inp_file}: expected {num_nodes} nodes, read {points.shape[0]}")

        connectivity, offsets = [], np.empty(num_cells, dtype=np.int64)
        cell_types = np.empty(num_cells, dtype=np.uint8)
        material_ids = np.empty(num_cells, dtype=np.int32)
        end = 0
        for i in range(num_cells):
            fields = f.readline().split()
            if len(fields) < 4:
                raise ValueError(f"{inp_file}: cell line {num_nodes + 2 + i} has fewer than 4 fields")
            cell_type = fields[2].lower()
            if cell_type not in VTK_CELL_TYPES:
                raise ValueError(f"{inp_file}: unsupported cell type '{fields[2]}'")
            nodes = fields[3:]
            connectivity.extend(nodes)
            end += len(nodes)
            offsets[i] = end
            cell_types[i] = VTK_CELL_TYPES[cell_type]
            material_ids[i] = int(fields[1])

    connectivity = np.asarray(connectivity, dtype=np.int64) - 1  # INP is 1-based
    return dict(points=points,
                connectivity=connectivity,
                offsets=offsets,
                cell_types=cell_types,
                material_ids=material_ids)


def _index_dtype(values):
    """Smallest of Int32/Int64 that holds the values (VTK reads either)."""
    return np.int32 if values.size == 0 or values.max() < 2**31 - 1 else np.int64


def _data_array(name, values, binary, n_components=1):
    """Return the XML text of one DataArray element."""
    values = np.ascontiguousarray(values)
    kind = values.dtype.kind
    if kind == "b":
        values = values.astype(np.uint8)
        kind = "u"
    type_name = _VTK_TYPE_NAMES.get((kind, values.dtype.itemsize))
    if type_name is None:
        values = values.astype(np.float64)
        type_name = "Float64"

    attrs = f'type="{type_name}"'
    if name is not None:
        attrs += f' Name="{escape(name)}"'
    if n_components > 1:
        attrs += f' NumberOfComponents="{n_components}"'

    if binary:
        raw = values.astype(values.dtype.newbyteorder("<"), copy=False).tobytes()
        payload = np.uint32(len(raw)).tobytes() + raw
        text = base64.b64encode(payload).decode("ascii")
        return f'<DataArray {attrs} format="binary">{text}</DataArray>\n'

    if kind == "f":
        text = " ".join(f"{v:.12e}" for v in values.ravel())
    else:
        text = " ".join(str(int(v)) for v in values.ravel())
    return f'<DataArray {attrs} format="ascii">{text}</DataArray>\n'


def _field_block(tag, fields, n_entities, binary):
    """Write a PointData or CellData block; returns XML text."""
    if not fields:
        return ""
    parts = [f"      <{tag}>\n"]
    for name, values in fields.items():
        values = np.asarray(values)
        if values.ndim == 1:
            n_comp = 1
        elif values.ndim == 2:
            n_comp = values.shape[1]
        else:
            raise ValueError(f"{tag} field '{name}' must be 1-D or 2-D, got shape {values.shape}")
        if values.shape[0] != n_entities:
            raise ValueError(f"{tag} field '{name}' has {values.shape[0]} values, expected {n_entities}")
        parts.append("        " + _data_array(sanitize_name(name), values, binary, n_comp))
    parts.append(f"      </{tag}>\n")
    return "".join(parts)


def write_vtu(vtu_file, mesh, point_data=None, cell_data=None, binary=True):
    """Write one XML VTK unstructured-grid (.vtu) file.

    Parameters
    ----------
        vtu_file : str or Path
            Destination path.

        mesh : dict
            Mesh returned by :func:`read_inp_mesh`.

        point_data : dict, optional
            ``{name: array}``. Each array has one value per mesh node (1-D) or
            ``(n_points, k)`` values for a k-component vector.

        cell_data : dict, optional
            ``{name: array}`` with one value (or row) per cell. The mesh's
            material IDs are always written as the cell array ``material_id``.

        binary : bool
            If True (default), data arrays are inline base64-encoded binary.
            If False, they are written as ASCII text.

    Returns
    -------
        None
    """
    vtu_file = Path(vtu_file)
    n_points = mesh["points"].shape[0]
    n_cells = mesh["cell_types"].shape[0]

    cells = {"material_id": mesh["material_ids"]}
    if cell_data:
        cells.update(cell_data)

    connectivity = mesh["connectivity"].astype(_index_dtype(mesh["connectivity"]), copy=False)
    offsets = mesh["offsets"].astype(_index_dtype(mesh["offsets"]), copy=False)

    with vtu_file.open("w", encoding="utf-8", newline="\n") as f:
        f.write('<?xml version="1.0"?>\n')
        f.write('<VTKFile type="UnstructuredGrid" version="1.0" '
                'byte_order="LittleEndian" header_type="UInt32">\n')
        f.write("  <UnstructuredGrid>\n")
        f.write(f'    <Piece NumberOfPoints="{n_points}" NumberOfCells="{n_cells}">\n')
        f.write(_field_block("PointData", point_data, n_points, binary))
        f.write(_field_block("CellData", cells, n_cells, binary))
        f.write("      <Points>\n")
        f.write("        " + _data_array(None, mesh["points"].astype(np.float64, copy=False), binary, 3))
        f.write("      </Points>\n")
        f.write("      <Cells>\n")
        f.write("        " + _data_array("connectivity", connectivity, binary))
        f.write("        " + _data_array("offsets", offsets, binary))
        f.write("        " + _data_array("types", mesh["cell_types"].astype(np.uint8, copy=False), binary))
        f.write("      </Cells>\n")
        f.write("    </Piece>\n")
        f.write("  </UnstructuredGrid>\n")
        f.write("</VTKFile>\n")


def write_pvd(pvd_file, datasets):
    """Write a ParaView collection (.pvd) file for a .vtu time series.

    Parameters
    ----------
        pvd_file : str or Path
            Destination path, e.g. ``pflotran_vtu_outputs/dfn_explicit.pvd``.

        datasets : list of (float, str)
            ``(time, vtu_path)`` pairs in chronological order. ``vtu_path`` is
            relative to the directory containing ``pvd_file``.

    Returns
    -------
        None
    """
    root = ET.Element("VTKFile", type="Collection", version="0.1", byte_order="LittleEndian")
    collection = ET.SubElement(root, "Collection")
    for time, vtu_path in datasets:
        ET.SubElement(collection, "DataSet",
                      timestep=f"{float(time):.12e}", group="", part="0", file=str(vtu_path))
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(Path(pvd_file), encoding="utf-8", xml_declaration=True)
