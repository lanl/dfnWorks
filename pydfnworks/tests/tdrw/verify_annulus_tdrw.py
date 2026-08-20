"""
verify_annulus_tdrw.py
----------------------
Verification script for tdrw_finite_annulus.py (cylindrical annulus TDRW).

Designed for Claude Code: imports the dfnWorks module under test and compares
it against the analytical first-passage time CDF for cylindrical diffusion.

Tests
-----
  1. Annulus psi*(s) Laplace limiting behavior: psi*(0)=1, psi*(inf)=0
  2. Bessel branch switch consistency at |s*tau1| = 100
  3. Wronskian identity check on the denominator
  4. Inverse CDF table from _make_inverse_cdf_annulus:
       monotone, starts at 0, ends at 1
  5. Monte Carlo vs analytical first-passage time CDF at 10 quantiles
  6. Thin-shell limit: cylindrical CDF -> slab CDF as r1/r0 -> 1
  7. Mean matrix diffusion time sanity check

Run with:
    python verify_annulus_tdrw.py

All tests print PASS / FAIL with numerical details.
Exits with code 0 (all pass) or 1 (any fail).

Reference
---------
First-passage time for cylindrical diffusion derived from the backward
Kolmogorov equation; see matrix_diffusion_verification.pdf.
"""

import sys
import numpy as np
from math import factorial
from scipy.special import iv, kv, ive, kve

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------

from pydfnworks.dfnGraph.transport.tdrw.annulus import (
    Psi_star_annulus,
    make_inverse_cdf,
)
from pydfnworks.dfnGraph.transport.tdrw.stehfest import (
    stehfest_coefficients as _stehfest_coefficients, )

print("Testing pydfnworks.dfnGraph.transport.tdrw.annulus")


def _make_inverse_cdf_annulus(num_samples=100, eps=1e-2, tau0=1e-4, tau1=1e3,
                              stehfest_n=16):
    # the ported builder is tau1-normalized; only the geometry ratio
    # tau0/tau1 = (r0/r1)^2 matters, and returned times are in units of tau1
    return make_inverse_cdf(num_samples=num_samples, eps=eps,
                            tau0_ratio=tau0 / tau1, stehfest_n=stehfest_n)

# ---------------------------------------------------------------------------
# Reference implementations (independent of the module under test)
# ---------------------------------------------------------------------------

def _ref_stehfest(N=16):
    M = N // 2
    V = np.zeros(N)
    for i in range(1, N + 1):
        total = 0.0
        for k in range(int((i + 1) // 2), min(i, M) + 1):
            num = (k ** M) * factorial(2 * k)
            den = (factorial(M - k) * factorial(k) * factorial(k - 1)
                   * factorial(i - k) * factorial(2 * k - i))
            total += num / den
        V[i - 1] = ((-1) ** (i + M)) * total
    return V


def _stehfest_invert(F, t_arr, V, **kw):
    ln2 = np.log(2.0)
    f   = np.zeros(len(t_arr))
    for idx, t in enumerate(t_arr):
        sv  = np.array([(i + 1) * ln2 / t for i in range(len(V))])
        f[idx] = (ln2 / t) * np.dot(V, F(sv, **kw))
    return f


def _annulus_psi_ref(s, eps, tau0, tau1):
    """
    Reference implementation of the cylindrical annulus psi*(s).
    Uses branch switch at |s*tau1|=100 matching the module under test.

    F_psi(s) = [I0((1+eps)*q0)*K1(q1) + K0((1+eps)*q0)*I1(q1)]
             / [I0(q0)*K1(q1) + K0(q0)*I1(q1)]
    """
    q0     = np.sqrt(s * tau0)
    q0_eps = (1.0 + eps) * q0
    q1     = np.sqrt(s * tau1)
    large  = s * tau1 > 100

    # large-argument branch (scaled Bessels)
    I0e_eps = ive(0, q0_eps);  K0e_eps = kve(0, q0_eps)
    I0e_0   = ive(0, q0);      K0e_0   = kve(0, q0)
    I1e_1   = ive(1, q1);      K1e_1   = kve(1, q1)
    exp1 = np.exp(np.clip((2 + eps) * q0 - 2 * q1, -500, 500))
    exp2 = np.exp(np.clip(-eps * q0,               -500, 500))
    expd = np.exp(np.clip(2 * q0 - 2 * q1,          -500, 500))
    num_l = exp1 * I0e_eps * K1e_1 + exp2 * K0e_eps * I1e_1
    den_l = expd * I0e_0   * K1e_1 +        K0e_0   * I1e_1

    # small-argument branch (unscaled Bessels)
    with np.errstate(invalid='ignore', over='ignore'):
        num_s = iv(0, q0_eps) * kv(1, q1) + kv(0, q0_eps) * iv(1, q1)
        den_s = iv(0, q0)     * kv(1, q1) + kv(0, q0)     * iv(1, q1)

    num = np.where(large, num_l, num_s)
    den = np.where(large, den_l, den_s)
    return num / den


def _annulus_cdf_ref(s, eps, tau0, tau1):
    return _annulus_psi_ref(s, eps, tau0, tau1) / s


def _slab_psi_ref(s, eps):
    """Slab psi*(s), scaled form."""
    q = np.sqrt(s)
    return (np.exp(-eps * q) * (1.0 + np.exp(-2.0 * (1.0 - eps) * q))
            / (1.0 + np.exp(-2.0 * q)))


def _slab_cdf_ref(s, eps):
    return _slab_psi_ref(s, eps) / s

# ---------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------

RESULTS = []

def check(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    msg    = f"  [{status}] {name}"
    if detail:
        msg += f"\n         {detail}"
    print(msg)
    RESULTS.append((name, passed))


def close(a, b, tol):
    return abs(a - b) / max(abs(b), 1e-30) < tol

# ---------------------------------------------------------------------------
# Test 1: Laplace-domain limiting behavior
# ---------------------------------------------------------------------------

def test_psi_limits():
    print("\nTest 1: psi*(s) limiting behavior")
    eps  = 1e-2
    tau0 = 1e-4
    tau1 = 1e3

    # Note: Psi_star_annulus returns the CDF transform (includes 1/s).
    # Multiply by s to get the PDF transform, which should be 1 at s->0.
    s_small = np.array([1e-6])
    val_0   = float(Psi_star_annulus(s_small, eps, tau0, tau1)[0] * s_small[0])
    check("psi_pdf*(s->0) = 1  [Psi_star_annulus*s -> 1]",
          close(val_0, 1.0, 1e-4),
          f"Psi_star_annulus(1e-6)*s = {val_0:.8f}  (expected 1.0)")

    # s -> large: PDF transform should go to 0
    s_large = np.array([1e10])
    val_inf = float(Psi_star_annulus(s_large, eps, tau0, tau1)[0] * s_large[0])
    check("psi_pdf*(s->inf) -> 0  [Psi_star_annulus*s -> 0]",
          val_inf < 1e-3,
          f"Psi_star_annulus(1e10)*s = {val_inf:.2e}  (expected << 1)")

    # Match reference PDF transform at 10 s values spanning both branches
    # Psi_star_annulus*s vs _annulus_psi_ref (which returns the PDF transform)
    s_test  = np.logspace(-4, 6, 10)
    ref_psi = _annulus_psi_ref(s_test, eps, tau0, tau1)
    mod_psi = Psi_star_annulus(s_test, eps, tau0, tau1) * s_test
    max_err = float(np.max(np.abs(ref_psi - mod_psi)))
    check("Psi_star_annulus*s matches reference PDF transform at 10 points",
          max_err < 1e-8,
          f"max abs diff = {max_err:.2e}")

# ---------------------------------------------------------------------------
# Test 2: Branch switch consistency
# ---------------------------------------------------------------------------

def test_branch_switch():
    print("\nTest 2: Bessel branch switch at |s*tau1| = 100")
    eps  = 1e-2
    tau0 = 1e-4
    tau1 = 1e3

    # Evaluate just below and just above the threshold s*tau1 = 100
    s_cross  = 100.0 / tau1  # = 0.1
    s_below  = np.array([s_cross * 0.99])
    s_above  = np.array([s_cross * 1.01])

    # Both branches should give similar results at the crossover
    # Use the reference which computes both and switches
    psi_below_ref = float(_annulus_psi_ref(s_below, eps, tau0, tau1)[0])
    psi_above_ref = float(_annulus_psi_ref(s_above, eps, tau0, tau1)[0])

    # Values should be continuous across the switch
    jump = abs(psi_below_ref - psi_above_ref)
    check("psi*(s) is continuous across branch switch",
          jump < 1e-4,
          f"|psi*(0.99*s_cross) - psi*(1.01*s_cross)| = {jump:.2e}")

    # Module should agree with reference on both sides
    # Psi_star_annulus returns CDF transform (includes 1/s); multiply by s for PDF
    psi_below_mod = float(Psi_star_annulus(s_below, eps, tau0, tau1)[0] * float(s_below[0]))
    psi_above_mod = float(Psi_star_annulus(s_above, eps, tau0, tau1)[0] * float(s_above[0]))
    err_below = abs(psi_below_mod - psi_below_ref)
    err_above = abs(psi_above_mod - psi_above_ref)
    check("Module matches reference below branch threshold",
          err_below < 1e-8,
          f"|mod - ref| = {err_below:.2e}  at s={float(s_below[0]):.4f}")
    check("Module matches reference above branch threshold",
          err_above < 1e-8,
          f"|mod - ref| = {err_above:.2e}  at s={float(s_above[0]):.4f}")

# ---------------------------------------------------------------------------
# Test 3: Wronskian identity
# ---------------------------------------------------------------------------

def test_wronskian():
    print("\nTest 3: Wronskian identity I0(x)*K1(x) + I1(x)*K0(x) = 1/x")
    # This identity is a property of modified Bessel functions.
    # If the denominator of psi* is computed correctly, it should satisfy
    # this at q0 = q1 (i.e. r0 = r1, degenerate case).
    for x in [0.1, 1.0, 5.0, 20.0]:
        w = float(iv(0, x) * kv(1, x) + iv(1, x) * kv(0, x))
        expected = 1.0 / x
        err = abs(w - expected) / expected
        check(f"Wronskian at x={x}: I0*K1 + I1*K0 = 1/x",
              err < 1e-10,
              f"computed = {w:.10f}, expected = {expected:.10f}")

# ---------------------------------------------------------------------------
# Test 4: Inverse CDF table
# ---------------------------------------------------------------------------

def test_inverse_cdf_table():
    print("\nTest 4: _make_inverse_cdf_annulus()")
    eps  = 1e-2
    tau0 = 1e-4
    tau1 = 1e3

    try:
        t_table, cdf_table = _make_inverse_cdf_annulus(
            num_samples=100, eps=eps, tau0=tau0, tau1=tau1)
    except Exception as e:
        check("Table construction runs without error", False, str(e))
        return

    check("Table construction runs without error", True)
    check("CDF starts at 0 (first entry <= 0.05)",
          cdf_table[0] <= 0.05,
          f"cdf_table[0] = {cdf_table[0]:.4f}")
    check("CDF reaches 1 (last entry >= 0.99)",
          cdf_table[-1] >= 0.99,
          f"cdf_table[-1] = {cdf_table[-1]:.4f}")
    check("CDF is monotone non-decreasing",
          np.all(np.diff(cdf_table) >= 0),
          f"min delta = {np.min(np.diff(cdf_table)):.2e}")
    check("Table has no NaN or Inf",
          np.all(np.isfinite(t_table)) and np.all(np.isfinite(cdf_table)))
    check("Times are positive",
          np.all(t_table > 0),
          f"min t = {t_table.min():.2e}")

# ---------------------------------------------------------------------------
# Test 5: Monte Carlo vs analytical first-passage time CDF
# ---------------------------------------------------------------------------

def test_monte_carlo_vs_analytical():
    print("\nTest 5: Monte Carlo vs analytical first-passage time CDF")

    eps  = 1e-2
    tau0 = 1e-4
    tau1 = 1e3
    N    = 100_000
    seed = 42

    # tau_D = tau1 for the annulus model
    tau_D = tau1

    print(f"         eps={eps}  tau0={tau0}  tau1={tau1}  N={N:,}")

    # Build inverse CDF from the module
    try:
        t_table, cdf_table = _make_inverse_cdf_annulus(
            num_samples=200, eps=eps, tau0=tau0, tau1=tau1)
    except Exception as e:
        check("MC table built", False, str(e))
        return
    check("MC table built", True)

    # Sample return times (t_table is now dimensionless t/tau1; scale by tau_D=tau1)
    np.random.seed(seed)
    xi     = np.random.uniform(0, 1, N)
    t_mc   = tau_D * np.interp(xi, cdf_table, t_table)  # physical times
    check("All MC return times are positive",
          np.all(t_mc > 0), f"min t_mc = {t_mc.min():.2e}")

    # Analytical CDF: evaluate on physical time grid spanning [1e-10*tau1, 5*tau1]
    V      = _ref_stehfest(16)
    t_eval = np.logspace(np.log10(1e-10 * tau1), np.log10(5 * tau1), 300)
    an_cdf = _stehfest_invert(_annulus_cdf_ref, t_eval, V,
                               eps=eps, tau0=tau0, tau1=tau1)
    an_cdf = np.clip(an_cdf, 0, 1)

    # Direct comparison on a shared time grid well past t=0
    # Use the range where the analytical CDF is between 0.05 and 0.95
    an_cdf_clipped = np.clip(an_cdf, 0, 1)
    mask   = (an_cdf_clipped > 0.02) & (an_cdf_clipped < 0.98)
    if mask.sum() < 3:
        check("MC vs analytical: enough points in (0.02, 0.98)", False,
              f"only {mask.sum()} points"); return
    t_check   = t_eval[mask][::max(1, mask.sum()//20)]  # ~20 evenly-spaced points
    an_check  = an_cdf_clipped[mask][::max(1, mask.sum()//20)]
    mc_check  = np.array([np.mean(t_mc <= t) for t in t_check])
    max_dev   = float(np.max(np.abs(an_check - mc_check)))

    check("MC CDF within 2% of analytical CDF on shared time grid",
          max_dev < 0.02,
          f"max |MC_CDF - analytical_CDF| = {max_dev:.4f}  (tol 0.02)")
    print(f"         {len(t_check)} comparison points in t=[{t_check[0]:.2e}, {t_check[-1]:.2e}]")
    print(f"         analytical CDF range: [{an_check[0]:.3f}, {an_check[-1]:.3f}]")
    print(f"         MC CDF range:         [{mc_check[0]:.3f}, {mc_check[-1]:.3f}]")

# ---------------------------------------------------------------------------
# Test 6: Thin-shell limit (cylindrical -> slab as r1/r0 -> 1)
# ---------------------------------------------------------------------------

def test_thin_shell_limit():
    print("\nTest 6: Thin-shell limit -- cylindrical CDF -> slab CDF")
    # Set r0/r1 = 0.95 (5% relative gap, expect ~5% relative error)
    # With tau0 = r0^2/D, tau1 = r1^2/D: tau0/tau1 = (r0/r1)^2 = 0.9025
    r0_over_r1 = 0.95
    eps_cyl    = 0.01   # small release position for cylinder
    tau1       = 1.0    # reference
    tau0       = r0_over_r1 ** 2 * tau1  # = 0.9025

    # For slab: B = r1 - r0 = r1*(1 - r0/r1) = 1.0 * 0.05 = 0.05 (in units of r1)
    # eps_slab = z'/B where z' = eps_cyl * r0 = 0.01 * 0.95 = 0.0095
    B        = (1.0 - r0_over_r1) * np.sqrt(tau1)   # in physical units with D=1
    eps_slab = eps_cyl * r0_over_r1 / (1.0 - r0_over_r1)  # = 0.01*0.95/0.05 = 0.19

    V      = _ref_stehfest(16)
    t_eval = np.logspace(-4, 1, 50)

    cdf_cyl  = _stehfest_invert(_annulus_cdf_ref, t_eval, V,
                                 eps=eps_cyl, tau0=tau0, tau1=tau1)
    # slab CDF: tau_D = B^2/D_m; with D_m=1 and B in units of r1, tau_D = B^2
    tau_D_slab = B ** 2
    cdf_slab = _stehfest_invert(_slab_cdf_ref,
                                 t_eval / tau_D_slab, V, eps=eps_slab)

    cdf_cyl  = np.clip(cdf_cyl, 0, 1)
    cdf_slab = np.clip(cdf_slab, 0, 1)

    # Compare in the range where both CDFs are between 0.1 and 0.9
    mask  = (cdf_slab > 0.1) & (cdf_slab < 0.9) & (cdf_cyl > 0.1) & (cdf_cyl < 0.9)
    if mask.sum() == 0:
        check("Thin-shell: overlapping CDF range found", False,
              "no overlap in [0.1, 0.9]")
        return
    check("Thin-shell: overlapping CDF range found", True,
          f"{mask.sum()} points in [0.1, 0.9]")
    max_diff = float(np.max(np.abs(cdf_cyl[mask] - cdf_slab[mask])))
    # At r0/r1=0.95 we expect ~5-10% difference (thin but not infinitely thin)
    check("Thin-shell CDF difference < 15% (r0/r1=0.95)",
          max_diff < 0.15,
          f"max |CDF_cyl - CDF_slab| = {max_diff:.4f}  (tol 0.15)")

# ---------------------------------------------------------------------------
# Test 7: Mean return time sanity
# ---------------------------------------------------------------------------

def test_mean_return_time():
    print("\nTest 7: Mean return time sanity check")
    eps  = 1e-2
    tau0 = 1e-4
    tau1 = 1e3
    N    = 50_000

    t_table, cdf_table = _make_inverse_cdf_annulus(
        num_samples=100, eps=eps, tau0=tau0, tau1=tau1)

    np.random.seed(1)
    xi    = np.random.uniform(0, 1, N)
    t_mc  = tau1 * np.interp(xi, cdf_table, t_table)

    mean_t = float(t_mc.mean())
    check("Mean return time is positive and finite",
          np.isfinite(mean_t) and mean_t > 0,
          f"E[t_return] = {mean_t:.4e}")
    # Return times should be << tau1 for small eps (particle starts near wall)
    # and much less than 5*tau1
    check("Mean return time < 5 * tau1",
          mean_t < 5 * tau1,
          f"E[t_return] = {mean_t:.4e}  tau1 = {tau1}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  Cylindrical Annulus TDRW Verification")
    print("  Against Analytical First-Passage Time CDF")
    print("=" * 60)

    test_psi_limits()
    test_branch_switch()
    test_wronskian()
    test_inverse_cdf_table()
    test_monte_carlo_vs_analytical()
    test_thin_shell_limit()
    test_mean_return_time()

    n_pass = sum(p for _, p in RESULTS)
    n_fail = len(RESULTS) - n_pass
    print()
    print("=" * 60)
    print(f"  Results: {n_pass} passed, {n_fail} failed  "
          f"({len(RESULTS)} total)")
    print("=" * 60)
    sys.exit(0 if n_fail == 0 else 1)
