import numpy as np
from pysimfrac.src.general.helper_functions import print_error, set_mean_and_var


def initialize_box_parameters(self):
    """ Initializes parameters used in method box for fracture surface generation
    
    Parameters
    ---------------
        simFrac Object

    Returns
    --------------
        None

    Notes
    ----------------
        Attaches dictionary with parameters onto the simfrac object

    """

    self.params = {
        'mean-aperture': {
            'value': 1,
            'description': "Mean Fracture Aperture"
        },
        'aperture-log-variance': {
            'value': 0.1,
            'description': "Variance of Log Aperture Field"
        },
        'lambda_x': {
            'value': self.lx / 10,
            'description': "Correlation of field in x-direction"
        },
        'lambda_y': {
            'value': self.ly / 10,
            'description': "Correlation of field in x-direction"
        },
        'seed': {
            'value':
            1,
            'description':
            "Seed for random number generator. Set to 0 to seed off clock"
        },
    }


def check_box_parameters(self):
    """ Check that all required parameters for Gaussian field generation are provided. Exits if not. 

    Parameters
    ----------------
        simfrac object


    Returns
    ------------
        None

    Notes
    --------------
        None
    
    """
    print("--> Checking Box Method Parameters: Startingg")

    self.check_generation_parameter("lambda_x", 0)
    # if the correlation in y is not provided, we assume it's an isotropic field and set lambda_y = lambda_x
    if "lambda_y" not in self.params:
        self.params["lambda_y"] = None

    self.check_generation_parameter("mean-aperture", 0)
    self.check_generation_parameter("aperture-log-variance", 0)

    if "seed" not in self.params:
        self.params["seed"] = None

    print("--> Checking Box Method Parameters: Complete")


def box_surface(lx, ly, nx, ny, h, lambda_x, lambda_y, seed):
    """ Box Kernel for convolution
     Generalized from Hyman and Winter J. Comput. Phys. 2014

    Parameters
    -------------
        lx : float
            length in x [mm]
        ly : float
            Length in y[mm]
        nx : float 
            number of points discretizing lx
        ny : float 
            number of points discretizing ly
        lambda_x : float
            Length of box kernal in x direction
        lambda_y : float
            Length of box kernal in y direction
        seed : int / none
            Seed for random number generator

    Returns
    ------------
        T : np.array of size (nx,ny)
            Random topography, standard normal distribution of values.  Correlation structure is based on sdx and sdy
        xv : Mesh grid X
        yv : Mesh grid Y

    Notes
    ---------
        For theoretical details see "Hyman, Jeffrey D., and C. Larrabee Winter. "Stochastic generation of explicit pore structures by thresholding Gaussian random fields." Journal of Computational Physics 277 (2014): 16-31."

    """
    print("--> Creating Topography")
    np.random.seed(
        seed
    )  ### if None, will read from /dev/urandom if available or seed from clock otherwise

    delta_x = np.ceil(lambda_x / h).astype(int)
    delta_y = np.ceil(lambda_y / h).astype(int)

    half_delta_x = (0.5 * delta_x).astype(int)
    half_delta_y = (0.5 * delta_y).astype(int)

    # print(f"delta_x: {delta_x}")
    # print(f"delta_y: {delta_y}")
    # print(f"1/2 delta_x: {half_delta_x}")
    # print(f"1/2 delta_y: {half_delta_y}")

    ## create field of i.i.d variables from U[0,1]
    U = np.random.random((ny + delta_y, nx + delta_x))
    T = np.zeros((ny, nx))

    for ix in range(half_delta_x, nx + half_delta_x):
        for iy in range(half_delta_y, ny + half_delta_y):
            # print(f"i,j {i},{j}")
            # print(f"y-range : {i-half_delta_y} : {i+half_delta_y}")
            # print(f"x-range : {j-half_delta_x} : {j+half_delta_x}")
            # print(U[i-half_delta_y:i+half_delta_y, j - half_delta_x : j + half_delta_x])
            T[iy - half_delta_y,
              ix - half_delta_x] = U[iy - half_delta_y:iy + half_delta_y, ix -
                                     half_delta_x:ix + half_delta_x].sum()

    ## convert to a standard normal distributiton
    # Center at 0.0
    T -= np.mean(T)
    #  Set Variance = 1.0
    T /= np.std(T)
    # make background arrays
    X = np.linspace(-0.5 * lx, 0.5 * lx, nx)
    Y = np.linspace(-0.5 * ly, 0.5 * ly, ny)
    # convert to a mesh grid
    xv, yv = np.meshgrid(X, Y)
    print("--> Creating Topography Complete")
    return T, xv, yv


def create_box(self):
    """ Box Kernel for convolution
    
    Parameters
    ----------------
        simfrac object


    Returns
    ------------
        None

    Notes
    ---------
        For theoretical details see "Hyman, Jeffrey D., and C. Larrabee Winter. "Stochastic generation of explicit pore structures by thresholding Gaussian random fields." Journal of Computational Physics 277 (2014): 16-31."


    """
    print("--> Creating fracture surface using a Box Kernel : Starting")
    self.print_method_params()
    ## create Standard normal surface
    T, self.X, self.Y = box_surface(self.lx, self.ly, self.nx, self.ny, self.h,
                                    self.params['lambda_x']['value'],
                                    self.params['lambda_y']['value'],
                                    self.params['seed']['value'])

    self.surface = set_mean_and_var(
        T, 0, self.params['aperture-log-variance']['value'])

    ## apply shear if non-zero
    self.mean_aperture = self.params['mean-aperture']['value']
    self.top = self.surface + 0.5 * self.mean_aperture
    self.bottom = self.surface - 0.5 * self.mean_aperture

    if self.shear > 0:
        self.apply_shear()
    self.project_to_aperture()

    print("--> Creating fracture surface using a Box Kernel : Complete ")
