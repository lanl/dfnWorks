"""
verify_spacing_optimizer.py
---------------------------
Verification script for pydfnworks.thermal.optimize_spacing.

Tests
-----
  1. Objective helpers: cumulative_heat and time_to_drawdown on synthetic
       curves, including interpolation and censoring
  2. Grid search returns the objective curve over the search range and a
       best spacing consistent with the surrogate physics (wider spacing
       extracts more heat at fixed fracture count)
  3. scipy refinements ("bounded", "differential_evolution") do at least as
       well as the grid and stay inside the bounds
  4. Explicit candidate spacings and a callable stage-count coupling
  5. Backend decoupling: pointing the optimizer at the Phase 2 stub changes
       nothing but the dispatch and surfaces NotImplementedError; unknown
       methods and bad bounds raise ValueError

Run with:
    python verify_spacing_optimizer.py
"""

import sys
import functools
import numpy as np

from pydfnworks.thermal import (optimize_spacing, cumulative_heat,
                                time_to_drawdown, get_backend, BACKENDS)
from pydfnworks.thermal import mpf_gringarten, dfn_heat
from pydfnworks.thermal.common import GRANITE_PROPS, WATER_PROPS, SECONDS_PER_YEAR

print("Testing pydfnworks.thermal.optimize_spacing")

T_EVAL = np.linspace(0.0, 30 * SECONDS_PER_YEAR, 181)
COMMON = dict(m_dot=60.0,
              T_res=226.0,
              T_inj=40.0,
              rock_props=GRANITE_PROPS,
              fluid_props=WATER_PROPS,
              fracture_height=60.0,
              t_eval=T_EVAL)


def test_objectives():
    t = np.array([0.0, 1.0, 2.0, 3.0])
    Q = np.array([10.0, 10.0, 5.0, 0.0])
    assert abs(cumulative_heat(t, Q) - 20.0) < 1e-12
    # threshold 0.9*10 = 9 crossed between t=1 (10) and t=2 (5): t = 1.2
    assert abs(time_to_drawdown(t, Q, fraction=0.9) - 1.2) < 1e-12
    # never reached: censored at t[-1]
    assert time_to_drawdown(t, np.full(4, 10.0)) == 3.0
    # already below at t[0]
    assert time_to_drawdown(t, Q, fraction=1.5) == 0.0
    print("  cumulative_heat = 20.0, time_to_drawdown = 1.2, censored = 3.0, immediate = 0.0")


def test_grid_search():
    res = optimize_spacing((2.0, 200.0), n_fractures=20, method="grid", n_grid=15, **COMMON)
    assert res["spacings"].size == 15
    assert np.all(np.diff(res["spacings"]) > 0)
    assert 2.0 <= res["spacing"] <= 200.0
    assert res["n_fractures"] == 20 and res["Q"].shape == T_EVAL.shape
    # fixed count: more rock per fracture extracts more heat over 30 years
    assert np.all(np.diff(res["objectives"]) >= -1e-6 * res["objectives"].max())
    assert res["spacing"] == res["spacings"][-1]
    print(f"  15 spacings evaluated; cumulative heat increases with spacing; "
          f"best = {res['spacing']:.1f} m, {res['objective']/1e15:.3f} PJ")


def test_scipy_refinement():
    grid = optimize_spacing((2.0, 200.0), n_fractures=20, method="grid", n_grid=10, **COMMON)
    for method in ("bounded", "differential_evolution"):
        res = optimize_spacing((2.0, 200.0), n_fractures=20, method=method, n_grid=10, **COMMON)
        assert res["scipy_result"] is not None
        assert 2.0 <= res["spacing"] <= 200.0
        assert res["objective"] >= grid["objective"] * (1 - 1e-12)
        assert res["spacings"].size > 10
        print(f"  {method}: best {res['spacing']:.2f} m after {res['spacings'].size} evaluations "
              f"(grid best {grid['spacing']:.2f} m)")


def test_candidates_and_coupling():
    lateral = 300.0
    n_of = lambda spacing: int(round(lateral / spacing))
    candidates = lateral / np.arange(2, 31)
    objective = functools.partial(time_to_drawdown, fraction=0.9)
    res = optimize_spacing((5.0, lateral), n_fractures=n_of, objective=objective,
                           spacings=candidates, **COMMON)
    assert res["spacings"].size == candidates.size
    assert res["n_fractures"] == n_of(res["spacing"])
    # fixed lateral and flow: the sharpest front (most stages) delays drawdown most
    assert res["spacing"] == candidates.min()
    print(f"  {candidates.size} stage counts; best spacing {res['spacing']:.1f} m "
          f"with {res['n_fractures']} stages, t_10% = {res['objective']/SECONDS_PER_YEAR:.2f} yr")


def test_backend_decoupling():
    assert get_backend() is mpf_gringarten.heat_extraction
    assert get_backend("dfn_heat") is dfn_heat.heat_extraction
    assert set(BACKENDS) == {"mpf_gringarten", "dfn_heat"}
    try:
        optimize_spacing((2.0, 200.0), n_fractures=20, n_grid=3,
                         heat_extraction=get_backend("dfn_heat"), **COMMON)
        raise AssertionError("Phase 2 stub did not raise")
    except NotImplementedError:
        pass
    for bad in (dict(method="newton"), dict(bounds=(10.0, 1.0))):
        args = dict(bounds=(2.0, 200.0), n_fractures=20, n_grid=3, **COMMON)
        args.update(bad)
        try:
            optimize_spacing(**args)
            raise AssertionError(f"accepted {bad}")
        except ValueError:
            pass
    try:
        get_backend("finite_element")
        raise AssertionError("unknown backend accepted")
    except ValueError:
        pass
    print("  backend swap raises NotImplementedError; bad method, bounds, and backend name raise ValueError")


TESTS = [
    ("Objective helpers", test_objectives),
    ("Grid search", test_grid_search),
    ("scipy refinements", test_scipy_refinement),
    ("Candidate spacings and stage-count coupling", test_candidates_and_coupling),
    ("Backend decoupling and argument checks", test_backend_decoupling),
]

if __name__ == "__main__":
    n_fail = 0
    for i, (label, test) in enumerate(TESTS, 1):
        print(f"\nTest {i}: {label}")
        try:
            test()
            print("  PASS")
        except Exception as err:
            n_fail += 1
            print(f"  FAIL: {type(err).__name__}: {err}")
    print(f"\n{'='*60}")
    print(f"  {len(TESTS) - n_fail} of {len(TESTS)} tests passed")
    print(f"{'='*60}")
    sys.exit(1 if n_fail else 0)
