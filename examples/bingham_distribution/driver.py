#"""
#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os
import numpy as np

jobname = os.getcwd() + "/output"
DFN = DFNWORKS(jobname, ncpu=8)

DFN.params['domainSize']['value'] = [20, 20, 20]
DFN.params['h']['value'] = 0.1
DFN.params['domainSizeIncrease']['value'] = [5, 5, 5]
DFN.params['ignoreBoundaryFaces']['value'] = True

DFN.params['boundaryFaces']['value'] = [0, 0, 0, 0, 1, 1]
DFN.params['seed']['value'] = 2
DFN.params['disableFram']['value'] = True
DFN.params['orientationOption']['value'] = 1



# # round cap,
DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        alpha=1.8,
                        min_radius=1.0,
                        max_radius=10.0,
                        orientation_distribution='bingham',
                        trend=0.0,
                        plunge=45.0,
                        kappa1=-20,
                        kappa2=-20,
                        p32=0.5,
                        hy_variable='aperture',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 10**-5,
                            "beta": 0.5
                        })

# # # elliptical cap
DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        alpha=1.8,
                        min_radius=1.0,
                        max_radius=10.0,
                        orientation_distribution='bingham',
                        trend=90.0,
                        plunge=30.0,
                        kappa1=-30,
                        kappa2=-5,
                        p32=10,
                        hy_variable='aperture',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 10**-5,
                            "beta": 0.5
                        })




# # # # elliptical girdle
DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        alpha=1.8,
                        min_radius=1.0,
                        max_radius=10.0,
                        orientation_distribution='bingham',
                        trend=0.0,
                        plunge=60.0,
                        kappa1=-20,
                        kappa2=-5,
                        p32=0.5,
                        hy_variable='aperture',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 10**-5,
                            "beta": 0.5
                        })

# # # #asymmetric lobes
DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        alpha=1.8,
                        min_radius=1.0,
                        max_radius=10.0,
                        orientation_distribution='bingham',
                        trend=45.0,
                        plunge=30.0,
                        kappa1=-20,
                        kappa2=-10,
                        p32=0.5,
                        hy_variable='aperture',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 10**-5,
                            "beta": 0.5
                        })
## Uncomment this to test Fisher and Bingham together 
DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        alpha=1.8,
                        min_radius=1.0,
                        max_radius=10.0,
                        orientation_distribution='fisher',
                        trend=90.0,
                        plunge=30.0,
                        kappa=30,
                        p32=1,
                        hy_variable='aperture',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 10**-5,
                            "beta": 0.5
                        })



DFN.make_working_directory(delete=True)
DFN.check_input()
exit() 


DFN.create_network()
DFN.output_report()
