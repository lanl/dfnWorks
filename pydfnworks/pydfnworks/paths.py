from tempfile import mkstemp
from shutil import move
import os
import subprocess

def valid(name):
    if not (os.path.isfile(os.path.abspath(os.environ[name])) or os.path.isdir(os.path.abspath(os.environ[name]))):
        error_msg = "ERROR: " + name  + " has an invalid path name: " + os.environ[name]
        print error_msg
        exit()

def compile_dfn_exe(directory):

    print("Compiling %s"%directory)
    cwd = os.getcwd()
    os.chdir(directory)
    subprocess.call("make", shell=True)
    os.chdir(cwd)
    print("Complete")

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
    os.environ['PFLOTRAN_EXE']='/Users/jhyman/src/pflotran/src/pflotran/pflotran'
    valid('PFLOTRAN_EXE')

    # Python executable
    os.environ['PYTHON_EXE'] = '/Users/jhyman/anaconda2/bin/python'
    valid('PYTHON_EXE')
    
    # LaGriT executable
    os.environ['LAGRIT_EXE'] = '/Users/jhyman/src/LaGriT/src/lagrit'
    valid('LAGRIT_EXE')

    os.environ['FEHM_EXE'] = '/Users/jhyman/bin/xfehm'
    valid('FEHM_EXE')
    # =================================================== 
    # THESE PATHS ARE AUTOMATICALLY SET. DO NOT CHANGE.
    # ====================================================
   
    # Directories
    os.environ['DFNGEN_EXE']=os.environ['dfnworks_PATH']+'DFNGen/DFNGen'
    if not os.path.isfile(os.environ['DFNGEN_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH']+'DFNGen/')

    os.environ['DFNTRANS_EXE']= os.environ['dfnworks_PATH'] +'ParticleTracking_TDRW/DFNTrans_TDRW'
    if not os.path.isfile(os.environ['DFNTRANS_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH']+'ParticleTracking_TDRW/')
    
    os.environ['CORRECT_UGE_EXE'] = os.environ['dfnworks_PATH']+'C_uge_correct/correct_uge'
    if not os.path.isfile(os.environ['CORRECT_UGE_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH']+'C_uge_correct/')

    os.environ['CORRECT_STOR_EXE'] = os.environ['dfnworks_PATH']+'C_stor_correct/correct_stor'
    if not os.path.isfile(os.environ['CORRECT_STOR_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH']+'C_stor_correct/')

    os.environ['CONNECT_TEST_EXE'] = os.environ['dfnworks_PATH']+'DFN_Mesh_Connectivity_Test/ConnectivityTest'
    if not os.path.isfile(os.environ['CONNECT_TEST_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH']+'DFN_Mesh_Connectivity_Test/')

