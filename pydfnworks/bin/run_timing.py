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
DFN = dfnworks.create_dfn()


DFN.make_working_directory()

DFN.check_input()
tic=time()
DFN.create_network()
toc=time()
dump_time(DFN._local_jobname,'generation',toc-tic) 


##DFN.output_report()

tic=time()
DFN.mesh_network()
toc=time()
dump_time(DFN._local_jobname,'meshing',toc-tic) 

exit()
tic=time()
DFN.lagrit2pflotran()
toc=time()
dump_time(DFN._local_jobname,'conversion',toc-tic) 

tic=time()
DFN.pflotran()
toc=time()
dump_time(DFN._local_jobname,'pflotran',toc-tic) 

DFN.parse_pflotran_vtk_python()       
DFN.pflotran_cleanup()

DFN.copy_dfn_trans_files()

tic=time()
DFN.run_dfn_trans()
toc=time()
dump_time(DFN._local_jobname,'transport',toc-tic) 

main_elapsed = time() - main_time
timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
print("*"*80)
print(DFN._jobname+' complete')
print("Thank you for using dfnWorks")
print("*"*80)

