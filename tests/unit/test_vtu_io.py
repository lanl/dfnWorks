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
