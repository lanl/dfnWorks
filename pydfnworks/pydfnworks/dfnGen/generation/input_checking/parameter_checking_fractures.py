"""
Module for checking DFN fracture family parameters in pydfnworks.

This module provides functions to validate various DFN parameters related to
fracture family definitions, including aspect ratios, number of points,
layer/region assignments, orientation options, and distribution parameters.

.. note::
   These functions will exit the program if any inconsistencies are found.
"""

import pydfnworks.dfnGen.generation.input_checking.helper_functions as hf
from pydfnworks.dfnGen.generation.input_checking.parameter_checking_distributions import *
from pydfnworks.general.logging import local_print_log

from numpy import pi


def check_aspect(params, prefix):
    """Check that each family’s aspect ratio is defined and positive.

    Verifies that the list of aspect ratios matches the number of
    families requested and that all values are greater than zero.

    Parameters
    ----------
    params : dict
        The DFN parameter dictionary.
    prefix : str
        Either 'e' for ellipse or 'r' for rectangle.

    Returns
    -------
    None

    Notes
    -----
    Exits program if inconsistencies are found.
    """
    key = prefix + "aspect"
    shape = "ellipse" if prefix == 'e' else "rectangle"
    num_families = params['nFamEll']['value'] if prefix == 'e' else params['nFamRect']['value']
    hf.check_none(key, params[key]['value'])
    hf.check_length(key, params[key]['value'], num_families)
    hf.check_values(key, params[key]['value'], 0)


def check_enum_points(params):
    """Check that enumPoints for each ellipse family is an integer ≥ 4.

    Ensures the number of defining vertices for each ellipse family
    meets the minimum required (4) and matches the number of families.

    Parameters
    ----------
    params : dict
        The DFN parameter dictionary.

    Returns
    -------
    None

    Notes
    -----
    Exits program if inconsistencies are found.
    """
    key = 'enumPoints'
    hf.check_none(key, params[key]['value'])
    hf.check_length(key, params[key]['value'], params['nFamEll']['value'])
    hf.check_values(key, params[key]['value'], 4)


def check_layers_fracture(params, prefix):
    """Validate layer assignments for each fracture family.

    Checks that the number of layer indices matches the number of families
    and that each index falls within the valid range [0, numOfLayers].

    Parameters
    ----------
    params : dict
        The DFN parameter dictionary.
    prefix : str
        Either 'e' for ellipse or 'r' for rectangle.

    Returns
    -------
    None

    Notes
    -----
    Exits program if inconsistencies are found.
    """
    key = prefix + "Layer"
    shape = "ellipse" if prefix == 'e' else "rectangle"
    num_families = params['nFamEll']['value'] if prefix == 'e' else params['nFamRect']['value']
    hf.check_none(key, params[key]['value'])
    hf.check_length(key, params[key]['value'], num_families)
    hf.check_values(key, params[key]['value'], 0, params["numOfLayers"]['value'])


def check_regions_fracture(params, prefix):
    """Validate region assignments for each fracture family.

    Checks that the number of region indices matches the number of families
    and that each index falls within the valid range [0, numOfRegions].

    Parameters
    ----------
    params : dict
        The DFN parameter dictionary.
    prefix : str
        Either 'e' for ellipse or 'r' for rectangle.

    Returns
    -------
    None

    Notes
    -----
    Exits program if inconsistencies are found.
    """
    key = prefix + "Region"
    shape = "ellipse" if prefix == 'e' else "rectangle"
    num_families = params['nFamEll']['value'] if prefix == 'e' else params['nFamRect']['value']
    hf.check_none(key, params[key]['value'])
    hf.check_length(key, params[key]['value'], num_families)
    hf.check_values(key, params[key]['value'], 0, params["numOfRegions"]['value'])


def check_regions_and_layers_fracture(params, prefix):
    """Ensure each family is defined in only one layer or region.

    Verifies that no family simultaneously specifies both a layer > 0
    and a region > 0.

    Parameters
    ----------
    params : dict
        The DFN parameter dictionary.
    prefix : str
        Either 'e' for ellipse or 'r' for rectangle.

    Returns
    -------
    None

    Notes
    -----
    Exits program if inconsistencies are found.
    """
    shape = "ellipse" if prefix == 'e' else "rectangle"
    num_families = params['nFamEll']['value'] if prefix == 'e' else params['nFamRect']['value']
    for i in range(num_families):
        if params[prefix + 'Region']['value'][i] > 0 and params[prefix + 'Layer']['value'][i] > 0:
            hf.print_error(
                f"The {shape} family #{i+1} is defined in both regions and layers. "
                "Only one can be specified and the other must be set to 0."
            )


def convert_angleOption_value(params):
    """Convert angleOption from 'radian'/'degree' to 0/1 for DFNGen.

    This conversion is required by the DFNGen backend.

    Parameters
    ----------
    params : dict
        The DFN parameter dictionary.

    Returns
    -------
    None

    Notes
    -----
    Exits program if the value is not 'radian' or 'degree'.
    """
    angle_option = params['angleOption']['value']
    if angle_option == 'radian':
        params['angleOption']['value'] = 0
        local_print_log("Converting angleOption value from 'radian' to 0 for DFNGen input")
    elif angle_option == 'degree':
        params['angleOption']['value'] = 1
        local_print_log("Converting angleOption value from 'degree' to 1 for DFNGen input")
    else:
        hf.print_error(
            f"Error. Unknown DFN.params['angleOption']['value'] provided: {angle_option}. "
            "Acceptable values are 'radian', 'degree'. Exiting."
        )


def check_orientations(params, prefix):
    """Validate orientation parameters for each family.

    Ensures that theta/phi (spherical), trend/plunge, or dip/strike
    are provided consistently and within valid ranges, and that
    kappa/kappa2 values are in [0, 100].

    Parameters
    ----------
    params : dict
        The DFN parameter dictionary.
    prefix : str
        Either 'e' for ellipse or 'r' for rectangle.

    Returns
    -------
    None

    Notes
    -----
    Exits program if inconsistencies are found.
    """
    shape = "ellipse" if prefix == 'e' else "rectangle"
    num_families = params['nFamEll']['value'] if prefix == 'e' else params['nFamRect']['value']
    angle_option_key = 'angleOption'

    if params["orientationOption"]["value"] == 0:
        keys = [prefix + name for name in ["theta", "phi"]]
    elif params["orientationOption"]["value"] == 1:
        if params[angle_option_key]['value'] == 0:
            hf.print_error(
                "Using Trend and Plunge but 'angleOption' is set to use radians. "
                "Trend and plunge must use degrees. Set 'angleOption' = 'degree'."
            )
        keys = [prefix + name for name in ["trend", "plunge"]]
    elif params["orientationOption"]["value"] == 2:
        if params[angle_option_key]['value'] == 0:
            hf.print_error(
                "Using Dip and Strike but 'angleOption' is set to use radians. "
                "Dip and strike must use degrees. Set 'angleOption' = 'degree'."
            )
        keys = [prefix + name for name in ["dip", "strike"]]
    else:
        hf.print_error("Unknown orientation option. Value must be 0, 1, or 2.")

    for key in keys:
        hf.check_none(key, params[key]['value'])
        hf.check_length(key, params[key]['value'], num_families)
        for i, val in enumerate(params[key]['value']):
            if params[angle_option_key]['value'] == 0:
                if val < 0 or val > 2 * pi:
                    hf.print_error(
                        f"\"{key}\" entry {i+1} has value {val} outside [0, 2π). "
                        "If you want to use degrees, set 'angleOption' = 1."
                    )
            else:
                if val < 0 or val > 360:
                    hf.print_error(
                        f"\"{key}\" entry {i+1} has value {val} outside [0, 360)."
                    )

    # Check kappa
    key = prefix + 'kappa'
    hf.check_none(key, params[key]['value'])
    hf.check_length(key, params[key]['value'], num_families)
    hf.check_values(key, params[key]['value'], 0, 100)

    k2_key = prefix + 'kappa2'
    if k2_key in params and params[k2_key]['value'] is not None:
        hf.check_none(k2_key, params[k2_key]['value'])
        hf.check_length(k2_key, params[k2_key]['value'], num_families)
        hf.check_values(k2_key, params[k2_key]['value'], 0, 100)


def check_beta_distribution(params, prefix):
    """Validate beta distribution flags and values.

    If any families specify a constant beta (value 1), ensures
    that corresponding beta angles are defined and within range.

    Parameters
    ----------
    params : dict
        The DFN parameter dictionary.
    prefix : str
        Either 'e' for ellipse or 'r' for rectangle.

    Returns
    -------
    None

    Notes
    -----
    Exits program if inconsistencies are found.
    """
    num_families = params['nFamEll']['value'] if prefix == 'e' else params['nFamRect']['value']

    # Check distribution flag
    key = prefix + 'betaDistribution'
    hf.check_none(key, params[key]['value'])
    hf.check_length(key, params[key]['value'], num_families)

    # If any constant flags, validate beta values
    num_beta = params[key]['value'].count(1)
    if num_beta > 0:
        beta_key = prefix + "beta"
        hf.check_none(beta_key, params[beta_key]['value'])
        hf.check_length(beta_key, params[beta_key]['value'], num_beta)
        for i, val in enumerate(params[beta_key]['value']):
            if params['angleOption']['value'] == 0:
                if val < 0 or val > 2 * pi:
                    hf.print_error(
                        f"\"{beta_key}\" entry {i+1} has value {val} outside [0, 2π)."
                    )
            else:
                if val < 0 or val > 360:
                    hf.print_error(
                        f"\"{beta_key}\" entry {i+1} has value {val} outside [0, 360)."
                    )


def cross_check(params):
    """Ensure consistency of angleOption across ellipse and rectangle families.

    Verifies that both 'eAngleOption' and 'rAngleOption' match.

    Parameters
    ----------
    params : dict
        The DFN parameter dictionary.

    Returns
    -------
    None

    Notes
    -----
    Exits program if inconsistencies are found.
    """
    for key in ['AngleOption']:
        if params['e' + key]['value'] != params['r' + key]['value']:
            hf.print_error(
                "Inconsistent values of \"{key}\" found in ellipses and rectangles. "
                "Values must be the same."
            )


def check_fracture_params(params, shape):
    """Run all checks for a given fracture family shape.

    Executes the full suite of validation functions for either
    ellipse or rectangle families.

    Parameters
    ----------
    params : dict
        The DFN parameter dictionary.
    shape : str
        Either 'ellipse' or 'rectangle'.

    Returns
    -------
    None

    Notes
    -----
    Exits program if inconsistencies are found.
    """
    if shape == "ellipse":
        prefix = "e"
        local_print_log("--> Checking Ellipse Family parameters")
        check_enum_points(params)
    elif shape == "rectangle":
        prefix = "r"
        local_print_log("--> Checking Rectangle Family parameters")

    check_aspect(params, prefix)
    check_layers_fracture(params, prefix)
    check_regions_fracture(params, prefix)
    check_regions_and_layers_fracture(params, prefix)
    check_orientations(params, prefix)
    check_beta_distribution(params, prefix)
    check_distributions(params, prefix)