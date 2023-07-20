import numpy as np
from pysimfrac.src.general.helper_functions import print_error

import warnings
warnings.filterwarnings("ignore", message=".*The 'nopython' keyword.*")



def initialize_spectral_parameters(self):
    """ Initializes parameters used in method spectral for fracture surface generation
    
    Parameters
    ---------------
        simFrac object
    

    Returns
    --------------
        None

    Notes
    ----------------
        Attaches dictionary with parameters onto the simfrac object
        
        For theoretical details see:
        "Brown, Simple mathematical model of a rough fracture, J. of Geophysical Research, 100 (1995): 5941-5952”
        “Glover et al., Synthetic rough fractures in rocks, J. of Geophysical Research, 103 (1998): 9609-9620”
        “Glover et al., Fluid flow in synthetic rough fractures and application to the Hachimantai geothermal hot dry rock test site, 103 (1998): 9621-9635”

    """
    self.params = {
        'H': {
            'value': 0.5,
            'description': "Hurst exponent. Determines fractal dimension. Range is (0, 1)"
        },
        'roughness': {
            'value': 0.01,
            'description': "Root-mean-squared value of heights [m], Range is (0, infty)"
        },
        'mean-aperture': {
            'value': 1,
            'description': "Mean Fracture Aperture"
        },
        'mismatch': {
            'value': 0.9,
            'description': "Mismatch length scale (wavelength) as a fraction of fracture size [0 < Mismatch < 1]"
        },
        'N': {
            'value': self.nx,
            'description': "Discretization of fracture self.lx/self.h"
        },
        'aniso': {
            'value': 0,
            'description': "Anisotropy Ratio [0 < Aniso < 1]. Setting to 0 is isotropic."
        },
        'seed': {
            'value': 1,
            'description': "Seed for the random number generator. Set to 0 to seed off clock."
        },
        'lambda_0': {
            'value': 1,
            'description': "(optional) 'roll-off' length scale as a fraction of fracture size [0 < lambda_0 < 1 (default)]"
        },
        'model': {
            'value': 'linear',
            'description': "(optional) Power spectral density model: 'linear' (default), 'bilinear', 'smooth'"
        }
    }


def check_spectral_parameters(self):
    """ Check that all required parameters for spectral field generation are provided. Exits if not. 

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
    print("--> Checking spectral Method Parameters: Starting")

    self.check_generation_parameter("mean-aperture", 0)
    self.check_generation_parameter("roughness", 0)
    self.check_generation_parameter("mismatch", 0, 1)
    self.check_generation_parameter("H", 0, 1)
    self.check_generation_parameter("aniso", 0, 1 - 10**-16)
    self.check_generation_parameter("lambda_0", 0, 1)

    if "seed" not in self.params:
        self.params["seed"] = None

    psd_models = ['linear', 'bilinear', 'smooth']
    if not self.params['model']['value'] in psd_models:
        print_error(
            f"spectral Model unknown. Value provided {self.params['model']['value']} \
            \nAcceptable models: 'linear', 'bilinear', 'smooth' ")
    print("--> Checking spectral Method Parameters: Complete")


def create_spectral(self):
    """ Generate a fracture surface using the spectral method.

    Parameters
    -----------
        self : simfrac object

    Returns
    --------
        None

    Notes
    ------
        This method initializes the spectral method parameters, checks the parameters for consistency, and generates a fracture surface using the spectral method.
    """
    print("--> Running Fracture surface method 'spectral': Starting")
    ## Check parameters for model consistency
    self.check_spectral_parameters()
    ## Print method parameters to screen
    self.print_method_params()

    ## set Random number streams
    rand_stream1 = np.random.RandomState(self.params['seed']['value'])
    rand_stream2 = np.random.RandomState(
        rand_stream1.randint(self.params['seed']['value']))

    # Derive parameters
    two_pi = 2.0 * np.pi
    Nyq = 1 / (2 * self.h)

    # Set different sampling of wave lengths for different facture sizes
    dq_x = 1 / (self.nx * self.h)
    dq_y = 1 / (self.ny * self.h)

    # Wavenumber increment
    wave_numbers_x = two_pi * np.linspace(-Nyq, Nyq - dq_x, self.nx)
    wave_numbers_y = two_pi * np.linspace(-Nyq, Nyq - dq_y, self.ny)

    # 2D Wavenumbers [m^-1]
    qx, qy = np.meshgrid(wave_numbers_x, wave_numbers_y)
    
    # Wavenumber modulus (Apply here the anisotropy conditions)
    q = (qx**2 + (qy / (1 - self.params['aniso']['value']))**2)**0.5
    wavelength_modulus = np.zeros_like(q)
    idx = np.where(q != 0)
    wavelength_modulus[idx] = two_pi / q[idx]
    # for i,val in q:
    #     if q != 0:
    #         wavelength_modulus[i] = two_pi / val  # Wavelengths modulus

    # Find wavelengths above the "roll-off" lengthscale
    roll_off = np.where(wavelength_modulus > self.params['lambda_0']['value'] * min(self.lx, self.ly))

    print(f"--> Power spectral density model: {self.params['model']['value'] }")

    Fmodulus = np.zeros_like(q)
    if self.params['model']['value'] == 'linear':
        Fmodulus[idx] = q[idx]**(- 1 - self.params['H']['value'])
        Fmodulus[roll_off] = 0
        
    elif self.params['model']['value'] == 'bilinear':
        Fmodulus[idx] = q[idx]**(- 1 - self.params['H']['value'])

        Fmodulus[roll_off] = (
            two_pi /
            (self.params['lambda_0']['value'] * min(self.lx, self.ly)))**(
                -1 - self.params['H']['value'])

    elif self.params['model']['value'] == 'smooth':
        Fmodulus[idx] = (
            two_pi /
            (self.params['lambda_0']['value'] * min(self.lx, self.ly)) +
            q[idx])**(-1 - self.params['H']['value'])


    # First surface spectrum
    Phase1 = two_pi * rand_stream1.rand(self.ny, self.nx)
    # Second surface specturm
    Phase2 = two_pi * rand_stream2.rand(self.ny, self.nx)

    # The phase spectrum of the second surface is different for short wavelengths
    # Find mismatching wavelengths 
    mismatching = np.where(
        wavelength_modulus < self.params['mismatch']['value'] *
        min(self.lx, self.ly))

    # Overwrite mismatching wave lengths
    Phase2[mismatching] = Phase1[mismatching]

    # Top surface in Fourier space
    A1 = Fmodulus * (np.cos(Phase1) + 1j * np.sin(Phase1)
                     ) / np.abs(np.cos(Phase1) + 1j * np.sin(Phase1))

    # Bottom surface in Fourier space
    A2 = Fmodulus * (np.cos(Phase2) + 1j * np.sin(Phase2)
                     ) / np.abs(np.cos(Phase2) + 1j * np.sin(Phase2))

    # Shift and invert FT to real space for both top and bottom
    # Upper surface
    self.top = np.fft.ifft2(np.fft.ifftshift(A1)).real
    # Lower surface
    self.bottom = np.fft.ifft2(np.fft.ifftshift(A2)).real

    # Roughness is used to rescale the surface variance
    # Divide out the variance and then multiple but the desired one.
    roughnessScale = self.params['roughness']['value'] / np.std(self.top)
     
    self.top *= roughnessScale
    self.bottom *= roughnessScale

    self.mean_aperture = self.params['mean-aperture']['value']

    ## apply shear if non-zero
    self.top = self.top + 0.5 * self.mean_aperture
    self.bottom = self.bottom - 0.5 * self.mean_aperture
    self.aperture = self.top - self.bottom

    # Attached mesh to the class
    X = np.linspace(-0.5 * self.lx, 0.5 * self.lx, self.nx)
    Y = np.linspace(-0.5 * self.ly, 0.5 * self.ly, self.ny)
    xv, yv = np.meshgrid(X, Y)
    self.X = xv
    self.Y = yv
    
    # Apply shear if non-zero
    if self.shear > 0:
        self.apply_shear()

    print("--> Running Fracture surface method 'spectral': Complete")
