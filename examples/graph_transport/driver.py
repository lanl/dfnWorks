#"""
#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

src_path = os.getcwd()
jobname =  f"{src_path}/output"

DFN = DFNWORKS(jobname,
               ncpu=8)

DFN.params['domainSize']['value'] = [400, 50, 50]
DFN.params['h']['value'] = 1
DFN.params['domainSizeIncrease']['value'] = [5,5,5]
DFN.params['ignoreBoundaryFaces']['value'] = True 
DFN.params['boundaryFaces']['value'] = [1,1,0,0,0,0]
DFN.params['keepOnlyLargestCluster']['value'] = True
DFN.params['disableFram']['value'] = True
DFN.params['eAngleOption']['value'] = 1

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=10,
                        p32=0.25,
                        aspect=1,
                        theta=0.0,
                        phi=0.0,
                        alpha=1.8,
                        min_radius=10.0,
                        max_radius=20.0, 
                        hy_variable='permeability',
                        hy_function='constant',
                        hy_params={"mu":2e-12})

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=10,
                        p32=0.25,
                        aspect=1,
                        theta=0.0,
                        phi=270.0,
                        alpha=1.8,
                        min_radius=10.0,
                        max_radius=20.0, 
                        hy_variable='permeability',
                        hy_function='constant',
                        hy_params={"mu":2e-12})

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=10,
                        p32=0.25,
                        aspect=1,
                        theta=45.0,
                        phi=0.0,
                        alpha=1.8,
                        min_radius=10.0,
                        max_radius=20.0, 
                        hy_variable='permeability',
                        hy_function='constant',
                        hy_params={"mu":3e-12})


DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.create_network()
# DFN.output_report()
# DFN.mesh_network()

pressure_in = 2*10**6
pressure_out = 10**6
G = DFN.run_graph_flow("left","right",pressure_in,pressure_out)
number_of_particles = 10**4

DFN.run_graph_transport(G,number_of_particles,"graph_partime.dat","graph_frac_sequence.dat")

