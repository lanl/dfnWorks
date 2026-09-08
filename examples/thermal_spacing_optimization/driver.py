#"""
#   :synopsis: Driver run file for hydraulic fracture spacing optimization
#              with the pydfnworks.thermal heat-extraction surrogate on a
#              FORGE-representative DFN and injection/production well pair
#   :version: 1.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#
# Workflow
#   1. Generate a FORGE-representative DFN (Utah FORGE granitoid, ~2.3 km
#      depth): one set parallel to the hydraulic fractures (strike along
#      S_Hmax, near vertical; the model x axis is the lateral direction and
#      the normal of this set) and one natural set (strike ~300, dip ~70).
#   2. Place an injection lateral (16A(78)-32 analogue) and a production
#      lateral 100 m above it (16B(78)-32 analogue) with the well package,
#      and find the fractures each well intersects.
#   3. Take the surrogate geometry from the DFN: the number of fractures
#      cut by the injection lateral and their mean diameter (fracture
#      height), plus the lateral length inside the domain.
#   4. Run the Gringarten multiple-parallel-fracture surrogate at the
#      DFN-derived spacing, then optimize the spacing for two objectives
#      and two stage-count couplings, and write Q(t) for the best spacing
#      and the objective-vs-spacing curves.
#   5. Point the same optimizer at the Phase 2 DFN backend to show that
#      swapping backends is a one-line change (it raises NotImplementedError
#      in this version).
#
# Reservoir numbers are representative of FORGE (T ~ 226 C, granitoid
# rho = 2750 kg/m^3, c = 790 J/kg/K, k = 3.05 W/m/K); the 600 m block is
# roughly a quarter of the 16A lateral, so the circulation rate is scaled
# down to 20 kg/s.
#"""

import os
import functools
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pydfnworks import *
from pydfnworks.dfnGen.well_package.wells import get_segments
from pydfnworks.thermal import (get_backend, optimize_spacing, cumulative_heat,
                                time_to_drawdown, GRANITE_PROPS, WATER_PROPS,
                                SECONDS_PER_YEAR)

src_path = os.getcwd()
jobname = f"{src_path}/output"

DFN = DFNWORKS(jobname, ncpu=8)

DFN.params['domainSize']['value'] = [600, 600, 600]
DFN.params['h']['value'] = 5.0
DFN.params['domainSizeIncrease']['value'] = [20, 20, 20]
DFN.params['stopCondition']['value'] = 1
DFN.params['ignoreBoundaryFaces']['value'] = True
DFN.params['boundaryFaces']['value'] = [1, 1, 0, 0, 0, 0]
DFN.params['keepOnlyLargestCluster']['value'] = False
# reduced mesh only: enough for the well intersection search
DFN.params['visualizationMode']['value'] = True
DFN.params['seed']['value'] = 1

# Set 1: parallel to the hydraulic fractures (normal along the lateral, x)
DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=25,
                        p32=0.03,
                        aspect=1,
                        theta=90.0,
                        phi=0.0,
                        alpha=2.4,
                        min_radius=60.0,
                        max_radius=200.0,
                        hy_variable="permeability",
                        hy_function="constant",
                        hy_params={"mu": 1e-11})

# Set 2: FORGE natural fracture set (strike ~300, dip ~70)
DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=12,
                        p32=0.01,
                        aspect=1,
                        theta=70.0,
                        phi=60.0,
                        alpha=2.6,
                        min_radius=40.0,
                        max_radius=120.0,
                        hy_variable="permeability",
                        hy_function="constant",
                        hy_params={"mu": 1e-12})

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.create_network()

# Wells: injection lateral at z = -50 m, production lateral at z = +50 m,
# both along x (8.5 inch hole, r = 0.11 m)
inject_well = {"name": "inject", "filename": "well_inject.dat", "r": 0.11}
extract_well = {"name": "extract", "filename": "well_extract.dat", "r": 0.11}
wells = [inject_well, extract_well]
for well in wells:
    os.symlink(f"{src_path}/{well['filename']}", well['filename'])

# builds reduced_mesh.inp (visualization mode) and well_points.dat
DFN.find_well_intersection_points(wells)

# ---------------------------------------------------------------------
# Surrogate geometry from the DFN
# ---------------------------------------------------------------------
_, _, inject_fractures = get_segments(f"well_{inject_well['name']}_intersect.inp")
_, _, extract_fractures = get_segments(f"well_{extract_well['name']}_intersect.inp")
inject_ids = np.unique(np.asarray(inject_fractures, dtype=int))
n_dfn = len(inject_ids)
if n_dfn < 2:
    DFN.print_log("Error. The injection lateral cuts fewer than two fractures; "
                  "increase p32 or the lateral length.", 'error')
fracture_height = float(np.mean(2 * DFN.radii[inject_ids - 1, 2]))

half_domain = 0.5 * np.asarray(DFN.params['domainSize']['value'], dtype=float)
well_xyz = np.loadtxt(f"{src_path}/{inject_well['filename']}")
lateral_length = float(
    np.linalg.norm(
        np.clip(well_xyz[-1], -half_domain, half_domain) -
        np.clip(well_xyz[0], -half_domain, half_domain)))
spacing_dfn = lateral_length / (n_dfn - 1)

DFN.print_log(f"--> Injection lateral cuts {n_dfn} fractures "
              f"({len(np.unique(extract_fractures))} for the production lateral)")
DFN.print_log(f"--> Mean diameter of those fractures (surrogate fracture height): {fracture_height:0.1f} m")
DFN.print_log(f"--> Lateral length in the domain: {lateral_length:0.1f} m, "
              f"mean spacing along the lateral: {spacing_dfn:0.1f} m")

# ---------------------------------------------------------------------
# Heat extraction surrogate (Phase 1)
# ---------------------------------------------------------------------
m_dot = 20.0  # kg/s, scaled to the 600 m block
T_res = 226.0  # deg C
T_inj = 40.0  # deg C
project_life = 30.0  # years
t_eval = np.linspace(0.0, project_life * SECONDS_PER_YEAR, 361)

heat_extraction = get_backend("mpf_gringarten")
common = dict(m_dot=m_dot,
              T_res=T_res,
              T_inj=T_inj,
              rock_props=GRANITE_PROPS,
              fluid_props=WATER_PROPS,
              fracture_height=fracture_height,
              t_eval=t_eval)

Q_dfn = heat_extraction(spacing_dfn, m_dot, T_res, T_inj, GRANITE_PROPS,
                        WATER_PROPS, n_dfn, fracture_height, t_eval)
DFN.print_log(f"--> DFN-derived spacing {spacing_dfn:0.1f} m, {n_dfn} fractures: "
              f"Q(0) = {Q_dfn[0]/1e6:0.2f} MW, Q({project_life:0.0f} yr) = {Q_dfn[-1]/1e6:0.2f} MW, "
              f"cumulative heat {cumulative_heat(t_eval, Q_dfn)/1e15:0.3f} PJ")
np.savetxt("heat_rate_dfn_spacing.csv",
           np.c_[t_eval / SECONDS_PER_YEAR, Q_dfn],
           delimiter=",",
           header=f"time [yr], heat rate [W]; spacing {spacing_dfn:0.2f} m, {n_dfn} fractures",
           comments="# ")

# Stage-count couplings:
#   fixed_lateral: stages fill the lateral, n = lateral_length / spacing
#                  (candidate spacings lateral_length / n for integer n)
#   fixed_count:   the DFN fracture count is kept, spacing is free
n_of_spacing = lambda spacing: int(round(lateral_length / spacing))
stage_spacings = lateral_length / np.arange(2, int(lateral_length / 5.0) + 1)

cases = {
    "time_to_10pct_drawdown_fixed_lateral":
    dict(objective=functools.partial(time_to_drawdown, fraction=0.9),
         n_fractures=n_of_spacing,
         spacings=stage_spacings,
         bounds=(5.0, lateral_length)),
    "cumulative_heat_30yr_fixed_lateral":
    dict(objective=cumulative_heat,
         n_fractures=n_of_spacing,
         spacings=stage_spacings,
         bounds=(5.0, lateral_length)),
    "cumulative_heat_30yr_fixed_count":
    dict(objective=cumulative_heat,
         n_fractures=n_dfn,
         spacings=None,
         bounds=(5.0, 200.0)),
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
# Backend swap: same optimizer, Phase 2 DFN backend (stub in this version)
# ---------------------------------------------------------------------
case = cases["cumulative_heat_30yr_fixed_count"]
for backend_name in ("mpf_gringarten", "dfn_heat"):
    try:
        optimize_spacing(case["bounds"],
                         heat_extraction=get_backend(backend_name),
                         objective=case["objective"],
                         n_fractures=case["n_fractures"],
                         n_grid=5,
                         **common)
        DFN.print_log(f"--> Backend '{backend_name}': optimizer ran")
    except NotImplementedError as err:
        DFN.print_log(f"--> Backend '{backend_name}': {err}")

# ---------------------------------------------------------------------
# Figure: objective curves and heat rate for the best spacings
# ---------------------------------------------------------------------
colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
labels = {
    "time_to_10pct_drawdown_fixed_lateral": "time to 10 percent drawdown, fixed lateral",
    "cumulative_heat_30yr_fixed_lateral": "cumulative heat, fixed lateral",
    "cumulative_heat_30yr_fixed_count": "cumulative heat, fixed count",
}
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
for color, (name, res) in zip(colors, results.items()):
    ax1.plot(res["spacings"],
             res["objectives"] / res["objectives"].max(),
             color=color,
             lw=2,
             label=labels[name])
    ax1.plot(res["spacing"], 1.0, "o", color=color, ms=8, mec="white")
    ax2.plot(t_eval / SECONDS_PER_YEAR,
             res["Q"] / 1e6,
             color=color,
             lw=2,
             label=f"{labels[name]}: {res['spacing']:0.0f} m, n = {res['n_fractures']}")
ax2.plot(t_eval / SECONDS_PER_YEAR,
         Q_dfn / 1e6,
         color=colors[3],
         lw=2,
         ls="--",
         label=f"DFN-derived: {spacing_dfn:0.0f} m, n = {n_dfn}")
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
