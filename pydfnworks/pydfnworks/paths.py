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
    os.environ['DFNWORKS_PATH'] = 'DUMMY/dfnworks-main/'
    valid('DFNWORKS_PATH')
    if not (os.path.isdir(os.path.abspath(os.environ['DFNWORKS_PATH'] + 'tests/'))):
        print "INVALID VERSION OF DFNWORKS - does not have tests folder of official release 2.0"
        exit()

    # PETSC paths
    os.environ['PETSC_DIR']='/home/satkarra/src/petsc-git/petsc-3.7-release'
    os.environ['PETSC_ARCH']='/Ubuntu-14.04-nodebug'
    valid('PETSC_DIR')
#    valid('PETSC_ARCH')

    # PFLOTRAN path
    os.environ['PFLOTRAN_DIR']='/home/satkarra/src/pflotran-dev-pt-testing'
    valid('PFLOTRAN_DIR')

    # Python executable
    os.environ['python_dfn'] = '/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/2.4.1/bin/python'
    valid('python_dfn')
    
    # LaGriT executable
#    os.environ['lagrit_dfn'] = '/n/swqa/LAGRIT/lagrit.lanl.gov/downloads/lagrit_ulin3.2' 
    os.environ['lagrit_dfn'] = '/n/swdev/mesh_tools/lagrit/install-Ubuntu-14.04-x86_64/3.2.0/dev/gcc-4.8.4/lagrit'
    valid('lagrit_dfn')

    # =================================================== 
    # THESE PATHS ARE AUTOMATICALLY SET. DO NOT CHANGE.
    # ====================================================
   
    # Directories
    os.environ['DFNGEN_PATH']=os.environ['DFNWORKS_PATH']+'DFNGen/'
    os.environ['DFNTRANS_PATH']= os.environ['DFNWORKS_PATH'] +'ParticleTracking/'
    os.environ['PYDFNWORKS_PATH'] = os.environ['DFNWORKS_PATH'] + 'pydfnworks/'
    os.environ['connect_test'] = os.environ['DFNWORKS_PATH']+'DFN_Mesh_Connectivity_Test/'
    os.environ['correct_uge_PATH'] = os.environ['DFNWORKS_PATH']+'C_uge_correct/' 
    os.environ['VTK_PATH'] = os.environ['DFNWORKS_PATH'] + 'inp_2_vtk/'

