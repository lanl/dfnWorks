#"""
#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os
import networkx as nx 

home = os.getcwd() 
jobname = os.getcwd() + "/output_prune"
dfnflow_file = os.getcwd() + "/dfn_explicit.in"

DFN = DFNWORKS(jobname,dfnFlow_file = dfnflow_file,
               ncpu=8)

DFN.params['domainSize']['value'] = [25, 25, 25]
DFN.params['h']['value'] = 0.1
DFN.params['domainSizeIncrease']['value'] = [.5,.5,.5]
DFN.params['keepOnlyLargestCluster']['value'] = True
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

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.create_network()

# Create a graph based on the DFN
G = DFN.create_graph("fracture", "left", "right")
# Plot the graph based on the DFN
DFN.plot_graph(G,output_name="full_dfn")
# Isolate the 2-Core of the graph
H = DFN.k_shortest_paths_backbone(G,1, 's', 't')
DFN.dump_fractures(H,"backbone.dat")
DFN.plot_graph(H,output_name="backbone")


H = nx.k_core(G,2)
# Dump out fractures in the 2-Core
DFN.dump_fractures(H,"2-core.dat")
# plot the 2 core of the graph
DFN.plot_graph(H,output_name="dfn_2_core")
DFN.to_pickle()

## Create a second DFN object for the backbone 
os.chdir(home)
jobname = os.getcwd() + "/output_backbone/"
src_path = os.getcwd() + '/output_prune/' 
BACKBONE = DFNWORKS( jobname = jobname, 
                    pickle_file = src_path + 'output_prune.pkl')
BACKBONE.prune_file = src_path + "/backbone.dat"
BACKBONE.path = src_path 
BACKBONE.make_working_directory(delete = True)
BACKBONE.mesh_network(prune=True)
BACKBONE.dfn_flow()


os.chdir(home)
jobname = os.getcwd() + "/output_2-core/"
src_path = os.getcwd() + '/output_prune/' 
CORE = DFNWORKS( jobname = jobname, 
                    pickle_file = src_path + 'output_prune.pkl')
CORE.prune_file = src_path + "/2-core.dat"
CORE.path = src_path 
CORE.make_working_directory(delete = True)
CORE.mesh_network(prune=True)
CORE.dfn_flow()



