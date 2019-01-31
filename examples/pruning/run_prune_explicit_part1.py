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

DFN.make_working_directory()
DFN.check_input()
DFN.create_network()
DFN.mesh_network(visual_mode=True)

G = DFN.create_graph("fracture", "left", "right")
DFN.plot_graph(G,output_name="full_dfn")
H = nx.k_core(G,2)
DFN.dump_fractures(H,"2_core.dat") 
DFN.plot_graph(H,output_name="dfn_2_core")

main_elapsed = time() - main_time
timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
print("*"*80)
print(DFN.jobname+' complete')
print("Thank you for using dfnWorks")
print("*"*80)
