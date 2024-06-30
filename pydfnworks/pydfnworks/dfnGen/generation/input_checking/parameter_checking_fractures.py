import pydfnworks.dfnGen.generation.input_checking.helper_functions as hf
from pydfnworks.dfnGen.generation.input_checking.parameter_checking_distributions import *
from pydfnworks.general.logging import local_print_log

from numpy import pi


def check_aspect(params, prefix):
    """ Check the aspect of the rectangle or ellipse families matches the number of families requested and is a positive value


    Parameters
    -------------
        params : dict
            parameter dictionary
        prefix : string
        	either 'e' or 'r' for ellipse or rectangle

    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    key = prefix + "aspect"
    shape = "ellipse" if prefix == 'e' else "rectangle"
    num_families = params['nFamEll']['value'] if prefix == 'e' else params[
        'nFamRect']['value']
    hf.check_none(key, params[key]['value'])
    hf.check_length(key, params[key]['value'], num_families)
    hf.check_values(key, params[key]['value'], 0)


def check_enum_points(params):
    """ Check that the value of enumPoints for each ellipse family is an integer greater than 4

    Parameters
    -------------
        params : dict
            parameter dictionary

    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """
    key = 'enumPoints'
    hf.check_none(key, params[key]['value'])
    hf.check_length(key, params[key]['value'], params['nFamEll']['value'])
    hf.check_values(key, params[key]['value'], 4)


def check_layers_fracture(params, prefix):
    """ Checks that the number of layers is each family is correct. Checks that the layers index is a known index. 

    Parameters
    -------------
        params : dict
            parameter dictionary
        prefix : string
            either 'e' or 'r' for ellipse or rectangle

    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    key = prefix + "Layer"
    shape = "ellipse" if prefix == 'e' else "rectangle"
    num_families = params['nFamEll']['value'] if prefix == 'e' else params[
        'nFamRect']['value']
    hf.check_none(key, params[key]['value'])
    hf.check_length(key, params[key]['value'], num_families)
    hf.check_values(key, params[key]['value'], 0,
                    params["numOfLayers"]['value'])


def check_regions_fracture(params, prefix):
    """ Checks that the number of regions is each family is correct. Checks that the region index is a known index. 

    Parameters
    -------------
        params : dict
            parameter dictionary
        prefix : string
            either 'e' or 'r' for ellipse or rectangle

    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    key = prefix + "Region"
    shape = "ellipse" if prefix == 'e' else "rectangle"
    num_families = params['nFamEll']['value'] if prefix == 'e' else params[
        'nFamRect']['value']
    hf.check_none(key, params[key]['value'])
    hf.check_length(key, params[key]['value'], num_families)
    hf.check_values(key, params[key]['value'], 0,
                    params["numOfRegions"]['value'])


def check_regions_and_layers_fracture(params, prefix):
    """ Checks that families are only defined in either a region or a layer or the whole domain.

    Parameters
    -------------
        params : dict
            parameter dictionary
        prefix : string
            either 'e' or 'r' for ellipse or rectangle

    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """
    shape = "ellipse" if prefix == 'e' else "rectangle"
    num_families = params['nFamEll']['value'] if prefix == 'e' else params[
        'nFamRect']['value']
    for i in range(num_families):
        if params[prefix + 'Region']['value'][i] > 0 and params[
                prefix + 'Layer']['value'][i] > 0:
            hf.print_error(
                f"The {shape} family #{i+1} is defined in both regions and layers. Only one can be specified and the other must be set to 0."
            )


def convert_angleOption_value(params):
    """ Changes angleOption value from 'radians' to 0 or 'degrees' to 1
    This change is required for dfnGen

    Parameters
    ------------
        params : dict
            parameter dictionary

    Returns
    ---------
        None

    Notes
    -------
    """
    angle_option = params['angleOption']['value']
    if angle_option == 'radian':
        params['angleOption']['value'] = 0
        local_print_log("Converting angleOption value from radian to 0 for dfnGen input")
    elif angle_option == 'degree':
        params['angleOption']['value'] = 1
        local_print_log("Converting angleOption value from degree to 1 for dfnGen input")
    else:
        hf.print_error(
            f"Error. Unknown DFN.params['angleOption']['value']. provided: {angle_option}. Acceptable values are 'radian', 'degree'.\nExiting."
        )


def check_orientations(params, prefix):
    """ Checks orientation options. If using trend/plunge, degrees must be used. If using spherical, radians are okay as well. Checks that values are within acceptable ranges. 

    Parameters
    -------------
        params : dict
            parameter dictionary
        prefix : string
            either 'e' or 'r' for ellipse or rectangle

    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """
    shape = "ellipse" if prefix == 'e' else "rectangle"
    num_families = params['nFamEll']['value'] if prefix == 'e' else params[
        'nFamRect']['value']
    angle_option_key = 'angleOption'

    if params["orientationOption"]["value"] == 0:
        #print("--> Using Spherical Coordinates")
        keys = [prefix + name for name in ["theta", "phi"]]

    elif params["orientationOption"]["value"] == 1:
        #print("--> Using Trend and Plunge")
        # 0 is radians, 1 is degrees
        if params[angle_option_key]['value'] == 'radian':
            hf.print_error(
                f"Using Trend and Plunge but {'angleOption'} is set to use radians. Trend and plunge must use degree. Set {'angleOption'} = 'degree'. "
            )
        keys = [prefix + name for name in ["trend", "plunge"]]

    elif params["orientationOption"]["value"] == 2:
        # using dip / strike
        if params[angle_option_key]['value'] == 'radian':
            hf.print_error(
                f"Using Dip and Strike but {'angleOption'} is set to use radian. Trend and plunge must use degree. Set {'angleOption'} = 'degree'. "
            )
        keys = [prefix + name for name in ["dip", "strike"]]
    else:
        hf.print_error(f"Unknown orientation option. Value must be 0,1, or 2.")

    for key in keys:
        hf.check_none(key, params[key]['value'])
        hf.check_length(key, params[key]['value'], num_families)
        for i, val in enumerate(params[key]['value']):
            # check radians
            if params[angle_option_key]['value'] == 0:
                if val < 0 or val > 2 * pi:
                    hf.print_error(
                        f"\"{key}\" entry {i+1} has value {val} which is outside of acceptable parameter range [0,2*pi). If you want to use degrees, please use {angle_option_key} = 1. "
                    )
            # check degrees
            else:
                if val < 0 or val > 360:
                    hf.print_error(
                        f"\"{key}\" entry {i+1} has value {val} which is outside of acceptable parameter range [0,360). "
                    )
    #check kappa
    key = prefix + 'kappa'
    hf.check_none(key, params[key]['value'])
    hf.check_length(key, params[key]['value'], num_families)
    hf.check_values(key, params[key]['value'], 0, 100)


def check_beta_distribution(params, prefix):
    """
    Verifies both the "ebetaDistribution" and "rBetaDistribution". If either contain any flags    indicating constant angle (1) then the corresponding "ebeta" and/or "rbeta" parameters are 
    also verified. 
    
    Parameters
    -------------
        params : dict
            parameter dictionary
        prefix : string
            either 'e' or 'r' for ellipse or rectangle

    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    shape = "ellipse" if prefix == 'e' else "rectangle"
    num_families = params['nFamEll']['value'] if prefix == 'e' else params[
        'nFamRect']['value']
    angle_option_key = 'angleOption'

    #check kappa
    key = prefix + 'betaDistribution'
    hf.check_none(key, params[key]['value'])
    hf.check_length(key, params[key]['value'], num_families)

    # check actual values of beta
    num_beta = params[key]['value'].count(1)
    if num_beta > 0:
        beta_key = prefix + "beta"
        hf.check_none(beta_key, params[beta_key]['value'])
        hf.check_length(beta_key, params[beta_key]['value'], num_beta)

        for i, val in enumerate(params[beta_key]['value']):
            if params[angle_option_key]['value'] == 0:
                if val < 0 or val > 2 * pi:
                    hf.print_error(
                        f"\"{key}\" entry {i+1} has value {val} which is outside of acceptable parameter range [0,2*pi). If you want to use degrees, please use {angle_option_key} = 1. "
                    )
            # check degrees
            else:
                if val < 0 or val > 360:
                    hf.print_error(
                        f"\"{key}\" entry {i+1} has value {val} which is outside of acceptable parameter range [0,360). "
                    )


def cross_check(params):
    """ Cross check parameters to make sure they are consistent across DFN. Checks that all angle parameters are degree/radians.


    Parameters
    -------------
        params : dict
            parameter dictionary

    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    keys = ['AngleOption']
    for key in keys:
        if params['e' + key]['value'] != params['r' + key]['value']:
            hf.print_error(
                f"Inconsistent values of \"{key}\" found in ellipses and rectangles. Values must be the same."
            )


def check_fracture_params(params, shape):
    """ Checks parameters of each fracture family and shape type. Used for both rectangles and ellipses.

    Parameters
    -------------
        params : dict
            parameter dictionary
        shape : string
            ellipse or rectangle

    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    if shape == "ellipse":
        prefix = "e"
        local_print_log(f"--> Checking Ellipse Family parameters")
        check_enum_points(params)

    elif shape == "rectangle":
        prefix = "r"
        local_print_log(f"--> Checking Rectangle Family parameters")

    check_aspect(params, prefix)
    check_layers_fracture(params, prefix)
    check_regions_fracture(params, prefix)
    check_regions_and_layers_fracture(params, prefix)
    check_orientations(params, prefix)
    check_beta_distribution(params, prefix)
    check_distributions(params, prefix)
