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
DFN.params['h']['value'] = 0.1
DFN.params['numOfRegions']['value'] = 1
DFN.params['regions']['value'] = [[-5,5,-5,5,-5,5]]
DFN.params['domainSizeIncrease']['value'] = [2.0,2.0,2.0]
DFN.params['keepOnlyLargestCluster']['value'] = True


DFN.add_fracture_family(shape = "rect", distribution = "constant", kappa = 20.0, aspect = 1.0, region = 1, beta_distribution = 1, beta = 0.0, theta = 0.0, phi = 0.0, constant = 1.0, p32 = 3.0, hy_variable='permeability', hy_function="constant", hy_params={"mu":1e-12})

DFN.add_fracture_family(shape = "rect", distribution = "constant", kappa = 20.0, aspect = 1.0, region = 0, beta_distribution = 1, beta = 0.0, theta = 90.0, phi = 0.0, constant = 5.0, p32 = .5, hy_variable='permeability', hy_function="constant", hy_params={"mu":2e-12})

DFN.add_fracture_family(shape = "rect", distribution = "constant", kappa = 20.0, aspect = 1.0, region = 0, beta_distribution = 1, beta = 0.0, theta = 45.0, phi = 135.0, constant = 5.0, p32 = .5, hy_variable='permeability', hy_function="constant", hy_params={"mu":3e-12})

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
