import numpy as np
from pysimfrac.src.general.helper_functions import print_error, print_warning

def gmean_effective_aperture(self):
    """ Estimates the effective aperture of the fracture using the geometric mean

    Parameters
    --------------
        None

    Returns
    --------------
        None

    Notes
    ---------------
        Adds value to the effective_aperture dictionary on the simfrac class. 

        self.effective_aperture['gmean'] 
    """

    from scipy.stats import gmean
    print("--> Estimating the effective aperture using the geometric mean")
    beff = gmean(self.aperture.reshape(self.ny*self.nx))
    print(f'--> Gmean - effective aperture : {beff:0.2e} {self.units}')
    # self.effective_aperture.update({'gmean': beff})
    self.effective_aperture.__setitem__('gmean', beff)


def hmean_effective_aperture(self):
    """ Estimates the effective aperture of the fracture using the harmonic mean

    Parameters
    --------------
        None

    Returns
    --------------
        None

    Notes
    ---------------
        Adds value to the effective_aperture dictionary on the simfrac class. 

        self.effective_aperture['hmean'] 
    """

    from scipy.stats import hmean
    print("--> Estimating the effective aperture using the harmonic mean")
    beff = hmean(self.aperture.reshape(self.ny*self.nx))
    print(f'--> hmean - effective aperture : {beff:0.2e} {self.units}')
    # self.effective_aperture.update({'gmean': beff})
    self.effective_aperture.__setitem__('hmean', beff)


def mean_effective_aperture(self):
    """ Estimates the effective aperture of the fracture using the arthimatic mean

    Parameters
    --------------
        None

    Returns
    --------------
        None

    Notes
    ---------------
        Adds value to the effective_aperture dictionary on the simfrac class. 

        self.effective_aperture['mean'] 
    """

    print("--> Estimating the effective aperture using the arthimatic mean")
    beff = np.mean(self.aperture.reshape(self.ny*self.nx))
    print(f'--> Arthimatic mean - effective aperture : {beff:0.2e} {self.units}')
    # self.effective_aperture.update({'gmean': beff})
    self.effective_aperture.__setitem__('mean', beff)

def get_effective_aperture(self, model):
    """ Estimate the effective aperture of the fractures. 

    Models:
        - numerical : Estimates the effective aperture of the fracture by solving the Darcy flow equations using a Laplace equation for pressure in 2-dimensions.
        - gmean : Geometric average
        - hmean : Harmonic average
        - mean : Arthimatic average (amean, mean, average, arthimatic)

    Parameters
    ----------------
        model : string
            Currently available models: numerical, gmean, hmean, amean
    
    Returns
    ----------------
        None

    Notes
    ----------------
        Adds value to the effective_aperture dictionary on the simfrac class. 

        self.effective_aperture['<model>'] 
    """

    print("\n--> Computing effective aperture")
    if model == "numerical":
        self.numerical_effective_aperture()
    elif model == "gmean":
        self.gmean_effective_aperture()
    elif model == "hmean":
        self.hmean_effective_aperture()
    elif model == "amean" or model == "mean" or model == "average" or model == "arthimatic":
        self.mean_effective_aperture()
    else:
        print_warning(f"--> Unknown effective aperture model. {model}.")

    print("--> Computing effective aperture - complete\n")