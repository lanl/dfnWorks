"""
.. file:: run_regions.py
   :synopsis: python run file for regions example 
   :version: 1.0
   :maintainer: Jeffrey Hyman
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

from pydfnworks import * 

DFN = create_dfn()
DFN.make_working_directory()
### dfnGen
DFN.check_input()
DFN.create_network()
DFN.output_report()
# make full mesh for flow and transport simulations
DFN.mesh_network()

##dfnFlow()
DFN.lagrit2pflotran()
DFN.pflotran()
DFN.parse_pflotran_vtk_python()       
DFN.pflotran_cleanup()

# dfnTrans
DFN.copy_dfn_trans_files()
DFN.check_dfn_trans_run_files()
DFN.run_dfn_trans()
