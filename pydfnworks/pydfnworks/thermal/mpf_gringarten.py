"""
.. module:: mpf_gringarten.py
   :synopsis: Phase 1 analytic heat-extraction surrogate: the Gringarten,
              Witherspoon and Ohnishi (1975) multiple parallel fractures
              (MPF) model, inverted numerically from the Laplace domain
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

Notes
-----
    Model. n identical planar fractures of height H (the flow direction)
    and width w are uniformly spaced a distance D apart in an infinite rock
    mass. Water enters every fracture at T_inj at the same rate and rock
    heat reaches the fracture only by conduction normal to the fracture
    plane, so each fracture draws on a slab of half-thickness D/2. The
    Laplace transform of the dimensionless outlet drawdown

        T_wD = (T_res - T_out) / (T_res - T_inj)

    is (Gringarten et al. 1975, Eq. A17)

        T_wD*(s) = (1/s) exp[ -sqrt(s) tanh( beta sqrt(s) ) ]

    with dimensionless time t_D = t / t_scale and

        Q_f     = m_dot / (rho_f n)                            [m^3/s per fracture]
        t_scale = 4 k rho_r c_r (w H)^2 / ((rho_f c_f)^2 Q_f^2)   [s]
        beta    = rho_f c_f Q_f D / (4 k w H)                  [-]

    beta * t_scale is the piston-displacement time of one slab: the time
    for the injected water to carry away all the heat stored in a rock
    volume D*w*H. Two limits anchor the model. beta -> infinity (wide
    spacing) recovers the single-fracture semi-infinite solution
    T_wD = erfc(1 / (2 sqrt(t_D))) (Lauwerier 1955; Bodvarsson and Tsang
    1982), and beta -> 0 (close spacing) tends to a step at t_D = beta.

    The Laplace-domain expression and the grouping of the physical
    parameters follow the open-source GEOPHIRES-X implementation (Beckers
    and McCabe 2019; NREL/GEOPHIRES-X, src/geophires_x/MPFReservoir.py,
    MIT licence). GEOPHIRES-X inverts with mpmath's Stehfest routine at 15
    significant digits; that route is retained here as method="mpmath" for
    cross-checks and is isolated in _invert_mpmath(). The default
    inversion is the double-precision Gaver-Stehfest algorithm already
    used by the finite matrix-diffusion TDRW models
    (pydfnworks.dfnGraph.transport.tdrw.stehfest), which evaluates a
    200-point curve in well under a millisecond. Against a 40-digit
    de Hoog reference the default 18 coefficients give a maximum error in
    T_wD of about 3e-5 for beta >= 1, 5e-4 at beta = 0.3 and 6e-3 at
    beta = 0.1 (uniformly at least as good as 16; 20 or more terms lose
    accuracy at large beta in double precision). Below beta ~ 0.05 the
    response is close to a step at t_D = beta and Stehfest ringing of a
    few percent is visible around it; the integrated heat is still
    correct to better than 1e-3. Everything vendored from GEOPHIRES-X sits
    behind heat_extraction(), so the inversion can be replaced without
    touching callers.

    References
        Gringarten, A. C., Witherspoon, P. A., Ohnishi, Y. (1975). Theory
        of heat extraction from fractured hot dry rock. J. Geophys. Res.
        80(8), 1120-1124.

        Beckers, K. F., McCabe, K. (2019). GEOPHIRES v2.0: updated
        geothermal techno-economic simulation tool. Geothermal Energy 7, 5.

        Bodvarsson, G. S., Tsang, C. F. (1982). Injection and thermal
        breakthrough in fractured geothermal reservoirs. J. Geophys. Res.
        87(B2), 1031-1048.
"""

import numpy as np
from scipy.special import erfc

from pydfnworks.dfnGraph.transport.tdrw.stehfest import stehfest_coefficients
from pydfnworks.thermal.common import (check_heat_extraction_inputs,
                                       volumetric_heat_capacity)

DEFAULT_STEHFEST_N = 18
DEFAULT_MPMATH_DPS = 15  # GEOPHIRES-X default 'Gringarten-Stehfest Precision'
INVERSION_METHODS = ("stehfest", "mpmath")


def laplace_drawdown(s, beta):
    """ Laplace transform of the MPF dimensionless outlet drawdown

    T_wD*(s) = (1/s) exp(-sqrt(s) tanh(beta sqrt(s)))

    Parameters
    ----------
        s : float or numpy array
            Laplace variable conjugate to dimensionless time t_D

        beta : float
            dimensionless spacing parameter, see dimensionless_parameters()

    Returns
    -------
        F : float or numpy array
            transform evaluated at s

    Notes
    -----
        Gringarten et al. (1975), Eq. A17. exp(-sqrt(s)) underflows to
        zero for large s, which is the correct early-time behaviour, so no
        special scaling is needed.
    """
    q = np.sqrt(s)
    return np.exp(-q * np.tanh(beta * q)) / s


def single_fracture_drawdown(t_D):
    """ Semi-infinite single-fracture limit of the MPF drawdown

    T_wD = erfc(1 / (2 sqrt(t_D)))

    Parameters
    ----------
        t_D : float or numpy array
            dimensionless time, see dimensionless_parameters()

    Returns
    -------
        T_wD : numpy array
            dimensionless outlet drawdown in [0, 1]; zero at t_D = 0

    Notes
    -----
        This is the beta -> infinity limit of laplace_drawdown() (Lauwerier
        1955; Bodvarsson and Tsang 1982 with negligible fracture storage),
        the wide-spacing asymptote used to verify the numerical inversion.
    """
    t_D = np.atleast_1d(np.asarray(t_D, dtype=float))
    out = np.zeros_like(t_D)
    pos = t_D > 0
    out[pos] = erfc(1.0 / (2.0 * np.sqrt(t_D[pos])))
    return out


def dimensionless_parameters(spacing,
                             m_dot,
                             rock_props,
                             fluid_props,
                             n_fractures,
                             fracture_height,
                             fracture_width=None):
    """ Dimensionless groups of the MPF model for a physical parameter set

    Parameters
    ----------
        spacing : float
            uniform fracture spacing D [m]

        m_dot : float
            total mass flow rate [kg/s], shared equally by the fractures

        rock_props : dict
            {"rho": kg/m^3, "c": J/kg/K, "k": W/m/K}

        fluid_props : dict
            {"rho": kg/m^3, "c": J/kg/K}

        n_fractures : int
            number of fractures

        fracture_height : float
            fracture extent in the flow direction H [m]

        fracture_width : float or None
            fracture extent perpendicular to the flow w [m]. Default None
            uses fracture_height (square fracture).

    Returns
    -------
        params : dict
            "beta"        dimensionless spacing parameter [-]
            "t_scale"     time scale so that t_D = t / t_scale [s]
            "t_piston"    beta * t_scale, the slab piston-displacement time [s]
            "Q_f"         volumetric flow rate per fracture [m^3/s]
            "q_w"         flow rate per unit fracture width [m^2/s]
            "heat_in_place" rock heat per unit temperature difference in the
                          n slabs, rho_r c_r n D w H [J/K]

    Notes
    -----
        Follows the parameter grouping of GEOPHIRES-X MPFReservoir.
    """
    if fracture_width is None:
        fracture_width = fracture_height
    rho_c_f = volumetric_heat_capacity(fluid_props)
    rho_c_r = volumetric_heat_capacity(rock_props)
    k = rock_props["k"]
    H = fracture_height
    w = fracture_width

    Q_f = m_dot / (fluid_props["rho"] * n_fractures)
    q_w = Q_f / w
    t_scale = 4.0 * k * rho_c_r * (w * H)**2 / (rho_c_f * Q_f)**2
    beta = rho_c_f * q_w * spacing / (4.0 * k * H)
    return {
        "beta": beta,
        "t_scale": t_scale,
        "t_piston": beta * t_scale,
        "Q_f": Q_f,
        "q_w": q_w,
        "heat_in_place": rho_c_r * n_fractures * spacing * w * H,
    }


def _invert_stehfest(beta, t_D, n=DEFAULT_STEHFEST_N):
    """ Gaver-Stehfest inversion of laplace_drawdown() in double precision

    f(t) ~ (ln 2 / t) sum_i V_i F(i ln 2 / t)

    Parameters
    ----------
        beta : float
            dimensionless spacing parameter

        t_D : numpy array
            strictly positive dimensionless times

        n : int
            number of Stehfest coefficients (even). Default 18.

    Returns
    -------
        T_wD : numpy array
            drawdown at t_D, not yet clipped to [0, 1]
    """
    V = stehfest_coefficients(n)
    ln2 = np.log(2.0)
    i = np.arange(1, n + 1)
    s = np.outer(ln2 / t_D, i)
    return (ln2 / t_D) * (laplace_drawdown(s, beta) @ V)


def _invert_mpmath(beta, t_D, dps=DEFAULT_MPMATH_DPS):
    """ Arbitrary-precision Stehfest inversion, as in GEOPHIRES-X

    Parameters
    ----------
        beta : float
            dimensionless spacing parameter

        t_D : numpy array
            strictly positive dimensionless times

        dps : int
            mpmath working precision in decimal digits. Default 15, the
            GEOPHIRES-X default (allowed there: 8 to 15).

    Returns
    -------
        T_wD : numpy array
            drawdown at t_D

    Notes
    -----
        Adapted from NREL/GEOPHIRES-X src/geophires_x/MPFReservoir.py
        (MIT licence): fp(s) = (1/s) exp(-sqrt(s) tanh(beta sqrt(s))),
        inverted with mpmath.invertlaplace(fp, t, method='stehfest') inside
        a workdps(precision) context. About three orders of magnitude
        slower than _invert_stehfest(); intended for verification.
    """
    from mpmath import exp, invertlaplace, sqrt, tanh, workdps

    def fp(s):
        return (1.0 / s) * exp(-sqrt(s) * tanh(beta * sqrt(s)))

    with workdps(dps):
        return np.array(
            [float(invertlaplace(fp, t, method='stehfest')) for t in t_D])


def dimensionless_drawdown(t_D,
                           beta,
                           method="stehfest",
                           stehfest_n=DEFAULT_STEHFEST_N):
    """ Dimensionless outlet drawdown T_wD(t_D; beta) of the MPF model

    Parameters
    ----------
        t_D : array_like
            dimensionless times >= 0

        beta : float
            dimensionless spacing parameter

        method : str
            Laplace inversion: "stehfest" (default, double precision numpy)
            or "mpmath" (GEOPHIRES-X route, slow)

        stehfest_n : int
            number of Stehfest coefficients for method "stehfest". Default
            18; 20 or more lose accuracy in double precision.

    Returns
    -------
        T_wD : numpy array
            drawdown clipped to [0, 1], zero at t_D = 0
    """
    if method not in INVERSION_METHODS:
        raise ValueError(
            f"Unknown inversion method '{method}'. Options: {INVERSION_METHODS}")
    t_D = np.atleast_1d(np.asarray(t_D, dtype=float))
    T_wD = np.zeros_like(t_D)
    pos = t_D > 0
    if np.any(pos):
        if method == "stehfest":
            T_wD[pos] = _invert_stehfest(beta, t_D[pos], stehfest_n)
        else:
            T_wD[pos] = _invert_mpmath(beta, t_D[pos])
    return np.clip(T_wD, 0.0, 1.0)


def production_temperature(spacing,
                           m_dot,
                           T_res,
                           T_inj,
                           rock_props,
                           fluid_props,
                           n_fractures,
                           fracture_height,
                           t_eval,
                           *,
                           fracture_width=None,
                           method="stehfest",
                           stehfest_n=DEFAULT_STEHFEST_N):
    """ Produced water temperature T_out(t) of the MPF model

    Parameters
    ----------
        Same as heat_extraction()

    Returns
    -------
        T_out : numpy array
            outlet temperature at each time in t_eval [deg C]
    """
    t = check_heat_extraction_inputs(spacing, m_dot, T_res, T_inj, rock_props,
                                     fluid_props, n_fractures,
                                     fracture_height, t_eval)
    params = dimensionless_parameters(spacing, m_dot, rock_props, fluid_props,
                                      n_fractures, fracture_height,
                                      fracture_width)
    T_wD = dimensionless_drawdown(t / params["t_scale"], params["beta"],
                                  method, stehfest_n)
    return T_res - T_wD * (T_res - T_inj)


def heat_extraction(spacing,
                    m_dot,
                    T_res,
                    T_inj,
                    rock_props,
                    fluid_props,
                    n_fractures,
                    fracture_height,
                    t_eval,
                    *,
                    fracture_width=None,
                    method="stehfest",
                    stehfest_n=DEFAULT_STEHFEST_N):
    """ Heat extraction rate Q(t) from the Gringarten MPF surrogate

    Parameters
    ----------
        spacing : float
            uniform fracture spacing [m]

        m_dot : float
            total mass flow rate [kg/s]

        T_res : float
            initial undisturbed reservoir temperature [deg C]

        T_inj : float
            injection temperature [deg C]

        rock_props : dict
            {"rho": kg/m^3, "c": J/kg/K, "k": W/m/K}

        fluid_props : dict
            {"rho": kg/m^3, "c": J/kg/K}

        n_fractures : int
            number of fractures sharing the flow

        fracture_height : float
            fracture extent in the flow direction [m]

        t_eval : array_like
            times at which to evaluate Q(t) [s]

        fracture_width : float or None
            keyword-only. Fracture extent perpendicular to flow [m]. Default
            None uses fracture_height (square fracture).

        method : str
            keyword-only. Laplace inversion, "stehfest" (default) or
            "mpmath" (GEOPHIRES-X route, for cross-checks)

        stehfest_n : int
            keyword-only. Number of Stehfest coefficients. Default 18.

    Returns
    -------
        Q : numpy array
            heat extraction rate m_dot c_f (T_out - T_inj) at each time in
            t_eval [W]

    Notes
    -----
        This is the Phase 1 backend of the pydfnworks.thermal interface.
        The nine positional arguments are the stable interface shared with
        pydfnworks.thermal.dfn_heat.heat_extraction(); backend-specific
        options are keyword-only. Runtime is tens of microseconds for a
        few hundred times, so it can sit inside an optimizer loop.
    """
    T_out = production_temperature(spacing,
                                   m_dot,
                                   T_res,
                                   T_inj,
                                   rock_props,
                                   fluid_props,
                                   n_fractures,
                                   fracture_height,
                                   t_eval,
                                   fracture_width=fracture_width,
                                   method=method,
                                   stehfest_n=stehfest_n)
    return m_dot * fluid_props["c"] * (T_out - T_inj)
