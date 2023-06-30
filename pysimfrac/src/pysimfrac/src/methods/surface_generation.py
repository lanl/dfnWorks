import sys
import numpy as np
from pysimfrac.src.general.helper_functions import print_error, print_warning
import timeit


def print_method_params(self):
    """ Prints the generation methods parameters to screen
    
    Parameters
    ---------------
        self : simfrac object

    Returns
    -------------
        None

    Notes
    -----------
        Different generation methods have different parameters used in their generation

    """

    print("\n")
    print(f"--> Generation Method: {self.method}")

    for key in self.params:
        print(f" * Parameter Name: {key}")
        print(f" * Value: {self.params[key]['value']}")
        print(f" * Description: {self.params[key]['description']}")
        print("\n")


def initialize_method(self):
    """ Initializes defaults for a generation method
    
    Parameters
    ---------------
        self : simfrac object

    Returns
    -------------
        None

    Notes
    -----------
        Currently supported methods are "Guassian" an "Combined"  
        
    """
    if self.method == 'gaussian':
        self.check_gaussian_parameters()
    elif self.method == 'spectral':
        self.check_spectral_parameters()
    elif self.method == 'box':
        self.check_box_parameters()
    elif self.method == 'combined':
        pass
    else:
        print_error(f"Error. Unknown method provided - {self.method}")


def initialize_parameters(self):
    """ Initializes defaults for a generation method
    
    Parameters
    ---------------
        self : simfrac object

    Returns
    -------------
        None

    Notes
    -----------
        Currently supported methods are "Guassian" and "Combined"  
        
    """
    if self.method == 'gaussian':
        self.initialize_gaussian_parameters()
    elif self.method == 'spectral':
        self.initialize_spectral_parameters()
    elif self.method == 'box':
        self.initialize_box_parameters()
    elif self.method == 'combined':
        pass
    else:
        print_error(f"Error. Unknown method provided - {self.method}")


def create_fracture(self):
    """ Prints the generation methods parameters to screen
    
    Parameters
    ---------------
        self : simfrac object

    Returns
    -------------
        None

    Notes
    -----------
        Currently supported methods are "Guassian" and "Combined"  

    """

    # Start Timer
    tic = timeit.default_timer()
    if self.method == 'gaussian':
        self.create_gaussian()
    elif self.method == 'spectral':
        self.create_spectral()
    elif self.method == 'box':
        self.create_box()
    elif self.method == 'combined':
        print(f"Method - combined. Nothing has been performed.")
        pass
    else:
        error = f"Error. Unknown method provided - {self.method}"
        sys.stderr.write(error)
        exit(1)
    if self.mean_aperture:
        self.set_mean_aperture()
    ## Print Time
    elapsed = timeit.default_timer() - tic
    print(f"--> Time required: {elapsed:.2f} seconds\n")
