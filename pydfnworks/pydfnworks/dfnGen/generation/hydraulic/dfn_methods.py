"""
DFN class methods for hydraulic property generation and assignment.
"""
import numpy as np

from .conversions import convert, check_key
from .distributions import DISTRIBUTIONS


def set_fracture_hydraulic_values(self, variable, fracture_list, value_list):
    """ Assigns hydraulic properties to a list of provided fractures. 

    Parameters
    -----------------
        self : object 
            DFN Class
        
        variable : string
            base variable in relationship. Options are: aperture, permeability, transmissivity
        
        fracture_list : list
            List of fracture indices whose variables are being assigned. 
            *Note* Fractures are indexed starting at 1.
        
        value_list : list  
            values to be assigned. 

    Returns 
    -------------
        None
    """
    if len(fracture_list) != len(value_list):
        error = f"Error. Length of fracture list is not equal to the length of the value list provided.\nExiting.\n"
        self.print_log(error, 'error')

    value_list = np.array(value_list)
    fracture_list = np.array(fracture_list)

    match variable:
        case 'aperture':
            b = value_list
            perm = convert(b, variable, "permeability")
            transmissivity = convert(b, variable, "transmissivity")

        case 'permeability':
            perm = value_list
            b = convert(perm, variable, "aperture")
            transmissivity = convert(perm, variable, "transmissivity")

        case 'transmissivity':
            transmissivity = value_list
            b = convert(transmissivity, variable, "aperture")
            perm = convert(transmissivity, variable, "permeability")

        case _:
            error = f"Error. The variable of choice '{variable}' is not known\nAcceptable names are aperture, permeability, transmissivity\nExiting.\n"
            self.print_log(error, 'error')

    self.aperture[fracture_list - 1] = b
    self.perm[fracture_list - 1] = perm
    self.transmissivity[fracture_list - 1] = transmissivity


def generate_hydraulic_values(self, variable, relationship, params, family_id=None):
    """ Generates hydraulic property values. 

    Parameters
    -----------
        self : object 
            DFN Class
        
        variable : string
            base variable in relationship. Options are: aperture, permeability, transmissivity
        
        relationship : string
            name of functional relationship for apertures. 
            options are log-normal, correlated, semi-correlated, constant, and exponential
        
        params : dictionary
            dictionary of parameters for functional relationship
                if correlated --> {"alpha":value, "beta":value}
                if semi-correlated --> {"alpha":value, "beta":value, "sigma":value}
                if constant --> {"mu":value}
                if log-normal --> {"mu":value, "sigma":value}
                if exponential --> {"lam":value}

        family_id : int
            family id of fractures

    Returns
    ----------
        None

    Notes
    ----------
    See Hyman et al. 2016 "Fracture size and transmissivity correlations: Implications 
    for transport simulations in sparse three-dimensional discrete fracture networks 
    following a truncated power law distribution of fracture size" Water Resources Research 
    for more details.

    Changes in hydraulic properties are added to DFN object.
    """
    # Check if the variable choice is defined
    variables = ["aperture", "permeability", "transmissivity"]
    if variable not in variables:
        error = f"Error. The variable of choice '{variable}' is not known\nAcceptable names are {', '.join(variables)}\nExiting.\n"
        self.print_log(error, 'error')

    # Check if the relationship is defined
    if relationship not in DISTRIBUTIONS:
        error = f"Error! The provided relationship '{relationship}' is unknown\nAcceptable relationships are {', '.join(DISTRIBUTIONS.keys())}\nExiting.\n"
        self.print_log(error, 'error')

    # Get distribution function and required keys
    dist_func, required_keys = DISTRIBUTIONS[relationship]

    # Validate params
    for key in required_keys:
        if not check_key(params, key):
            error = f"Error. The required key '{key}' was not found in the params dictionary\nExiting\n"
            self.print_log(error, 'error')

    # Get fracture data
    radii = self.radii[:, 2]
    families = self.families
    number_of_fractures = self.num_frac

    if family_id is not None:
        self.print_log(f"--> Working on Fracture Family {family_id}")
        idx = np.where(families == family_id)
        if len(idx[0]) == 0:
            error = f"Error. No fractures in the network are in the requested family. {family_id}.\nUser Rectangles = -1\nUser Ellipses = 0.\nStochastic Families > 0.\nExiting\n"
            self.print_log(error, 'error')

    # Call distribution function with appropriate arguments
    match relationship:
        case "correlated":
            b, perm, transmissivity = dist_func(params, variable, radii)
        case "semi-correlated":
            b, perm, transmissivity = dist_func(params, variable, radii, number_of_fractures)
        case "log-normal" | "exponential" | "constant":
                b, perm, transmissivity = dist_func(params, variable, number_of_fractures)

    # Assign values
    match family_id:
        case None:
            self.aperture = b
            self.perm = perm
            self.transmissivity = transmissivity
        case _:
            idx = np.where(families == family_id)
            self.aperture[idx] = b[idx]
            self.perm[idx] = perm[idx]
            self.transmissivity[idx] = transmissivity[idx]
