"""
.. module:: run_meshing.py
   :synopsis: functions to mesh fracture network in parallel 
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import subprocess
import os
import sys
import time
import multiprocessing as mp
from shutil import copy, rmtree
from numpy import genfromtxt
from pydfnworks.dfnGen.meshing import mesh_dfn_helper as mh


def mesh_fracture(fracture_id, visual_mode, num_poly):
    """Child function for parallelized meshing of fractures

    Parameters
    ----------
        fracture_id : int
            Current Fracture ID number
        visual_mode : bool
            True/False for reduced meshing
        num_poly : int 
            Total Number of Fractures in the DFN
        poisson : bool
            True/False if running with Poisson sampling 
    
    Returns
    -------
        None
    
    Notes
    -----
    If meshing fails, information about that fracture will be put into a directory failure_(fracture_id)

    """

    tic = time.time()
    p = mp.current_process()
    digits = len(str(num_poly))
    print(
        f"--> Fracture {fracture_id:0{digits}d} out of {num_poly} is starting on {p.name}"
    )

    _, cpu_id = p.name.split("-")
    cpu_id = int(cpu_id)-16

    # Create Symbolic Links
    os.symlink(f"polys/poly_{fracture_id}.inp", f"poly_CPU{cpu_id}.inp")

    os.symlink(f"parameters/parameters_{fracture_id}.mlgi",\
        f"parameters_CPU{cpu_id}.mlgi")

    if not visual_mode:
        os.symlink(f"intersections/intersections_{fracture_id}.inp",\
            f"intersections_CPU{cpu_id}.inp")

        os.symlink(f"points/points_{fracture_id}.xyz",
                   f"points_CPU{cpu_id}.xyz")

    mh.run_lagrit_script(
        f"mesh_poly_CPU{cpu_id}.lgi",
        output_file=f"lagrit_logs/log_lagrit_{fracture_id:0{digits}d}.out",
        quite=True)

    if not visual_mode:
        ## Once meshing is complete, check if the lines of intersection are in the final mesh
        cmd_check = f"{os.environ['CONNECT_TEST_EXE']} \
            intersections_CPU{cpu_id}.inp \
            id_tri_node_CPU{cpu_id}.list \
            mesh_{fracture_id}.inp \
            {fracture_id}"

        failure = subprocess.call(cmd_check, shell=True)

        # If the lines of intersection are not in the final mesh, put depending files
        # into a directory for debugging.
        if failure:
            print(f"--> WARNING: MESH CHECKING FAILED on {fracture_id}!!!!")

            with open("failure.txt", "a") as failure_file:
                failure_file.write(f"{fracture_id}\n")

            folder = f"failure_{fracture_id}/"
            try:
                os.mkdir(folder)
            except:
                print(f"Warning! Unable to make new folder: {folder}")

            copy(f"mesh_{fracture_id}.inp", folder)
            copy(f"{fracture_id}_mesh_errors.txt", folder)
            copy(f"poly_CPU{cpu_id}.inp", folder)
            copy(f"id_tri_node_CPU{cpu_id}.list", folder)
            copy(f"intersections_CPU{cpu_id}.inp", folder)
            copy(f"lagrit_logs/log_lagrit_{fracture_id:0{digits}d}.out",
                 folder)
            copy(f"parameters_CPU{cpu_id}.mlgi", folder)
            copy(f"mesh_poly_CPU{cpu_id}.lgi", folder)

            ## remove links
            files = [
                f'poly_CPU{cpu_id}.inp', f'intersections_CPU{cpu_id}.inp',
                f'points_CPU{cpu_id}.xyz', f'parameters_CPU{cpu_id}.mlgi'
            ]
            for f in files:
                try:
                    os.unlink(f)
                except:
                    print(f'Warning: Could unlink {f}')
            # exit run
            sys.stderr.write(error)
            sys.exit(1)

        # Mesh checking was a success. Remove check files and move on
        files = [f"id_tri_node_CPU{cpu_id}.list", f"mesh_{fracture_id}.inp"]
        for f in files:
            try:
                os.remove(f)
            except:
                print(f"Could not remove {f}\n")
    else:
        failure = 0

    # Remove old links and files
    if visual_mode:
        files = [f'poly_CPU{cpu_id}.inp', f'parameters_CPU{cpu_id}.mlgi']
    else:
        files = [
            f'poly_CPU{cpu_id}.inp', f'intersections_CPU{cpu_id}.inp',
            f'points_CPU{cpu_id}.xyz', f'parameters_CPU{cpu_id}.mlgi'
        ]
    for f in files:
        try:
            os.unlink(f)
        except:
            print(f'Warning: Could unlink {f}')

    elapsed = time.time() - tic

    print(
        f"--> Fracture {fracture_id:0{digits}d} out of {num_poly} is complete on {p.name}. Time required: {elapsed:.2f} seconds\n"
    )


def single_worker(work_queue, visual_mode, num_poly):
    """ Worker function for parallelized meshing 
    
    Parameters
    ----------
        work_queue : multiprocessing queue
            Queue of fractures to be meshed
        visual_mode : bool
            True/False for reduced meshing
        num_poly : int
            Total Number of Fractures

    Returns
    -------
        True : bool
            If job is complete

"""
    try:
        for fracture_id in iter(work_queue.get, 'STOP'):
            mesh_fracture(fracture_id, visual_mode, num_poly)
    except:
        #print('Error on Fracture ',fracture_id)
        pass
    return True


def mesh_fractures_header(fracture_list, ncpu, visual_mode):
    """ Header function for Parallel meshing of fractures
    
    Creates a queue of fracture numbers ranging from 1, num_poly
    
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
        num_poly : int
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
    t_all = time.time()
    print()
    print('=' * 80)
    print(
        f"\n--> Triangulating {len(fracture_list)} fractures using {ncpu} processors\n\n"
    )

    if os.path.isdir('lagrit_logs'):
        rmtree('lagrit_logs')
    os.mkdir('lagrit_logs')

    # create failure log file
    f = open('failure.txt', 'w')
    f.close()

    #fracture_list = range(1, num_poly + 1)
    work_queue = mp.Queue()  # reader() reads from queue
    processes = []

    for i in fracture_list:
        work_queue.put(i)

    for i in range(ncpu):
        p = mp.Process(target=single_worker, args=(work_queue, \
            visual_mode, len(fracture_list)))
        p.daemon = True
        p.start()
        processes.append(p)
        work_queue.put('STOP')

    for p in processes:
        p.join()

    elapsed = (time.time() - t_all)

    if os.stat("failure.txt").st_size > 0:
        failure_list = genfromtxt("failure.txt")
        failure_flag = True
        if type(failure_list) is list:
            failure_list = sort(failure_list)
        else:
            print('--> Fractures:', failure_list, 'Failed')
        print('--> Main process exiting.')
    else:
        failure_flag = False
        os.remove("failure.txt")
        print('--> Triangulating Polygons: Complete')

        if elapsed > 60:
            print(f"--> Total Time to Mesh Network: {elapsed:.2f} minutes")
        else:
            print(f"--> Total Time to Mesh Network: {elapsed:.2f} seconds")

        print('=' * 80)
    return failure_flag


def merge_worker(job):
    """Parallel worker for merge meshes into final mesh 

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

    print(f"--> Starting merge: {job}")
    tic = time.time()

    if mh.run_lagrit_script(f"merge_poly_part_{job}.lgi",
                            f"lagrit_logs/log_merge_poly_part{job}.out",
                            quite=True):
        print(f"Error {job} failed")
        return True

    toc = time.time()
    elapsed = toc - tic
    print(
        f"--> Merge Number {job} Complete. Time elapsed: {elapsed:.2f} seconds"
    )
    return False


def merge_the_meshes(num_poly, ncpu, n_jobs, visual_mode):
    """Runs the LaGrit Scripts to merge meshes into final mesh 

    Parameters
    ----------
        num_poly : int
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
    print('=' * 80)
    if n_jobs == 1:
        print(f"--> Merging triangulated fracture meshes using {n_jobs} processor")
    else:
        print(f"--> Merging triangulated fracture meshes using {n_jobs} processors")

    jobs = range(1, n_jobs + 1)

    num_cpu = len(jobs)
    pool = mp.Pool(num_cpu)
    outputs = pool.map(merge_worker, jobs)
    pool.close()
    pool.join()
    pool.terminate()

    for output in outputs:
        if output:
            error = "ERROR!!! One of the merges failed\nExiting\n"
            sys.stderr.write(error)
            sys.exit(1)

    print('=' * 80)
    print("--> Starting Final Merge")
    tic = time.time()
    mh.run_lagrit_script('merge_rmpts.lgi',
                         'lagrit_logs/log_merge_all.out',
                         quite=True)
    toc = time.time()
    elapsed = toc - tic
    print(f"--> Final merge took {elapsed:.2f} seconds")

    if not visual_mode:
        if (os.stat("full_mesh.lg").st_size > 0):
            print("--> Final merge successful")

        else:
            error = "ERROR: Final merge Failed\n"
            sys.stderr.write(error)
            sys.exit(1)

    else:
        if os.stat("reduced_mesh.inp").st_size > 0:
            print("--> Final merge successful")
        else:
            error = "ERROR: Final merge Failed\n"
            sys.stderr.write(error)
            sys.exit(1)
    print('=' * 80)
