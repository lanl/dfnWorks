import sys
from itertools import groupby
import numpy as np
import pickle
import os


def print_error(error_string):
    """ Prints Error to screen and exits program. 
    
    Parameters
    ----------------
        error_string : str
            a string describing the error

    Returns
    -----------
        None

    Notes
    -------------

    """
    sys.stderr.write(error_string)
    sys.exit(1)


def print_warning(warning_string):
    """ Prints warning to screen
    
    Parameters
    ----------------
        warning_string : str
            a string describing the warning 

    Returns
    -----------
        None

    Notes
    -------------
        Does not exit program
    """

    print(f"Warning --- {warning_string}")


def check_generation_parameter(self, name, min_val=None, max_val=None):
    """ Check parameter dictionary that the required key exists and has an acceptable value.
    
    Parameters
    ----------------
        name : str
            Name of the parameter
        min_val : float
            Minimum accpetable value of the parameter
        max_val : float
            Maximum accpetable value of the parameter

    Returns
    -----------
        None

    Notes
    -------------

    """

    if name not in self.params:
        print_error(f"Required parameter {name} not provided for generation")

    value = self.params[name]['value']
    if min_val is not None:
        if value < min_val:
            print_error(
                f"\"{name}\" entry has value {value}, which is less than minimum value of {min_val}"
            )
    if max_val is not None:
        if value > max_val:
            print_error(
                f"\"{name}\" entry has value {value}, which above the maximum value {max_val}."
            )


def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


def set_mean_and_var(array, mu, sigma):
    """ Rescale field to lognormal distribution with desired mean and log variance. 

    Parameters
    -------------
        array : numpy array
            values to be rescaled
        mu : float 
            desired log mean
        sigma : float
            desired log variance

    Returns
    ------------
        output : numpy array 
            Rescaled values

    Notes
    ---------  

    """
    if mu > 0:
        mu = np.log(mu)

    output = np.exp(mu + np.sqrt(sigma) * array)

    if mu == 0:
        output -= np.mean(output)

    return output

