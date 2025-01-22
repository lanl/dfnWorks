from shutil import move
import os
import sys
import json

DFNPARAMS = '~/.dfnworksrc'
DFNPARAMS = os.path.expanduser(DFNPARAMS)


def valid(self, name, path, path_type):
    """" Check that path is valid for a executable
    Parameters
    ----------
        self : object
            DFN Class

        name : string
            Path to file or executable
        
        path : string
            path to executable

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
            self.print_log(error,  'critical')
            # sys.stderr.write(error)
            sys.exit(1)
        else:
            if not os.access(path, os.X_OK):
                error = f"Error checking {name}\n{path} is not an executable.\nPlease check file permissions.\nExiting\n"
                self.print_log(error,  'critical')
                sys.stderr.write(error)
                sys.exit(1)

    if path_type == "directory":
        if not os.path.isdir(path):
            error = f"Error checking {name}\n{path} is not a directory.\nPlease check the path in either pydfnworks/general/paths.py or .dfnworksrc.\nExiting\n"
            self.print_log(error,  'critical')
            sys.stderr.write(error)
            sys.exit(1)


def compile_dfn_exe(self,path):
    """Compile executables used in the DFN workflow including: DFNGen, DFNTrans, correct_uge, correct_stor, mesh_checking. The executables LaGriT, PFLOTRAN, and FEHM are not compiled in this function
    Parameters
    ----------
        self : object
            DFN Class

        directory : string
        
        Path : string
            path to dfnWorks executable 
    Returns
    -------
        None
    
    Notes
    -----
        This function is only called if an executable is not found. 
"""

    self.print_log(f"Compiling {path}" )
    cwd = os.getcwd()
    os.chdir(path)
    self.call_executable("make")
    os.chdir(cwd)
    self.print_log("Complete" )


def print_paths(self):
    """ Print enviromental variable paths to screen 
    
    Parameters
    -------------
        self : object
            DFN Class

    Returns
    -------------
        None

    Notes
    -------------
        None

    """

    self.print_log("dfnWorks paths:")
    self.print_log("---------------")
    self.print_log(f"* dfnworks_PATH: {os.environ['dfnworks_PATH']}")
    self.print_log(f"* LAGRIT_EXE: {os.environ['LAGRIT_EXE']}")
    self.print_log(f"* PETSC_DIR: {os.environ['PETSC_DIR']}")
    self.print_log(f"* PETSC_ARCH: {os.environ['PETSC_ARCH']}")
    self.print_log(f"* PFLOTRAN_EXE: {os.environ['PFLOTRAN_EXE']}")
    self.print_log(f"* FEHM_EXE: {os.environ['FEHM_EXE']}\n")


def define_paths(self):
    """ Defines environmental variables for use in dfnWorks. The user must change these to match their workspace.
    
    Parameters
    ----------
        self : object
            DFN Class
    
    Returns
    -------
        None
    
    Notes
    -----
        Environmental variables are set to executables
    """
    docker = True
    # ================================================
    # THESE PATHS MUST BE SET BY THE USER.
    # ================================================
    self.print_log("--> Loading and checking dfnWorks dependency paths" )
    if not docker:
    # Either write paths to ~/.dfnworksrc in a JSON format...
        if os.path.isfile(DFNPARAMS):
            with open(DFNPARAMS, 'r') as f:
                env_paths = json.load(f)
        # Or, change the paths here
        else:
            env_paths = {
                'dfnworks_PATH': None, 
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
            self.valid("dfnworks_PATH", os.environ['dfnworks_PATH'], "directory")
        else:
            error = f"Error. dfnWorks path not provided. Must be set to the github cloned repo.\nExiting\n"
            self.print_log(error,  'critical')
        # PETSC paths
        if env_paths['PETSC_DIR']:
            os.environ['PETSC_DIR'] = env_paths['PETSC_DIR']
            os.environ['PETSC_ARCH'] = env_paths['PETSC_ARCH']
            self.valid('PETSC_DIR', os.environ['PETSC_DIR'], "directory")
            self.valid('PETSC_ARCH',
                os.environ['PETSC_DIR'] + os.sep + os.environ['PETSC_ARCH'],
                "directory")
        else:
            self.print_log("--> Warning. No PETSC Directory provided.",  'warning')

        # PFLOTRAN path
        if env_paths['PETSC_DIR']:
            os.environ['PFLOTRAN_EXE'] = env_paths['PFLOTRAN_EXE']
            self.valid('PFLOTRAN_EXE', os.environ['PFLOTRAN_EXE'], "executable")
        else:
            self.print_log("--> Warning. No PFLOTRAN path provided.",  'warning')

        if env_paths['FEHM_EXE']:
            os.environ['FEHM_EXE'] = env_paths['FEHM_EXE']
            self.valid('FEHM_EXE', os.environ['FEHM_EXE'], "executable")
        else:
            self.print_log("Warning. No FEHM path provided.",  'warning')

        # LaGriT executable
        if env_paths['LAGRIT_EXE']:
            os.environ['LAGRIT_EXE'] = env_paths['LAGRIT_EXE']
            self.valid('LAGRIT_EXE', os.environ['LAGRIT_EXE'], "executable")
        else:
            self.print_log("--> Warning. No LaGriT path provided.",  'warning')

        ===================================================
        THESE PATHS ARE AUTOMATICALLY SET. DO NOT CHANGE.
        ====================================================

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

    if docker:
        ### for DOCKER
        os.environ['dfnworks_PATH']  = '/dfnWorks/bin/'
        os.environ['DFNGEN_EXE'] = '/dfnWorks/bin/DFNGen'
        os.environ['DFNTRANS_EXE'] = '/dfnWorks/bin/DFNTrans'
        os.environ['CORRECT_UGE_EXE'] = '/dfnWorks/bin/correct_uge'
        os.environ['CORRECT_STOR_EXE'] = '/dfnWorks/bin/correct_stor'
        os.environ['CONNECT_TEST_EXE'] = '/dfnWorks/bin/ConnectivityTest'
        os.environ['PFLOTRAN_EXE'] = '/dfnWorks/bin/pflotran' 
        os.environ['FEHM_EXE'] = '/dfnWorks/bin/fehm' 
        os.environ['LAGRIT_EXE'] = '/dfnWorks/bin/lagrit'
        os.environ['PETSC_DIR'] = '/dfnWorks/lib/petsc'
        os.environ['PETSC_ARCH'] = 'arch-linux2-c-debug'

    self.print_paths() 
    self.print_log("--> Loading and checking dfnWorks dependency paths successful")
