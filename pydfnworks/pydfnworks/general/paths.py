from shutil import move
import os
import sys
import subprocess
import json

DFNPARAMS = '~/.dfnworksrc'
DFNPARAMS = os.path.expanduser(DFNPARAMS)


def valid(name, path, path_type):
    """" Check that path is valid for a executable
    Parameters
    ----------
        name : string
            Path to file or executable
        path_type : string
            Path type can either be an executable or a directory

    Returns
    -------
        0 if paths are valid

    Notes
    -----
        If file is not found, file is not an executable, or directory does not exists then program exits
    """

    if path_type == "executable":
        if not os.path.isfile(path):
            error = f"Error checking {name}\n{path} is not a valid path to a file name.\nPlease check the path in either pydfnworks/general/paths.py or .dfnworksrc.\nExiting\n"
            sys.stderr.write(error)
            sys.exit(1)
        else:
            if not os.access(path, os.X_OK):
                error = f"Error checking {name}\n{path} is not an executable.\nPlease check file permissions.\nExiting\n"
                sys.stderr.write(error)
                sys.exit(1)

    if path_type == "directory":
        if not os.path.isdir(path):
            error = f"Error checking {name}\n{path} is not a directory.\nPlease check the path in either pydfnworks/general/paths.py or .dfnworksrc.\nExiting\n"
            sys.stderr.write(error)
            sys.exit(1)


def compile_dfn_exe(path):
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

    print(f"Compiling {path}")
    cwd = os.getcwd()
    os.chdir(path)
    subprocess.call("make", shell=True)
    os.chdir(cwd)
    print("Complete")


def print_paths(self):
    """ Print enviromental variable paths to screen 
    
    Parameters
    -------------
        None

    Returns
    -------------
        None

    Notes
    -------------
        None

    """
    print("\ndfnWorks paths:")
    print("---------------")
    print(f"* dfnworks_PATH: {os.environ['dfnworks_PATH']}")
    print(f"* LAGRIT_EXE: {os.environ['LAGRIT_EXE']}")
    print(f"* PETSC_DIR: {os.environ['PETSC_DIR']}")
    print(f"* PETSC_ARCH: {os.environ['PETSC_ARCH']}")
    print(f"* PFLOTRAN_EXE: {os.environ['PFLOTRAN_EXE']}")
    print(f"* FEHM_EXE: {os.environ['FEHM_EXE']}\n")


def define_paths(self):
    """ Defines environmental variables for use in dfnWorks. The user must change these to match their workspace.
    Parameters
    ----------
        None
    Returns
    -------
        None
    Notes
    -----
        Environmental variables are set to executables
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
            'dfnworks_PATH': '/Users/jhyman/src/dfnworks-jdhdev/',
            'PETSC_DIR': None,
            'PETSC_ARCH': None,
            'PFLOTRAN_EXE': None,
            'LAGRIT_EXE': None,
            'FEHM_EXE': None
        }

    # Or, read the variables from the environment
    for envVar in env_paths:
        if env_paths[envVar] == '':
            env_paths[envVar] = os.environ.get(envVar, '')

    # the dfnworks  repository
    if env_paths['dfnworks_PATH']:
        os.environ['dfnworks_PATH'] = env_paths['dfnworks_PATH']
        valid("dfnworks_PATH", os.environ['dfnworks_PATH'], "directory")
    else:
        error = f"Error. dfnWorks path not provided. Must be set to the github cloned repo.\nExiting\n"
        sys.stderr.write(error)
        sys.exit(1)

    # PETSC paths
    if env_paths['PETSC_DIR']:
        os.environ['PETSC_DIR'] = env_paths['PETSC_DIR']
        os.environ['PETSC_ARCH'] = env_paths['PETSC_ARCH']
        valid('PETSC_DIR', os.environ['PETSC_DIR'], "directory")
        valid('PETSC_ARCH',
              os.environ['PETSC_DIR'] + os.sep + os.environ['PETSC_ARCH'],
              "directory")
    else:
        print("--> Warning. No PETSC Directory provided.")

    # PFLOTRAN path
    if env_paths['PETSC_DIR']:
        os.environ['PFLOTRAN_EXE'] = env_paths['PFLOTRAN_EXE']
        valid('PFLOTRAN_EXE', os.environ['PFLOTRAN_EXE'], "executable")
    else:
        print("--> Warning. No PFLOTRAN path provided.")

    if env_paths['FEHM_EXE']:
        os.environ['FEHM_EXE'] = env_paths['FEHM_EXE']
        valid('FEHM_EXE', os.environ['FEHM_EXE'], "executable")
    else:
        print("Warning. No FEHM path provided.")

    # LaGriT executable
    if env_paths['LAGRIT_EXE']:
        os.environ['LAGRIT_EXE'] = env_paths['LAGRIT_EXE']
        valid('LAGRIT_EXE', os.environ['LAGRIT_EXE'], "executable")
    else:
        print("--> Warning. No LaGriT path provided.")

    # ===================================================
    # THESE PATHS ARE AUTOMATICALLY SET. DO NOT CHANGE.
    # ====================================================

    # Directories
    os.environ['DFNGEN_EXE'] = os.environ['dfnworks_PATH'] + 'DFNGen/DFNGen'
    if not os.path.isfile(os.environ['DFNGEN_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH'] + 'DFNGen/')
        valid('DFNGen', os.environ['DFNGEN_EXE'], "executable")

    os.environ[
        'DFNTRANS_EXE'] = os.environ['dfnworks_PATH'] + 'DFNTrans/DFNTrans'
    if not os.path.isfile(os.environ['DFNTRANS_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH'] + 'DFNTrans/')
    valid('DFNTrans', os.environ['DFNTRANS_EXE'], "executable")

    os.environ['CORRECT_UGE_EXE'] = os.environ[
        'dfnworks_PATH'] + 'C_uge_correct/correct_uge'
    if not os.path.isfile(os.environ['CORRECT_UGE_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH'] + 'C_uge_correct/')
    valid('CORRECT_UGE_EXE', os.environ['CORRECT_UGE_EXE'], "executable")

    os.environ['CORRECT_STOR_EXE'] = os.environ[
        'dfnworks_PATH'] + 'C_stor_correct/correct_stor'
    if not os.path.isfile(os.environ['CORRECT_STOR_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH'] + 'C_stor_correct/')
    valid('CORRECT_STOR_EXE', os.environ['CORRECT_STOR_EXE'], "executable")

    os.environ['CONNECT_TEST_EXE'] = os.environ[
        'dfnworks_PATH'] + 'DFN_Mesh_Connectivity_Test/ConnectivityTest'
    if not os.path.isfile(os.environ['CONNECT_TEST_EXE']):
        compile_dfn_exe(os.environ['dfnworks_PATH'] +
                        'DFN_Mesh_Connectivity_Test/')
    valid('CONNECT_TEST_EXE', os.environ['CONNECT_TEST_EXE'], "executable")
