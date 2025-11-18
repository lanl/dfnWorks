# Pruning Example Summary
# This example demonstrates the complete workflow of DFN generation, analysis, and pruning using the truncated power law (TPL) fracture size distribution in pydfnworks. It shows how to configure domain parameters, add multiple fracture families, and generate a discrete fracture network (DFN). The script constructs a network graph representation of the DFN, identifies and extracts the hydraulic backbone (i.e., the connected flow network), and then prunes the original DFN to retain only those flow-connected fractures. Finally, it rebuilds and meshes the pruned backbone network for further simulation or visualization.

# Key steps illustrated include:
# 	•	Setting up the DFNWORKS environment and parameters
# 	•	Adding fracture families with TPL size distributions
# 	•	Generating and graphing the DFN
# 	•	Computing and visualizing the flow backbone
# 	•	Saving and reloading the DFN from a pickle file
# 	•	Creating and meshing the pruned DFN for downstream modeling


from pydfnworks import *
import os
import networkx as nx

home = os.getcwd()
jobname = os.getcwd() + "/output_prune"

DFN = DFNWORKS(jobname, ncpu=8)

DFN.params['domainSize']['value'] = [25, 25, 25]
DFN.params['h']['value'] = 0.1
DFN.params['domainSizeIncrease']['value'] = [.5, .5, .5]
DFN.params['keepOnlyLargestCluster']['value'] = True
DFN.params['boundaryFaces']['value'] = [1, 1, 0, 0, 0, 0]

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
                        hy_params={"mu": 2e-6})

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
                        hy_params={"mu": 1e-6})

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.create_network()

# Create a graph based on the DFN
G = DFN.create_graph("fracture", "left", "right")
# Plot the graph based on the DFN
DFN.plot_graph(G, output_name="full_dfn")
# remove dead-end features from network
H = DFN.current_flow_threshold(G, 's', 't', weight = None, thrs = 1e-16)
DFN.dump_fractures(H, "backbone.dat")
DFN.plot_graph(H, output_name="backbone")

DFN.to_pickle()
del DFN

## Create a second DFN object for the backbone
os.chdir(home)
jobname = os.getcwd() + os.sep + "output_backbone"
src_path = os.getcwd() + '/output_prune/'
BACKBONE = DFNWORKS(jobname=jobname, 
                    pickle_file = src_path + 'output_prune.pkl')
BACKBONE.prune_file = src_path + "/backbone.dat"
BACKBONE.path = src_path
BACKBONE.jobname = jobname + os.sep
BACKBONE.local_jobname = "output_backbone" 
BACKBONE.visual_mode = True 
BACKBONE.make_working_directory(delete=True)
BACKBONE.mesh_network()
