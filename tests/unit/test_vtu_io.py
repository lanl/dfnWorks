"""Unit tests for pydfnworks.general.vtu_io.

Run with ``python3 -m pytest tests/unit`` (or ``python3 tests/unit/test_vtu_io.py``).
The round-trip tests read the files back with VTK's own XML reader and are
skipped if the ``vtk`` package is not installed.
"""

import os
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "pydfnworks"))

from pydfnworks.general import vtu_io  # noqa: E402

try:
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy
except ImportError:  # pragma: no cover
    vtk = None

# Two triangles and one tetrahedron sharing nodes; material IDs 1, 2, 7.
INP_TEXT = """6 3 0 0 0
1 0.0 0.0 0.0
2 1.0 0.0 0.0
3 0.0 1.0 0.0
4 1.0 1.0 0.0
5 0.0 0.0 1.0
6 0.5 0.5 0.5
1 1 tri 1 2 3
2 2 tri 2 4 3
3 7 tet 1 2 3 5
"""


def _write_inp(directory):
    path = Path(directory) / "mesh.inp"
    path.write_text(INP_TEXT)
    return path


def test_read_inp_mesh():
    with tempfile.TemporaryDirectory() as d:
        mesh = vtu_io.read_inp_mesh(_write_inp(d))
    assert mesh["points"].shape == (6, 3)
    assert mesh["points"][5].tolist() == [0.5, 0.5, 0.5]
    assert mesh["connectivity"].tolist() == [0, 1, 2, 1, 3, 2, 0, 1, 2, 4]
    assert mesh["offsets"].tolist() == [3, 6, 10]
    assert mesh["cell_types"].tolist() == [5, 5, 10]
    assert mesh["material_ids"].tolist() == [1, 2, 7]


def test_sanitize_name():
    assert vtu_io.sanitize_name("Liquid Pressure [Pa]") == "Liquid_Pressure_Pa"
    assert vtu_io.sanitize_name("1st value") == "_1st_value"
    assert vtu_io.sanitize_name("  ") == "field"


def _read_back(path):
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(str(path))
    reader.Update()
    return reader.GetOutput()


def _check_roundtrip(binary):
    if vtk is None:
        print("SKIP: vtk not installed")
        return
    with tempfile.TemporaryDirectory() as d:
        mesh = vtu_io.read_inp_mesh(_write_inp(d))
        pressure = np.linspace(1.0e6, 2.0e6, 6)
        velocity = np.arange(18, dtype=np.float64).reshape(6, 3) * 1.0e-3
        ids = np.arange(6, dtype=np.int32)
        out = Path(d) / ("bin.vtu" if binary else "ascii.vtu")
        vtu_io.write_vtu(out,
                         mesh,
                         point_data={"Liquid Pressure": pressure, "velocity": velocity, "node_id": ids},
                         cell_data={"aperture": np.array([1e-4, 2e-4, 3e-4])},
                         binary=binary)
        text = out.read_text()
        assert ('format="binary"' in text) == binary
        grid = _read_back(out)

    assert grid.GetNumberOfPoints() == 6
    assert grid.GetNumberOfCells() == 3
    assert [grid.GetCellType(i) for i in range(3)] == [5, 5, 10]
    assert np.allclose(vtk_to_numpy(grid.GetPoints().GetData()), mesh["points"])
    pd, cd = grid.GetPointData(), grid.GetCellData()
    assert np.allclose(vtk_to_numpy(pd.GetArray("Liquid_Pressure")), pressure)
    assert vtk_to_numpy(pd.GetArray("velocity")).shape == (6, 3)
    assert np.allclose(vtk_to_numpy(pd.GetArray("velocity")), velocity)
    assert vtk_to_numpy(pd.GetArray("node_id")).tolist() == ids.tolist()
    assert vtk_to_numpy(cd.GetArray("material_id")).tolist() == [1, 2, 7]
    assert np.allclose(vtk_to_numpy(cd.GetArray("aperture")), [1e-4, 2e-4, 3e-4])
    # second cell (tri 2 4 3) keeps its connectivity
    cell = grid.GetCell(1)
    assert [cell.GetPointId(k) for k in range(3)] == [1, 3, 2]


def test_roundtrip_binary():
    _check_roundtrip(binary=True)


def test_roundtrip_ascii():
    _check_roundtrip(binary=False)


def test_write_pvd():
    with tempfile.TemporaryDirectory() as d:
        pvd = Path(d) / "series.pvd"
        vtu_io.write_pvd(pvd, [(0.0, "a-000.vtu"), (8.64e6, "a-001.vtu")])
        root = ET.parse(pvd).getroot()
    assert root.get("type") == "Collection"
    sets = root.find("Collection").findall("DataSet")
    assert [float(s.get("timestep")) for s in sets] == [0.0, 8.64e6]
    assert [s.get("file") for s in sets] == ["a-000.vtu", "a-001.vtu"]


def test_bad_field_length():
    with tempfile.TemporaryDirectory() as d:
        mesh = vtu_io.read_inp_mesh(_write_inp(d))
        try:
            vtu_io.write_vtu(Path(d) / "x.vtu", mesh, point_data={"p": np.zeros(5)})
        except ValueError as e:
            assert "expected 6" in str(e)
        else:
            raise AssertionError("expected ValueError for wrong field length")


LOG_TEXT = """ --> write vtk output file: dfn_explicit-000.vtk
 Step      1 Time=  1.00000E-01 Dt=  1.00000E-01 [d] conv_reason: 3
 --> write rate output file: dfn_explicit-darcyvel-001
 Step      2 Time=  1.00000E+02 Dt=  9.99000E+01 [d] conv_reason: 3
 --> write vtk output file: dfn_explicit-001.vtk
 Step      3 Time=  3.60000E+03 Dt=  1.00000E+00 [s] conv_reason: 3
 --> write vtk output file: dfn_explicit-002.vtk
"""


def test_pflotran_snapshot_times():
    from pydfnworks.dfnFlow.pflotran import _pflotran_snapshot_times, _parse_time_group
    with tempfile.TemporaryDirectory() as d:
        log = Path(d) / "dfn_explicit.out"
        log.write_text(LOG_TEXT)
        times = _pflotran_snapshot_times(str(log))
        assert _pflotran_snapshot_times(str(Path(d) / "missing.out")) == {}
    assert times == {"dfn_explicit-000.vtk": 0.0,
                     "dfn_explicit-001.vtk": 100 * 86400.0,
                     "dfn_explicit-002.vtk": 3600.0}
    assert _parse_time_group("   1 Time  1.00000E+02 d") == (1, 8.64e6)
    assert _parse_time_group("Provenance") is None


def test_read_pflotran_vtk_fields():
    from pydfnworks.dfnFlow.pflotran import _read_pflotran_vtk_fields
    text = """# vtk DataFile Version 2.0
PFLOTRAN output
ASCII
DATASET UNSTRUCTURED_GRID
CELL_DATA    3
SCALARS Liquid_Pressure      float 1
LOOKUP_TABLE default
 1.0E+06  2.0E+06
 3.0E+06
SCALARS Material_ID          int 1
LOOKUP_TABLE default
 1 1 2
VECTORS Liquid_Velocity float
 1 0 0 0 1 0 0 0 1
"""
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "a-001.vtk"
        f.write_text(text)
        fields = _read_pflotran_vtk_fields(str(f), 3)
    assert fields["Liquid_Pressure"].tolist() == [1e6, 2e6, 3e6]
    assert fields["Material_ID"].dtype.kind == "i" and fields["Material_ID"].tolist() == [1, 1, 2]
    assert fields["Liquid_Velocity"].shape == (3, 3)


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as e:  # noqa: BLE001
                failures += 1
                print(f"FAIL {name}: {e!r}")
    sys.exit(1 if failures else 0)
