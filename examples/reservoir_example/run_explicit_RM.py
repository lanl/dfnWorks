"""
.. file:: run_dfnworks.py
   :synopsis: run file for dfnworks 
   :version: 1.0
   :maintainer: Jeffrey Hyman, Carl Gable
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""
import os 
from pydfnworks import * 
import subprocess

DFN = create_dfn()
# DFNGen

# run DFNGen, where circular hydraulic fractures and rectangular well are defined as deterministic fractures
DFN.make_working_directory()
DFN.check_input()
DFN.create_network()
DFN.mesh_network()

# call LaGriT to run a script for identifying all the nodes on the well
cmd = os.environ['LAGRIT_EXE'] + ' < DUMMY/dfnworks-main/examples/reservoir_example/CreateWellZone.lgi '
subprocess.call(cmd,shell=True)

# run python  script to combine 4 boundary faces nodes into one zone file  -> inflow boundary
# and the well zone file -> outflow boundary 

cmd = 'python DUMMY/dfnworks-main/examples/reservoir_example/create_boundaries.py'
subprocess.call(cmd,shell=True)

DFN.lagrit2pflotran()
# create a "well.ex" for assigning pressure boundary conditions to the well 
DFN.zone2ex(zone_file="well.zone",face="none")

DFN.pflotran()
DFN.parse_pflotran_vtk_python()       
DFN.pflotran_cleanup()

# DFNtrans
DFN.dfn_trans()
