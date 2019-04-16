"""
.. file:: run_dfnworks.py
   :synopsis: run file for dfnworks 
   :version: 1.0
   :maintainer: Jeffrey Hyman, Carl Gable, Nathaniel Knapp
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import os, sys
from time import time
from pydfnworks import * 
import networkx as nx 

define_paths()
main_time = time()
DFN = create_dfn()

# Create network but don't mesh it
DFN.make_working_directory()
DFN.check_input()
DFN.create_network()
DFN.mesh_network(visual_mode=True)

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

main_elapsed = time() - main_time
timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
print("*"*80)
print(DFN.jobname+' complete')
print("Thank you for using dfnWorks")
print("*"*80)
