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

DFN.params['domainSize']['value'] = [25, 25, 25]
DFN.params['h']['value'] = 0.1
DFN.params['domainSizeIncrease']['value'] = [.5,.5,.5]
DFN.params['keepOnlyLargestCluster']['value'] = True
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [1,1,0,0,0,0]


DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=0.1,
                        aspect=1,
                        beta_distribution=0,
                        beta=0.0,
                        theta=0.0,
                        phi=0.0,
                        alpha=2.1,
                        min_radius=1.0,
                        max_radius=10.0,
                        p32=0.5,
                        hy_variable='aperture',
                        hy_function='constant',
                        hy_params={"mu":2e-6})

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=0.1,
                        aspect=1,
                        beta_distribution=0,
                        beta=0.0,
                        theta=0.0,
                        phi=0.0,
                        alpha=2.1,
                        min_radius=1.0,
                        max_radius=10.0,
                        p32=0.5,
                        hy_variable='aperture',
                        hy_function='constant',
                        hy_params={"mu":1e-6})

DFN.print_family_information(1)

DFN.make_working_directory(delete=True)

DFN.check_input()

for key in DFN.params.keys():
    print(key, DFN.params[key]['value'])

# define_paths()
DFN.create_network()
# DFN.output_report()
DFN.mesh_network()

# Create a graph based on the DFN
G = DFN.create_graph("fracture", "left", "right")
# Plot the graph based on the DFN
DFN.plot_graph(G,output_name="full_dfn")
# Isolate the 2-Core of the graph
H = nx.k_core(G,2)
# Dump out fractures in the 2-Core
DFN.dump_fractures(H,"2_core.dat")
# plot the 2 core of the graph
DFN.plot_graph(H,output_name="dfn_2_core")
