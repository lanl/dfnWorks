from tempfile import mkstemp
from shutil import move
import os
import subprocess

def valid(name):
    """" Check that path is valid for a executable

    Parameters
    ----------
        name : string
            Path to file or executable

    Returns
    -------
        None

    Notes
    -----
        If file is not found, program exits

"""
    if not (os.path.isfile(os.path.abspath(os.environ[name])) or os.path.isdir(os.path.abspath(os.environ[name]))):
        error_msg = "ERROR: " + name  + " has an invalid path name: " + os.environ[name]
        print error_msg
        exit()

def compile_dfn_exe(directory):
    """Compile executables used in the DFN workflow including: DFNGen, DFNTrans, correct_uge, correct_stor, mesh_checking. The executables LaGriT, PFLOTRAN, and FEHM are not compiled in this function

    Parameters
    ----------
        directory : string
            Path to dfnWorks executable 

    Returns
    -------
        None
    
    Notes
    -----
        This function is only called if an executable is not found. 

"""


    print("Compiling %s"%directory)
    cwd = os.getcwd()
    os.chdir(directory)
    subprocess.call("make", shell=True)
    os.chdir(cwd)
    print("Complete")

def define_paths():
    """Defines enviromental variables for use in dfnWorks. The user must change these to match their workspace.

    Parameters
    ----------
        None

    Returns
    -------
        None

    Notes
    -----
        Enviromental variables are set to executables


"""



    # ================================================
    # THESE PATHS MUST BE SET BY THE USER.
    # ================================================
    
    # the dfnworks-main  repository 
    os.environ['dfnworks_PATH'] = 'DUMMY/dfnworks-main/'
    valid('dfnworks_PATH')
    if not (os.path.isdir(os.path.abspath(os.environ['dfnworks_PATH'] + 'tests/'))):
        print "INVALID VERSION OF dfnworks - does not have tests folder of official release 2.0"
        exit()

    # PETSC paths
    os.environ['PETSC_DIR']='/home/satkarra/src/petsc-3.10.2'
    os.environ['PETSC_ARCH']='/Ubuntu-18.04-nodebug/'
    valid('PETSC_DIR')
#    valid('PETSC_ARCH')

    # PFLOTRAN path
    os.environ['PFLOTRAN_EXE']='/home/satkarra/src/pflotran-petsc.3.10.2/src/pflotran/pflotran'
    valid('PFLOTRAN_EXE')

    # Python executable
    os.environ['PYTHON_EXE'] = '/n/swdev/packages/Ubuntu-16.04-x86_64/anaconda-python/4.4.0/bin/python'
    valid('PYTHON_EXE')
    
    # LaGriT executable
    os.environ['LAGRIT_EXE'] = '/n/swdev/mesh_tools/lagrit/install-Ubuntu-16.04-x86_64-gcc5.4.0/bin/lagrit'
    valid('LAGRIT_EXE')

    #os.environ['FEHM_EXE'] = 'home//jhyman/bin/xfehm'
    #valid('FEHM_EXE')
    # =================================================== 
    # THESE PATHS ARE AUTOMATICALLY SET. DO NOT CHANGE.
    # ====================================================
   
    # Directories
    os.environ['DFNGEN_EXE']=os.environ['dfnworks_PATH']+'DFNGen/DFNGen'
    if not os.path.isfile(os.environ['DFNGEN_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH']+'DFNGen/')

    os.environ['DFNTRANS_EXE']= os.environ['dfnworks_PATH'] +'DFNTrans/DFNTrans'
    if not os.path.isfile(os.environ['DFNTRANS_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH']+'DFNTrans')
    
    os.environ['CORRECT_UGE_EXE'] = os.environ['dfnworks_PATH']+'C_uge_correct/correct_uge'
    if not os.path.isfile(os.environ['CORRECT_UGE_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH']+'C_uge_correct/')

    os.environ['CORRECT_STOR_EXE'] = os.environ['dfnworks_PATH']+'C_stor_correct/correct_stor'
    if not os.path.isfile(os.environ['CORRECT_STOR_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH']+'C_stor_correct/')

    os.environ['CONNECT_TEST_EXE'] = os.environ['dfnworks_PATH']+'DFN_Mesh_Connectivity_Test/ConnectivityTest'
    if not os.path.isfile(os.environ['CONNECT_TEST_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH']+'DFN_Mesh_Connectivity_Test/')

