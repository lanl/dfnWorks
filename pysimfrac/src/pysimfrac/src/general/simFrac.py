#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "Jeffrey Hyman"
__version__ = "0.2"
__maintainer__ = "Jeffrey Hyman"
__email__ = "jhyman@lanl.gov"
"""
SimFrac object class. 
"""
import os, sys
import numpy as np
from pysimfrac.src.general.helper_functions import print_error

class SimFrac():
    """ The SimFrac Object 
        
        Parameters
        ----------------
            self : simFrac Object 
            units : string 
                SI units for domain size, e.g., mm
            lx : float
                Length of domain in x direction 
            ly : float
                Length of domain in x direction 
            h : float 
                Dicretization length of domain. Uniform in x and y
            nx : int
                Number of nodes in x
            ny : int 
                Number of nodes in y
            shear : float
                Shear to apply in x direction
            method : string
                name of generation method. Options are "spectral", "Gaussian", or "box"
            pickle_file : string
                Name of pickled simFrac object. If a value is provided. The object will be loaded from file. 
        
        Returns
        ------------
            None

        Notes
        ------------
            * If nx and ny are provided, the resulted hx and hy must be the same. 
        
    """


    from pysimfrac.src.general.helper_functions import check_generation_parameter

    ##object functions
    from pysimfrac.src.methods.surface_generation import create_fracture, initialize_method, print_method_params, initialize_parameters

    from pysimfrac.src.methods.gaussian import create_gaussian, check_gaussian_parameters, initialize_gaussian_parameters

    from pysimfrac.src.methods.box import create_box, check_box_parameters, initialize_box_parameters

    from pysimfrac.src.methods.spectral import create_spectral, check_spectral_parameters, initialize_spectral_parameters

    from pysimfrac.src.methods.combine_fractures import combine_fractures

    from pysimfrac.src.analysis.geostats import compute_moments, print_moments, get_surface_pdf, get_surface_cdf, plot_surface_pdf

    from pysimfrac.src.analysis.geostats_acf import compute_acf, plot_acf

    from pysimfrac.src.analysis.geostats_variogram import single_field_variogram, compute_variogram, plot_variogram

    from pysimfrac.src.analysis.make_plots import plot_aperture_field, plot_surface, plot_3D

    from pysimfrac.src.analysis.voxelization import pad, voxelize

    from pysimfrac.src.analysis.modify_surfaces import apply_shear, set_mean_aperture, aperture_check, reset_bottom, project_to_aperture, rescale_surface

    from pysimfrac.src.io.dump_ascii import dump_surface_ascii, dump_ascii

    from pysimfrac.src.io.dump_pickle import to_pickle, from_pickle

    from pysimfrac.src.analysis.effective_aperture.effective_aperture import get_effective_aperture, gmean_effective_aperture, hmean_effective_aperture, mean_effective_aperture

    from pysimfrac.src.analysis.effective_aperture.numerical_effective_aperture import numerical_effective_aperture

    def __init__(self,
                 lx=None,
                 ly=None,
                 h=None,
                 nx=None,
                 ny=None,
                 shear=None,
                 method=None,
                 units=None,
                 pickle_file=None):
        """ Instanication of the SimFrac Object 


        Parameters
        ----------------
            self : simFrac Object 
            units : string 
                SI units for domain size, e.g., mm
            lx : float
                Length of domain in x direction 
            ly : float
                Length of domain in x direction 
            h : float 
                Dicretization length of domain. Uniform in x and y
            nx : int
                Number of nodes in x
            ny : int 
                Number of nodes in y
            shear : float
                Shear to apply in x direction
            method : string
                name of generation method. Options are "spectral", "Gaussian", or "box"
            pickle_file : string
                Name of pickled simFrac object. If a value is provided. The object will be loaded from file. 
        
        Returns
        ------------
            None

        Notes
        ------------
            * If nx and ny are provided, the resulted hx and hy must be the same. 
        
        """



        ## object attributes
        self.method = str  # Generation method
        self.dimension = int  ## Number of dimensions (2,3)
        self.lx = float  # size of fracture in x-dimension (mm)
        self.ly = float  # size of fracture in y-dimension (mm)
        self.h = float  # dicretization length (mm)
        self.params = dict

        self.aperture = None  # 2D array of aperture field
        self.mean_aperture = None  # Mean aperture value (mean of 2D field)
        self.shear = 0
        self.top = None  # 2D array of top surface height
        self.bottom = None  # 2D array of bottom surface height

        self.units = 'mm'  # Units of length, Default is mm.

        ## dictionary for autocorrelation
        self.acf = {
            "top": {
                "x": {
                    "correlation": None,
                    "lags": None,
                    "acf": None
                },
                "y": {
                    "correlation": None,
                    "lags": None,
                    "acf": None
                },
                "anisotropy": None
            },
            "bottom": {
                "x": {
                    "correlation": None,
                    "lags": None,
                    "acf": None
                },
                "y": {
                    "correlation": None,
                    "lags": None,
                    "acf": None
                },
                "anisotropy": None
            },
            "aperture": {
                "x": {
                    "correlation": None,
                    "lags": None,
                    "acf": None
                },
                "y": {
                    "correlation": None,
                    "lags": None,
                    "acf": None
                },
                "anisotropy": None
            }
        }

        # dictionary for moments of the surface distributions
        self.moments = {
            "aperture": {
                "mean": None,
                "variance": None,
                "skewness": None,
                "kurtosis": None
            },
            "top": {
                "mean": None,
                "variance": None,
                "skewness": None,
                "kurtosis": None
            },
            "bottom": {
                "mean": None,
                "variance": None,
                "skewness": None,
                "kurtosis": None
            }
        }

        self.variogram = {"aperture": None, "top": None, "bottom": None}

        self.effective_aperture = {}

        if pickle_file:
            self.from_pickle(pickle_file)
        else:
            ## determine number of cells in x and y
            if lx > 0:
                self.lx = lx
            else:
                print_error(f"lx value must be positive, value provided {lx}")

            if shear:
                self.shear = shear

            if self.shear > self.lx:
                print_error(
                    f"Desired shear longer than fracture. Shear {self.shear}. Fracture length {self.lx}"
                )

            ## determine number of cells in x and y
            if ly > 0:
                self.ly = ly
            else:
                print_error(f"ly value must be positive, Value provided {ly}")
            if h:
                if h <= 0:
                    print_error(f" h must be postive. Value provided {h}")

                self.h = h
                self.nx = int(np.ceil(self.lx / self.h))
                self.ny = int(np.ceil(self.ly / self.h))

            # check number of points....
            elif nx > 0 and ny > 0:
                hx = self.lx / nx
                hy = self.ly / ny
                if hx != hy:
                    print_error(
                        "Resolution is not uniform in x and y. Check lx/nx and ly/ny"
                    )
                else:
                    self.h = hx
                    self.nx = nx
                    self.ny = ny

            ## initialize defaults
            self.method = method
            self.initialize_parameters()
            if units:
                self.units = units

            self.initialize_method()
