import pydfnworks.dfnGen.generation.input_checking.helper_functions as hf
from pydfnworks.general.logging import local_print_log

import numpy as np


def check_distributions(params, prefix):
    """ 
    Verifies "edistr" and "rdistr" making sure one distribution is defined per family and each distribution is either 1 (log-normal), 2 (Truncated Power Law), 3 (Exponential), or 4 (constant).

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
    local_print_log("\n--> Checking Length Distributions: Starting")
    key = prefix + "distr"
    shape = "ellipse" if prefix == 'e' else "rectangle"
    num_families = params['nFamEll']['value'] if prefix == 'e' else params[
        'nFamRect']['value']
    hf.check_none(key, params[key]['value'])
    hf.check_length(key, params[key]['value'], num_families)
    hf.check_values(key, params[key]['value'], 1, 4)

    #check lengths
    for i in params[key]['value']:
        cnt = params[key]['value'].count(i)
        if i == 1:
            ## logNormal
            dist_keys = [
                prefix + name
                for name in ["LogMean", "sd", "LogMin", "LogMax"]
            ]
            for dist_key in dist_keys:
                hf.check_none(dist_key, params[dist_key]['value'])
                hf.check_length(dist_key, params[dist_key]['value'], cnt)
            check_lognormal_dist(params, prefix, shape, cnt)
        elif i == 2:
            # TPL
            dist_keys = [prefix + name for name in ["min", "max", "alpha"]]
            for dist_key in dist_keys:
                hf.check_none(dist_key, params[dist_key]['value'])
                hf.check_length(dist_key, params[dist_key]['value'], cnt)
            check_tpl_dist(params, prefix, shape, cnt)
        elif i == 3:
            # Exp
            dist_keys = [
                prefix + name for name in ["ExpMean", "ExpMin", "ExpMax"]
            ]
            for dist_key in dist_keys:
                hf.check_none(dist_key, params[dist_key]['value'])
                hf.check_length(dist_key, params[dist_key]['value'], cnt)
            check_exponential_dist(params, prefix, shape, cnt)
        elif i == 4:
            # constant
            dist_keys = [prefix + name for name in ["const"]]
            for dist_key in dist_keys:
                hf.check_none(dist_key, params[dist_key]['value'])
                hf.check_length(dist_key, params[dist_key]['value'], cnt)
            check_constant_dist(params, prefix, shape, cnt)
    local_print_log("--> Checking Length Distributions: Complete")


def check_lognormal_dist(params, prefix, shape, cnt):
    """
    Verifies all logNormal Parameters for ellipses and Rectangles.

     Parameters
    -------------
        params : dict
            parameter dictionary
        prefix : string
            either 'e' or 'r' for ellipse or rectangle
        shape: string
            The shape of the fracture
        cnt : int
            The maximum range of the loop.

    Returns
    ---------
        None

    Notes
    ---------
        None
    """
    #print(f"checking log normal {shape}")
    for i in range(cnt):
        min_val = params[prefix + "LogMin"]["value"][i]
        max_val = params[prefix + "LogMax"]["value"][i]
        mean_val = params[prefix + "LogMean"]["value"][i]
        std_val = params[prefix + "sd"]["value"][i]

        hf.check_values(prefix + "LogMax", min_val, 0)
        hf.check_values(prefix + "LogMin", max_val, 0)
        hf.check_min_max(min_val, max_val, i, f"{shape} log-normal")

        if std_val <= 0:
            hf.print_error(
                f"A standard deviation equal of {std_val} was provided for {shape} log-normal entry {i+1}. Value must be post"
            )

        # Get the mean and variance of the final distribution.
        # Note these are the actual values, not the input variables
        mu = np.exp(mean_val + std_val**2 / 2)
        variance = (np.exp(std_val**2) - 1) * np.exp(2 * mean_val + std_val**2)

        if mu <= min_val:
            hf.print_error(
                f"Requested mean value of final {shape} log-normal {mu} is smaller than minimum value {min_val}. Note that the mean value is determined by {prefix+'LogMean'} and {prefix+'sd'}. See documentation for more details."
            )

        if mu >= max_val:
            hf.print_error(
                f"Requested mean value of {shape} log-normal {mu} is larger than maximum value {max_val}. Note that the mean value is determined by {prefix+'LogMean'} and {prefix+'sd'}. See documentation for more details."
            )

        hf.check_min_frac_size(params, min_val)


def check_tpl_dist(params, prefix, shape, cnt):
    """
    Verifies parameters for truncated power law distribution of fractures.

     Parameters
    -------------
        params : dict
            parameter dictionary
        prefix : string
            either 'e' or 'r' for ellipse or rectangle
        shape: string
            The shape of the fracture
        cnt : int
            The maximum range of the loop.

    Returns
    ---------
        None

    Notes
    ---------
        None
    """
    #print(f"checking tpl {shape}")
    for i in range(cnt):
        min_val = params[prefix + "min"]["value"][i]
        max_val = params[prefix + "max"]["value"][i]
        alpha = params[prefix + "alpha"]["value"][i]
        hf.check_values(prefix + "min", min_val, 0)
        hf.check_values(prefix + "max", max_val, 0)
        hf.check_values(prefix + "alpha", alpha, 0)
        hf.check_min_max(min_val, max_val, i, f"{shape} Truncated Power law")
        hf.check_min_frac_size(params, min_val)

    # x = np.linspace(min_val, xmax, 1000)
    # norm_const = 1.0 / ( (1 - ((min_val / max_val)**alpha)) - (1 - ((min_val / min_val)**alpha)))
    # pdf = norm_const * ((alpha * (min_val**alpha)) / x**(alpha + 1))


def check_exponential_dist(params, prefix, shape, cnt):
    """
    Verifies parameters for exponential distribution of fractures.

     Parameters
    -------------
        params : dict
            parameter dictionary
        prefix : string
            either 'e' or 'r' for ellipse or rectangle
        shape: string
            The shape of the fracture
        cnt : int
            The maximum range of the loop.

    Returns
    ---------
        None

    Notes
    ---------
        None
    """
    #print(f"checking exp {shape}")
    for i in range(cnt):
        min_val = params[prefix + "ExpMin"]["value"][i]
        max_val = params[prefix + "ExpMax"]["value"][i]
        mean_val = params[prefix + "ExpMean"]["value"][i]
        hf.check_values(prefix + "min", min_val, 0)
        hf.check_values(prefix + "max", max_val, 0)
        hf.check_values(prefix + "ExpMean", mean_val, 0)

        hf.check_values(prefix + "ExpMean",
                        mean_val,
                        min_val=min_val,
                        max_val=max_val)

        hf.check_min_max(min_val, max_val, i, f"{shape} exponential")
        hf.check_min_frac_size(params, min_val)


def check_constant_dist(params, prefix, shape, cnt):
    """
    Verifies parameters for constant distribution of fractures.

     Parameters
    -------------
        params : dict
            parameter dictionary
        prefix : string
            either 'e' or 'r' for ellipse or rectangle
        shape: string
            The shape of the fracture
        cnt : int
            The maximum range of the loop.

    Returns
    ---------
        None

    Notes
    ---------
        None
    """
    # print(f"checking constant {shape}")
    for i in range(cnt):
        value = params[prefix + "const"]["value"][i]
        hf.check_values(prefix + "const", value, 0)
        hf.check_min_frac_size(params, value)

