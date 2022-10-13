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

DFN.params['domainSize']['value'] = [10, 10, 10]
DFN.params['h']['value'] = 0.1
DFN.params['stopCondition']['value'] = 0
DFN.params['nPoly']['value'] = 40


DFN.add_fracture_family(shape = "rect", distribution = "exp", kappa = 1.0, probability = 1.0, aspect = 1.0, beta_distribution = 1, beta = 0.0, theta = 9.52, phi = 80.82, exp_mean = 3.373, min_radius = 1.0, max_radius = 50.0, hy_variable='permeability', hy_function='semi-correlated', hy_params={"alpha":1, "beta":2, "sigma":3})

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
