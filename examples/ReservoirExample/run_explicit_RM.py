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
import matplotlib.pyplot as plt

define_paths()
main_time = time()
DFN = create_dfn()

# DFNGen

# run DFNGen, where circular hydraulic fractures and rectangular well are defined as deterministic fractures
DFN.make_working_directory()
DFN.check_input()
DFN.create_network()
DFN.mesh_network(visual_mode=False)


# DFNFlow

os.chdir(DFN.jobname)

# call LaGriT to run a script for identifying all the nodes on the well
cmd = 'lagrit  </dfnWorks/work/ReservoirExample/CreateWellZone.lgi '
os.system(cmd)

# run python  script to combine 4 boundary faces nodes into one zone file  -> inflow boundary
# and the well zone file -> outflow boundary 
os.chdir(DFN.jobname)
cmd = 'python  /dfnWorks/work/ReservoirExample/createbound.py'
os.system(cmd)

DFN.lagrit2pflotran()

# create a "well.ex" for assigning pressure boundary conditions to the well 
DFN.zone2ex(zone_file="well.zone",face="none")

DFN.pflotran()
DFN.parse_pflotran_vtk_python()       
DFN.pflotran_cleanup()


# DFNtrans

DFN.dfn_trans()

main_elapsed = time() - main_time
timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
print("*"*80)
print(DFN.jobname+' complete')
print("Thank you for using dfnWorks")
print("*"*80)
