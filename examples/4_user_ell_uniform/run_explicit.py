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
DFN.check_input()
DFN.create_network()
DFN.output_report()
# Uniform mesh resolution
DFN.mesh_network(uniform_mesh=True)

DFN.dfn_flow()
DFN.dfn_trans() 

