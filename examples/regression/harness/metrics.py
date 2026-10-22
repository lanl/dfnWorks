"""Extract scalar metrics from the output files a driver leaves behind.

Each extractor returns (metrics, missing): a flat {key: number} dict and a list
of human-readable names of required files that were not found. Keys are
"<stage>.<name>" so tolerances can be chosen per stage in compare.py.
"""

import glob
import os
import re
from pathlib import Path

import numpy as np

# DFN_output.txt lines we keep (post-isolated-removal block plus totals)
_GEN_KEYS = {
    "Final Number of Fractures": ("final_fractures", int),
    "Isolated Fractures Removed": ("isolated_removed", int),
    "Total Fractures Rejected": ("rejected", int),
    "Total Fractures Re-translated": ("retranslated", int),
    "Total Surface Area": ("surface_area", float),
    "Total Fracture Density   (P30)": ("p30", float),
    "Total Fracture Intensity (P32)": ("p32", float),
    "Number of Intersections": ("n_intersections", int),
    "Intersections Shortened": ("intersections_shortened", int),
    "Final Intersection Length": ("intersection_length", float),
}
_TRIPLE = re.compile(r"Number of Triple Intersection Points.*:\s*(\d+)")


def _num(value, kind):
    value = value.strip().split()[0]
    return kind(float(value)) if kind is int else float(value)


def gen_metrics(outdir):
    path = Path(outdir) / "DFN_output.txt"
    if not path.is_file():
        return {}, ["DFN_output.txt"]
    metrics = {}
    post_iso = False
    for line in path.read_text(errors="replace").splitlines():
        if "Statistics After Isolated Fractures Removed" in line:
            post_iso = True
        m = _TRIPLE.search(line)
        if m:
            metrics["gen.triple_points"] = int(m.group(1))
            continue
        if ": " not in line:
            continue
        key, _, value = line.partition(": ")
        key = key.strip() if key.strip() in ("Number of Intersections", "Intersections Shortened",
                                             "Final Intersection Length") else key.rstrip()
        if key in _GEN_KEYS and value.strip():
            name, kind = _GEN_KEYS[key]
            # bulk stats appear twice (pre/post isolated removal); keep the post block
            if name in ("surface_area", "p30", "p32") and not post_iso:
                continue
            try:
                metrics[f"gen.{name}"] = _num(value, kind)
            except ValueError:
                pass
    return metrics, []


def _inp_header(path):
    with open(path) as fp:
        first = fp.readline().split()
    return int(first[0]), int(first[1])


def mesh_metrics(outdir, visual=False):
    name = "reduced_mesh.inp" if visual else "full_mesh.inp"
    path = Path(outdir) / name
    if not path.is_file():
        return {}, [name]
    nodes, elems = _inp_header(path)
    return {"mesh.nodes": nodes, "mesh.elements": elems}, []


def dfm_metrics(scratch):
    hits = glob.glob(str(Path(scratch) / "**" / "dfm_tet_mesh.inp"), recursive=True)
    if not hits:
        return {}, ["dfm_tet_mesh.inp"]
    nodes, elems = _inp_header(hits[0])
    return {"dfm.nodes": nodes, "dfm.elements": elems}, []


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def pflotran_metrics(outdir, scratch):
    """Last row of every *-mas.dat (PFLOTRAN mass balance) plus effective perm if written."""
    metrics, missing = {}, []
    mas_files = sorted(glob.glob(str(Path(outdir) / "*-mas.dat")))
    if not mas_files:
        missing.append("*-mas.dat")
    for mas in mas_files:
        stem = Path(mas).name[:-len("-mas.dat")]
        with open(mas) as fp:
            lines = [l for l in fp.read().splitlines() if l.strip()]
        if len(lines) < 2:
            missing.append(f"{Path(mas).name} (no data rows)")
            continue
        header = [h.strip().strip('"') for h in lines[0].split(",")]
        values = lines[-1].split()
        for name, val in zip(header, values):
            slug = _slug(name)
            if slug.startswith(("time_", "dt_flow")):
                continue
            metrics[f"pflotran.{stem}.{slug}"] = float(val)
    for keff in glob.glob(str(Path(scratch) / "**" / "*_effective_perm.txt"), recursive=True):
        for line in Path(keff).read_text().splitlines():
            if "effective permeability" in line:
                metrics["pflotran.keff"] = float(line.split(":")[-1])
            elif "mass flow rate" in line:
                metrics["pflotran.mass_rate"] = float(line.split(":")[-1])
    return metrics, missing


def fehm_metrics(outdir):
    stor = Path(outdir) / "full_mesh_vol_area.stor"
    if not stor.is_file():
        return {}, ["full_mesh_vol_area.stor"]
    with open(stor) as fp:
        n = sum(1 for _ in fp)
    return {"fehm.stor_lines": n}, []


def _percentiles(prefix, values):
    values = np.asarray(values, dtype=float)
    return {
        f"{prefix}.n": int(values.size),
        f"{prefix}.mean": float(values.mean()),
        f"{prefix}.p10": float(np.percentile(values, 10)),
        f"{prefix}.p50": float(np.percentile(values, 50)),
        f"{prefix}.p90": float(np.percentile(values, 90)),
    }


def dfntrans_metrics(outdir):
    """DFNTrans travel times from the partime file named by `out_time:`."""
    hits = [p for p in glob.glob(str(Path(outdir) / "**" / "partime*"), recursive=True)
            if not p.endswith(".inp")]
    if not hits:
        return {}, ["partime"]
    try:
        data = np.loadtxt(hits[0], comments="#", ndmin=2)
    except Exception:  # noqa: BLE001
        return {}, [f"{Path(hits[0]).name} (unreadable)"]
    if data.size == 0:
        return {}, [f"{Path(hits[0]).name} (no particles)"]
    metrics = _percentiles("dfntrans.travel_time", data[:, 2])
    metrics["dfntrans.length_mean"] = float(data[:, -1].mean())
    metrics["dfntrans.n_particles"] = metrics.pop("dfntrans.travel_time.n")
    total = Path(hits[0]).parent / "TotalNumberP"
    if total.is_file():
        metrics["dfntrans.total_number_p"] = int(total.read_text().split()[0])
    return metrics, []


def graph_flow_metrics(scratch):
    import h5py
    hits = glob.glob(str(Path(scratch) / "**" / "graph_flow.hdf5"), recursive=True)
    if not hits:
        return {}, ["graph_flow.hdf5"]
    with h5py.File(hits[0], "r") as f5:
        q = np.asarray(f5["vol_flow_rate"])
        vol = np.asarray(f5["volume"])
    return {"graph_flow.n_edges": int(q.size),
            "graph_flow.sum_vol_flow_rate": float(np.abs(q).sum()),
            "graph_flow.sum_volume": float(vol.sum())}, []


def graph_transport_metrics(scratch):
    import h5py
    key = "Total travel time [s]"
    metrics, found = {}, False
    for path in sorted(glob.glob(str(Path(scratch) / "**" / "*.hdf5"), recursive=True)):
        name = Path(path).stem
        if name in ("graph_flow", "trajectories"):
            continue
        with h5py.File(path, "r") as f5:
            if key not in f5:
                continue
            found = True
            metrics.update(_percentiles(f"graph_transport.{name}", np.asarray(f5[key])))
    return metrics, ([] if found else ["<partime>.hdf5 with 'Total travel time [s]'"])


def report_check(outdir):
    hits = glob.glob(str(Path(outdir) / "*_output_report.pdf"))
    return {}, ([] if hits else ["*_output_report.pdf"])


def collect(stages, scratch, outdir):
    """Run every extractor named in `stages`. Returns (metrics, missing)."""
    metrics, missing = {}, []
    for stage in stages:
        if stage == "gen":
            m, miss = gen_metrics(outdir)
        elif stage == "mesh":
            m, miss = mesh_metrics(outdir)
        elif stage == "mesh_visual":
            m, miss = mesh_metrics(outdir, visual=True)
        elif stage == "dfm":
            m, miss = dfm_metrics(scratch)
        elif stage == "pflotran":
            m, miss = pflotran_metrics(outdir, scratch)
        elif stage == "fehm":
            m, miss = fehm_metrics(outdir)
        elif stage == "dfntrans":
            m, miss = dfntrans_metrics(outdir)
        elif stage == "graph_flow":
            m, miss = graph_flow_metrics(scratch)
        elif stage == "graph_transport":
            m, miss = graph_transport_metrics(scratch)
        elif stage == "report":
            m, miss = report_check(outdir)
        else:
            raise ValueError(f"unknown stage {stage!r}")
        metrics.update(m)
        missing.extend(miss)
    return metrics, missing
