from tempfile import mkstemp
from shutil import move
import os
import subprocess

def valid(name):
    if not (os.path.isfile(os.path.abspath(os.environ[name])) or os.path.isdir(os.path.abspath(os.environ[name]))):
        error_msg = "ERROR: " + name  + " has an invalid path name: " + os.environ[name]
        print error_msg
        exit()

def define_paths():

    # ================================================
    # THESE PATHS MUST BE SET BY THE USER.
    # ================================================
    
    # the dfnworks-main  repository 
    os.environ['dfnworks_PATH'] = '/Users/jhyman/src/dfnworks-main/'
    valid('dfnworks_PATH')
    if not (os.path.isdir(os.path.abspath(os.environ['dfnworks_PATH'] + 'tests/'))):
        print "INVALID VERSION OF dfnworks - does not have tests folder of official release 2.0"
        exit()

    # PETSC paths
    os.environ['PETSC_DIR']='/Users/jhyman/src/petsc/'
    os.environ['PETSC_ARCH']='/arch-darwin-c-debug/'
    valid('PETSC_DIR')
#    valid('PETSC_ARCH')

    # PFLOTRAN path
    os.environ['PFLOTRAN_DIR']='/Users/jhyman/src/pflotran'
    valid('PFLOTRAN_DIR')

    # PFLOTRAN path
    os.environ['FEHM_DIR']='/Users/jhyman/src/fehm'
    valid('FEHM_DIR')
    
    # Python executable
    os.environ['python_dfn'] = '/Users/jhyman/anaconda2/bin/python'
    valid('python_dfn')
    
    # LaGriT executable
    os.environ['lagrit_dfn'] = '/Users/jhyman/bin//lagrit'
    valid('lagrit_dfn')

    # =================================================== 
    # THESE PATHS ARE AUTOMATICALLY SET. DO NOT CHANGE.
    # ====================================================
   
    # Directories
    os.environ['DFNGEN_PATH']=os.environ['dfnworks_PATH']+'DFNGen/'
    os.environ['DFNTRANS_PATH']= os.environ['dfnworks_PATH'] +'ParticleTracking/'
    os.environ['PYdfnworks_PATH'] = os.environ['dfnworks_PATH'] + 'pydfnworks/'
    os.environ['connect_test'] = os.environ['dfnworks_PATH']+'DFN_Mesh_Connectivity_Test/'
    os.environ['correct_uge_PATH'] = os.environ['dfnworks_PATH']+'C_uge_correct/' 
    os.environ['VTK_PATH'] = os.environ['dfnworks_PATH'] + 'inp_2_vtk/'

