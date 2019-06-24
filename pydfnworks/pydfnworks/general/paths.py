from tempfile import mkstemp
from shutil import move
import os
import sys
import subprocess
import json

DFNPARAMS = '~/.dfnworksrc'
DFNPARAMS = os.path.expanduser(DFNPARAMS)


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
    if not (os.path.isfile(os.path.abspath(os.environ[name]))
            or os.path.isdir(os.path.abspath(os.environ[name]))):
        error = "ERROR: " + name + " has an invalid path name: " + os.environ[
            name]
        sys.stderr.write(error)
        sys.exit(1)


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

    print("Compiling %s" % directory)
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

    # Either write paths to ~/.dfnworksrc in a JSON format...
    if os.path.isfile(DFNPARAMS):
        with open(DFNPARAMS, 'r') as f:
            env_paths = json.load(f)
    # Or, change the paths here
    else:
        env_paths = {
            'dfnworks_PATH': '',
            'PETSC_DIR': '',
            'PETSC_ARCH': '',
            'PFLOTRAN_EXE': '',
            'PYTHON_EXE': '',
            'LAGRIT_EXE': '',
            'FEHM_EXE': ''
        }

    # the dfnworks-main  repository
    os.environ['dfnworks_PATH'] = env_paths['dfnworks_PATH']
    valid('dfnworks_PATH')

    # PETSC paths
    os.environ['PETSC_DIR'] = env_paths['PETSC_DIR']
    os.environ['PETSC_ARCH'] = env_paths['PETSC_ARCH']
    valid('PETSC_DIR')
    #   valid('PETSC_ARCH')

    # PFLOTRAN path
    os.environ['PFLOTRAN_EXE'] = env_paths['PFLOTRAN_EXE']
    valid('PFLOTRAN_EXE')

    # Python executable
    os.environ['PYTHON_EXE'] = env_paths['PYTHON_EXE']
    valid('PYTHON_EXE')

    # LaGriT executable
    os.environ['LAGRIT_EXE'] = env_paths['LAGRIT_EXE']
    valid('LAGRIT_EXE')

    os.environ['FEHM_EXE'] = env_paths['FEHM_EXE']
    valid('FEHM_EXE')

    # ===================================================
    # THESE PATHS ARE AUTOMATICALLY SET. DO NOT CHANGE.
    # ====================================================

    # Directories
    os.environ['DFNGEN_EXE'] = os.environ['dfnworks_PATH'] + 'DFNGen/DFNGen'
    if not os.path.isfile(os.environ['DFNGEN_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH'] + 'DFNGen/')

    os.environ[
        'DFNTRANS_EXE'] = os.environ['dfnworks_PATH'] + 'DFNTrans/DFNTrans'
    if not os.path.isfile(os.environ['DFNTRANS_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH'] + 'DFNTrans')

    os.environ['CORRECT_UGE_EXE'] = os.environ[
        'dfnworks_PATH'] + 'C_uge_correct/correct_uge'
    if not os.path.isfile(os.environ['CORRECT_UGE_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH'] + 'C_uge_correct/')

    os.environ['CORRECT_STOR_EXE'] = os.environ[
        'dfnworks_PATH'] + 'C_stor_correct/correct_stor'
    if not os.path.isfile(os.environ['CORRECT_STOR_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH'] + 'C_stor_correct/')

    os.environ['CONNECT_TEST_EXE'] = os.environ[
        'dfnworks_PATH'] + 'DFN_Mesh_Connectivity_Test/ConnectivityTest'
    if not os.path.isfile(os.environ['CONNECT_TEST_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH'] +
                        'DFN_Mesh_Connectivity_Test/')
