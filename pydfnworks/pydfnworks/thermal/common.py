"""
.. module:: common.py
   :synopsis: Argument validation and property helpers shared by the
              pydfnworks.thermal heat-extraction backends
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

Notes
-----
    The thermal backends are pure functions meant to sit inside an
    optimizer inner loop, so invalid arguments raise ValueError instead of
    going through print_log(..., 'error'), which exits the interpreter.
"""

import numpy as np

# required keys of the property dictionaries accepted by heat_extraction()
ROCK_KEYS = ("rho", "c", "k")
FLUID_KEYS = ("rho", "c")

# Representative property sets. Rock: Utah FORGE granitoid (density
# 2750 kg/m^3, specific heat 790 J/kg/K, conductivity 3.05 W/m/K). Fluid:
# liquid water. Both are conveniences for examples and tests; site work
# should pass its own values.
GRANITE_PROPS = {"rho": 2750.0, "c": 790.0, "k": 3.05}
WATER_PROPS = {"rho": 1000.0, "c": 4200.0}

SECONDS_PER_YEAR = 365.25 * 24 * 3600.0


def check_props(props, keys, name):
    """ Check that a property dictionary has the required positive entries

    Parameters
    ----------
        props : dict
            property dictionary, e.g. {"rho": 2750, "c": 790, "k": 3.0}

        keys : tuple of str
            keys that must be present

        name : str
            name used in error messages ("rock_props" or "fluid_props")

    Returns
    -------
        None

    Notes
    -----
        Raises ValueError if a key is missing or its value is not a
        positive finite number.
    """
    if not isinstance(props, dict):
        raise ValueError(f"{name} must be a dict with keys {keys}")
    for key in keys:
        if key not in props:
            raise ValueError(f"{name} is missing required key '{key}'")
        value = props[key]
        if not np.isfinite(value) or value <= 0:
            raise ValueError(
                f"{name}['{key}'] must be a positive finite number, got {value}"
            )


def volumetric_heat_capacity(props):
    """ Volumetric heat capacity rho * c [J/m^3/K] of a property dictionary

    Parameters
    ----------
        props : dict
            property dictionary with keys "rho" [kg/m^3] and "c" [J/kg/K]

    Returns
    -------
        rho_c : float
            volumetric heat capacity [J/m^3/K]
    """
    return props["rho"] * props["c"]


def thermal_diffusivity(rock_props):
    """ Thermal diffusivity alpha = k / (rho c) [m^2/s] of the rock

    Parameters
    ----------
        rock_props : dict
            property dictionary with keys "rho", "c", and "k"

    Returns
    -------
        alpha : float
            thermal diffusivity [m^2/s]
    """
    return rock_props["k"] / volumetric_heat_capacity(rock_props)


def check_heat_extraction_inputs(spacing, m_dot, T_res, T_inj, rock_props,
                                 fluid_props, n_fractures, fracture_height,
                                 t_eval):
    """ Validate the common positional arguments of heat_extraction()

    Parameters
    ----------
        spacing : float
            uniform fracture spacing [m]

        m_dot : float
            total mass flow rate through all fractures [kg/s]

        T_res : float
            initial undisturbed reservoir temperature [deg C]

        T_inj : float
            injection temperature [deg C]; must be below T_res

        rock_props : dict
            {"rho": kg/m^3, "c": J/kg/K, "k": W/m/K}

        fluid_props : dict
            {"rho": kg/m^3, "c": J/kg/K}

        n_fractures : int
            number of fractures sharing the flow

        fracture_height : float
            fracture extent in the flow direction [m]

        t_eval : array_like
            times at which to evaluate the heat extraction rate [s]

    Returns
    -------
        t : numpy array
            t_eval as a 1D float array

    Notes
    -----
        Raises ValueError with a description of the offending argument.
        Both backends call this so that they reject the same inputs.
    """
    for name, value in (("spacing", spacing), ("m_dot", m_dot),
                        ("fracture_height", fracture_height)):
        if not np.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be a positive finite number, got {value}")

    if not np.isfinite(T_res) or not np.isfinite(T_inj):
        raise ValueError("T_res and T_inj must be finite")
    if T_inj >= T_res:
        raise ValueError(
            f"T_inj ({T_inj}) must be lower than T_res ({T_res}) to extract heat")

    check_props(rock_props, ROCK_KEYS, "rock_props")
    check_props(fluid_props, FLUID_KEYS, "fluid_props")

    if int(n_fractures) != n_fractures or n_fractures < 1:
        raise ValueError(
            f"n_fractures must be a positive integer, got {n_fractures}")

    t = np.atleast_1d(np.asarray(t_eval, dtype=float)).ravel()
    if t.size == 0:
        raise ValueError("t_eval must contain at least one time")
    if not np.all(np.isfinite(t)) or np.any(t < 0):
        raise ValueError("t_eval must contain finite, non-negative times [s]")
    return t
