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
DFN.create_network()
DFN.mesh_network()

DFN.set_flow_solver("PFLOTRAN")

DFN.map_to_continuum(l=0.1,orl=1)
DFN.upscale(mat_perm=1e-15,mat_por=0.01)

restart_file = "/home/msweeney2796/dfnworks-main/examples/octree_example/dfn_restart.in"
DFN.zone2ex(uge_file='full_mesh.uge',zone_file='all')
DFN.pflotran(restart=True,restart_file=restart_file)

DFN.parse_pflotran_vtk_python(grid_vtk_file='')
DFN.pflotran_cleanup()
DFN.pflotran_cleanup(index_finish=69,filename=restart_file)

main_elapsed = time() - main_time
timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
f = open("time.txt",'w')
f.write("{0}\n".format(main_elapsed))
f.close()
print("*"*80)
print(DFN.jobname+' complete')
print("Thank you for using dfnWorks")
print("*"*80)

