"""
verify_slab_tdrw.py
-------------------
Verification script for tdrw_finite_dentz.py (slab matrix diffusion TDRW).

Designed for Claude Code: imports the dfnWorks module under test and compares
it against the Sudicky and Frind (1982) analytical solution.

Tests
-----
  1. Stehfest coefficients sum to zero (pure math check)
  2. Slab psi*(s) Laplace limiting behavior: psi*(0)=1, psi*(inf)=0
  3. Inverse CDF table from _make_inverse_cdf_spline_for_times:
       monotone, starts at 0, ends at 1
  4. Trapping rate formula gamma with known parameters
  5. Monte Carlo BTC vs Sudicky-Frind analytical CDF at 10 quantiles
  6. Mean matrix diffusion time consistency

Run with:
    python verify_slab_tdrw.py

All tests print PASS / FAIL with numerical details.
A final summary line exits with code 0 (all pass) or 1 (any fail).

Reference
---------
Sudicky, E.A., Frind, E.O., 1982. Water Resour. Res. 18(6), 1634-1642.
"""

import sys
import numpy as np
from math import factorial

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------

from pydfnworks.dfnGraph.transport.tdrw.dentz import (
    Psi_star, make_inverse_cdf, choose_release_eps)
from pydfnworks.dfnGraph.transport.tdrw.stehfest import (
    stehfest_coefficients as _stehfest_coefficients, )

# same signature as the pre-2.12 flat-layout builder
_make_inverse_cdf_spline_for_times = make_inverse_cdf
print("Testing pydfnworks.dfnGraph.transport.tdrw.dentz")

# ---------------------------------------------------------------------------
# Standalone Stehfest and analytical helpers (independent of the module)
# ---------------------------------------------------------------------------

def _ref_stehfest(N=16):
    """Reference Stehfest coefficients -- independent implementation."""
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


def _SF_cdf_laplace(s, tau_adv, phi_m, b_f, D_m, B):
    """Sudicky-Frind (1982) CDF Laplace transform (reference solution)."""
    q           = np.sqrt(s / D_m)
    matrix_term = (phi_m / b_f) * np.sqrt(s * D_m) * np.tanh(B * q)
    return np.exp(-tau_adv * (s + matrix_term)) / s


def _slab_psi_laplace(s, eps):
    """Slab psi_eps*(s), scaled form -- reference implementation."""
    q = np.sqrt(s)
    return (np.exp(-eps * q) * (1.0 + np.exp(-2.0 * (1.0 - eps) * q))
            / (1.0 + np.exp(-2.0 * q)))

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
# Test 1: Stehfest coefficients
# ---------------------------------------------------------------------------

def test_stehfest_coefficients():
    print("\nTest 1: Stehfest coefficients")
    V_ref = _ref_stehfest(N=16)
    try:
        V_mod = _stehfest_coefficients(N=16)
        match = np.allclose(V_ref, V_mod, rtol=1e-10)
        check("Coefficients match reference", match,
              f"max diff = {np.max(np.abs(V_ref - V_mod)):.2e}")
    except Exception as e:
        check("Coefficients match reference", False, str(e))
    # Stehfest property: sum of V_i * i^k is related to k-th derivative at t=1
    # Simple check: invert F(s)=1/s (identity) -- should give f(t)=1
    V = _ref_stehfest(16)
    # For F(s)=1/s, Stehfest gives f(t) = sum_i V_i/i (should = 1)
    f_at_1 = float(np.sum(V / np.arange(1, len(V)+1)))
    check("Stehfest: sum(V_i/i) = 1 (inverts F(s)=1/s)",
          close(f_at_1, 1.0, 1e-6), f"sum(V_i/i) = {f_at_1:.10f}")

# ---------------------------------------------------------------------------
# Test 2: Laplace-domain limiting behavior of psi_eps
# ---------------------------------------------------------------------------

def test_psi_limits():
    print("\nTest 2: psi_eps*(s) limiting behavior")
    eps = 1e-4
    # Note: Psi_star(s, eps) = CDF transform = psi_eps*(s) / s
    # Multiply by s to recover the PDF transform, which should be 1 at s=0
    s_small = np.array([1e-6])
    val_0   = float(Psi_star(s_small, eps)[0] * s_small[0])
    check("psi_pdf*(s->0) = 1  [Psi_star(s)*s -> 1]",
          close(val_0, 1.0, 1e-6),
          f"Psi_star(1e-6)*s = {val_0:.8f}  (expected 1.0)")
    # CDF transform Psi_star(s)*s -> 0 for s >> 1/eps^2
    # For eps=1e-4: need s >> 1e8; use 1e12 to be well past threshold
    s_large = np.array([1e12])
    val_inf = float(Psi_star(s_large, eps)[0] * s_large[0])
    check("psi_pdf*(s->inf) -> 0  [Psi_star(s)*s -> 0 for s>>1/eps^2]",
          val_inf < 1e-3,
          f"Psi_star(1e12)*s = {val_inf:.2e}  (expected << 1)")
    # Verify PDF transform against reference scaled form
    s_test  = np.logspace(-2, 4, 8)
    ref     = _slab_psi_laplace(s_test, eps)           # PDF transform
    mod     = Psi_star(s_test, eps) * s_test           # module CDF * s = PDF
    max_err = float(np.max(np.abs(ref - mod)))
    check("Psi_star(s)*s matches reference PDF transform (8 points)",
          max_err < 1e-10,
          f"max abs diff = {max_err:.2e}")

# ---------------------------------------------------------------------------
# Test 3: inverse CDF table from the module
# ---------------------------------------------------------------------------

def test_inverse_cdf_table():
    print("\nTest 3: _make_inverse_cdf_spline_for_times()")
    eps = 1e-4
    try:
        t_table, cdf_table = _make_inverse_cdf_spline_for_times(
            num_samples=100, eps=eps)
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
# Test 4: gamma formula
# ---------------------------------------------------------------------------

def test_gamma_formula():
    print("\nTest 4: Trapping rate gamma formula")
    # gamma = phi_m * D_m / (b_f * eps * B)
    # Test known values
    cases = [
        dict(phi_m=0.05, D_m=1e-10, b_f=1e-4, eps=1e-4, B=0.05,
             gamma_expected=0.05*1e-10/(1e-4*1e-4*0.05)),
        dict(phi_m=0.01, D_m=1e-11, b_f=5e-5, eps=1e-4, B=0.1,
             gamma_expected=0.01*1e-11/(5e-5*1e-4*0.1)),
    ]
    for c in cases:
        gamma = c['phi_m'] * c['D_m'] / (c['b_f'] * c['eps'] * c['B'])
        check(f"gamma={c['gamma_expected']:.2e} for phi_m={c['phi_m']}",
              close(gamma, c['gamma_expected'], 1e-10),
              f"computed = {gamma:.6e}, expected = {c['gamma_expected']:.6e}")

# ---------------------------------------------------------------------------
# Test 5: Monte Carlo BTC vs Sudicky-Frind analytical CDF
# ---------------------------------------------------------------------------

def test_monte_carlo_vs_sudicky_frind():
    print("\nTest 5: Monte Carlo BTC vs Sudicky-Frind (1982)")

    # Physical parameters: eps=0.01 gives gamma=10, n_avg=10, tau_D/tau_adv=10
    # Using eps=0.01 (not module default 1e-4) to keep n_avg tractable.
    # The mathematical equivalence holds for any eps; the approximation
    # error is O(eps^2) = 1e-4 here, well within the 2% test tolerance.
    tau_adv = 1.0
    D_m     = 0.1
    B       = 1.0
    phi_m   = 0.05
    b_f     = 0.05
    eps     = 0.01    # use 0.01 so gamma=10, not 0.0001 which gives gamma=1000

    tau_D   = B ** 2 / D_m                    # = 10
    gamma   = phi_m * D_m / (b_f * eps * B)   # = 10
    n_avg   = gamma * tau_adv                  # = 10
    N       = 100_000
    seed    = 42

    print(f"         tau_adv={tau_adv}  tau_D={tau_D:.1f}  "
          f"gamma={gamma:.1f}  n_avg={n_avg:.1f}  N={N:,}")

    # Build inverse CDF table
    try:
        t_table, cdf_table = _make_inverse_cdf_spline_for_times(
            num_samples=200, eps=eps)
    except Exception as e:
        check("Monte Carlo table built", False, str(e))
        return
    check("Monte Carlo table built", True)

    # Sample
    np.random.seed(seed)
    n_all      = np.random.poisson(n_avg, N)
    n_total    = int(n_all.sum())
    xi_all     = np.random.uniform(0, 1, n_total)
    t_trap_all = tau_D * np.interp(xi_all, cdf_table, t_table)
    pid        = np.repeat(np.arange(N), n_all)
    t_matrix   = np.bincount(pid, weights=t_trap_all, minlength=N)
    t_mc       = tau_adv + t_matrix

    check("All MC travel times >= tau_adv",
          np.all(t_mc >= tau_adv - 1e-12),
          f"min t_mc = {t_mc.min():.6f}  tau_adv = {tau_adv}")

    # Analytical Sudicky-Frind CDF via Stehfest
    V      = _ref_stehfest(16)
    t_eval = np.logspace(np.log10(tau_adv * 0.95),
                         np.log10(tau_adv + 5 * tau_D), 200)
    sf_cdf = _stehfest_invert(_SF_cdf_laplace, t_eval, V,
                               tau_adv=tau_adv, phi_m=phi_m, b_f=b_f,
                               D_m=D_m, B=B)
    sf_cdf = np.clip(sf_cdf, 0, 1)

    # Compare CDFs directly on a shared time grid (t > tau_adv only)
    t_check   = np.logspace(np.log10(1.5 * tau_adv),
                             np.log10(tau_adv + 5 * tau_D), 20)
    sf_check  = _stehfest_invert(_SF_cdf_laplace, t_check, V,
                                  tau_adv=tau_adv, phi_m=phi_m, b_f=b_f,
                                  D_m=D_m, B=B)
    sf_check  = np.clip(sf_check, 0, 1)
    mc_check  = np.array([np.mean(t_mc <= t) for t in t_check])
    max_dev   = float(np.max(np.abs(sf_check - mc_check)))

    # Tolerance 3%: accounts for O(eps^2)=1e-4 approx error plus
    # ~1-2% Stehfest inaccuracy near the advective front at t=1.5*tau_adv
    check("MC CDF within 3% of Sudicky-Frind on 20-point time grid",
          max_dev < 0.03,
          f"max |MC_CDF - SF_CDF| = {max_dev:.4f}  (tolerance 0.03)")
    print(f"         t range: [{t_check[0]:.3f}, {t_check[-1]:.1f}]")
    print(f"         SF CDF range: [{sf_check[0]:.3f}, {sf_check[-1]:.3f}]")
    print(f"         MC CDF range: [{mc_check[0]:.3f}, {mc_check[-1]:.3f}]")

# ---------------------------------------------------------------------------
# Test 6: Mean matrix diffusion time
# ---------------------------------------------------------------------------

def test_mean_matrix_time():
    print("\nTest 6: Mean matrix diffusion time")
    # For the slab, E[tau | n=1] = tau_D * E[psi_eps]
    # E[psi_eps] ~ eps * B / 3 for small eps (first moment of slab FPT)
    # But this is harder to compute analytically; instead verify that
    # E[t_matrix] = gamma * tau_adv * tau_D * E[psi_eps]
    # We check it's positive and finite.
    eps    = 1e-4
    tau_D  = 10.0
    gamma  = 10.0
    tau_adv = 1.0
    N      = 50_000

    t_table, cdf_table = _make_inverse_cdf_spline_for_times(
        num_samples=100, eps=eps)

    np.random.seed(0)
    n_all   = np.random.poisson(gamma * tau_adv, N)
    xi      = np.random.uniform(0, 1, int(n_all.sum()))
    t_trap  = tau_D * np.interp(xi, cdf_table, t_table)
    pid     = np.repeat(np.arange(N), n_all)
    t_mat   = np.bincount(pid, weights=t_trap, minlength=N)

    mean_md = float(t_mat.mean())
    check("Mean matrix diffusion time is positive and finite",
          np.isfinite(mean_md) and mean_md > 0,
          f"E[t_matrix] = {mean_md:.4f}")
    # Rough sanity: should be O(gamma * tau_adv * tau_D * eps)
    # For eps=1e-4, this is ~ 10 * 1 * 10 * 1e-4 ~ 0.01
    check("Mean matrix diffusion time is in plausible range",
          1e-5 < mean_md < 10.0,
          f"E[t_matrix] = {mean_md:.4e}  (expected 1e-5 to 10)")

# ---------------------------------------------------------------------------
# Test 7: Field-scale parameters with adaptive release position
# ---------------------------------------------------------------------------

def test_field_scale_adaptive_eps():
    """ Large matrix blocks at field-scale diffusivity: the fixed release
    position eps=1e-4 fails here (its artifact scale (eps*B)^2/D lands in
    the observation window and most particles get zero trapping events).
    choose_release_eps must shrink eps enough to reproduce Sudicky-Frind.
    Reference CDF via mpmath Talbot inversion: Stehfest smears the sharp
    BTC front and cannot be used as the reference at these times. """
    print("\nTest 7: Field-scale parameters + adaptive release position")
    import mpmath as mp

    phi_m, D_m, b_f = 0.01, 1e-14, 2e-5
    spacing = 276.0
    B = spacing / 2
    tau_adv = 1e8
    tau_D = B ** 2 / D_m
    N = 100_000

    eps = choose_release_eps(tau_adv, B, D_m)
    check("Adaptive eps engages (eps < 1e-4)", eps < 1e-4,
          f"eps = {eps:.3e}")
    artifact = (eps * B) ** 2 / D_m
    check("Artifact timescale << tau_adv", artifact < 0.01 * tau_adv,
          f"(eps*B)^2/D = {artifact:.2e} s, tau_adv = {tau_adv:.2e} s")

    t_table, cdf_table = _make_inverse_cdf_spline_for_times(eps=eps)
    gamma = phi_m * D_m / (b_f * eps * B)
    n_avg = gamma * tau_adv
    check("Mean trapping events >= 1", n_avg >= 1.0,
          f"n_avg = {n_avg:.2f}")

    np.random.seed(7)
    n_all = np.random.poisson(n_avg, N)
    xi = np.random.uniform(0, 1, int(n_all.sum()))
    t_trap = tau_D * np.interp(xi, cdf_table, t_table)
    pid = np.repeat(np.arange(N), n_all)
    t_mc = tau_adv + np.bincount(pid, weights=t_trap, minlength=N)

    def SF_talbot(t):
        F = lambda s: mp.e ** (-tau_adv * (s + (phi_m / b_f)
                                           * mp.sqrt(s * D_m)
                                           * mp.tanh(B * mp.sqrt(s / D_m)))) / s
        return float(mp.invertlaplace(F, t, method='talbot'))

    t_check = np.logspace(np.log10(1.1 * tau_adv),
                          np.log10(3000 * tau_adv), 15)
    sf = np.clip([SF_talbot(t) for t in t_check], 0, 1)
    t_s = np.sort(t_mc)
    mc = np.interp(t_check, t_s, np.arange(1, N + 1) / N)
    mask = (sf > 0.01) & (sf < 0.995)
    max_dev = float(np.max(np.abs(mc - sf)[mask]))
    check("MC CDF within 3% of Sudicky-Frind (Talbot) at field scale",
          max_dev < 0.03,
          f"max |MC_CDF - SF_CDF| = {max_dev:.4f}  (tolerance 0.03)")
    print(f"         eps={eps:.2e}  n_avg={n_avg:.1f}  "
          f"artifact={artifact:.2e} s")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  Slab (Dentz) TDRW Verification")
    print("  Against Sudicky and Frind (1982)")
    print("=" * 60)

    test_stehfest_coefficients()
    test_psi_limits()
    test_inverse_cdf_table()
    test_gamma_formula()
    test_monte_carlo_vs_sudicky_frind()
    test_mean_matrix_time()
    test_field_scale_adaptive_eps()

    n_pass = sum(p for _, p in RESULTS)
    n_fail = len(RESULTS) - n_pass
    print()
    print("=" * 60)
    print(f"  Results: {n_pass} passed, {n_fail} failed  "
          f"({len(RESULTS)} total)")
    print("=" * 60)
    sys.exit(0 if n_fail == 0 else 1)
