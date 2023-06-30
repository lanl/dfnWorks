import numpy as np


def initialize_gaussian_parameters(self):
    """ Initializes parameters used in method gaussian for fracture surface generation
    
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
            'value': 1e-4,
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


def check_gaussian_parameters(self):
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
    print("--> Checking Gaussian Method Parameters: Startingg")

    self.check_generation_parameter("lambda_x", 0)
    # if the correlation in y is not provided, we assume it's an isotropic field and set lambda_y = lambda_x
    if "lambda_y" not in self.params:
        self.params["lambda_y"] = None

    self.check_generation_parameter("mean-aperture", 0)
    self.check_generation_parameter("aperture-log-variance", 0)

    if "seed" not in self.params:
        self.params["seed"] = None

    print("--> Checking Gaussian Method Parameters: Complete")


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


def guassian_surface_2D(lx, ly, nx, ny, sdx, sdy, seed):
    """ Fourier Surface 2D 
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
        sdx : float
            Standard deviation of Gaussian kernal in x direction
        sdy : float
            Standard deviation of Gaussian kernal in y direction
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
    ## create field of i.i.d variables from U[0,1]
    U = np.random.random((ny, nx))
    # make background arrays
    X = np.linspace(-0.5 * lx, 0.5 * lx, nx)
    Y = np.linspace(-0.5 * ly, 0.5 * ly, ny)
    # convert to a mesh grid
    xv, yv = np.meshgrid(X, Y)
    # lambda function the Gaussian Kernal
    gauss_func = lambda x, y: 1.0 / (sdx * sdy * 2.0 * np.pi) \
        * np.exp(-0.5 * ((x / sdx)**2) - 0.5 * ((y / sdy)**2))

    # Values for the Gaussian Kernal over the space
    gaussian2D = gauss_func(yv, xv)

    # perform the convolution of the kernal with the white noise field in Fourier space
    # k * U  = F^{-1} (F[k] x F[U])
    # Transform the fields to Fourier Space
    F_g = np.fft.fft2(gaussian2D)
    F_U = np.fft.fft2(U)
    # Multiply them together
    F_T = np.multiply(F_g, F_U)
    # invert the Fourier Transform
    T = np.fft.ifft2(F_T)
    # Grab Real part of T (There's often junk noise in the complex part)
    T = T.real
    ## convert to a standard normal distributiton
    # Center at 0.0
    T -= np.mean(T)
    #  Set Variance = 1.0
    T /= np.std(T)
    print("--> Creating Topography Complete")
    return T, xv, yv


def create_gaussian(self):
    """ Main generator of random fields following method described by Zinn and Harvey, 2003.
    
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
    print(
        "--> Creating fracture surface using a multivariant Guassian Random Field : Starting"
    )
    self.print_method_params()

    ## convert user desired correlation length to generation parameters
    ## This relationship is empirical
    sdx = self.params['lambda_x']['value']**(3 / 2)
    if self.params['lambda_y']['value'] is None:
        sdy = sdx
    else:
        sdy = self.params['lambda_y']['value']**(3 / 2)

    ## create Standard normal surface
    T, self.X, self.Y = guassian_surface_2D(self.lx, self.ly, self.nx, self.ny,
                                            sdx, sdy,
                                            self.params['seed']['value'])

    self.surface = set_mean_and_var(
        T, 0, self.params['aperture-log-variance']['value'])

    self.mean_aperture = self.params['mean-aperture']['value']
    
    ## apply shear if non-zero
    # self.mean_aperture = self.params['mean-aperture']['value']
    self.top = self.surface + 0.5 * self.mean_aperture
    self.bottom = self.surface - 0.5 * self.mean_aperture

    if self.shear > 0:
        self.apply_shear()

    self.project_to_aperture()

    print(
        "--> Creating fracture surface using a multivariant Guassian Random Field : Complete "
    )
