import sys
import numpy as np
from pysimfrac.src.general.helper_functions import print_error, print_warning
import timeit


def set_mean_aperture(self, mean_aperture=None):
    """ Sets the mean aperture of the surface to the value mean_aperture

    Parameters
    --------------------
        self : object
            simFrac Class
        mean_aperture : float
            Desired mean aperture value

    Returns
    --------------------
        None

    Notes
    --------------------
        None
    
    """
    if mean_aperture:
        self.mean_aperture = mean_aperture
    print(f"--> Setting mean aperture value to {self.mean_aperture}")
    # reset top and bottom to be mean zero
    self.top -= np.mean(self.top)
    self.bottom -= np.mean(self.bottom)
    # set top to 1/2 mean value
    self.top += 0.5 * self.mean_aperture
    # set bottomr mean
    self.bottom -= 0.5 * self.mean_aperture
    # Reset aperture field
    self.project_to_aperture()
    print("--> Complete")


def aperture_check(self):

    print(f"--> Checking aperture values")
    surface_ap = self.top - self.bottom
    neg_aps = np.sum(surface_ap < 0)
    if neg_aps > 0:
        print_warning(
            f'Negative apertures were found, clipping {neg_aps} values')
        self.bottom[self.bottom > self.top] = self.top[self.bottom > self.top]
        self.aperture = self.top - self.bottom
    print("--> Complete")


def reset_bottom(self):
    """ Sets the minimum value of the bottom surface to 0

    Parameters
    --------------------
        self : object
            simFrac Class

    Returns
    --------------------
        None

    Notes
    --------------------
        Needs to be called for voxelization
    
    """

    print(f"--> Setting minimum surface value of bottom to 0")
    min_val = self.bottom.min()  # min value of bottom
    # push the distributions to start at 0
    self.top -= min_val
    self.bottom -= min_val
    print("--> Complete")


def rescale_surface(self, method='mean'):
    """
    
    Parameters
    --------------------
        aperture : TYPE
            DESCRIPTION.
        method : TYPE, optional
            DESCRIPTION. The default is 'mean'.

    Returns
    --------------------
        None.

    """
    print(f"--> Rescaling surface by method: {method}")

    self.aperture_check()

    if method == 'mean':
        factor = self.aperture / self.aperture.mean()  # re-scaling factor
    if method == 'max':
        factor = self.aperture / self.aperture.max()  # re-scaling factor

    self.top *= factor
    self.bottom *= factor

    self.reset_bottom()
    self.project_to_aperture()

    print("--> Complete")


def project_to_aperture(self):
    """ Project the top and bottom surfaces onto a 2D aperture field. 

    Parameters
    --------------------
        self : simfrac object 

    Returns
    --------------------
        None

    Notes
    --------------------
        If bottom value is higher than top, set aperture on those nodes equal to 0.

    """
    print("--> Projecting surfaces to 2D aperture field")
    ## take difference
    self.aperture = self.top - self.bottom
    ## find values where bottom surface is larger than the top
    neg_idx = np.where(self.aperture < 0)
    # set those values to 0
    self.aperture[neg_idx] = 0
    print("--> Complete")


def apply_shear(self, shear=None):
    """ Shifts the top surface along the x direction a distance of shear. Units of shear are in self.units. 

    Parameters
    --------------------
        self : object
            simFrac Class
        shear : float
            Value of shear in the x direction (Units are self.units)

    Returns
    --------------------
        None

    Notes
    --------------------
        Needs to be called for voxelization
    
    """

    print("--> Applying shear to fracture : Starting")
    if shear:
        self.shear = shear

    print(f"--> Shear value : {self.shear} [{self.units}]")
    # tranlate the shear into discrete units
    n = np.ceil(self.shear / self.h).astype(int)
    ## translation of indices
    idx = [(i + n) % self.nx for i in range(self.nx)]
    self.top = self.top[:, idx]
    self.project_to_aperture()
    print("--> Applying shear to fracture : Complete")
