"""
plot_fmd_demo.py
----------------
Three demonstration figures from the finite-matrix-diffusion run matrix
produced by forsmark_percolation_comparison.py:

  fig 1  spacing sweep at D = 1e-13 (cutoffs march right; 10 m overlays infinite)
  fig 2  diffusivity sweep at spacing = 1 m (paired infinite refs, dashed)
  fig 3  site-tied spacing = 1/P32_total vs infinite (expected overlay)

Usage:  python plot_fmd_demo.py forsmark_pc_1_seed101
"""
import sys
import numpy as np
import h5py
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

YEAR = np.pi * 1e7
D_REF = 1e-13
SPACING_SWEEP = [0.1, 0.5, 2.0, 10.0]
D_SWEEP = [1e-15, 1e-13, 1e-11]

dirname = sys.argv[1] if len(sys.argv) > 1 else "forsmark_pc_1_seed101"
matrix = pd.read_csv(f"{dirname}/fmd_run_matrix.csv")
site_rows = matrix[matrix.label.notna() & (matrix.label != "")]


def load_times(name, column="Total travel time [s]"):
    with h5py.File(f"{dirname}/{name}.hdf5", "r") as f5:
        return np.asarray(f5[column][:]) / YEAR


def log_pdf(t, num_bins=100):
    bins = np.logspace(np.log10(t.min()), np.log10(t.max()), num_bins + 1)
    counts, edges = np.histogram(t, bins=bins, density=True)
    return np.sqrt(edges[:-1] * edges[1:]), counts


def base_axes(title):
    fig, ax = plt.subplots(figsize=(10, 8))
    t_adv = load_times(f"graph_partime_infinite_D{D_REF:.0e}",
                       "Advective time [s]")
    tc, pdf = log_pdf(t_adv)
    t_peak = tc[np.argmax(pdf)]
    ax.loglog(tc / t_peak, pdf, color="0.4", lw=2, label="Advective")
    ax.set_xlabel(r"Normalized Time [t / $t_{peak}$]", fontsize=18)
    ax.set_ylabel("PDF [-]", fontsize=18)
    ax.tick_params(axis="both", which="major", labelsize=14)
    ax.grid(True, which="both", alpha=0.3)
    ax.set_title(title, fontsize=14)
    return fig, ax, t_peak


def add_curve(ax, name, t_peak, label, **kw):
    tc, pdf = log_pdf(load_times(name))
    ax.loglog(tc / t_peak, pdf, label=label, **kw)


# --- fig 1: spacing sweep at D_REF -----------------------------------
fig, ax, t_peak = base_axes(
    rf"Spacing sweep, $D_m = {D_REF:.0e}$ m$^2$/s, $\phi_m = 0.01$")
add_curve(ax, f"graph_partime_infinite_D{D_REF:.0e}", t_peak,
          "Infinite matrix", color="k", lw=2.5)
for spacing, c in zip(SPACING_SWEEP, plt.cm.viridis(np.linspace(0, 0.85, 4))):
    row = matrix[(matrix.model == "dentz")
                 & (matrix.fracture_spacing == spacing)
                 & (np.isclose(matrix.matrix_diffusivity, D_REF))].iloc[0]
    add_curve(ax, row.partime_file, t_peak,
              rf"FMD {spacing:g} m  ($\tau_D = {row.tau_D_over_tpeak:.0e}\,t_p$, R={row.retardation_R:.0f})",
              color=c, lw=2)
ax.legend(fontsize=13)
plt.tight_layout(); plt.savefig("fmd_fig1_spacing_sweep.png", dpi=150)

# --- fig 2: diffusivity sweep at spacing = 1 m -----------------------
fig, ax, t_peak = base_axes(
    r"Diffusivity sweep, spacing = 1 m  (dashed: matching infinite)")
for D, c in zip(D_SWEEP, ["tab:blue", "tab:green", "tab:red"]):
    add_curve(ax, f"graph_partime_infinite_D{D:.0e}", t_peak,
              rf"Inf., $D={D:.0e}$", color=c, lw=1.5, ls="--")
    add_curve(ax, f"graph_partime_dentz_D{D:.0e}_s1.00", t_peak,
              rf"FMD 1 m, $D={D:.0e}$", color=c, lw=2)
ax.legend(fontsize=13)
plt.tight_layout(); plt.savefig("fmd_fig2_diffusivity_sweep.png", dpi=150)

# --- fig 3: site-tied spacings (1/P32 and 1/dQ) ----------------------
fig, ax, t_peak = base_axes(
    rf"Site-tied spacings, $D_m = {D_REF:.0e}$ m$^2$/s")
add_curve(ax, f"graph_partime_infinite_D{D_REF:.0e}", t_peak,
          "Infinite matrix", color="k", lw=2.5)
for (_, row), c in zip(site_rows.iterrows(), ["tab:orange", "tab:purple"]):
    spacing = float(row.fracture_spacing)
    add_curve(ax, row.partime_file, t_peak,
              rf"FMD {row.label} = {spacing:.1f} m", color=c, lw=2)
ax.legend(fontsize=13)
plt.tight_layout(); plt.savefig("fmd_fig3_site_spacing.png", dpi=150)

print("saved fmd_fig1_spacing_sweep.png, fmd_fig2_diffusivity_sweep.png, "
      "fmd_fig3_site_spacing.png")
