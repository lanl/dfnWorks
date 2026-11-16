from shutil import move
import os
import sys
import json

DFNPARAMS = '~/.dfnworksrc'
DFNPARAMS = os.path.expanduser(DFNPARAMS)

DFNGEN_REQUIRED_VERSION = "2.3"


def valid(self, name, path, path_type, fatal=True):
    """ Check that a path is valid

    Parameters
    ----------
        self : object
            DFN Class

        name : string
            Name of the path variable, e.g., LAGRIT_EXE

        path : string
            path to check

        path_type : string
            "executable", "file", or "directory"

        fatal : bool
            If True (default), exit when the path is invalid. If False, print
            a warning to the screen and log and keep going.

    Returns
    -------
        True if the path is valid, False otherwise (when fatal is False)

    Notes
    -----
        Used with fatal=False for paths read from ~/.dfnworksrc
    """

    error = None
    if path_type == "executable":
        if not os.path.isfile(path):
            error = f"{name}: {path} is not a valid path to a file name."
        elif not os.access(path, os.X_OK):
            error = f"{name}: {path} is not an executable. Please check file permissions."
    elif path_type == "file":
        if not os.path.isfile(path):
            error = f"{name}: {path} is not a valid path to a file name."
    elif path_type == "directory":
        if not os.path.isdir(path):
            error = f"{name}: {path} is not a directory."

    if error is None:
        return True

    error += "\nPlease check the path in either pydfnworks/general/paths.py or .dfnworksrc."
    if fatal:
        self.print_log(f"Error checking {error}\nExiting\n", 'critical')
        sys.exit(1)
    self.print_log(f"--> Warning. {error}", 'warning')
    return False


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
    for name in ['dfnworks_PATH', 'LAGRIT_EXE', 'PETSC_DIR', 'PETSC_ARCH',
                 'PFLOTRAN_EXE', 'FEHM_EXE', 'MOOSE_EXE', 'MOOSE_ENV_SH']:
        self.print_log(f"* {name}: {os.environ.get(name, 'NOT SET')}")
    self.print_log("")


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

    # ================================================
    # THESE PATHS MUST BE SET BY THE USER.
    # ================================================

    self.print_log("--> Loading and checking dfnWorks dependency paths." )
    # Either write paths to ~/.dfnworksrc in a JSON format...
    if os.path.isfile(DFNPARAMS):
        self.print_log(f"--> {DFNPARAMS} found.\n")
        with open(DFNPARAMS, 'r') as f:
            env_paths = json.load(f)
    # Or, change the paths here
    else:
        self.print_log("--> Warning. ~/.dfnworksrc not found. Checking for environmantal variables.",  'warning')
        env_paths = {}

    # Each path is read from ~/.dfnworksrc, falling back to an environment
    # variable of the same name. A missing or invalid dfnworks_PATH exits;
    # anything else is a warning so runs that do not need it can continue.
    user_paths = [
        ('dfnworks_PATH', 'directory'),
        ('PETSC_DIR', 'directory'),
        ('PETSC_ARCH', 'directory'),
        ('PFLOTRAN_EXE', 'executable'),
        ('LAGRIT_EXE', 'executable'),
        ('FEHM_EXE', 'executable'),
        ('MOOSE_EXE', 'executable'),
        ('MOOSE_ENV_SH', 'file'),
    ]
    for name, path_type in user_paths:
        path = env_paths.get(name) or os.environ.get(name)
        # dfnworks_PATH is required. Everything else is a warning.
        fatal = (name == 'dfnworks_PATH')
        if not path:
            if fatal:
                self.print_log(f"Error. dfnworks_PATH not found in {DFNPARAMS} or the environment. Must be set to the github cloned repo.\nExiting\n", 'critical')
                sys.exit(1)
            self.print_log(f"--> Warning. {name} not found in {DFNPARAMS} or the environment.", 'warning')
            continue
        path = os.path.expanduser(path)
        os.environ[name] = path
        # PETSC_ARCH is a subdirectory of PETSC_DIR
        if name == 'PETSC_ARCH':
            path = os.path.join(os.environ.get('PETSC_DIR', ''), path)
        self.valid(name, path, path_type, fatal=fatal)

    # ===================================================
    # THESE PATHS ARE AUTOMATICALLY SET. DO NOT CHANGE.
    # ====================================================

    # Directories
    os.environ['DFNGEN_EXE'] = os.environ['dfnworks_PATH'] + 'DFNGen/DFNGen'
    if not os.path.isfile(os.environ['DFNGEN_EXE']):
        self.compile_dfn_exe(os.environ['dfnworks_PATH'] + 'DFNGen/')
    self.valid('DFNGen', os.environ['DFNGEN_EXE'], "executable")
    self.check_dfngen_version()

    os.environ[
        'DFNTRANS_EXE'] = os.environ['dfnworks_PATH'] + 'DFNTrans/DFNTrans'
    if not os.path.isfile(os.environ['DFNTRANS_EXE']):
         self.compile_dfn_exe(os.environ['dfnworks_PATH'] + 'DFNTrans/')
    self.valid('DFNTrans', os.environ['DFNTRANS_EXE'], "executable")

    os.environ['CORRECT_VOLUME_EXE'] = os.environ[
        'dfnworks_PATH'] + 'CPP_correct_volumes/correct_volume'
    if not os.path.isfile(os.environ['CORRECT_VOLUME_EXE']):
         self.compile_dfn_exe(os.environ['dfnworks_PATH'] +
                        'CPP_correct_volumes/')
    self.valid('CORRECT_VOLUME_EXE', os.environ['CORRECT_VOLUME_EXE'], "executable")

    os.environ['CONNECT_TEST_EXE'] = os.environ[
        'dfnworks_PATH'] + 'DFN_Mesh_Connectivity_Test/ConnectivityTest'
    if not os.path.isfile(os.environ['CONNECT_TEST_EXE']):
         self.compile_dfn_exe(os.environ['dfnworks_PATH'] +
                        'DFN_Mesh_Connectivity_Test/')
    self.valid('CONNECT_TEST_EXE', os.environ['CONNECT_TEST_EXE'], "executable")

    self.print_paths()
    self.print_log("--> Loading and checking dfnWorks dependency paths successful")


def check_dfngen_version(self):
    """Check that the compiled DFNGen binary matches the required version.

    Parameters
    ----------
        self : object
            DFN Class

    Returns
    -------
        None

    Notes
    -----
        Version is written to DFNGen/.dfngen_version by the makefile at
        build time. If the file is missing or the version does not match
        DFNGEN_REQUIRED_VERSION, an error is raised and the program exits.
    """
    version_file = os.path.join(
        os.environ['dfnworks_PATH'], 'DFNGen', '.dfngen_version'
    )
    if not os.path.isfile(version_file):
        error = (
            f"Error: DFNGen version file not found at {version_file}.\n"
            f"Please rebuild DFNGen (cd DFNGen && make).\nExiting\n"
        )
        self.print_log(error, 'critical')
        sys.exit(1)

    with open(version_file, 'r') as f:
        installed_version = f.read().strip()

    if installed_version != DFNGEN_REQUIRED_VERSION:
        error = (
            f"Error: DFNGen version mismatch.\n"
            f"  Required : {DFNGEN_REQUIRED_VERSION}\n"
            f"  Installed: {installed_version}\n"
            f"Please rebuild DFNGen (cd DFNGen && make).\nExiting\n"
        )
        self.print_log(error, 'critical')
        sys.exit(1)

    self.print_log(f"--> DFNGen version {installed_version} verified.")
