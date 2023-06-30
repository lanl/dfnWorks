import numpy as np
from pysimfrac.src.general.helper_functions import print_error, all_equal
from pysimfrac.src.general import simFrac


def combine_fractures(self, fracture_list, weights=None):
    """ Combines multiple fracture surfaces using a point wise weighted linear superposition. Each point on the new fracture surface is the weighted summation of the points in the provided surfaces. 

    Parameters
    --------------
        fracture_list : list
            List of simfrac objects

        weights : list
            List of floats for weighting in superposition. The length must match that of  fracture_list

    Returns
    --------------
        combined_fracture_list : simfrac object


    Notes
    -------------
        * All entries of fracture_list (simfrac objects) must have the same size and dimension. 
        * If the weights are not normalizes, sum to 1, then the are normalized in proporiton. 
        * If no weights are provided, the weights are set to be equal
    
    
    """
    fracture_list.insert(0, self)
    # Ensure dimensions of the fracture_list are all the same.
    num_fractures = len(fracture_list)
    print(f"--> Combining {num_fractures} fractures")
    lx_list = [None] * num_fractures
    ly_list = [None] * num_fractures
    nx_list = [None] * num_fractures
    ny_list = [None] * num_fractures

    for i in range(num_fractures):
        lx_list[i] = fracture_list[i].lx
        ly_list[i] = fracture_list[i].ly
        nx_list[i] = fracture_list[i].nx
        ny_list[i] = fracture_list[i].ny

    if not all_equal(nx_list) or not all_equal(ny_list) or not all_equal(ly_list) or not all_equal(lx_list):
        print_error(
            "--> Fractures in fracture list are not the same size. Exiting")

    # Check weights are the correct size, and are normalized.
    if weights is not None:
        if len(weights) != num_fractures:
            print_error("Number of weights does not match number of weights")

        weights = np.asarray(weights)
        if weights.sum() != 1:
            print("--> Normalizing weights")
            weights /= weights.sum()
    else:
        weights = np.ones(num_fractures) / num_fractures

    ## create new surface object
    combined_fracture = simFrac.SimFrac(h=self.h,
                                        lx=self.lx,
                                        ly=self.ly,
                                        nx=self.nx,
                                        ny=self.ny,
                                        method="combined")

    ## Initialize new aperture / top / bottome fields.
    combined_fracture.aperture = np.zeros_like(self.aperture)
    combined_fracture.top = np.zeros_like(self.aperture)
    combined_fracture.bottom = np.zeros_like(self.aperture)

    combined_fracture.X = self.X
    combined_fracture.Y = self.Y
    
    ## combined the surfaces
    for i, fracture in enumerate(fracture_list):
        combined_fracture.top += weights[i] * fracture.top
        combined_fracture.bottom += weights[i] * fracture.bottom

    combined_fracture.project_to_aperture()

    return combined_fracture
