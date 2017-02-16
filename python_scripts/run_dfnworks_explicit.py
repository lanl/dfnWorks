"""
.. file:: run_dfnworks.py
   :synopsis: run file for dfnworks 
   :version: 1.0
   :maintainer: Jeffrey Hyman, Carl Gable, Nathaniel Knapp
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import os
import sys
from time import time
sys.path.append("/home/nknapp/dfnworks-main/python_scripts/") 
from modules import dfnworks, helper

def define_paths():
	# Set Environment Variables
	# PETSC and PFLOTRAN PATHS
    os.environ['PETSC_DIR']='/home/satkarra/src/petsc-git/petsc-3.7-release'
	os.environ['PETSC_ARCH']='/Ubuntu-14.04-nodebug'
	os.environ['PFLOTRAN_DIR']='/home/satkarra/src/pflotran-dev-pt-testing'

    # set to your python (Anacdona Python 2.7.12)	
	os.environ['python_dfn'] = '/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/2.4.1/bin/python'
    # set path to lagrit executable
	os.environ['lagrit_dfn'] = '/n/swdev/mesh_tools/lagrit/install-Ubuntu-14.04-x86_64/3.2.0/release/gcc-4.8.4/bin/lagrit'

    # Set this to the git repo
    os.environ['DFNWORKS_PATH'] = '/home/nknapp/dfnworks-main/'
    # Do not touch these	
	os.environ['DFNTRANS_PATH']= os.environ['DFNWORKS_PATH'] +'ParticleTracking/'
	os.environ['DFNGEN_PATH']=os.environ['DFNWORKS_PATH']+'DFNGen/DFNC++Version'
	os.environ['connect_test'] = os.environ['DFNWORKS_PATH']+'/DFN_Mesh_Connectivity_Test/ConnectivityTest'
	os.environ['correct_uge_PATH'] = os.environ['DFNWORKS_PATH']+'/C_uge_correct/correct_uge' 

define_paths()

main_time = time()

DFN = dfnworks.create_dfn()

DFN.make_working_directory()
DFN.check_input()
DFN.create_network()
DFN.output_report()
DFN.mesh_network()

DFN.lagrit2pflotran()
DFN.pflotran()
DFN.parse_pflotran_vtk()       
DFN.pflotran_cleanup()

DFN.copy_dfnTrans_files()
DFN.run_dfnTrans()

main_elapsed = time() - main_time
timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
print("*"*80)
print(DFN._jobname+' complete')
print("Thank you for using dfnWorks")
print("*"*80)

