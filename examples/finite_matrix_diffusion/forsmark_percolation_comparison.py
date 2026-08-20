"""
Forsmark FFM01 fracture network: calibrated versus inflated intensity.

Generates two DFN realizations over the same 1000 m cubic domain that differ
ONLY in the areal fracture intensity P32 of the three sets. Set orientations,
Fisher concentrations, size exponents, radius range, transmissivity model,
domain, and random seed are identical between the two cases, so any visual or
transport difference is attributable to the intensity alone.

  follin : calibrated site intensities, near-critical  (p_c = 1.00)
  snl    : SNL (2016) reference-case intensities       (p_c = 3.31)

Set SCENARIO below and run.  VISUAL_MODE = True produces a coarse mesh
suitable for rendering rather than a flow-quality mesh.
"""

from pydfnworks import DFNWORKS
import os

# ----------------------------------------------------------------------
SCENARIO    = "pc_1"      # "follin" or "snl"
SEED        = 101           # same seed for both cases
VISUAL_MODE = True          # True -> coarse mesh for visualization only
NCPU        = 8
# ----------------------------------------------------------------------

# Areal fracture intensity P32 over the operational radius range [15, 500] m.
# Values from the percolation analysis; the calibrated column is the Follin
# hydrogeological DFN, the SNL column is the reference-case parameterization.
#
#   set     P32 follin     P32 snl      inflation
#   NS       0.00591       0.03682        6.2x
#   EW       0.00480       0.02769        5.8x
#   HZ       0.02181       0.04597        2.1x
#
# NOTE: the dfnBoard case files use 5.96e-3 / 4.81e-3 / 2.23e-2, which differ
# from these in the third significant figure. The values here are the ones the
# percolation analysis was computed from.

P32 = {
    "pc_1": {"NS": 5.91000e-03, "EW": 4.80000e-03, "HZ": 2.18100e-02},
    "pc_2": {"NS": 1.18200e-02, "EW": 9.60000e-03, "HZ": 4.36200e-02},
    "pc_3": {"NS": 1.77300e-02, "EW": 1.44000e-02, "HZ": 6.54300e-02},
}


# Shared set geometry. Trend and plunge define the mean fracture POLE.
#   NS  pole 090/00 -> vertical, striking N-S
#   EW  pole 180/00 -> vertical, striking E-W
#   HZ  pole 360/90 -> sub-horizontal
SETS = [
    # name, alpha, trend, plunge, kappa
    ("NS", 2.50,  90.0,  0.0, 22.0),
    ("EW", 2.70, 180.0,  0.0, 22.0),
    ("HZ", 2.40, 360.0, 90.0, 10.0),
]

# Follin's calibrated values for the HZ set are kappa = 8 and alpha = 2.38.
# The values above follow the SNL convention so that the two cases differ in
# P32 alone. To run the fully calibrated variant, use ("HZ", 2.38, 360.0, 90.0, 8.0).

R_MIN, R_MAX = 15.0, 500.0          # operational radius range, m
HY_ALPHA, HY_BETA = 1.6e-9, 0.8     # transmissivity: T = alpha * r^beta

assert SCENARIO in P32, f"SCENARIO must be one of {list(P32)}"
jobname = os.path.join(os.getcwd(), f"forsmark_{SCENARIO}_seed101")

DFN = DFNWORKS(jobname=jobname, ncpu=NCPU)

DFN.params['domainSize']['value']            = [1000.0, 1000.0, 1000.0]
DFN.params['domainSizeIncrease']['value']    = [100.0, 100.0, 100.0]
DFN.params['h']['value']                     = 1.0
DFN.params['boundaryFaces']['value']         = [1, 1, 0, 0, 0, 0]   # flow in x
DFN.params['keepOnlyLargestCluster']['value'] = True
DFN.params['ignoreBoundaryFaces']['value']   = False
DFN.params['orientationOption']['value']     = 1                    # trend / plunge
DFN.params['seed']['value']                  = SEED
DFN.params['visualizationMode']['value']     = VISUAL_MODE

for name, alpha, trend, plunge, kappa in SETS:
    DFN.add_fracture_family(
        shape="ell",
        distribution="tpl",
        alpha=alpha,
        min_radius=R_MIN,
        max_radius=R_MAX,
        kappa=kappa,
        trend=trend,
        plunge=plunge,
        aspect=1,
        p32=P32[SCENARIO][name],
        number_of_points=8,
        hy_variable="transmissivity",
        hy_function="correlated",
        hy_params={"alpha": HY_ALPHA, "beta": HY_BETA},
    )

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.create_network()
# DFN.output_report()                       # stereonets, rose diagrams, radii, FRAM
# DFN.mesh_network()

print(f"\n{SCENARIO}: {DFN.num_frac} fractures retained in the connected network")

pressure_in = 1.1* 10**6
pressure_out = 10**6
G = DFN.run_graph_flow("left", "right",   
                       pressure_in, pressure_out, conductance_model = "doolaeghe")

p32, dQ, _ = DFN.compute_dQ(G)

nparticles = 10**5     # 1e5 for tails resolved to PDF ~1e-7

# ----------------------------------------------------------------------
# Finite matrix diffusion demonstration matrix
# ----------------------------------------------------------------------
# Three timescales position every feature (b_f ~ 2e-5 m, t_peak ~ 1e8 s):
#   departure from advective : t* ~ (b_f/phi)^2 / D = 4e-6 / D
#   finite-block cutoff      : tau_D = (spacing/2)^2 / D
#   equilibrium retardation  : R = 1 + phi*(spacing/2)/b_f ~ 1 + 250*spacing
#
# Config 1  spacing sweep at D = 1e-13: cutoffs at ~2.5e2, 6e3, 1e5,
#           off-window t_peak; the 10 m curve should overlay the infinite
#           reference (convergence to the infinite-matrix limit).
# Config 2  diffusivity sweep at spacing = 1 m: departure and cutoff slide
#           together; all three approach the same R = 251 equilibrium shift.
# Config 3  site-tied spacings 1/P32 and 1/dQ (network values from
#           compute_dQ) at D = 1e-13: expected to overlay infinite
#           (block-size effects invisible at Forsmark intensity over
#           this window).

import csv

D_REF = 1e-13
D_SWEEP = [1e-15, 1e-13, 1e-11]
SPACING_SWEEP = [0.1, 0.5, 2.0, 10.0]          # config 1
SPACING_P32 = 1.0 / p32                            # config 3 (compute_dQ)
SPACING_DQ = 1.0 / dQ                              # config 3 (compute_dQ)

PHI_M = 0.01
B_F_NOMINAL = 2e-5     # half-aperture from T = 1.6e-9 r^0.8 + cubic law
T_PEAK_NOMINAL = 1e8   # s, for the predicted-feature columns only

runs = []
for D in D_SWEEP:                                  # infinite references
    runs.append(("infinite", D, None, ""))
for spacing in SPACING_SWEEP:                      # config 1
    runs.append(("dentz", D_REF, spacing, ""))
for D in D_SWEEP:                                  # config 2
    runs.append(("dentz", D, 1.0, ""))
runs.append(("dentz", D_REF, SPACING_P32, "1/P32"))   # config 3
runs.append(("dentz", D_REF, SPACING_DQ, "1/dQ"))     # config 3

with open("fmd_run_matrix.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["partime_file", "model", "matrix_diffusivity",
                     "fracture_spacing", "label", "tau_D_s",
                     "tau_D_over_tpeak", "retardation_R"])
    for model, D, spacing, label in runs:
        if model == "infinite":
            name = f"graph_partime_infinite_D{D:.0e}"
            writer.writerow([name, model, D, "", label, "", "", ""])
        else:
            name = f"graph_partime_dentz_D{D:.0e}_s{spacing:0.2f}"
            tau_D = (spacing / 2)**2 / D
            R = 1 + PHI_M * (spacing / 2) / B_F_NOMINAL
            writer.writerow([name, model, D, spacing, label,
                             f"{tau_D:.3e}",
                             f"{tau_D / T_PEAK_NOMINAL:.2e}", f"{R:.0f}"])

for model, D, spacing, label in runs:
    if model == "infinite":
        name = f"graph_partime_infinite_D{D:.0e}"
    else:
        name = f"graph_partime_dentz_D{D:.0e}_s{spacing:0.2f}"
    print(f"\n=== {name} ===")
    DFN.run_graph_transport(G, nparticles,
                            partime_file=name,
                            frac_id_file=None,
                            format="hdf5",
                            initial_positions="flux",
                            dump_traj=False,
                            tdrw_flag=True,
                            tdrw_model=model,
                            matrix_porosity=PHI_M,
                            matrix_diffusivity=D,
                            fracture_spacing=spacing)
