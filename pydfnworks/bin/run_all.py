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

DFN.make_working_directory()
DFN.check_input() 

tic = time()
DFN.create_network()
toc = time()
dump_time(DFN.local_jobname, 'generation', toc-tic)
DFN.output_report()

tic = time()
DFN.mesh_network()
toc = time()
dump_time(DFN.local_jobname, 'meshing', toc-tic)
os.chdir(DFN.jobname)

tic = time()
DFN.dfn_flow()
toc  = time()
dump_time(DFN.local_jobname, 'flow', toc-tic)

tic = time()
DFN.dfn_trans() # for parallel, comment this section
toc = time()
dump_time(DFN.local_jobname, 'trans', toc-tic)


#os.chdir(DFN.jobname)
##DFN.lagrit2pflotran()
#DFN.pflotran()
##DFN.parse_pflotran_vtk_python()       
#DFN.pflotran_cleanup()

#DFN.copy_dfn_trans_files()
#DFN.run_dfn_trans()

main_elapsed = time() - main_time
timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
print("*"*80)
print(DFN.jobname+' complete')
print("Thank you for using dfnWorks")
print("*"*80)
