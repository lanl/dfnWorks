"""
.. module:: run_meshing.py
   :synopsis: functions to mesh fracture network in parallel 
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import subprocess
import os
import sys
import timeit
import glob
import importlib.resources

import numpy as np
import multiprocessing as mp

mp.set_start_method("fork")

from shutil import copy, rmtree
from numpy import genfromtxt
from pydfnworks.general import helper_functions as hf
from pydfnworks.dfnGen.meshing.mesh_dfn import mesh_dfn_helper as mh
from pydfnworks.general.logging import local_print_log 


def cleanup_failed_run(fracture_id, digits):
    """ If meshing fails, this function moves all relavent files
    to a folder for debugging

    Parameters
    ----------
        fracture_id : int
            Current Fracture ID number
        digits : int
            Number of digits in total number of fractures

    Returns
    -------
        None

    Notes
    ------
    This will throw warnings depending on when in the work-flow it is called. Some files
    might not be created at those times. It's okay.

"""

    local_print_log(f"--> Cleaning up meshing run for fracture {fracture_id}")

    if not os.path.isfile("failure.txt"):
        with open('failure.txt', "w+") as failure_file:
            failure_file.write(f"{fracture_id}\n")
    else:
        with open('failure.txt', "a") as failure_file:
            failure_file.write(f"{fracture_id}\n")

    folder = f"failure_{fracture_id}/"
    try:
        os.mkdir(folder)
    except:
        local_print_log(f"Unable to make new folder: {folder}", "warning")
        pass

    files = [
        f"mesh_{fracture_id:0{digits}d}.inp", f"{fracture_id}_mesh_errors.txt",
        f"id_tri_node_{fracture_id}.list",
        f"lagrit_logs/log_lagrit_{fracture_id:0{digits}d}.out",
        f"polys/poly_{fracture_id}.inp",
        f"intersections/intersections_{fracture_id}.inp",
        f"lagrit_scripts/parameters_{fracture_id:0{digits}d}.mlgi",
        f"lagrit_scripts/mesh_poly_{fracture_id:0{digits}d}.lgi",
        "user_resolution.mlgi"
    ]

    for f in files:
        try:
            copy(f, folder)
        except:
            local_print_log(f'--> Could not copy {f} to failure folder', "warning")
            pass

    symlinks = [
        f"poly_{fracture_id}.inp",
        f"intersections_{fracture_id}.inp",
        f"parameters_{fracture_id:0{digits}d}.mlgi",
        f"mesh_poly_{fracture_id:0{digits}d}.lgi",
    ]

    for f in symlinks:
        try:
            os.unlink(f)
        except:
            local_print_log(f'--> Could not unlink {f}',"warning")
            pass

    local_print_log(f"--> Cleanup for Fracture {fracture_id} complete")


def create_symbolic_links(fracture_id, digits, visual_mode):
    """ Creates the symbolic links for meshing. 

    Parameters
    --------------------
        fracture_id : int 
            fracture index
        digits : int
            number of digits in total number of fractures
        visual_mode : bool
            Boolean to toggle vis mode on/off. Creates reduced_mesh.inp if true

    Returns
    ----------------
        Error index : boolean
            True if all symbolic links have beeb created and False if any symbolic links failed.

    
    
    """
    # Create Symbolic Links
    try:
        os.symlink(f"polys/poly_{fracture_id}.inp", f"poly_{fracture_id}.inp")
    except:
        local_print_log(
            f"--> Error creating link for poly_{fracture_id}.inp\n","warning")
        return False

    try:
        os.symlink(f"lagrit_scripts/parameters_{fracture_id:0{digits}d}.mlgi",\
            f"parameters_{fracture_id:0{digits}d}.mlgi")
    except:
        local_print_log(
            f"--> Error creating link for parameters_{fracture_id:0{digits}d}.mlgi\n","warning"
        )
        return False

    try:
        os.symlink(f"lagrit_scripts/mesh_poly_{fracture_id:0{digits}d}.lgi",\
            f"mesh_poly_{fracture_id:0{digits}d}.lgi")
    except:
        local_print_log(
            f"--> Error creating link for mesh_poly_{fracture_id:0{digits}d}.mlgi\n","warning"
        )
        return False

    if not visual_mode:
        try:
            os.symlink(f"intersections/intersections_{fracture_id}.inp",\
                f"intersections_{fracture_id}.inp")
        except:
            local_print_log(
                f"--> Error creating link for intersections_{fracture_id}.inp\n", "warning"
            )
            return False

    return True


def mesh_fracture(fracture_id, visual_mode, num_frac, r_fram, quiet):
    """ Child function for parallelized meshing of fractures

    Parameters
    ----------
        fracture_id : int
            Current Fracture ID number
        visual_mode : bool
            True/False for reduced meshing
        num_frac : int 
            Total Number of Fractures in the DFN
        r_fram : boolean
            relaxed fram

    Returns
    -------
        success index: 
        0 - run was successful
        -1 - error making symbolic link
        -2 - run failed to produce mesh files
        -3 - mesh file created but empty
        -4 - line of intersection not preserved
    
    Notes
    -----
    If meshing run fails, information about that fracture will be put into a directory failure_(fracture_id)

    """

    # get current process information
    try:
        p = mp.current_process()
        _, cpu_id = p.name.split("-")
        cpu_id = int(cpu_id)
    except:
        cpu_id = 1

    # get leading digits
    digits = len(str(num_frac))

    if not quiet:
        local_print_log(
            f"--> Fracture id {fracture_id:0{digits}d} out of {num_frac} is starting on worker {cpu_id}"
        )
    if fracture_id == 1 and digits != 1:
        local_print_log(
            f"\t* Starting on Fracture {fracture_id:0{digits}d} out of {num_frac} *"
        )
    if fracture_id % 10**(digits - 1) == 0:
        local_print_log(
            f"\t* Starting on Fracture {fracture_id:0{digits}d} out of {num_frac} *"
        )
    tic = timeit.default_timer()

    if not create_symbolic_links(fracture_id, digits, visual_mode):
        return (fracture_id, -1)

    # run LaGriT Meshing
    try:
        mh.run_lagrit_script(
            f"mesh_poly_{fracture_id:0{digits}d}.lgi",
            output_file=f"lagrit_logs/mesh_poly_{fracture_id:0{digits}d}",
            quiet=quiet)
    except:
        local_print_log(
            f"Error occurred during meshing fracture {fracture_id}\n","warning")
        cleanup_failed_run(fracture_id, digits)
        return (fracture_id, -2)

    # Check if mesh*.lg file was created, if not exit.
    if not os.path.isfile(f'mesh_{fracture_id:0{digits}d}.lg') or os.stat(
            f'mesh_{fracture_id:0{digits}d}.lg') == 0:
        local_print_log(
            f" Mesh for fracture {fracture_id} was either not produced or has zero size\n","warning"
        )
        cleanup_failed_run(fracture_id, digits)
        return (fracture_id, -3)

    ## Once meshing is complete, check if the lines of intersection are in the final mesh
    if not visual_mode:
        connect_test_exe = importlib.resources.files("pydfnworks") / "bin" / "ConnectivityTest"
        cmd_check = f"{connect_test_exe} \
            intersections_{fracture_id}.inp \
            id_tri_node_{fracture_id:0{digits}d}.list \
            mesh_{fracture_id:0{digits}d}.inp \
            {fracture_id}"

        # If the lines of intersection are not in the final mesh, put depending files
        # into a directory for debugging.
        try:
            if subprocess.call(cmd_check, shell=True):
                if not r_fram:
                    local_print_log(
                        f"Meshing checking failed on {fracture_id}.\n","warning")
                    cleanup_failed_run(fracture_id, digits)
                    return (fracture_id, -4)
        except:
            local_print_log(
                f"Unable to run mesh checking checking on {fracture_id}.\n","warning")
            cleanup_failed_run(fracture_id, digits)
            return (fracture_id, -4)

        # Mesh checking was a success. Remove check files and move on
        files = [
            f"id_tri_node_{fracture_id:0{digits}d}.list",
            f"mesh_{fracture_id:0{digits}d}.inp"
        ]
        if not r_fram:
            files.append(f'{fracture_id}_mesh_errors.txt')

        for f in files:
            try:
                os.remove(f)
            except:
                local_print_log(f"--> Could not remove {f}\n","warning")
                pass

    # Remove symbolic
    if visual_mode:
        files = [
            f'poly_{fracture_id}.inp',
            f'parameters_{fracture_id:0{digits}d}.mlgi',
            f"mesh_poly_{fracture_id:0{digits}d}.lgi"
        ]
    else:
        files = [
            f'poly_{fracture_id}.inp', f'intersections_{fracture_id}.inp',
            f'parameters_{fracture_id:0{digits}d}.mlgi',
            f"mesh_poly_{fracture_id:0{digits}d}.lgi"
        ]
    for f in files:
        try:
            os.unlink(f)
        except:
            local_print_log(f'--> Warning: Could unlink {f}', 'warning')
            pass

    elapsed = timeit.default_timer() - tic
    if not quiet:
        local_print_log(
            f"--> Fracture {fracture_id:0{digits}d} out of {num_frac} is complete on worker {cpu_id}. Time required: {elapsed:.2f} seconds\n"
        )
    return (fracture_id, 0)


def mesh_fractures_header(self, quiet=True):
    """ Header function for Parallel meshing of fractures
    
    Creates a queue of fracture numbers ranging from 1, num_frac
    
    Each fractures is meshed using mesh_fracture called within the
    worker function.

    If any fracture fails to mesh properly, then a folder is created with 
    that fracture information and the fracture number is written into
    failure.txt.

    Parameters
    ----------
        fracture_list : list
            Fractures to be meshed
        visual_mode : bool
            True/False for reduced meshing
        num_frac : int
            Total Number of Fractures

    Returns
    -------
        True/False : bool
            True - If failure.txt is empty then all fractures have been meshed correctly
            False - If failure.txt is not empty, then at least one fracture failed.  

    Notes
    -----
        If one fracture fails meshing, program will exit. 

    """
    t_all = timeit.default_timer()
    self.print_log('=' * 80)
    self.print_log(
        f"--> Triangulating {self.num_frac} fractures using {self.ncpu} processors\n"
    )

    pool = mp.Pool(min(self.num_frac, self.ncpu))
    result_list = []

    def log_result(result):
        # This is called whenever foo_pool(i) returns a result.
        # result_list is modified only by the main process, not the pool workers.
        result_list.append(result)
        if result[1] != 0:
            pool.terminate()
            # If a run fails, kill all other processes, and clean up the directory
            names = [
                "poly_*.inp",
                "mesh_poly_*.lgi",
                "parameters_*.mlgi",
                "intersections_*.inp",
            ]
            for name in names:
                files_to_remove = glob.glob(name)
                for f in files_to_remove:
                    os.remove(f)

    # get leading digits
    digits = len(str(self.num_frac))

    for i in self.fracture_list:
        pool.apply_async(mesh_fracture,
                         args=(i, self.visual_mode, self.num_frac, self.r_fram,
                               quiet),
                         callback=log_result)

    pool.close()
    pool.join()

    elapsed = timeit.default_timer() - t_all
    self.print_log('--> Triangulating Polygons: Complete\n')
    time_sec = elapsed
    time_min = elapsed / 60
    time_hrs = elapsed / 3600
    self.print_log("--> Total Time to Mesh Network:")
    self.print_log(
        f"--> {time_sec:.2e} seconds\t{time_min:.2e} minutes\t{time_hrs:.2e} hours"
    )
    self.print_log('=' * 80)

    self.print_log("* Checking for meshing issues.")
    for result in result_list:
        if result[1] != 0:
            self.print_log(
                f"--> Fracture number {result[0]} failed with error {result[1]}\n"
            )
            details = """
        Error index: 
0 - run was successful
-1 - error making symbolic link
-2 - run failed to produce mesh files
-3 - mesh file created but empty
-4 - line of intersection not preserved
        """
            self.print_log(details)
            return False

    if os.path.isfile("failure.txt"):
        failure_list = genfromtxt("failure.txt")
        if type(failure_list) is list:
            failure_list = np.sort(failure_list)
        else:
            self.print_log('--> Fractures:', failure_list, 'Failed', 'warning')
        self.print_log('--> Main process exiting.')
        return True

    ## check for meshing errors in r_fram
    if self.r_fram:
        if self.check_for_missing_edges():
            return True


def check_for_missing_edges(self):
    """ Checks for missing edges that can occur with relaxed FRAM.

    Parameters
    ------------------
        self : DFN Object

    Returns
    ------------------
        failure_flag : bool
            True if too many edges were lost, False if mesh is okay.    
    """
    self.print_log('=' * 80)
    self.print_log("* Checking missed edges from relaxed FRAM")
    # get total number of edges
    total_edges = 0
    for ifrac in self.fracture_list:
        with open(f"intersections/intersections_{ifrac}.inp", "r") as fp:
            header = fp.readline()
            header = header.split()
            num_edges = int(header[1])
        total_edges += num_edges

    missed_edges = 0
    missed_edges_list = []
    error_file_list = glob.glob("*_mesh_errors.txt")
    num_frac_missed = 0
    for filename in error_file_list:
        with open(filename, 'r') as fp:
            for i, line in enumerate(fp.readlines()):
                continue
            missed_edges += i
            missed_edges_list.append(i)
            if i > 1:
                num_frac_missed += 1

    for filename in error_file_list:
        #print(f"--> Removing filename :{filename}")
        os.remove(filename)

    self.print_log(
        f"* Total number of fractures with missed edges: {num_frac_missed} out of {self.num_frac}")
    if num_frac_missed > 0:
        self.print_log(
            f"* Average number of missed edges per fracture: {missed_edges/num_frac_missed}"
        ,"warning")
        self.print_log(f"* Minimum number of missed edges: {min(missed_edges_list)}","warning")
        self.print_log(f"* Maximum number of missed edges: {max(missed_edges_list)}","warning")
        self.print_log(f"* Total number of missed edges: {missed_edges}","warning")
        self.print_log(f"* Total number of intersection edges: {total_edges}","warning")
        self.print_log(
            f"* Percentage of missed intersection edges: {100*missed_edges/total_edges:0.2f}%","warning")

    if missed_edges / total_edges > 0.1:
        self.print_log(
            f"* Percentage of missed edges too large (> 10%). Exitting program."
        ,"warning")
        self.print_log('=' * 80)
        return True
    else:
        self.print_log('=' * 80)
        return False


def merge_worker(job, quiet=True):
    """ Parallel worker for merge meshes into final mesh 

    Parameters
    ----------
        job : int
            job number

    Returns
    -------
        bool : True if failed / False if successful

    Notes
    -----
    """

    if not quiet:
        local_print_log(f"--> Starting merge: {job}")

    tic = timeit.default_timer()
    if mh.run_lagrit_script(f"lagrit_scripts/merge_part_{job}.lgi",
                            f"lagrit_logs/merge_part_{job}",
                            quiet=True):
        local_print_log(f" Merge job : {job} failed", 'warning')
        return True

    elapsed = timeit.default_timer() - tic
    if not quiet:
        local_print_log(
            f"--> Merge Number {job} Complete. Time elapsed: {elapsed:.2f} seconds."
        )
    return False


def merge_the_fractures(ncpu):
    """ Runs the LaGrit Scripts to merge meshes into final mesh 

    Parameters
    ----------
        num_frac : int
            Number of Fractures
        ncpu : int
            Number of Processors
        n_jobs : int
            Number of mesh pieces
        visual_mode : bool
            True/False for reduced meshing

    Returns
    -------
        None

    Notes
    -----
        Meshes are merged in batches for efficiency  
    """
    local_print_log('=' * 80)
    if ncpu == 1:
        local_print_log(
            f"--> Merging triangulated fracture meshes using {ncpu} processor."
        )
    else:
        local_print_log(
            f"--> Merging triangulated fracture meshes using {ncpu} processors."
        )

    jobs = range(1, ncpu + 1)
    tic = timeit.default_timer()
    pool = mp.Pool(ncpu)
    outputs = pool.map(merge_worker, jobs)
    pool.close()
    pool.join()
    pool.terminate()
    elapsed = timeit.default_timer() - tic
    local_print_log(
        f"--> Initial merging complete. Time elapsed: {elapsed:.2e} seconds.\n"
    )
    for output in outputs:
        if output:
            error = "Error!!! One of the merges failed\nExiting\n"
            local_print_log(error,'error')


def merge_final_mesh():
    """ Merge the mesh into a single mesh object. 

    Parameters
    --------------------
        None

    Returns
    -----------------
        None

    Notes
    -----------------
        None
    """
    local_print_log('=' * 80)
    local_print_log("--> Starting Final Merge")
    tic = timeit.default_timer()
    mh.run_lagrit_script('lagrit_scripts/merge_network.lgi',
                         'lagrit_logs/log_merge_all',
                         quiet=True)

    elapsed = timeit.default_timer() - tic
    local_print_log(f"--> Final merge complete. Time elapsed: {elapsed:.2e} seconds")


def check_for_final_mesh(visual_mode):
    """ Check that the final mesh was successfully created

    Parameters
    --------------------
        visual_mode : bool
            True/False for reduced meshing
    Returns
    -----------------
        None

    Notes
    -----------------
        None
    """

    local_print_log("--> Checking for final mesh")
    if visual_mode:
        mesh_name = "reduced_mesh.inp"
    else:
        mesh_name = "full_mesh.lg"

    if (os.stat(mesh_name).st_size > 0):
        local_print_log("--> Checking for final mesh: Complete")
    else:
        local_print_log(
            f"Final merge failed. Mesh '{mesh_name}' is either empty or cannot be found.", "error"
        )


def merge_network(self):
    """ Merges the individual meshed fractures into a single mesh objection. This is done in stages. First, individual fractures are merged into sub-networks, then those sub-networks are merged to form the whole network. 

    Parameters
    ----------------
        self : DFN Object

    Returns
    ----------------
        Notes

    Notes
    -----------------
        This is a driver function that class sub-functions. More details are in those sub-functions. 
    
    """
    self.print_log("Merging the mesh: Starting")
    self.create_merge_poly_scripts()
    self.create_final_merge_script()
    merge_the_fractures(self.ncpu)
    merge_final_mesh()
    check_for_final_mesh(self.visual_mode)
    self.print_log("Merging the mesh: Complete")
