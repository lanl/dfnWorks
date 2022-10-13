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
dfnTrans_file = os.getcwd() + '/PTDFN_control_tdrw.dat'

DFN = DFNWORKS(jobname,
               dfnFlow_file=dfnFlow_file,
               dfnTrans_file=dfnTrans_file,
               ncpu=8)

DFN.params['domainSize']['value'] = [10, 5, 5]
DFN.params['h']['value'] = 0.1
DFN.params['stopCondition']['value'] = 0
DFN.params['nPoly']['value'] = 1250
DFN.params['outputFinalRadiiPerFamily']['value'] = True
DFN.params['outputAcceptedRadiiPerFamily']['value'] = True
DFN.params['forceLargeFractures']['value'] = True
DFN.params['domainSizeIncrease']['value'] = [2,2,2]
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [1,1,0,0,0,0]
DFN.params['rejectsPerFracture']['value'] = 350

DFN.add_fracture_family(shape="rect",
                        distribution="constant",
                        kappa=1.0,
                        probability=.5,
                        aspect=1,
                        beta_distribution=1,
                        beta=0.0,
                        theta=0.0,
                        phi=23.32,
                        constant=1,
                        hy_variable = 'transmissivity', 
                        hy_function='correlated', 
                        hy_params = {"alpha":1e-13, "beta":1})

DFN.add_fracture_family(shape="rect",
                        distribution="constant",
                        kappa=1.0,
                        probability=.5,
                        aspect=1,
                        beta_distribution=1,
                        beta=0.0,
                        theta=1.42,
                        phi=26.81,
                        constant=1,
                        hy_variable = 'transmissivity', 
                        hy_function='correlated', 
                        hy_params = {"alpha":1e-13, "beta":1})

DFN.print_family_information(1)

DFN.make_working_directory(delete=True)

DFN.check_input()

for key in DFN.params.keys():
    print(key, DFN.params[key]['value'])

# define_paths()
DFN.create_network()
# DFN.output_report()
DFN.mesh_network(coarse_factor=10)

DFN.dfn_flow()
DFN.dfn_trans()
