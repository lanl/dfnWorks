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

DFN.params['domainSize']['value'] = [10.0, 10.0, 20.0]
DFN.params['h']['value'] = 0.1
DFN.params['numOfLayers']['value'] = 2
DFN.params['layers']['value'] = [[-10.0,-2.0],[2.0,10.0]]
DFN.params['domainSizeIncrease']['value'] = [1.0, 1.0, 1.0]
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [0,0,0,0,1,1]

DFN.add_fracture_family(shape = "ell", distribution = "tpl", kappa = 20.0, probability = .25, aspect = 1.0, layer = 1, beta_distribution = 0.0, beta = 0.0, theta = 90.0, phi = 0.0, alpha = 2.6, min_radius = 1.0, max_radius = 10.0, p32 = .65, hy_variable = "transmissivity", hy_function = "correlated", hy_params = {"alpha":6.7*10**-7,"beta":1.4})

DFN.add_fracture_family(shape = "ell", distribution = "tpl", kappa = 20.0, probability = .25, aspect = 1.0, layer = 1, beta_distribution = 0.0, beta = 0.0, theta = 0.0, phi = 0.0, alpha = 2.3, min_radius = 1.0, max_radius = 10.0, p32 = .75, hy_variable = "transmissivity", hy_function = "semi-correlated", hy_params = {"alpha":6.3*10**-7,"beta":0.5,"sigma":1.0})

DFN.add_fracture_family(shape = "ell", distribution = "tpl", kappa = 20.0, probability = .25, aspect = 1.0, layer = 2, beta_distribution = 0.0, beta = 0.0, theta = 90.0, phi = 0.0, alpha = 2.6, min_radius = 1.0, max_radius = 5.0, p32 = 1.5, hy_variable = "transmissivity", hy_function = "constant", hy_params = {"mu":6.3*10**-9})

DFN.add_fracture_family(shape = "ell", distribution = "tpl", kappa = 20.0, probability = .25, aspect = 1.0, layer = 2, beta_distribution = 0.0, beta = 0.0, theta = 0.0, phi = 0.0, alpha = 2.3, min_radius = 1.0, max_radius = 5.0, p32 = 1.55, hy_variable = "transmissivity", hy_function = "log-normal", hy_params = {"mu":6.3*10**-9,"sigma":0.5})

DFN.print_family_information(1)

DFN.make_working_directory(delete=True)

DFN.check_input()

for key in DFN.params.keys():
    print(key, DFN.params[key]['value'])

# define_paths()
DFN.create_network()
# DFN.output_report()
DFN.mesh_network(coarse_factor=10)

# Add transmissivity values to the mesh for visualization
DFN.add_variable_to_mesh("trans","transmissivity.dat","full_mesh.inp")

##dfnFlow()
DFN.dfn_flow()

# dfnTrans
DFN.dfn_trans()

print("*"*80)
print(DFN.jobname+' complete')
print("Thank you for using dfnWorks")
print("*"*80)
