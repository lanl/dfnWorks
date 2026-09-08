"""
.. module:: optimize_spacing.py
   :synopsis: Minimal hydraulic-fracture spacing optimizer over a
              heat_extraction() backend
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

Notes
-----
    The optimizer only sees the heat_extraction() interface, so the Phase
    1 surrogate and the Phase 2 DFN backend are interchangeable through
    the heat_extraction argument. Objectives are callables
    objective(t, Q) -> float that are maximized; two are provided and any
    user function with that signature is accepted.
"""

import numpy as np
from scipy.optimize import minimize_scalar, differential_evolution

from pydfnworks.thermal.mpf_gringarten import heat_extraction as _default_backend

OPTIMIZER_METHODS = ("grid", "bounded", "differential_evolution")

# numpy 2 renamed trapz; keep working on both
_trapezoid = getattr(np, "trapezoid", None) or np.trapz


def cumulative_heat(t, Q):
    """ Objective: cumulative heat extracted over the evaluation window

    Parameters
    ----------
        t : numpy array
            times [s], increasing

        Q : numpy array
            heat extraction rate at t [W]

    Returns
    -------
        E : float
            integral of Q over t [J]
    """
    return float(_trapezoid(Q, t))


def time_to_drawdown(t, Q, fraction=0.9):
    """ Objective: time until the heat rate falls to a fraction of its initial value

    Parameters
    ----------
        t : numpy array
            times [s], increasing

        Q : numpy array
            heat extraction rate at t [W]

        fraction : float
            drawdown threshold as a fraction of Q[0]. Default 0.9 (10 %
            thermal decline).

    Returns
    -------
        t_dd : float
            first time at which Q <= fraction * Q[0], linearly
            interpolated between samples [s]. If the threshold is not
            reached inside the window, t[-1] is returned (censored).

    Notes
    -----
        Use functools.partial(time_to_drawdown, fraction=0.8) to change
        the threshold when passing this as an objective.
    """
    threshold = fraction * Q[0]
    below = np.nonzero(Q <= threshold)[0]
    if below.size == 0:
        return float(t[-1])
    i = below[0]
    if i == 0:
        return float(t[0])
    # linear interpolation between the last sample above and first below
    t0, t1 = t[i - 1], t[i]
    Q0, Q1 = Q[i - 1], Q[i]
    if Q0 == Q1:
        return float(t1)
    return float(t0 + (Q0 - threshold) / (Q0 - Q1) * (t1 - t0))


def optimize_spacing(bounds,
                     m_dot,
                     T_res,
                     T_inj,
                     rock_props,
                     fluid_props,
                     n_fractures,
                     fracture_height,
                     t_eval,
                     heat_extraction=_default_backend,
                     objective=cumulative_heat,
                     method="grid",
                     n_grid=25,
                     spacings=None,
                     seed=0,
                     **backend_kwargs):
    """ Find the fracture spacing that maximizes an objective of Q(t)

    Parameters
    ----------
        bounds : tuple of float
            (spacing_min, spacing_max) search range [m]

        m_dot, T_res, T_inj, rock_props, fluid_props, fracture_height, t_eval :
            passed through to heat_extraction(), see
            pydfnworks.thermal.mpf_gringarten.heat_extraction()

        n_fractures : int or callable
            fixed number of fractures, or a function n_fractures(spacing)
            returning the number of fractures for a given spacing (for
            example int(lateral_length // spacing) + 1 for stages placed
            along a fixed lateral).

        heat_extraction : callable
            backend with the pydfnworks.thermal heat_extraction()
            signature. Default: the Phase 1 Gringarten surrogate. This is
            the only place a backend is chosen.

        objective : callable
            objective(t, Q) -> float, maximized. Default cumulative_heat.

        method : str
            "grid" (default; log-spaced grid of n_grid spacings),
            "bounded" (scipy minimize_scalar, bounded Brent), or
            "differential_evolution" (scipy, global). The scipy methods
            evaluate the grid first and refine from it, so the objective
            curve is always available in the result.

        n_grid : int
            number of grid spacings. Default 25.

        spacings : array_like or None
            explicit candidate spacings [m] used instead of the log-spaced
            grid, for example lateral_length / n for integer stage counts
            n. Values outside bounds are dropped. Default None.

        seed : int
            random seed for differential_evolution. Default 0.

        backend_kwargs :
            keyword-only options forwarded to heat_extraction() (for
            example fracture_width for the surrogate, or dfn and G for the
            DFN backend)

    Returns
    -------
        result : dict
            "spacing"     best spacing found [m]
            "objective"   objective value at the best spacing
            "n_fractures" number of fractures at the best spacing
            "Q"           heat extraction rate at the best spacing [W]
            "t_eval"      times of Q [s]
            "spacings"    every spacing evaluated, sorted [m]
            "objectives"  objective at each of those spacings
            "method"      optimizer method used
            "scipy_result" scipy OptimizeResult for the scipy methods, else None

    Notes
    -----
        The objective is treated as noise-free; the Phase 2 particle
        backend will be stochastic, in which case "grid" or
        "differential_evolution" are the appropriate choices.
    """
    if method not in OPTIMIZER_METHODS:
        raise ValueError(
            f"Unknown optimizer method '{method}'. Options: {OPTIMIZER_METHODS}")
    lo, hi = float(bounds[0]), float(bounds[1])
    if not (0 < lo < hi):
        raise ValueError(f"bounds must satisfy 0 < spacing_min < spacing_max, got {bounds}")
    if callable(n_fractures):
        n_of = n_fractures
    else:
        n_of = lambda spacing: n_fractures
    t = np.atleast_1d(np.asarray(t_eval, dtype=float))

    history = {}

    def evaluate(spacing):
        spacing = float(spacing)
        n = int(n_of(spacing))
        Q = heat_extraction(spacing, m_dot, T_res, T_inj, rock_props,
                            fluid_props, n, fracture_height, t,
                            **backend_kwargs)
        value = float(objective(t, Q))
        history[spacing] = (value, n, Q)
        return value

    # objective curve over the search range (also the starting point for
    # the scipy refinements)
    if spacings is None:
        candidates = np.geomspace(lo, hi, int(n_grid))
    else:
        candidates = np.asarray(spacings, dtype=float).ravel()
        candidates = candidates[(candidates >= lo) & (candidates <= hi)]
        if candidates.size == 0:
            raise ValueError("no candidate spacings fall inside bounds")
    for spacing in candidates:
        evaluate(spacing)

    scipy_result = None
    if method == "bounded":
        scipy_result = minimize_scalar(lambda x: -evaluate(x),
                                       bounds=(lo, hi),
                                       method="bounded")
    elif method == "differential_evolution":
        scipy_result = differential_evolution(lambda x: -evaluate(x[0]),
                                              [(lo, hi)],
                                              seed=seed,
                                              polish=False,
                                              tol=1e-6)

    spacings = np.array(sorted(history))
    objectives = np.array([history[s][0] for s in spacings])
    best = spacings[np.argmax(objectives)]
    value, n_best, Q_best = history[best]
    return {
        "spacing": float(best),
        "objective": value,
        "n_fractures": n_best,
        "Q": Q_best,
        "t_eval": t,
        "spacings": spacings,
        "objectives": objectives,
        "method": method,
        "scipy_result": scipy_result,
    }
