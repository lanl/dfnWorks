import os
import sys
import shutil
from time import time
import subprocess


def dfn_trans(self):
    """Primary driver for dfnTrans. 

    Parameters
    ---------
        self : object
            DFN Class 
   
    Returns
    --------
        Nonie
    """
    self.print_log('=' * 80)
    self.print_log("dfnTrans Starting")
    self.print_log('=' * 80)
    tic = time()
    self.copy_dfn_trans_files()
    self.check_dfn_trans_run_files()
    self.run_dfn_trans()
    delta_time = time() - tic
    self.dump_time('Process: dfnTrans', delta_time)
    self.print_log('=' * 80)
    self.print_log("dfnTrans Complete")
    self.print_log("Time Required for dfnTrans: %0.2f Seconds\n" % delta_time)
    self.print_log('=' * 80)


def copy_dfn_trans_files(self):
    """Creates symlink to dfnTrans Execuateble and copies input files for dfnTrans into working directory

    Parameters
    ---------
        self : object
            DFN Class
 
    Returns
    --------
        None
    """

    self.print_log(f"Attempting to Copy {self.dfnTrans_file}")
    try:
        shutil.copy(self.dfnTrans_file, os.path.abspath(os.getcwd()))
    except OSError:
        self.print_log(f"--> Problem copying {self.local_dfnTrans_fil} file")
        self.print_log(f"--> Trying to delete and recopy")
        os.remove(self.local_dfnTrans_file)
        shutil.copy(self.dfnTrans_file, os.path.abspath(os.getcwd()))
    except:
        error = f"--> Error: Problem copying {self.dfnTrans_file} file\n" "Unable to replace. Exiting Program\n"
        self.print_log(error, 'critical')
        sys.exit(1)


def run_dfn_trans(self):
    """ Execute dfnTrans

    Parameters
    ---------
        self : object
            DFN Class  
 
    Returns
    --------
    None
    """
    tic = time()
    cmd = os.environ['DFNTRANS_EXE'] + ' ' + self.local_dfnTrans_file
    self.call_executable(cmd)
    self.dump_time("Function: DFNTrans ", time() - tic)


def create_dfn_trans_links(self, path='../'):
    """ Create symlinks to files required to run dfnTrans that are in another directory. 

    Parameters
    ---------
        self : object 
            DFN Class
        path : string 
            Absolute path to primary directory. 
   
    Returns
    --------
    None

    Notes
    -------
    Typically, the path is DFN.path, which is set by the command line argument -path

    """
    files = [
        'params.txt', 'allboundaries.zone', 'full_mesh.stor', 'poly_info.dat',
        'full_mesh.inp', 'aperture.dat'
    ]
    if self.flow_solver == 'PFLOTRAN':
        files.append('cellinfo.dat')
        files.append('darcyvel.dat')
        files.append('full_mesh_vol_area.uge')
    if self.flow_solver == 'FEHM':
        files.append('tri_frac.fin')

    for f in files:
        try:
            os.symlink(path + f, f)
        except:
            self.print_log(f"--> Error Creating link for {f}\n", "error")


def check_dfn_trans_run_files(self):
    """ Ensures that all files required for dfnTrans run are in the current directory
 
    Parameters
    ---------
        self : object 
            DFN Class
   
    Returns
    --------
        None

    Notes
    -------
        None
    """
    cwd = os.getcwd()
    self.print_log(
        "\nChecking that all files required for dfnTrans are in the current directory"
    )
    self.print_log(f"--> Current Working Directory: {cwd}")
    self.print_log(f"--> dfnTrans is running from: {self.local_dfnTrans_file}")

    self.print_log("--> Checking DFNTrans Parameters")
    params = {
        "param:": None,
        "poly:": None,
        "inp:": None,
        "stor:": None,
        "boundary:": None,
        "out_grid:": None,
        "out_3dflow:": None,
        "out_init:": None,
        "out_tort:": None,
        "out_curv:": None,
        "out_avs:": None,
        "out_traj:": None,
        "out_fract:": None,
        "out_filetemp:": None,
        "out_dir:": None,
        "out_path:": None,
        "out_time:": None,
        "ControlPlane:": None,
        "control_out:": None,
        "delta_Control:": None,
        "flowdir:": None,
        "init_nf:": None,
        "init_partn:": None,
        "init_eqd:": None,
        "init_npart:": None,
        "init_fluxw:": None,
        "init_totalnumber:": None,
        "init_oneregion:": None,
        "in_partn:": None,
        "init_well:": None,
        "init_nodepart:": None,
        "in_xmin:": None,
        "in_xmax:": None,
        "in_ymin:": None,
        "in_ymax:": None,
        "in_zmin:": None,
        "in_zmax:": None,
        "init_random:": None,
        "in_randpart:": None,
        "init_matrix:": None,
        "inm_coord:": None,
        "inm_nodeID:": None,
        "inm_porosity:": None,
        "inm_diffcoeff:": None,
        "streamline_routing:": None,
        "tdrw:": None,
        "tdrw_porosity:": None,
        "tdrw_diffcoeff:": None,
        "timesteps:": None,
        "time_units:": None,
        "flux_weight:": None,
        "seed:": None,
        "in-flow-boundary:": None,
        "out-flow-boundary:": None,
        "aperture:": None,
        "aperture_type:": None,
        "aperture_file:": None,
        "porosity": None,
        "density:": None,
        "satur:": None,
        "thickness:": None
    }

    files = ["param:", "poly:", "inp:", "stor:", "boundary:"]

    if self.flow_solver == "PFLOTRAN":
        params["PFLOTRAN_vel:"] = None
        files.append("PFLOTRAN_vel:")

        params["PFLOTRAN_cell:"] = None
        files.append("PFLOTRAN_cell:")

        params["PFLOTRAN_uge:"] = None
        files.append("PFLOTRAN_uge:")

    if self.flow_solver == "FEHM":
        params["FEHM_fin:"] = None
        files.append("FEHM_fin:")

    # Parse DFNTrans input and fill dictionary
    keys = params.keys()
    with open(self.local_dfnTrans_file) as fp:

        for line in fp.readlines():
            if "/*" in line:
                comment = line
                line = line[:line.index(
                    "/*")]  ## only process text before '/*' comment
            if "//" in line:
                line = line[:line.index("//")]

            if len(line) > 0:
                for key in keys:
                    if key in line:
                        if params[key] == None:
                            params[key] = line.split()[1]

    #for p in params.keys():
    #    print(p,params[p])

    # Check if file required for the run are in the directory and are not empty
    for key in files:
        if params[key] is None:
            error = f"Error\nRequired file {key} was not provided.\nPlease check DFNTrans control file\nExiting Program\n"
            self.print_log(error, 'error')
            sys.exit(1)
        elif not os.path.isfile(params[key]):
            error = "Error\nRequired file %s is not in the current directory.\nPlease check required files\nExiting Program\n" % params[
                key]
            self.print_log(error, 'error')
            sys.stderr.write(error)
            sys.exit(1)

    self.print_log(
        "--> All files required for dfnTrans have been found in current directory\n\n"
    )

    for required in [
            "out_grid:", "out_3dflow:", "out_init:", "out_tort:", "out_curv:",
            "out_avs:", "out_traj:", "out_fract:", "out_filetemp:", "out_dir:",
            "out_path:", "out_time:", "timesteps:", "time_units:",
            "flux_weight:", "seed:", "in-flow-boundary:", "out-flow-boundary:",
            "aperture:", "porosity", "density:", "satur:",
            "streamline_routing:"
    ]:
        if params[required] == None:
            error = f"Error\n{required} not provided. Exiting\n\n"
            self.print_log(error, 'error')
            sys.exit(1)

    # Check Initial conditions, make sure only 1 Initial condition is selected and that
    # required parameters have been defined
    self.print_log("--> Checking Initial Conditions")
    initial_conditions = [
        ("init_nf:", "init_partn:"), ("init_eqd:", "init_npart:"),
        ("init_fluxw:", "init_totalnumber:"), ("init_random:", "in_randpart:"),
        ("init_oneregion:", "in_partn:", "in_xmin:", "in_ymin:", "in_zmin:",
         "in_xmax:", "in_ymax:", "in_zmax:"),
        ("init_matrix:", "inm_coord:", "inm_nodeID:", "inm_porosity:"),
        ("init_well:", "init_nodepart:")
    ]
    ic_selected = []
    for ic in initial_conditions:
        #print(ic,params[ic[0]])
        if params[ic[0]] == "yes":
            ic_selected.append(ic[0])
            for i in ic:
                if params[i] == None:
                    error = "Initial condition %s selected but %s not provided\n" % (
                        ic[0], i)
                    self.print_log(error, 'error')
                    sys.exit(1)
    if len(ic_selected) > 1:
        error = "Error. More than one initial condition defined\nExiting\n"
        self.print_log(error, 'error')
        self.print_log("Selected Initial Conditions:\n:")
        for ic in ic_selected:
            self.print_log(ic)
        sys.exit(1)
    elif len(ic_selected) == 0:
        error = "Error. No initial condition defined\nExiting\n"
        self.print_log(error, 'error')
        sys.stderr.write(error)
        sys.exit(1)

    if params["ControlPlane:"] != None:
        for required in ["control_out:", "delta_Control:", "flowdir:"]:
            if params[required] == None:
                error = f"Parameter {required} required for ControlPlane\n"
                self.print_log(error, 'error')
                sys.exit(1)

    if params["tdrw:"] == "yes":
        if params["time_units:"] != "seconds":
            error = "Error. You must use seconds for the time_units to run TDRW"
            self.print_log(error, 'error')
            sys.exit(1)

        for required in ["tdrw_porosity:", "tdrw_diffcoeff:"]:
            if params[required] == None:
                error = f"Parameter {required} required for tdrw\n"
                self.print_log(error, 'error')
                sys.exit(1)

    if params["aperture:"] == "yes":
        if params["aperture_type:"] == None:
            error = "Parameter aperture_type: required for aperture: yes\n"
            self.print_log(error, 'error')
            sys.exit(1)

        else:
            if not os.path.isfile(params["aperture_file:"]) or os.stat(params["aperture_file:"]).st_size == 0:
                error = f"aperture_file: {params['aperture_file:']} not found or empty\n" 
                self.print_log(error, 'error')
                sys.exit(1)

    else:
        if params["thickness:"] == None:
            error = "Parameter thickness: required for aperture: no:\n"
            self.print_log(error, 'error')
            sys.exit(1)

    self.print_log("--> Checking Initial Conditions Complete")
