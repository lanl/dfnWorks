#"""
#   :synopsis: Driver run file for heat extraction on a graph representation
#              of a DFN: graph flow, finite-slab TDRW with thermal
#              properties, and the Gringarten spacing surrogate
#   :version: 1.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#
# Built on examples/graph_transport. The DFN, graph flow, and graph
# transport steps are the same, except that the fracture permeability is
# raised from 2e-12 to 2e-9 m^2 (aperture about 0.15 mm, a stimulated
# network) so that the 1 MPa drop drives a flow of geothermal scale
# through this 400 m block; what is added is
#   1. the surrogate geometry read from the flow graph: the fractures on
#      the inflow face (count and mean diameter) and the DFN's
#      characteristic fracture spacing from compute_dQ (1/dQ and 1/p32),
#   2. graph particle transport with TDRW driven by thermal rather than
#      solute properties, using the Phase 2 parameter mapping in
#      pydfnworks.thermal.dfn_heat (matrix_porosity ->
#      (rho c)_rock/(rho c)_fluid, matrix_diffusivity -> rock thermal
#      diffusivity), which is the ingredient the DFN-based heat backend
#      will build on. The infinite-matrix model is used: the finite-slab
#      models sample matrix excursions event by event at a rate
#      proportional to matrix_porosity * matrix_diffusivity, which is
#      about 1e7 times larger for heat than for a solute, and a single
#      particle takes minutes (see the notes in dfn_heat.py),
#   3. the Phase 1 Gringarten surrogate and spacing optimizer on the
#      graph-derived geometry, and the Phase 2 backend called with the DFN
#      and flow graph (raises NotImplementedError in this version).
#"""

import os
import functools
import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pydfnworks import *
from pydfnworks.thermal import (get_backend, optimize_spacing, cumulative_heat,
                                time_to_drawdown, thermal_to_tdrw_parameters,
                                mpf_gringarten, GRANITE_PROPS, WATER_PROPS,
                                SECONDS_PER_YEAR)

src_path = os.getcwd()
jobname = f"{src_path}/output"

DFN = DFNWORKS(jobname, ncpu=8)

DFN.params['domainSize']['value'] = [400, 50, 50]
DFN.params['h']['value'] = 1
DFN.params['domainSizeIncrease']['value'] = [5, 5, 5]
DFN.params['ignoreBoundaryFaces']['value'] = True
DFN.params['boundaryFaces']['value'] = [1, 1, 0, 0, 0, 0]
DFN.params['keepOnlyLargestCluster']['value'] = True
DFN.params['disableFram']['value'] = True

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=10,
                        p32=0.25,
                        aspect=1,
                        theta=0.0,
                        phi=0.0,
                        alpha=1.8,
                        min_radius=10.0,
                        max_radius=20.0,
                        hy_variable='permeability',
                        hy_function='constant',
                        hy_params={"mu": 2e-9})

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=10,
                        p32=0.25,
                        aspect=1,
                        theta=0.0,
                        phi=270.0,
                        alpha=1.8,
                        min_radius=10.0,
                        max_radius=20.0,
                        hy_variable='permeability',
                        hy_function='constant',
                        hy_params={"mu": 2e-9})

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=10,
                        p32=0.25,
                        aspect=1,
                        theta=45.0,
                        phi=0.0,
                        alpha=1.8,
                        min_radius=10.0,
                        max_radius=20.0,
                        hy_variable='permeability',
                        hy_function='constant',
                        hy_params={"mu": 3e-9})

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.create_network()

pressure_in = 2 * 10**6
pressure_out = 10**6
G = DFN.run_graph_flow("left", "right", pressure_in, pressure_out)

# ---------------------------------------------------------------------
# Surrogate geometry from the flow graph
# ---------------------------------------------------------------------
# inlet vertices are intersections of a fracture with the inflow face;
# their 'frac' attribute is (fracture id, 's')
inlet_nodes = [v for v in G.nodes if G.nodes[v]['inletflag']]
inlet_fractures = np.unique([G.nodes[v]['frac'][0] for v in inlet_nodes]).astype(int)
n_inlet = len(inlet_fractures)
fracture_height = float(np.mean(2 * DFN.radii[inlet_fractures - 1, 2]))
graph_flow_rate = sum(G.edges[u, v]['vol_flow_rate']
                      for u in inlet_nodes for v in G.successors(u))
p32, dQ, _ = DFN.compute_dQ(G)
spacing_dfn = 1.0 / dQ
DFN.print_log(f"--> {n_inlet} fractures on the inflow face, mean diameter {fracture_height:0.1f} m")
DFN.print_log(f"--> Graph flow rate for {pressure_in - pressure_out:0.1e} Pa drop: "
              f"{graph_flow_rate:0.3e} m^3/s ({graph_flow_rate * WATER_PROPS['rho']:0.3e} kg/s)")
DFN.print_log(f"--> Characteristic spacings: 1/dQ = {spacing_dfn:0.2f} m, 1/p32 = {1/p32:0.2f} m")

# ---------------------------------------------------------------------
# Graph transport with thermal properties (Phase 2 ingredient). The
# infinite-matrix TDRW model draws one closed-form retention time per
# edge; do not pass fracture_spacing here, which would switch
# run_graph_transport to the finite-slab sampler (see the header notes).
# ---------------------------------------------------------------------
tdrw = thermal_to_tdrw_parameters(GRANITE_PROPS, WATER_PROPS)
DFN.print_log(f"--> Thermal TDRW parameters: matrix_porosity {tdrw['matrix_porosity']:0.3f}, "
              f"matrix_diffusivity {tdrw['matrix_diffusivity']:0.2e} m^2/s")
number_of_particles = 10**4
particles = DFN.run_graph_transport(G,
                                    number_of_particles,
                                    "thermal_partime",
                                    "thermal_frac_sequence",
                                    tdrw_flag=True,
                                    tdrw_model="infinite",
                                    matrix_porosity=tdrw["matrix_porosity"],
                                    matrix_diffusivity=tdrw["matrix_diffusivity"])
with h5py.File("thermal_partime.hdf5", "r") as fp:
    advective = np.asarray(fp["Advective time [s]"])
    total = np.asarray(fp["Total travel time [s]"])
# With an infinite matrix the retention distribution is heavy-tailed; its
# early quantiles, not its median, control thermal breakthrough
q = [1, 10, 50]
DFN.print_log(f"--> Advective time quantiles {q} %: "
              + ", ".join(f"{v:0.2e}" for v in np.percentile(advective, q)) + " s")
DFN.print_log(f"--> Thermally retarded time quantiles {q} %: "
              + ", ".join(f"{v:0.2e}" for v in np.percentile(total, q)) + " s")

# ---------------------------------------------------------------------
# Phase 1 surrogate and spacing optimizer on the graph-derived geometry
# ---------------------------------------------------------------------
# mass flow rate from the graph flow solution, so the surrogate sees the
# rate the network actually carries under the imposed pressure drop
m_dot = WATER_PROPS["rho"] * graph_flow_rate  # kg/s
T_res = 226.0  # deg C
T_inj = 40.0  # deg C
t_eval = np.linspace(0.0, 30.0 * SECONDS_PER_YEAR, 361)
common = dict(m_dot=m_dot,
              T_res=T_res,
              T_inj=T_inj,
              rock_props=GRANITE_PROPS,
              fluid_props=WATER_PROPS,
              fracture_height=fracture_height,
              t_eval=t_eval)

heat_extraction = get_backend("mpf_gringarten")
Q_dfn = heat_extraction(spacing_dfn, m_dot, T_res, T_inj, GRANITE_PROPS,
                        WATER_PROPS, n_inlet, fracture_height, t_eval)
params = mpf_gringarten.dimensionless_parameters(spacing_dfn, m_dot, GRANITE_PROPS,
                                                 WATER_PROPS, n_inlet, fracture_height)
DFN.print_log(f"--> Surrogate at 1/dQ spacing {spacing_dfn:0.2f} m, {n_inlet} fractures: "
              f"beta = {params['beta']:0.3f}, piston time {params['t_piston']/SECONDS_PER_YEAR:0.2f} yr, "
              f"Q(0) = {Q_dfn[0]/1e6:0.2f} MW, Q(30 yr) = {Q_dfn[-1]/1e6:0.2f} MW")
np.savetxt("heat_rate_dfn_spacing.csv",
           np.c_[t_eval / SECONDS_PER_YEAR, Q_dfn],
           delimiter=",",
           header=f"time [yr], heat rate [W]; spacing {spacing_dfn:0.2f} m, {n_inlet} fractures",
           comments="# ")

domain_x = DFN.params['domainSize']['value'][0]
n_of_spacing = lambda spacing: int(round(domain_x / spacing))
cases = {
    "time_to_10pct_drawdown_fixed_domain":
    dict(objective=functools.partial(time_to_drawdown, fraction=0.9),
         n_fractures=n_of_spacing,
         spacings=domain_x / np.arange(2, int(domain_x / 2.0) + 1),
         bounds=(2.0, domain_x)),
    "cumulative_heat_30yr_fixed_count":
    dict(objective=cumulative_heat,
         n_fractures=n_inlet,
         spacings=None,
         bounds=(1.0, 100.0)),
}
results = {}
for name, case in cases.items():
    DFN.print_log(f"\n--> Optimizing spacing: {name}")
    res = optimize_spacing(case["bounds"],
                           heat_extraction=heat_extraction,
                           objective=case["objective"],
                           n_fractures=case["n_fractures"],
                           spacings=case["spacings"],
                           method="grid" if case["spacings"] is not None else "bounded",
                           n_grid=40,
                           **common)
    results[name] = res
    DFN.print_log(f"--> Best spacing {res['spacing']:0.2f} m with {res['n_fractures']} fractures, "
                  f"objective {res['objective']:0.4e} ({len(res['spacings'])} evaluations)")
    np.savetxt(f"objective_vs_spacing_{name}.csv",
               np.c_[res["spacings"], res["objectives"]],
               delimiter=",",
               header="spacing [m], objective",
               comments="# ")
    np.savetxt(f"heat_rate_best_{name}.csv",
               np.c_[t_eval / SECONDS_PER_YEAR, res["Q"]],
               delimiter=",",
               header=f"time [yr], heat rate [W]; spacing {res['spacing']:0.2f} m, {res['n_fractures']} fractures",
               comments="# ")

# ---------------------------------------------------------------------
# Phase 2 backend with the DFN and flow graph (stub in this version)
# ---------------------------------------------------------------------
try:
    get_backend("dfn_heat")(spacing_dfn, m_dot, T_res, T_inj, GRANITE_PROPS,
                            WATER_PROPS, n_inlet, fracture_height, t_eval,
                            dfn=DFN, G=G, nparticles=number_of_particles)
except NotImplementedError as err:
    DFN.print_log(f"--> Backend 'dfn_heat': {err}")

# ---------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------
colors = ["#2a78d6", "#eb6834", "#eda100"]
labels = {
    "time_to_10pct_drawdown_fixed_domain": "time to 10 percent drawdown, fixed domain",
    "cumulative_heat_30yr_fixed_count": "cumulative heat, fixed count",
}
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
for color, (name, res) in zip(colors, results.items()):
    ax1.plot(res["spacings"], res["objectives"] / res["objectives"].max(),
             color=color, lw=2, label=labels[name])
    ax1.plot(res["spacing"], 1.0, "o", color=color, ms=8, mec="white")
    ax2.plot(t_eval / SECONDS_PER_YEAR, res["Q"] / 1e6, color=color, lw=2,
             label=f"{labels[name]}: {res['spacing']:0.1f} m, n = {res['n_fractures']}")
ax2.plot(t_eval / SECONDS_PER_YEAR, Q_dfn / 1e6, color=colors[2], lw=2, ls="--",
         label=f"1/dQ spacing: {spacing_dfn:0.1f} m, n = {n_inlet}")
ax1.set_xscale("log")
ax1.set_xlabel("fracture spacing [m]")
ax1.set_ylabel("objective / max")
ax1.set_title("Objective vs spacing")
ax2.set_xlabel("time [yr]")
ax2.set_ylabel("heat extraction rate [MW]")
ax2.set_title(f"Heat rate, {m_dot:0.0f} kg/s, {T_res:0.0f} C reservoir")
for ax in (ax1, ax2):
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig("spacing_optimization.png", dpi=150)
DFN.print_log("--> Wrote spacing_optimization.png and the CSV files in the output directory")
