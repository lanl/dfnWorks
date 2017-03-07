"""
.. file:: run_dfnworks.py
   :synopsis: run file for dfnworks 
   :version: 1.0
   :maintainer: Jeffrey Hyman, Carl Gable, Nathaniel Knapp
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import os, sys
sys.path.append("/Users/jhyman/Documents/code/dfnworks-main/python_scripts/") 
from time import time
from modules import dfnworks, helper 

def define_paths():
    # Set Environment Variables
    os.environ['PETSC_DIR']='/Users/jhyman/Documents/code/petsc'
    os.environ['PETSC_ARCH']='arch-darwin-c-debug'

    os.environ['PFLOTRAN_DIR']='/Users/jhyman/Documents/code/pflotran-dev/'


    os.environ['DFNWORKS_PATH'] = '/Users/jhyman/Documents/code/dfnworks-main/'
    os.environ['DFNGEN_PATH']=os.environ['DFNWORKS_PATH']+'/DFNGen/DFNC++Version'
    os.environ['DFNTRANS_PATH']= os.environ['DFNWORKS_PATH'] +'ParticleTracking/'

    # Executables	
    os.environ['python_dfn'] = '/Applications/anaconda/bin/python2.7'
    os.environ['lagrit_dfn'] = '/Users/jhyman/Applications/LaGriT/lagrit_macOS12_GCC4.8_o'

    os.environ['connect_test'] = os.environ['DFNWORKS_PATH']+'/DFN_Mesh_Connectivity_Test/ConnectivityTest'
    os.environ['correct_uge_PATH'] = os.environ['DFNWORKS_PATH']+'/C_uge_correct/correct_uge' 
    os.environ['VTK_PATH'] = os.environ['DFNWORKS_PATH'] + '/inp_2_vtk/inp2vtk'


define_paths()
main_time = time()
DFN = dfnworks.create_dfn()
if type(DFN) is ' NoneType':
    print 'ERROR: DFN object not created correctly'
    exit()
# General Work Flow
DFN.dfnGen()
DFN.dfnFlow()
DFN.dfnTrans()

main_elapsed = time() - main_time
timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
print timing
helper.dump_time(DFN._local_jobname, DFN._jobname,main_elapsed) 
#dfn.print_run_time()    
print("*"*80)
print(DFN._jobname+' complete')
print("Thank you for using dfnWorks")
print("*"*80)

