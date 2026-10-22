# dfnWorks regression suite

Runs the shipped examples as regression tests, judges each one from the output
files it leaves behind, compares scalar metrics against committed baselines,
and writes a self-contained HTML report.

```bash
cd examples/regression
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

1. The example directory named by `source` in `manifest.toml` is copied into
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
| fehm | `full_mesh_vol_area.stor` | line count |
| dfntrans | `partime*`, `TotalNumberP` | particle count, travel-time mean/p10/p50/p90, mean path length |
| graph_flow | `graph_flow.hdf5` | edge count, total flow rate, total volume |
| graph_transport | `<partime>.hdf5` | particle count, travel-time mean/p10/p50/p90 |
| report | `*_output_report.pdf` | presence only |

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
source = "../my_example"        # or "cases/my_case" for a driver that is not an example
stages = ["gen", "mesh", "pflotran"]
timeout = 900
```

Then run it once with `--update-baselines`. Requirements (which binaries must
exist) are derived from the stages; add `requires = [...]` to override.

## Tiers

- **baseline**: one deterministic case per generator feature and mesh mode;
  the cheapest cases carry the full gen → mesh → PFLOTRAN → DFNTrans chain.
- **modest** (planned): FEHM, TDRW, stress apertures, UDFM upscaling, pruning,
  wells, PFLOTRAN restart transport, dense networks.
- **advanced** (planned): mapdfn ECPM, finite matrix diffusion, p32
  calibration, and scale-up networks.
