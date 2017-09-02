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
import subprocess

define_paths()
main_time = time()
DFN = create_dfn()
#
DFN.make_working_directory()
##DFN.check_input()
##DFN.create_network()
#
##DFN.output_report()
##DFN.mesh_network()

os.chdir(DFN.jobname)
DFN.create_mesh_links(path='../')
keep_file_path="../10_shortest_paths_bb.txt"
DFN.mesh_network(prune=True, keep_file=keep_file_path)
DFN.clean_up_files_after_prune(path='../', keep_file=keep_file_path)

DFN.dfn_flow()

#DFN.dfn_trans()

#DFN.lagrit2pflotran()
#DFN.pflotran()
#DFN.parse_pflotran_vtk_python()       
#os.chdir(DFN.jobname)
#DFN.pflotran_cleanup()

#DFN.copy_dfn_trans_files()
#DFN.run_dfn_trans()

main_elapsed = time() - main_time
timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
print("*"*80)
print(DFN.jobname+' complete')
print("Thank you for using dfnWorks")
print("*"*80)
