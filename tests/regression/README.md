# dfnWorks regression suite

Runs the shipped examples as regression tests, judges each one from the output
files it leaves behind, compares scalar metrics against committed baselines,
and writes a self-contained HTML report.

```bash
cd tests/regression
python3 run_regression.py                 # baseline tier (default)
python3 run_regression.py --tier modest   # baseline + modest (tiers are cumulative)
python3 run_regression.py --only TPL exp  # a subset of cases
python3 run_regression.py --list          # show cases and tiers
```

Exit code is 0 only when every selected case is PASS or SKIP. The report lands
in `_runs/<timestamp>/report.html` (plus `results.json`) and is copied to
`latest_report.html`. Add `--report PATH` to copy it somewhere else.

## Statuses

| status | meaning |
|---|---|
| PASS | driver exited 0, no ERROR/CRITICAL in `output.log`, every expected output present, all metrics within tolerance |
| DIFF | ran cleanly but at least one metric is outside tolerance of its baseline (the report highlights which) |
| FAIL | nonzero exit, timeout, log errors, or a missing output file |
| NEW  | no baseline exists yet; run with `--update-baselines` to record one |
| SKIP | a binary the case needs (PFLOTRAN, FEHM, LaGriT, ...) failed preflight |
| SLOW | warning tag: wall time more than 2x the baseline time |

Scratch directories of FAIL and DIFF cases are kept under `_runs/<timestamp>/<case>/`
(the stdout, stderr, `output.log` and the full output tree). Passing cases are
deleted unless `--keep` is given.

## How a case runs

1. The example directory named by `source` in `manifest.toml` (a name under
   `examples/`, or a `./` path relative to the manifest) is copied into
   `_runs/<timestamp>/<case>/`, minus any old `output*/` dirs, logs and legacy
   `*_example/` folders.
2. `python3 driver.py` runs in that copy with stdin closed (so no interactive
   prompt can hang it), `MPLBACKEND=Agg`, and a per-case timeout.
3. `harness/metrics.py` extracts scalars for each stage listed in the manifest:

| stage | source file | metrics |
|---|---|---|
| gen | `DFN_output.txt` | final fracture count, isolated removed, rejected, P30, P32, surface area, intersections, intersection length, triple points |
| mesh / mesh_visual | `full_mesh.inp` / `reduced_mesh.inp` header | nodes, elements |
| dfm | `dfm_tet_mesh.inp` header | nodes, elements |
| pflotran | `*-mas.dat` last row, `*_effective_perm.txt` | mass balance columns, k_eff |
| fehm | `full_mesh_vol_area.stor`, FEHM `*.out` | stor line count; end time, timesteps, Newton iterations, mass conservation error |
| dfntrans | `partime*`, `TotalNumberP` | particle count, travel-time mean/p10/p50/p90, mean path length |
| graph_flow | `graph_flow.hdf5` | edge count, total flow rate, total volume |
| graph_transport | `<partime>.hdf5` | particle count, travel-time mean/p10/p50/p90 (one set per partime file) |
| report | `*_output_report.pdf` | presence only |
| udfm | `octree_dfn.inp`, `mesh_permeability.h5`, `mesh_porosity.h5` | octree nodes/elements, size and mean of each upscaled field |
| ecpm | `anisotropic_k.h5`, `porosity.h5`, `tortuosity.h5` | size and mean of each mapdfn ECPM field |
| stress | `aperture.dat`, `perm.dat`, `stress_aper_by_node.dat` | count, mean, min, max of the stress-adjusted per-fracture and per-node fields |

A stage may be written `name:dir` (e.g. `gen:output_prune`) to read that
stage's files from `<scratch>/<dir>` rather than `output_dir`, for drivers that
write more than one job directory.

4. `harness/compare.py` checks each metric against `baselines/<case>.json`.
   Integers must match exactly; floats use a relative tolerance per stage
   (gen 1e-6, pflotran 1e-4, dfntrans 1e-3, graph 1e-6). Override per case with
   `tolerances = { "pflotran" = 1e-3 }` or a full metric name in the manifest.

## Baselines

`baselines/<case>.json` holds the metrics, the wall time, and where/when it was
made. They are committed. Regenerate after an intentional change in behaviour:

```bash
python3 run_regression.py --only TPL --update-baselines
```

Review the diff of the baseline file before committing it; that diff *is* the
record of what changed.

## Adding a case

Add a block to `manifest.toml`:

```toml
[cases.my_case]
tier = "modest"
source = "my_example"           # a directory under examples/
# source = "./cases/my_case"    # or a driver kept under tests/regression/
stages = ["gen", "mesh", "pflotran"]
timeout = 900
```

Then run it once with `--update-baselines`. Requirements (which binaries must
exist) are derived from the stages; add `requires = [...]` to override.

## Tiers

- **baseline** (default, ~3 min): one deterministic case per generator feature
  and mesh mode; the cheapest cases carry the full gen → mesh → PFLOTRAN →
  DFNTrans chain.
- **modest**: one case per optional workflow: TDRW transport, stress-based
  apertures, wells, FEHM, PFLOTRAN restart (ade_example), hydraulic-property
  functions (hy_test), UDFM octree upscaling, graph pruning to a backbone, and
  Bingham orientations.
- **advanced**: the long ones: mapdfn ECPM on a km-scale network with two
  PFLOTRAN runs, the finite-matrix-diffusion TDRW sweep on a graph, and the
  p32-calibration network at h = 1 m.

Known gaps: `tdrw` fails the rFram-off UGE check on one near-degenerate
connection (area -1.3e-7 at h = 0.1, well above round-off); it stays in the
manifest so the failure is visible until the example or the policy changes.
`stress` compares flow but not transport, because its ~50-particle DFNTrans
run is not reproducible run to run.

Examples whose drivers live only on feature branches (tough, dfntrans2,
edfm_tpl, thermal_graph_transport, thermal_spacing_optimization) are not in the
manifest; add them when those branches merge. `calibrate_p32.py` in
calibrate_p32_from_p10 is also left out: it wraps generation in an optimiser
and has no fixed run length.
