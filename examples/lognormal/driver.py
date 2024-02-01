#"""
#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

jobname = os.getcwd() + "/output"
dfnFlow_file = os.getcwd() + '/dfn_explicit.in'
dfnTrans_file = os.getcwd() + '/PTDFN_control.dat'

DFN = DFNWORKS(jobname,
               dfnFlow_file=dfnFlow_file,
               dfnTrans_file=dfnTrans_file,
               ncpu=8)

DFN.params['domainSize']['value'] = [20, 20, 20]
DFN.params['h']['value'] = 0.15
DFN.params['stopCondition']['value'] = 0
DFN.params['nPoly']['value'] = 100
DFN.params['outputFinalRadiiPerFamily']['value'] = True
DFN.params['outputAcceptedRadiiPerFamily']['value'] = True
DFN.params['forceLargeFractures']['value'] = True
DFN.params['domainSizeIncrease']['value'] = [5, 5, 5]
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [0, 0, 0, 0, 1, 1]
DFN.params['rejectsPerFracture']['value'] = 350

DFN.add_fracture_family(shape="rect",
                        distribution="log_normal",
                        kappa=25.78,
                        probability=.5,
                        aspect=1.0,
                        beta_distribution=1,
                        beta=0.0,
                        theta=95.47,
                        phi=23.32,
                        log_mean=1.38,
                        log_std=.06,
                        min_radius=2.0,
                        max_radius=20.0,
                        hy_variable="aperture",
                        hy_function="correlated",
                        hy_params={
                            "alpha": 1e-7,
                            "beta": 2
                        })

DFN.add_fracture_family(shape="rect",
                        distribution="log_normal",
                        kappa=32.0,
                        probability=.5,
                        aspect=1.0,
                        beta_distribution=1,
                        beta=0.0,
                        theta=1.42,
                        phi=26.81,
                        log_mean=2.08,
                        log_std=.06,
                        min_radius=2.0,
                        max_radius=20.0,
                        hy_variable="aperture",
                        hy_function="correlated",
                        hy_params={
                            "alpha": 1e-7,
                            "beta": 2
                        })

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.create_network()
DFN.mesh_network(max_resolution_factor=10)

DFN.dfn_flow()
DFN.dfn_trans()
