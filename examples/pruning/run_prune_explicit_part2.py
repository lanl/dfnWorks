"""
.. file:: run_dfnworks.py
   :synopsis: run file for dfnworks 
   :version: 1.0
   :maintainer: Jeffrey Hyman, Carl Gable
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""


from pydfnworks import * 

DFN = create_dfn()
DFN.make_working_directory()

# Mesh the network based on the 2 core, assigned by the command line file
DFN.mesh_network(prune=True)

# run flow and transport on the 2-Core DFN
DFN.dfn_flow()
DFN.dfn_trans()

