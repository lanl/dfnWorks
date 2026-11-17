"""
Utility functions for hydraulic property conversions and unit handling.
"""
import numpy as np

from pydfnworks.general.logging import local_print_log


def get_units(variable):
    """
    Returns a string of appropriate units for different variable

    Parameters
    -----------
        variable : string
            name of variable. Acceptable values are aperture, permeability, and transmissivity
    
    Returns
    ----------
        units : string
            appropriate units for provided variable
    """
    match variable:
        case "aperture":
            return "m"
        case "permeability":
            return "m^2"
        case "transmissivity":
            return "m^2/s"
        case _:
            error = f"Error. The variable of choice '{variable}' is not known in the function get_units()\nAcceptable names are aperture, permeability, and transmissivity\nExiting."
            local_print_log(error, 'error')


def check_key(d, key):
    """ 
    Checks if key is in dictionary

    Parameters
    -----------
        d : dictionary
        
        key : string
    
    Returns
    ----------
        bool : bool
            True if key is in dictionary, False if not
    """
    return key in d.keys()


def load_fractures(filename, quiet):
    """ 
    Loads fracture information from filename. 

    Parameters
    -----------
        filename : string
            name of fracture radii file

        quiet : bool
            If True details are not printed to screen, if False they are
    
    Returns
    ----------
        r : array of doubles
            maximum radii of fractures

        family_id : array of ints
            family id for each fracture
        
        n : int
            number of fractures in the domain 
    """
    if not quiet:
        local_print_log(f"--> Loading Fracture information from {filename}")

    data = np.genfromtxt(filename, skip_header=2)
    family_id = (data[:, 2]).astype(int)
    n, _ = np.shape(data)
    r = np.zeros(n)
    for i in range(n):
        if data[i, 0] >= data[i, 1]:
            r[i] = data[i, 0]
        else:
            r[i] = data[i, 1]
    return r, family_id, n


def convert(x, source, target):
    """ 
    Converts between variables aperture, permeability, and transmissivity

    Parameters
    -----------
        x : numpy array
            input values
        
        source : string
            variable name of source
        
        target : string
            variable name of output 
    
    Returns
    ----------
        y : numpy array
            array of converted values

    Notes
    -----
    permeability/Transmissivty are defined using the cubic law

    k = b^2/12

    T = (b^3 rho g)/(12 mu)
    """
    mu = 8.9e-4  # dynamic viscosity of water at 20 degrees C, Pa*s
    g = 9.8  # gravity acceleration
    rho = 997  # water density

    match (source, target):
        case ("aperture", "permeability"):
            return (x**2) / 12
        case ("aperture", "transmissivity"):
            return (x**3 * rho * g) / (12 * mu)
        case ("permeability", "aperture"):
            return np.sqrt(12.0 * x)
        case ("permeability", "transmissivity"):
            b = np.sqrt(12.0 * x)
            return (b * x * rho * g) / (12 * mu)
        case ("transmissivity", "aperture"):
            return ((x * 12 * mu) / (rho * g))**(1 / 3)
        case ("transmissivity", "permeability"):
            b = ((x * 12 * mu) / (rho * g))**(1 / 3)
            return (b**2) / 12
        case _:
            error = f"Error in conversion. Unknown name provided in convert. Either '{source}' or '{target}' is not known\nAcceptable names are aperture, permeability, and transmissivity\nExiting.\n"
            local_print_log(error, 'error')
