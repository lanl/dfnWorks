"""
verify_mpf_gringarten.py
------------------------
Verification script for pydfnworks.thermal.mpf_gringarten (Phase 1
Gringarten multiple parallel fractures heat-extraction surrogate) and the
pydfnworks.thermal.dfn_heat interface stub.

Tests
-----
  1. Laplace-domain limits: s F(s) -> 1 as s -> 0, F(s) -> 0 as s -> inf
  2. Wide-spacing asymptote equals the semi-infinite single-fracture
       solution (Bodvarsson and Tsang 1982 / Lauwerier), erfc closed form
  3. Close spacing gives earlier, stronger thermal decline than wide
       spacing at the same flow rate
  4. Energy balance at close spacing: cumulative heat equals the heat
       stored in the rock slabs
  5. numpy Stehfest inversion matches the GEOPHIRES-X mpmath route
  6. Physical bounds: Q(0) = m_dot c (T_res - T_inj), 0 <= Q <= Q(0),
       T_inj <= T_out <= T_res
  7. Runtime well under a second per call
  8. Interface: both backends reject the same bad inputs with ValueError;
       the Phase 2 stub raises NotImplementedError; thermal-to-TDRW
       parameter mapping
  9. Finite spacing: independent finite-difference solution of the
       coupled slab-conduction / fracture-advection equations converges
       to the Stehfest-inverted Gringarten solution at beta = 1

Run with:
    python verify_mpf_gringarten.py

Each test prints PASS / FAIL with numerical details; the summary line
exits with code 0 (all pass) or 1 (any fail). The test_* functions also
run under pytest.

References
----------
Gringarten, Witherspoon, Ohnishi (1975). J. Geophys. Res. 80(8), 1120-1124.
Bodvarsson, Tsang (1982). J. Geophys. Res. 87(B2), 1031-1048.
Beckers, McCabe (2019). Geothermal Energy 7, 5 (GEOPHIRES-X).
"""

import sys
import time
import numpy as np
from scipy.special import erfc
from scipy.linalg import solve_banded

from pydfnworks.thermal import mpf_gringarten as mpf
from pydfnworks.thermal import dfn_heat
from pydfnworks.thermal.optimize_spacing import time_to_drawdown
from pydfnworks.thermal.common import GRANITE_PROPS, WATER_PROPS, SECONDS_PER_YEAR

print("Testing pydfnworks.thermal.mpf_gringarten and pydfnworks.thermal.dfn_heat")

ROCK = GRANITE_PROPS
FLUID = WATER_PROPS
M_DOT = 60.0
T_RES = 226.0
T_INJ = 40.0
N_FRAC = 20
HEIGHT = 60.0
T_EVAL = np.linspace(0.0, 30 * SECONDS_PER_YEAR, 361)
_trapezoid = getattr(np, "trapezoid", None) or np.trapz


def _call(spacing, t_eval=T_EVAL, **kwargs):
    return mpf.heat_extraction(spacing, M_DOT, T_RES, T_INJ, ROCK, FLUID,
                               N_FRAC, HEIGHT, t_eval, **kwargs)


# ---------------------------------------------------------------------------
# 1. Laplace-domain limits
# ---------------------------------------------------------------------------
def test_laplace_limits():
    beta = 1.0
    small = 1e-12
    large = 1e6
    early = mpf.laplace_drawdown(large, beta)
    late = small * mpf.laplace_drawdown(small, beta)
    print(f"  s F(s) at s=1e-12: {late:.6f} (expect 1);  F(s) at s=1e6: {early:.2e} (expect 0)")
    assert abs(late - 1.0) < 1e-5
    assert early < 1e-12


# ---------------------------------------------------------------------------
# 2. Wide-spacing asymptote: Bodvarsson and Tsang semi-infinite solution
# ---------------------------------------------------------------------------
def test_wide_spacing_limit():
    spacing = 1e6  # m, effectively semi-infinite rock
    Q = _call(spacing)
    params = mpf.dimensionless_parameters(spacing, M_DOT, ROCK, FLUID, N_FRAC, HEIGHT)
    alpha = ROCK["k"] / (ROCK["rho"] * ROCK["c"])
    rho_c_f = FLUID["rho"] * FLUID["c"]
    # outlet drawdown of a single fracture between semi-infinite rock
    # blocks, negligible fracture storage: erfc(k H / (rho_f c_f q_w sqrt(alpha t)))
    T_D = np.zeros_like(T_EVAL)
    pos = T_EVAL > 0
    T_D[pos] = erfc(ROCK["k"] * HEIGHT /
                    (rho_c_f * params["q_w"] * np.sqrt(alpha * T_EVAL[pos])))
    Q_ref = M_DOT * FLUID["c"] * (T_RES - T_INJ) * (1.0 - T_D)
    err = np.max(np.abs(Q - Q_ref)) / Q_ref[0]
    # and the dimensionless form directly against single_fracture_drawdown
    t_D = np.logspace(-3, 3, 50)
    err_D = np.max(np.abs(mpf.dimensionless_drawdown(t_D, params["beta"]) -
                          mpf.single_fracture_drawdown(t_D)))
    print(f"  beta = {params['beta']:.1e}; max |Q - Q_BT| / Q(0) = {err:.2e}; "
          f"max |T_wD - erfc| = {err_D:.2e}")
    assert err < 1e-5
    assert err_D < 1e-5


# ---------------------------------------------------------------------------
# 3. Close vs wide spacing at the same flow rate
# ---------------------------------------------------------------------------
def test_close_spacing_declines_earlier():
    Q_close = _call(5.0)
    Q_wide = _call(100.0)
    Q0 = Q_close[0]
    # never higher (allow Stehfest ringing of 1e-3 Q0)
    excess = np.max(Q_close - Q_wide) / Q0
    E_close = _trapezoid(Q_close, T_EVAL)
    E_wide = _trapezoid(Q_wide, T_EVAL)

    # time to 10 % decline on a fine early-time grid (interpolated)
    t_fine = np.linspace(0.0, 2 * SECONDS_PER_YEAR, 4001)

    def t_decline(spacing, fraction):
        Q = _call(spacing, t_eval=t_fine)
        return time_to_drawdown(t_fine, Q, fraction=fraction)

    # 10 % decline happens in the single-fracture (erfc) regime before the
    # slabs interact, so close spacing is at most as late as wide; 75 %
    # decline needs slab depletion and comes clearly earlier at close spacing
    t10_close, t10_wide = t_decline(5.0, 0.9), t_decline(100.0, 0.9)
    t75_close, t75_wide = t_decline(5.0, 0.25), t_decline(100.0, 0.25)
    print(f"  max (Q_close - Q_wide)/Q0 = {excess:.2e}; E_close/E_wide = {E_close/E_wide:.3f}; "
          f"t_10% close {t10_close/86400:.1f} d vs wide {t10_wide/86400:.1f} d; "
          f"t_75% close {t75_close/86400:.1f} d vs wide {t75_wide/86400:.1f} d")
    assert excess < 1e-3
    assert E_close < 0.5 * E_wide
    assert t10_close <= t10_wide * 1.01
    assert t75_close < 0.8 * t75_wide


# ---------------------------------------------------------------------------
# 4. Energy balance at close spacing
# ---------------------------------------------------------------------------
def test_energy_balance_close_spacing():
    for spacing in (2.0, 5.0):
        params = mpf.dimensionless_parameters(spacing, M_DOT, ROCK, FLUID, N_FRAC, HEIGHT)
        t = np.linspace(0.0, 6 * params["t_piston"], 2001)
        Q = _call(spacing, t_eval=t)
        E = _trapezoid(Q, t)
        E_rock = params["heat_in_place"] * (T_RES - T_INJ)
        print(f"  spacing {spacing} m, beta = {params['beta']:.3f}: "
              f"E / E_rock = {E/E_rock:.4f}, Q(6 t_piston)/Q(0) = {Q[-1]/Q[0]:.1e}")
        assert abs(E / E_rock - 1.0) < 1e-2
        assert Q[-1] / Q[0] < 1e-2


# ---------------------------------------------------------------------------
# 5. numpy Stehfest vs GEOPHIRES-X mpmath inversion
# ---------------------------------------------------------------------------
def test_stehfest_matches_mpmath():
    t_D = np.logspace(-1, 3, 30)
    for beta in (0.5, 1.5, 6.0):
        a = mpf.dimensionless_drawdown(t_D, beta, method="stehfest")
        b = mpf.dimensionless_drawdown(t_D, beta, method="mpmath")
        err = np.max(np.abs(a - b))
        print(f"  beta = {beta}: max |stehfest - mpmath| = {err:.2e}")
        assert err < 1e-3


# ---------------------------------------------------------------------------
# 6. Physical bounds
# ---------------------------------------------------------------------------
def test_physical_bounds():
    for spacing in (1.0, 20.0, 1e4):
        Q = _call(spacing)
        T_out = mpf.production_temperature(spacing, M_DOT, T_RES, T_INJ, ROCK,
                                           FLUID, N_FRAC, HEIGHT, T_EVAL)
        Q0 = M_DOT * FLUID["c"] * (T_RES - T_INJ)
        assert abs(Q[0] - Q0) < 1e-9 * Q0
        assert np.all(Q >= 0.0) and np.all(Q <= Q0 * (1 + 1e-12))
        assert np.all(T_out >= T_INJ) and np.all(T_out <= T_RES)
    print(f"  Q(0) = {Q0/1e6:.2f} MW; Q and T_out inside physical bounds for spacings 1, 20, 1e4 m")


# ---------------------------------------------------------------------------
# 7. Runtime
# ---------------------------------------------------------------------------
def test_runtime():
    _call(20.0)  # warm up
    n = 200
    tic = time.perf_counter()
    for _ in range(n):
        _call(20.0)
    per_call = (time.perf_counter() - tic) / n
    print(f"  {per_call*1e6:.0f} microseconds per call ({T_EVAL.size} times)")
    assert per_call < 0.1


# ---------------------------------------------------------------------------
# 8. Interface: shared validation, Phase 2 stub, TDRW mapping
# ---------------------------------------------------------------------------
def test_interface():
    bad_inputs = [
        dict(spacing=-1.0),
        dict(m_dot=0.0),
        dict(T_inj=T_RES),
        dict(n_fractures=0),
        dict(rock_props={"rho": 2750.0, "c": 790.0}),
        dict(t_eval=np.array([-1.0, 1.0])),
    ]
    base = dict(spacing=20.0, m_dot=M_DOT, T_res=T_RES, T_inj=T_INJ,
                rock_props=ROCK, fluid_props=FLUID, n_fractures=N_FRAC,
                fracture_height=HEIGHT, t_eval=T_EVAL)
    for backend in (mpf.heat_extraction, dfn_heat.heat_extraction):
        for bad in bad_inputs:
            args = {**base, **bad}
            try:
                backend(*[args[k] for k in base])
            except ValueError:
                continue
            raise AssertionError(f"{backend.__module__} accepted {bad}")
    try:
        dfn_heat.heat_extraction(*[base[k] for k in base])
        raise AssertionError("dfn_heat stub did not raise NotImplementedError")
    except NotImplementedError as err:
        assert "run_graph_transport" in str(err)
    tdrw = dfn_heat.thermal_to_tdrw_parameters(ROCK, FLUID)
    alpha = ROCK["k"] / (ROCK["rho"] * ROCK["c"])
    ratio = ROCK["rho"] * ROCK["c"] / (FLUID["rho"] * FLUID["c"])
    assert abs(tdrw["matrix_diffusivity"] - alpha) < 1e-15
    assert abs(tdrw["matrix_porosity"] - ratio) < 1e-12
    print(f"  6 bad inputs rejected by both backends; stub raises NotImplementedError; "
          f"TDRW mapping: porosity-like {ratio:.3f}, diffusivity {alpha:.2e} m^2/s")


# ---------------------------------------------------------------------------
# 9. Finite spacing: finite-difference solution of the governing equations
# ---------------------------------------------------------------------------
def fd_outlet_drawdown(beta, t_end, nz, nx, nt):
    """ Independent finite-difference solution of the MPF equations in the
    dimensionless form of the mpf_gringarten module notes:

        slab:      d theta_r/dt_D = d^2 theta_r/dx_D^2 on 0 < x_D < beta,
                   theta_r(0) = theta_w(z_D), d theta_r/dx_D = 0 at x_D = beta
        fracture:  d theta_w/dz_D = d theta_r/dx_D |_(x_D=0+), theta_w(0) = 1

    Crank-Nicolson in t_D per slab column, first-order upwind march in z_D
    with the wall flux treated implicitly (second-order one-sided
    difference), so the column solve is a (1, 2)-banded system. Returns
    the outlet drawdown theta_w(z_D = 1, t_D) on the time grid used.
    """
    dx = beta / nx
    dz = 1.0 / nz
    theta_r = np.zeros((nz + 1, nx + 1))
    T = 0.0
    times = [0.0]
    out = [0.0]
    dts = list(np.geomspace(t_end / nt * 1e-3, t_end / nt, 100)) + [t_end / nt] * nt
    c = dz / (2 * dx)
    for dt in dts:
        if T >= t_end - 1e-12:
            break
        r = dt / (2 * dx**2)
        ab = np.zeros((4, nx + 1))
        ab[2, :] = 1 + 2 * r
        ab[1, 1:] = -r
        ab[3, :-1] = -r
        ab[3, nx - 1] = -2 * r  # insulated mid-plane (ghost node)
        ab[2, 0] = 1 + 3 * c  # wall row: theta_w(j) = theta_w(j-1) + dz * flux
        ab[1, 1] = -4 * c
        ab[0, 2] = c
        ab_inlet = ab.copy()
        ab_inlet[2, 0], ab_inlet[1, 1], ab_inlet[0, 2] = 1.0, 0.0, 0.0
        theta_w = 1.0
        for j in range(nz + 1):
            old = theta_r[j]
            rhs = old.copy()
            rhs[1:-1] = old[1:-1] + r * (old[:-2] - 2 * old[1:-1] + old[2:])
            rhs[-1] = old[-1] + r * (2 * old[-2] - 2 * old[-1])
            rhs[0] = 1.0 if j == 0 else theta_w
            theta_r[j] = solve_banded((1, 2), ab_inlet if j == 0 else ab, rhs)
            theta_w = theta_r[j, 0]
        T += dt
        times.append(T)
        out.append(theta_w)
    return np.array(times), np.array(out)


def test_finite_difference_cross_check():
    beta = 1.0
    errors = {}
    for label, (nz, nx, nt) in (("coarse", (50, 100, 1500)), ("fine", (100, 200, 3000))):
        t, fd = fd_outlet_drawdown(beta, t_end=6.0, nz=nz, nx=nx, nt=nt)
        st = mpf.dimensionless_drawdown(t, beta)
        mask = t > 0.05
        errors[label] = np.max(np.abs(fd[mask] - st[mask]))
    print(f"  beta = {beta}: max |FD - Stehfest| coarse {errors['coarse']:.2e}, fine {errors['fine']:.2e}")
    assert errors["fine"] < errors["coarse"]
    assert errors["fine"] < 1e-2


TESTS = [
    ("Laplace-domain limits", test_laplace_limits),
    ("Wide-spacing asymptote (Bodvarsson-Tsang)", test_wide_spacing_limit),
    ("Close spacing declines earlier than wide", test_close_spacing_declines_earlier),
    ("Energy balance at close spacing", test_energy_balance_close_spacing),
    ("Stehfest vs GEOPHIRES-X mpmath inversion", test_stehfest_matches_mpmath),
    ("Physical bounds", test_physical_bounds),
    ("Runtime per call", test_runtime),
    ("Interface and Phase 2 stub", test_interface),
    ("Finite-difference cross-check at finite spacing", test_finite_difference_cross_check),
]

if __name__ == "__main__":
    n_fail = 0
    for i, (label, test) in enumerate(TESTS, 1):
        print(f"\nTest {i}: {label}")
        try:
            test()
            print("  PASS")
        except Exception as err:  # report and continue
            n_fail += 1
            print(f"  FAIL: {type(err).__name__}: {err}")
    print(f"\n{'='*60}")
    print(f"  {len(TESTS) - n_fail} of {len(TESTS)} tests passed")
    print(f"{'='*60}")
    sys.exit(1 if n_fail else 0)
