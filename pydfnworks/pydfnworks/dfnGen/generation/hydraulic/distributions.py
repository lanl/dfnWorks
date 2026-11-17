"""
Distribution functions for generating hydraulic property values.
"""
import numpy as np

from pydfnworks.general.logging import local_print_log
from .conversions import get_units, convert


def log_normal(params, variable, number_of_fractures):
    """ Creates Fracture Based Log-Normal values that is number_of_fractures long.
    The values has a mean mu and log-variance sigma. 
    
    Parameters
    -----------
        params : dict 
            Dictionary of parameters for the Log Normal values. Must contain keys mu and sigma. 
        
        variable : string 
            name of values being generated. Acceptable values are aperture, permeability, and transmissivity
        
        number_of_fractures : int
            number of fractures in the DFN 

    Returns
    ----------
        b : array
            aperture values
        
        perm : array
            permeability values
        
        T : array
            transmissivity values

    Notes
    ----------
        Values are generated for the variable provided. The two remaining variables are derived using those values.
    """
    local_print_log(f'--> Creating uncorrelated lognormal {variable} values.')
    units = get_units(variable)
    local_print_log(f"--> Mean: {params['mu']} {units}")
    local_print_log(f"--> Log Variance: {params['sigma']}")

    match variable:
        case "aperture":
            b = np.log(params["mu"]) * np.ones(number_of_fractures)
            perturbation = np.random.normal(0.0, 1.0, number_of_fractures)
            b = np.exp(b + np.sqrt(params["sigma"]) * perturbation)
            perm = convert(b, variable, "permeability")
            T = convert(b, variable, "transmissivity")

        case "permeability":
            perm = np.log(params["mu"]) * np.ones(number_of_fractures)
            perturbation = np.random.normal(0.0, 1.0, number_of_fractures)
            perm = np.exp(perm + np.sqrt(params["sigma"]) * perturbation)
            b = convert(perm, variable, "aperture")
            T = convert(perm, variable, "transmissivity")

        case "transmissivity":
            T = np.log(params["mu"]) * np.ones(number_of_fractures)
            perturbation = np.random.normal(0.0, 1.0, number_of_fractures)
            T = np.exp(T + np.sqrt(params["sigma"]) * perturbation)
            b = convert(T, variable, "aperture")
            perm = convert(T, variable, "permeability")

        case _:
            error = f"Error. The variable of choice '{variable}' is not known\nAcceptable names are aperture, permeability, and transmissivity\nExiting.\n"
            local_print_log(error, 'error')

    local_print_log('--> Complete\n')
    return b, perm, T


def exponential(params, variable, number_of_fractures):
    """ Creates Fracture Based Exponential values that is number_of_fractures long.
    Values are drawn from an exponential distribution with rate parameter lam.
    
    Parameters
    -----------
        params : dict 
            Dictionary of parameters for the Exponential distribution. Must contain key lam (the rate parameter). 
            The mean of the distribution is 1/lam.
        
        variable : string 
            name of values being generated. Acceptable values are aperture, permeability, and transmissivity
        
        number_of_fractures : int
            number of fractures in the DFN 

    Returns
    ----------
        b : array
            aperture values
        
        perm : array
            permeability values
        
        T : array
            transmissivity values

    Notes
    ----------
        Values are generated for the variable provided. The two remaining variables are derived using those values.
        The exponential distribution has PDF: f(x) = lam * exp(-lam * x) for x >= 0
    """
    local_print_log(f'--> Creating uncorrelated exponential {variable} values.')
    units = get_units(variable)
    local_print_log(f"--> Lambda (rate): {params['lam']} 1/{units}")

    match variable:
        case "aperture":
            b = np.random.exponential(scale=1.0/params["lam"], size=number_of_fractures)
            perm = convert(b, variable, "permeability")
            T = convert(b, variable, "transmissivity")

        case "permeability":
            perm = np.random.exponential(scale=1.0/params["lam"], size=number_of_fractures)
            b = convert(perm, variable, "aperture")
            T = convert(perm, variable, "transmissivity")

        case "transmissivity":
            T = np.random.exponential(scale=1.0/params["lam"], size=number_of_fractures)
            b = convert(T, variable, "aperture")
            perm = convert(T, variable, "permeability")

        case _:
            error = f"Error. The variable of choice '{variable}' is not known\nAcceptable names are aperture, permeability, and transmissivity\nExiting.\n"
            local_print_log(error, 'error')

    local_print_log('--> Complete\n')
    return b, perm, T


def correlated(params, variable, radii):
    """ Creates hydraulic properties of fractures based on power-law relationship with 
    fracture radius. For example, T = alpha*r^beta
    
    Parameters
    -----------
        params : dict 
            Dictionary of parameters for the power-law relationship. Must contain alpha and beta. 
        
        variable : string 
            name of values being generated. Acceptable values are aperture, permeability, and transmissivity
        
        radii : array
            array of fracture radii in the domain

    Returns
    ----------
        b : array
            aperture values
        
        perm : array
            permeability values
        
        T : array
            transmissivity values

    Notes
    ----------
        Values are generated for the variable provided. The two remaining variables are derived using those values.
    """
    local_print_log(
        f'--> Creating Perfectly Correlated {variable} values based on fracture radius.'
    )
    units = get_units(variable)

    match variable:
        case "aperture":
            local_print_log(f"b = {params['alpha']:0.2e} * r^{params['beta']} {units}")
            b = params["alpha"] * radii**params["beta"]
            perm = convert(b, variable, "permeability")
            T = convert(b, variable, "transmissivity")

        case "permeability":
            local_print_log(f"k = {params['alpha']:0.2e} * r^{params['beta']} {units}")
            perm = params["alpha"] * radii**params["beta"]
            b = convert(perm, variable, "aperture")
            T = convert(perm, variable, "transmissivity")

        case "transmissivity":
            local_print_log(f"T = {params['alpha']:0.2e} * r^{params['beta']} {units}")
            T = params["alpha"] * radii**params["beta"]
            b = convert(T, variable, "aperture")
            perm = convert(T, variable, "permeability")

    local_print_log("--> Complete\n")
    return b, perm, T


def semi_correlated(params, variable, radii, number_of_fractures):
    """ Creates hydraulic properties of fractures based on power-law relationship with 
    fracture radius with a noise term. For example, log(T) = log(alpha*r^beta) + sigma * N(0,1)
    
    Parameters
    -----------
        params : dict 
            Dictionary of parameters for the power-law relationship. Must contain alpha, beta, and sigma. 
        
        variable : string 
            name of values being generated. Acceptable values are aperture, permeability, and transmissivity
        
        radii : array
            array of fracture radii in the domain
        
        number_of_fractures : int
            number of fractures in the DFN 

    Returns
    ----------
        b : array
            aperture values
        
        perm : array
            permeability values
        
        T : array
            transmissivity values

    Notes
    ----------
        Values are generated for the variable provided. The two remaining variables are derived using those values.
    """
    local_print_log(f"--> Creating Semi-Correlated {variable} values based on fracture radius.")
    local_print_log(f'--> Coefficient: {params["alpha"]}')
    local_print_log(f'--> Exponent : {params["beta"]}')
    local_print_log(f'--> Log Variance: {params["sigma"]}')

    match variable:
        case "aperture":
            b = params["alpha"] * radii**params["beta"]
            perturbation = np.random.normal(0.0, 1.0, number_of_fractures)
            b = np.exp(np.log(b) + np.sqrt(params["sigma"]) * perturbation)
            perm = convert(b, variable, "permeability")
            T = convert(b, variable, "transmissivity")

        case "permeability":
            perm = params["alpha"] * radii**params["beta"]
            perturbation = np.random.normal(0.0, 1.0, number_of_fractures)
            perm = np.exp(np.log(perm) + np.sqrt(params["sigma"]) * perturbation)
            b = convert(perm, variable, "aperture")
            T = convert(perm, variable, "transmissivity")

        case "transmissivity":
            T = params["alpha"] * radii**params["beta"]
            perturbation = np.random.normal(0.0, 1.0, number_of_fractures)
            T = np.exp(np.log(T) + np.sqrt(params["sigma"]) * perturbation)
            b = convert(T, variable, "aperture")
            perm = convert(T, variable, "permeability")

    local_print_log('--> Complete\n')
    return b, perm, T


def constant(params, variable, number_of_fractures):
    """ Creates hydraulic properties of fractures with constant values
    
    Parameters
    -----------
        params : dict 
            Dictionary of parameters. Must contain mu (the constant value). 
        
        variable : string 
            name of values being generated. Acceptable values are aperture, permeability, and transmissivity
        
        number_of_fractures : int
            number of fractures in the DFN 

    Returns
    ----------
        b : array
            aperture values
        
        perm : array
            permeability values
        
        T : array
            transmissivity values

    Notes
    ----------
        Values are generated for the variable provided. The two remaining variables are derived using those values.
    """
    local_print_log(f"--> Creating constant {variable} values.")
    units = get_units(variable)
    local_print_log(f"--> Value: {params['mu']} {units}")

    match variable:
        case "aperture":
            b = params["mu"] * np.ones(number_of_fractures)
            perm = convert(b, variable, "permeability")
            T = convert(b, variable, "transmissivity")

        case "permeability":
            perm = params["mu"] * np.ones(number_of_fractures)
            b = convert(perm, variable, "aperture")
            T = convert(perm, variable, "transmissivity")

        case "transmissivity":
            T = params["mu"] * np.ones(number_of_fractures)
            b = convert(T, variable, "aperture")
            perm = convert(T, variable, "permeability")

    local_print_log('--> Complete\n')
    return b, perm, T


# Registry mapping relationship names to (function, required_keys)
DISTRIBUTIONS = {
    "log-normal": (log_normal, ["mu", "sigma"]),
    "exponential": (exponential, ["lam"]),
    "correlated": (correlated, ["alpha", "beta"]),
    "semi-correlated": (semi_correlated, ["alpha", "beta", "sigma"]),
    "constant": (constant, ["mu"]),
}
