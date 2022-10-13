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

DFN.params['domainSize']['value'] = [15, 15, 15]
DFN.params['h']['value'] = 0.1
DFN.params['stopCondition']['value'] = 0
DFN.params['nPoly']['value'] = 500
DFN.params['domainSizeIncrease']['value'] = [.5,.5,.5]
DFN.params['keepOnlyLargestCluster']['value'] = True
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [1,1,0,0,0,0]
DFN.params['keepOnlyLargestCluster']['value'] = True

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=0.1,
                        probability=.5,
                        aspect=1,
                        beta_distribution=0,
                        beta=0.0,
                        theta=0.0,
                        phi=0.0,
                        alpha=2.6,
                        min_radius=1.0,
                        max_radius=5.0, 
                        hy_variable='permeability',
                        hy_function='constant',
                        hy_params={"mu":1e-12})

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=0.1,
                        probability=.5,
                        aspect=1,
                        beta_distribution=0,
                        beta=0.0,
                        theta=0.0,
                        phi=0.0,
                        alpha=2.6,
                        min_radius=1.0,
                        max_radius=5.0,
                        hy_variable='permeability',
                        hy_function='constant',
                        hy_params={"mu":1e-12})

DFN.print_family_information(1)

DFN.make_working_directory(delete=True)

DFN.check_input()

#for key in DFN.params.keys():
#    print(key, DFN.params[key]['value'])

# define_paths()
DFN.create_network()
# DFN.output_report()
DFN.mesh_network(coarse_factor=10)

pressure_in = 2*10**6
pressure_out = 10**6
G = DFN.run_graph_flow("left","right",pressure_in,pressure_out)

number_of_particles = 10**4

DFN.run_graph_transport(G,number_of_particles,"graph_partime.dat","graph_frac_sequence.dat")

