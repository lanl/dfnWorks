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


_FEHM_END = re.compile(r"simulation ended:\s+days\s+([-+0-9.Ee]+)\s+timesteps\s+(\d+)")
_FEHM_NR = re.compile(r"total N-R iterations\s*=\s*(\d+)")
_FEHM_CONS = re.compile(r"Conservation Errors:\s+([-+0-9.Ee]+)\s+\(mass\),\s+([-+0-9.Ee]+)\s+\(energy\)")


def fehm_metrics(outdir):
    """Size of the FEHM stor file plus the run summary at the end of the FEHM *.out."""
    metrics, missing = {}, []
    stor = Path(outdir) / "full_mesh_vol_area.stor"
    if stor.is_file():
        with open(stor) as fp:
            metrics["fehm.stor_lines"] = sum(1 for _ in fp)
    else:
        missing.append("full_mesh_vol_area.stor")
    outs = [p for p in glob.glob(str(Path(outdir) / "*.out"))
            if not Path(p).name.endswith(".lgi.out")]
    if not outs:
        missing.append("FEHM *.out")
    for out in outs:
        text = Path(out).read_text(errors="replace")
        m = _FEHM_END.search(text)
        if m:
            metrics["fehm.end_days"] = float(m.group(1))
            metrics["fehm.timesteps"] = int(m.group(2))
        m = _FEHM_NR.search(text)
        if m:
            metrics["fehm.nr_iterations"] = int(m.group(1))
        m = _FEHM_CONS.search(text)
        if m:
            metrics["fehm.mass_conservation_error"] = float(m.group(1))
        if "fehm.timesteps" not in metrics:
            missing.append(f"{Path(out).name} (no 'simulation ended' summary)")
    return metrics, missing


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


def _h5_stats(path, prefix, limit=12):
    """Size and mean of every numeric dataset in an HDF5 file (first `limit`)."""
    import h5py
    metrics = {}
    with h5py.File(path, "r") as f5:
        names = []
        f5.visititems(lambda name, obj: names.append(name) if isinstance(obj, h5py.Dataset) else None)
        for name in sorted(names)[:limit]:
            if name.lower().endswith(("id", "ids")):      # cell/material ids: not a result
                continue
            arr = np.asarray(f5[name])
            if arr.dtype.kind not in "fiu" or arr.size == 0:
                continue
            key = f"{prefix}.{_slug(name)}"
            metrics[f"{key}.n"] = int(arr.size)
            metrics[f"{key}.mean"] = float(arr.astype(float).mean())
    return metrics


def _first(scratch, pattern):
    hits = sorted(glob.glob(str(Path(scratch) / "**" / pattern), recursive=True))
    return hits[0] if hits else None


def udfm_metrics(scratch):
    """Octree continuum mesh (map_to_continuum) and upscaled properties (upscale)."""
    metrics, missing = {}, []
    octree = _first(scratch, "octree_dfn.inp")
    if octree:
        nodes, elems = _inp_header(octree)
        metrics.update({"udfm.octree_nodes": nodes, "udfm.octree_elements": elems})
    else:
        missing.append("octree_dfn.inp")
    for name in ("mesh_permeability.h5", "mesh_porosity.h5"):
        path = _first(scratch, name)
        if path:
            metrics.update(_h5_stats(path, "udfm." + name[:-3]))
        else:
            missing.append(name)
    return metrics, missing


def ecpm_metrics(scratch):
    """mapdfn ECPM property fields (anisotropic_k.h5, porosity.h5, tortuosity.h5)."""
    metrics, missing = {}, []
    for name in ("anisotropic_k.h5", "porosity.h5", "tortuosity.h5"):
        path = _first(scratch, name)
        if path:
            metrics.update(_h5_stats(path, "ecpm." + name[:-3]))
        else:
            missing.append(name)
    return metrics, missing


def _dat_last_column(path):
    """Last numeric column of a whitespace table, tolerating a header line."""
    for skip in (0, 1):
        try:
            data = np.loadtxt(path, skiprows=skip, ndmin=2)
            if data.size:
                return data[:, -1]
        except Exception:  # noqa: BLE001
            continue
    return None


def stress_metrics(outdir):
    """Fields left by stress_based_apertures + the final dump_hydraulic_values.

    aperture.dat / perm.dat are per fracture (after the stress adjustment);
    stress_aper_by_node.dat is the per-node aperture written onto the mesh.
    """
    metrics, missing = {}, []
    for name in ("aperture.dat", "perm.dat", "stress_aper_by_node.dat"):
        path = Path(outdir) / name
        col = _dat_last_column(path) if path.is_file() else None
        if col is None:
            missing.append(name)
            continue
        key = "stress." + name[:-4]
        metrics[f"{key}.n"] = int(col.size)
        metrics[f"{key}.mean"] = float(col.mean())
        metrics[f"{key}.min"] = float(col.min())
        metrics[f"{key}.max"] = float(col.max())
    return metrics, missing


def split_stage(stage):
    """'gen' -> ('gen', None); 'gen:output_prune' -> ('gen', 'output_prune')."""
    name, _, subdir = stage.partition(":")
    return name, (subdir or None)


def collect(stages, scratch, outdir):
    """Run every extractor named in `stages`. Returns (metrics, missing).

    A stage may be written ``name:dir`` to read that stage's files from
    ``<scratch>/<dir>`` instead of the case's default output directory, for
    drivers that write more than one job directory.
    """
    metrics, missing = {}, []
    default_outdir = outdir
    for spec in stages:
        stage, subdir = split_stage(spec)
        outdir = Path(scratch) / subdir if subdir else default_outdir
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
        elif stage == "udfm":
            m, miss = udfm_metrics(scratch)
        elif stage == "ecpm":
            m, miss = ecpm_metrics(scratch)
        elif stage == "stress":
            m, miss = stress_metrics(outdir)
        else:
            raise ValueError(f"unknown stage {stage!r}")
        if subdir:
            miss = [f"{subdir}/{x}" for x in miss]
        metrics.update(m)
        missing.extend(miss)
    return metrics, missing
