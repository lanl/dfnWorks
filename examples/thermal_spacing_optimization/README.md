# Hydraulic fracture spacing optimization (pydfnworks.thermal)

Runs the Phase 1 heat-extraction surrogate (Gringarten et al. 1975
multiple parallel fractures model, `pydfnworks.thermal.mpf_gringarten`)
inside the spacing optimizer on a FORGE-representative DFN and well pair.

The DFN supplies the surrogate geometry: the number of fractures the
injection lateral cuts and their mean diameter (fracture height), found
with the well package (`find_well_intersection_points`) on a reduced mesh.
Reservoir numbers are representative of Utah FORGE (226 C granitoid at
~2.3 km); the 600 m block is about a quarter of the 16A(78)-32 lateral, so
the circulation rate is scaled to 20 kg/s.

`driver.py` writes, in `output/`:

- `heat_rate_dfn_spacing.csv`: Q(t) at the spacing implied by the DFN
- `objective_vs_spacing_<case>.csv` and `heat_rate_best_<case>.csv` for
  three cases: time to 10 % thermal drawdown and 30-year cumulative heat
  with stages filling a fixed lateral (n = L / spacing), and 30-year
  cumulative heat with the DFN fracture count fixed and spacing free
- `spacing_optimization.png`: objective curves and Q(t) for the best
  spacing of each case

Expect the surrogate on its own to give monotone objectives: at fixed
total flow and fixed rock volume the sharpest thermal front (closest
spacing, most fractures) is best, and at fixed fracture count more rock
(wider spacing) is best. A trade-off appears once a cost per stage or the
Phase 2 DFN backend (flow partition and connectivity) enters the
objective; both plug into `optimize_spacing` without changing it. The
driver ends by pointing the optimizer at the Phase 2 backend
(`pydfnworks.thermal.dfn_heat`), which raises `NotImplementedError` in
this version.

The surrogate call takes about 100 microseconds, so the DFN generation and
well intersection dominate the run time.
