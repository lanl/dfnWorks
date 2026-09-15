# Finite matrix diffusion demonstration (Forsmark FFM01)

Demonstrates the finite matrix-diffusion TDRW models on a Forsmark-like
fracture network, focusing on the two controlling parameters: fracture
spacing and matrix diffusivity.

Three timescales position every feature of the breakthrough curves
(with half-aperture b_f ~ 2e-5 m and t_peak ~ 1e8 s for this network):

- departure from advective:  t* ~ (b_f/phi_m)^2 / D_m
- finite-block cutoff:       tau_D = (spacing/2)^2 / D_m
- equilibrium retardation:   R = 1 + phi_m * (spacing/2) / b_f

`forsmark_percolation_comparison.py` generates the network, solves graph
flow (Doolaeghe conductance), and runs a 12-case transport matrix at
1e5 particles:

1. **Spacing sweep** (D = 1e-13 m^2/s; spacings 0.1, 0.5, 2, 10 m):
   cutoffs march to later times with spacing; the 10 m curve overlays
   the infinite-matrix reference, demonstrating convergence to the
   semi-infinite limit.
2. **Diffusivity sweep** (spacing = 1 m; D = 1e-15, 1e-13, 1e-11):
   departure and cutoff slide together; all finite curves approach the
   same D-independent retardation shift R = 251.
3. **Site-tied spacings** (1/P32 and 1/dQ from `compute_dQ`, D = 1e-13):
   both overlay the infinite curve -- block-size effects are invisible
   at Forsmark intensity over this observation window.

Each run writes its parameters and predicted feature locations
(tau_D, tau_D/t_peak, R) to `fmd_run_matrix.csv`. After the driver
completes, generate the three figures with:

    python plot_fmd_demo.py forsmark_pc_1_seed101

The transport log reports the adaptive release position chosen for each
dentz run (`--> Dentz release position eps = ...`); it caps at 1e-4 for
small blocks and shrinks for large ones so the TDRW artifact timescale
(eps * spacing/2)^2 / D_m stays below the earliest arrivals.
