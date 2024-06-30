"""
.. module:: mesh_dfn_helper.py
   :synopsis: helper functions for meshing DFN using LaGriT  
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""
import os
import sys
import glob
import shutil
import numpy as np
import subprocess
import pyvtk as pv
# from pydfnworks.general import helper_functions as hf
from pydfnworks.general.logging import local_print_log 

def check_dudded_points(dudded, hard=False):
    """Parses LaGrit log_merge_all.out and checks if number of dudded points is the expected number

    Parameters
    ---------
        dudded : int 
            Expected number of dudded points from params.txt
        hard : bool
            If hard is false, up to 1% of nodes in the mesh can be missed. If hard is True, no points can be missed. 
    Returns
    ---------
        True/False : bool
            True if the number of dudded points is correct and  False if the number of dudded points is incorrect 
    
    Notes
    -----
        If number of dudded points is incorrect by over 1%, program will exit. 
    """

    local_print_log("--> Checking that number of dudded points is correct\n")
    with open("lagrit_logs/log_merge_all.out", encoding='latin-1') as fp:
        for line in fp.readlines():
            if 'Dudding' in line:
                local_print_log(f'--> From LaGriT: {line}')
                try:
                    pts = int(line.split()[1])
                except:
                    pts = int(line.split()[-1])
            if 'RMPOINT:' in line:
                local_print_log(f'--> From LaGriT: {line}')
                total_points = int(line.split()[-1])
                break

    diff = abs(dudded - pts)
    local_print_log(f"--> Expected Number of dudded points: {dudded}")
    local_print_log(f"--> Actual Number of dudded points: {pts}")
    local_print_log(f"--> Difference between expected and actual dudded points: {diff}")
    if diff == 0:
        local_print_log('--> The correct number of points were removed. Onward!\n')
        return True
    elif diff > 0:
        local_print_log(
            'Number of points removed does not match the expected value', 'warning')
        ## compare with total number poins
        diff_ratio = 100 * (float(diff) / float(total_points))
        if diff_ratio < 0.01 and hard == False:
            local_print_log(f"--> However value is small: {diff}", 'warning')
            local_print_log("--> Proceeding\n", 'warning')
            return True
        else:
            local_print_log(
                f"Incorrect Number of points removed\nOver 0.01% of nodes removed. Value is {diff_ratio:.2f}", "warning"
            )
            return False


def gather_mesh_information(self):
    """ Prints information about the final mesh to file
    
    Parameters
    ----------
        local_jobname : string
            Name of current DFN job (not path) 
    visual_mode : bool
        Determines is reduced_mesh or full_mesh is dumped

    Returns
    -------
        None
   
    Notes
    -----
        None 
"""

    if self.visual_mode:
        with open('reduced_mesh.inp', 'r') as finp:
            header = finp.readline()
            header = header.split()
            self.num_nodes = int(header[0])
        self.print_log(
            f"--> The reduced mesh in reduced_mesh.inp has {self.num_nodes} nodes and {int(header[1])} triangular elements"
        )
    else:
        with open('full_mesh.inp', 'r') as finp:
            header = finp.readline()
            header = header.split()
            self.num_nodes = int(header[0])
        self.print_log(
            f"--> The primary mesh in full_mesh.inp has {self.num_nodes} nodes and {int(header[1])} triangular elements"
        )
        ## get material -ids
        self.material_ids = np.genfromtxt('materialid.dat',
                                          skip_header=3).astype(int)
        self.aperture_cell = np.zeros(self.num_nodes)
        self.perm_cell = np.zeros(self.num_nodes)


def create_mesh_links(self, path):
    ''' Makes symlinks for files in path required for meshing
    
    Parameters
    ----------
        self : DFN object
        path : string
            Path to where meshing files are located

    Returns
    -------
        None
    
    Notes
    -----
        None

    '''
    import os.path
    from shutil import rmtree
    self.print_log(f"--> Creating links for meshing from {path}")
    files = [
        'params.txt',
        'poly_info.dat',
        'polys',
        'intersections',
        'dfnGen_output/connectivity.dat',
        'dfnGen_output/left.dat',
        'dfnGen_output/right.dat',
        'dfnGen_output/front.dat',
        'dfnGen_output/back.dat',
        'dfnGen_output/top.dat',
        'dfnGen_output/fracture_info.dat',
        'dfnGen_output/intersection_list.dat',
        'dfnGen_output/bottom.dat',
    ]
    for filename in files:
        if os.path.isfile(filename) or os.path.isdir(filename):
            self.print_log(f"Removing {filename}")
            try:
                rmtree(filename)
            except:
                self.print_log(f"Unable to remove {filename}", 'warning')
        try:
            os.symlink(path + filename, filename)
        except:
            self.print_log(f"Unable to make link for {filename}", 'warning')
            pass
    self.print_log("--> Complete")


def inp2gmv(self, inp_file=None):
    """ Convert inp file to gmv file, for general mesh viewer. Name of output file for base.inp is base.gmv

    Parameters
    ----------
        self : object
            DFN Class
        inp_file : str
            Name of inp file if not an attribure of self

    Returns
    ----------
    None

    Notes
    ---------
    """

    if inp_file:
        self.inp_file = inp_file
    else:
        inp_file = self.inp_file

    if not inp_file:
        local_print_log('inp file must be specified in inp2gmv', 'error')

    gmv_file = inp_file[:-4] + '.gmv'

    with open('inp2gmv.lgi', 'w') as fid:
        fid.write(f'read / avs / {inp_file} / mo\n')
        fid.write(f'dump / gmv / {gmv_file} / mo\n')
        fid.write('finish \n\n')

    failure = run_lagrit_script('inp2gmv.lgi')

    if failure:
        local_print_log('Failed to run LaGrit to get gmv from inp file.', 'error')
    local_print_log("--> Finished writing gmv format from avs format")


def inp2vtk_python(self):
    """ Using Python VTK library, convert inp file to VTK file.  

    Parameters
    ----------
        self : object 
            DFN Class

    Returns
    --------
        None

    Notes
    --------
        For a mesh base.inp, this dumps a VTK file named base.vtk
    """

    if self.flow_solver != "PFLOTRAN":
        self.print_log("inp2vtk requires PFLOTRAN flow solver be selected", 'error')

    self.print_log("--> Using Python to convert inp files to VTK files")
    if self.inp_file:
        inp_file = self.inp_file

    if not inp_file:
        self.print_log("inp filename not provided", 'error')

    if self.vtk_file:
        vtk_file = self.vtk_file
    else:
        vtk_file = inp_file[:-4]
        self.vtk_file = vtk_file + '.vtk'

    self.print_log("--> Reading inp data")

    with open(inp_file, 'r') as f:
        line = f.readline()
        num_nodes = int(line.strip(' ').split()[0])
        num_elems = int(line.strip(' ').split()[1])

        coord = np.zeros((num_nodes, 3), 'float')
        elem_list_tri = []
        elem_list_tetra = []

        for i in range(num_nodes):
            line = f.readline()
            coord[i, 0] = float(line.strip(' ').split()[1])
            coord[i, 1] = float(line.strip(' ').split()[2])
            coord[i, 2] = float(line.strip(' ').split()[3])

        for i in range(num_elems):
            line = f.readline().strip(' ').split()
            line.pop(0)
            line.pop(0)
            elem_type = line.pop(0)
            if elem_type == 'tri':
                elem_list_tri.append([int(i) - 1 for i in line])
            if elem_type == 'tet':
                elem_list_tetra.append([int(i) - 1 for i in line])

    self.print_log('--> Writing inp data to vtk format')
    vtk = pv.VtkData(
        pv.UnstructuredGrid(coord,
                            tetra=elem_list_tetra,
                            triangle=elem_list_tri),
        'Unstructured pflotran grid')

    vtk.tofile(vtk_file)


def run_lagrit_script(lagrit_file, output_file=None, quiet=False):
    """
    Runs LaGriT

    Parameters
    -----------
    ----------
        lagrit_file : string
            Name of LaGriT script to run
        output_file : string
            Name of file to dump LaGriT output
        quiet : bool
            If false, information will be printed to screen.

    Returns
    ----------
        failure: int
            If the run was successful, then 0 is returned. 

    """
    if output_file == None:
        cmd = f"{os.environ['LAGRIT_EXE']} < {lagrit_file} -log {lagrit_file}.log -out {lagrit_file}.out"
    else:
        cmd = f"{os.environ['LAGRIT_EXE']} < {lagrit_file} -log {output_file}.log -out {output_file}.out > {output_file}.dump"
    if not quiet:
        local_print_log(f"--> Running: {cmd}")
    failure = subprocess.call(cmd, shell=True)
    if failure:
        local_print_log(f"LaGriT script {lagrit_file} failed to run properly", "error")
    else:
        if not quiet:
            local_print_log(f"--> LaGriT script {lagrit_file} ran successfully")
        return failure


def setup_meshing_directory():

    dirs = ["lagrit_scripts", "lagrit_logs"]
    for d in dirs:
        try:
            if os.path.isdir(d):
                shutil.rmtree(d)
            os.mkdir(d)
        except:
            local_print_log(f"Unable to make directory {d}",'error')


def cleanup_meshing_files():
    """ Removes mesh files and directories 

    Parameters
    ----------
        None

    Returns
    -------
        None

    Notes
    -----
    Only runs if cleanup is true
    """
    local_print_log("\n--> Cleaning up directory after meshing")
    batch_files_to_remove = [
        'part*', 'log_merge*', 'merge*', 'mesh_poly_CPU*', 'mesh*inp',
        'mesh*lg'
    ]
    for files in batch_files_to_remove:
        for fl in glob.glob(files):
            os.remove(fl)

    dirs_to_remove = ['lagrit_scripts', 'lagrit_logs']
    for d in dirs_to_remove:
        try:
            if os.path.isdir(d):
                shutil.rmtree(d)
        except:
            local_print_log(f"Unable to remove directory {d}", 'error')

    files_to_remove = ['user_resolution.mlgi']
    for filename in files_to_remove:
        try:
            if os.path.isfile(filename):
                os.remove(filename)
        except:
            local_print_log(f"Unable to remove file {filename}", "error")
    local_print_log("--> Cleaning up directory after meshing complete")


def compute_mesh_slope_and_intercept(h, min_dist, max_dist,
                                     max_resolution_factor, uniform_mesh):
    """ computes the slope and intercept of the meshing resolution. The mesh resolution is a piecewise constant and linear function of the distance (d) from the intersection. 


    if  0 < d < x0*h, then  r(d) = h/2
    if x0*h <= d <= x1*h then r(d) = m * d + b
    if d < x1 then r(d) = max_resolution_factor*h

    Note that x0 and x1 are factors of h, not spatial units of Length. 
   
    Parameters
    -------------------
        h : float
            FRAM h scale. Mesh resolution along intersections is h/2
        min_dist : float
            Defines the minimum distance from the intersections with resolution h/2. This value is the factor of h, distance = min_dist * h
        max_dist : float
            Defines the minimum distance from the intersections with resolution max_resolution * h. This value is the factor of h, distance = max_dist * h
        max_resolution_factor : float
            Maximum factor of the mesh resolultion (max_resolution *h). Depending on the slope of the linear function and size of the fracture, this may not be realized in the mesh. 
        uniform_mesh : bool
            Boolean for uniform mesh resolution

    Returns
    -------------------
        slope : float 
            slope of the linear function of the mesh resolution
        intercept : float 
            Intercept of the linear function of the mesh resolution 


    Notes
    -------------------

    
    """
    local_print_log("--> Computing mesh resolution function")
    if uniform_mesh:
        local_print_log("--> Uniform Mesh Resolution Selected")
        local_print_log("*** Mesh resolution ***")
        local_print_log(f"\tr(d) = {0.5*h}\n")
        slope = 0
        intercept = 0.5 * h
    else:
        local_print_log("--> Variable Mesh Resolution Selected")
        local_print_log(
            f"*** Minimum distance [m] from intersection with constant resolution h/2 : {min_dist*h}"
        )
        local_print_log(
            f"*** Maximum distance [m] from intersection variable resolution : {max_dist*h}"
        )
        local_print_log(
            f"*** Upper bound on resolution [m] : {max_resolution_factor*h:0.2f}\n"
        )
        ## do some algebra to figure out the slope and intercept
        if min_dist >= max_dist:
            local_print_log(
                f"min_dist greater than or equal to max_dist.\nmin_dist : {min_dist}\nmax_dist : {max_dist}", "error"
            )
        slope = h * (max_resolution_factor - 0.5) / (max_dist - min_dist)
        if slope > 1:
            local_print_log(
                f"Meshing slope too large. {slope} > 1. Resetting to 0.9", "warning")
            slope = 0.9

        intercept = h * (0.5 - slope * min_dist)

        local_print_log("*** Meshing function : ")
        x0 = (0.5 * h - intercept) / (slope * h)
        x1 = (max_resolution_factor * h - intercept) / (slope * h)
        local_print_log(f"\tr(d) = {0.5*h:0.2f}\t\t\tfor 0 < d < {x0:0.2f}")
        if intercept > 0:
            local_print_log(
                f"\tr(d) = {slope:0.2f} * d + {intercept:0.2f}\t\tfor {x0:0.2f} <= d <= {x1:0.2f} "
            )
        else:
            local_print_log(
                f"\tr(d) = {slope:0.2f} * d {intercept:0.2f}\t\tfor {x0:0.2f} < d < {x1:0.2f} "
            )
        local_print_log(
            f"\tr(d) = {max_resolution_factor*h:0.2f} \t\t\tfor {x1:0.2f} <= d"
        )
    local_print_log("--> Computing mesh resolution function : complete \n")
    return slope, intercept
