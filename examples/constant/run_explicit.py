"""
.. file:: run_explicit.py
   :synopsis: run file for dfnWorks 
   :version: 1.0
   :maintainer: Jeffrey Hyman, Carl Gable
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

from pydfnworks import * 
import os

define_paths()
main_time = time()
DFN = create_dfn()

DFN.make_working_directory()

## dfnGen
DFN.check_input()
DFN.create_network()
DFN.output_report()
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

