# Heat extraction on a graph representation of a DFN (pydfnworks.thermal)

Built on `examples/graph_transport`: same three-family truncated power-law
DFN in a 400 x 50 x 50 m domain, graph flow from the left to the right face,
and graph particle transport, with no meshing. The fracture permeability is
raised a thousandfold (2e-9 m^2, aperture about 0.15 mm, a stimulated
network) so the 1 MPa drop drives a geothermal-scale flow, and that graph
flow rate is the mass flow the surrogate uses. Three things are added.

1. **Surrogate geometry from the flow graph.** The fractures on the inflow
   face (count and mean diameter) become the fracture count and height of
   the Gringarten multiple-parallel-fracture surrogate, and `compute_dQ`
   gives the DFN's characteristic spacing (1/dQ, with 1/p32 for
   comparison).
2. **TDRW with thermal properties.** `run_graph_transport` is run with
   the Phase 2 parameter mapping from
   `pydfnworks.thermal.dfn_heat.thermal_to_tdrw_parameters` (matrix
   porosity -> rock/fluid volumetric heat capacity ratio, matrix
   diffusivity -> rock thermal diffusivity). The infinite-matrix model is
   used: the finite-slab models sample matrix excursions event by event
   at a rate proportional to porosity times diffusivity, about 1e7 times
   the solute value under this mapping, and one particle takes minutes
   (documented in `dfn_heat.py`). The thermally retarded arrival times in
   `thermal_partime.hdf5` are the ingredient the DFN-based heat backend
   will convert to Q(t).
3. **Spacing optimization with the Phase 1 surrogate**, and a call to the
   Phase 2 backend with the DFN and flow graph, which raises
   `NotImplementedError` in this version.

Outputs in `output/`: `thermal_partime.hdf5`, `heat_rate_dfn_spacing.csv`,
`objective_vs_spacing_<case>.csv`, `heat_rate_best_<case>.csv`, and
`spacing_optimization.png`. As in `thermal_spacing_optimization`, the
surrogate alone gives monotone objectives; see that example's README.

## Running on another machine

Check out the branch and reinstall pydfnworks so the new `pydfnworks.thermal`
subpackage is picked up, then run the verification scripts:

    git fetch origin && git checkout feature/thermal-mpf-surrogate
    cd pydfnworks && pip install -e . && python tests/thermal/run_thermal_verification.py

Then run this example from its directory:

    python driver.py

`thermal_spacing_optimization` needs dfnGen and LaGriT (well intersections on
a reduced mesh); `thermal_graph_transport` needs only dfnGen. Both write their
CSV files and `spacing_optimization.png` into `output/`. Neither needs
PFLOTRAN or FEHM.
