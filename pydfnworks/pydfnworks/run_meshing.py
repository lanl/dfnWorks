"""
.. module:: run_meshing.py
   :synopsis: functions to mesh fracture network in parallel 
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import subprocess
import os
import time
import multiprocessing as mp 
from shutil import copy, rmtree
from numpy import genfromtxt

def mesh_fracture(fracture_id, visual_mode, num_poly):
    """Child function for parallelized meshing of fractures

    Parameters
    ----------
    fracture_id (int): Current Fracture ID number
    visual_mode (bool): True/False for reduced meshing
    num_poly (int): Total Number of Fractures
    
    Returns
    -------
    None
    
    Notes
    -----
    If meshing fails, information about that fracture will be put into a directory failure_(fracture_id)

    """

    t = time.time()
    p = mp.current_process()
    print('Fracture %d \tstarting on %s\n'%(fracture_id,p.name)) 
    a, cpu_id = p.name.split("-")
    cpu_id = int(cpu_id)
   
    # Create Symbolic Links 
    os.symlink("polys/poly_%d.inp"%fracture_id, "poly_CPU%d.inp"%cpu_id)    
    os.symlink("parameters/parameters_%d.mlgi"%fracture_id,\
        "parameters_CPU%d.mlgi"%cpu_id)
   
    #if prune:
    #    os.symlink('intersections/intersections_%d_prune.inp'%fracture_id,\
    #        'intersections_CPU%d.inp'%cpu_id)
    #else:
    os.symlink('intersections/intersections_%d.inp'%fracture_id,\
        'intersections_CPU%d.inp'%cpu_id)

    cmd = os.environ['LAGRIT_EXE']+ ' < mesh_poly_CPU%d.lgi' \
         + ' > lagrit_logs/log_lagrit_%d'
    subprocess.call(cmd%(cpu_id,fracture_id), shell = True)

    if not visual_mode:
        cmd_check = os.environ['CONNECT_TEST_EXE'] \
        + ' intersections_CPU%d.inp' \
        + ' id_tri_node_CPU%d.list ' \
        + ' mesh_%d.inp' \
        + ' %d'
        cmd_check = cmd_check%(cpu_id,cpu_id,fracture_id,fracture_id)
        failure = subprocess.call(cmd_check, shell = True)
        if failure > 0:
            print("MESH CHECKING HAS FAILED!!!!")
            print('Fracture %d \tstarting on %s\n'%(fracture_id,p.name)) 

            with open("failure.txt", "a") as failure_file:
                failure_file.write("%d\n"%fracture_id)

            folder='failure_'+str(fracture_id)
            os.mkdir(folder)
            copy('mesh_'+str(fracture_id)+'.inp', folder + '/')
            copy(str(fracture_id)+'_mesh_errors.txt', folder + '/')
            copy('poly_CPU'+str(cpu_id)+'.inp', folder + '/')
            copy('id_tri_node_CPU'+str(cpu_id)+'.list', folder + '/')
            copy('intersections_CPU'+str(cpu_id)+'.inp',  folder +'/')    
            copy('lagrit_logs/log_lagrit_'+str(fracture_id),  folder +'/')
            copy('parameters_CPU' + str(cpu_id) + '.mlgi', folder +'/')    
            copy('mesh_poly_CPU' + str(cpu_id) + '.lgi', folder + '/')    
            copy('user_function.lgi', folder +'/')    
            copy('user_function2.lgi', folder +'/')   
        try:
            os.remove('id_tri_node_CPU%d.list'%cpu_id)
        except: 
            print('Could not remove id_tri_node_CPU%d.list'%cpu_id)
        try:
            os.remove('mesh_%d.inp'%fracture_id)
        except:
            print('Could not remove mesh_%d.inp'%fracture_id)
    else:
        failure = 0

    # Remove old links and files
    files = ['poly_CPU%d.inp', 'intersections_CPU%d.inp', 'parameters_CPU%d.mlgi']
    for f in files:
        fp=f%cpu_id
        try:
            os.remove(fp)
        except:
            print('Could not remove %s'%fp)
    elapsed = time.time() - t

    if failure > 0:
        print('Fracture %d out of %d complete, but mesh checking failed'%(fracture_id,num_poly))
        sys.exit("Exiting Program")
    else:
        print('Fracture %d out of %d complete'%(fracture_id,num_poly))
        print('Time for meshing: %0.2f seconds\n'%elapsed)

def worker(work_queue, visual_mode, num_poly):
    """ Worker function for parallelized meshing 
    
    Parameters
    ----------
    work_queue (multiprocessing queue): Queue fractures still to be meshed
    visual_mode (bool): True/False for reduced meshing
    num_poly (int): Total Number of Fractures

    Returns
    -------
    True if job is complete

    Notes:
    -----
    None   
    
    """    
    try:
        for fracture_id in iter(work_queue.get, 'STOP'):
            mesh_fracture(fracture_id, visual_mode, num_poly )
    except: 
        #print('Error on Fracture ',fracture_id)
        pass
    return True

def mesh_fractures_header(fracture_list, ncpu, visual_mode):
    """ Header function for Parallel meshing of fractures
    
    Creates a queue of fracture numbers ranging form 1, num_poly
    
    Each fractures is meshed using mesh_fracture called within the
    worker function.

    If any fracture fails to mesh properly, then a folder is created with 
    that fracture information and the fracture number is written into
    failure.txt.

    Parameters
    ----------
    fracture_list (list): Fractures to be meshed
    visual_mode (bool): True/False for reduced meshing
    num_poly (int): Total Number of Fractures

    Returns
    -------
    True: If failure.txt is empty meaning all fractures meshed correctly
    False: If failure.txt is not empty, then at least one fracture failed.  

    Notes
    -----
    None

    """ 
    t_all = time.time()

    print "\nTriangulate %d fractures:"%len(fracture_list)
    try:
        rmtree('lagrit_logs')
    except OSError:
        pass
    os.mkdir('lagrit_logs')
    
    # create failure log file
    f = open('failure.txt', 'w')
    f.close()

    print("Meshing using %d CPUS"%ncpu)

    #fracture_list = range(1, num_poly + 1)
    work_queue = mp.Queue()   # reader() reads from queue
    processes = []

    for i in fracture_list:
        work_queue.put(i)

    for i in xrange(ncpu):
        p = mp.Process(target=worker, args=(work_queue, \
            visual_mode, len(fracture_list)))
        p.daemon = True
        p.start()        
        processes.append(p)
        work_queue.put('STOP')

    for p in processes:
        p.join()

    elapsed = time.time() - t_all
    print('Total Time to Mesh Network: %0.2f seconds'%elapsed)
    elapsed /= 60.
    print('--> %0.2f Minutes'%elapsed)

    if os.stat("failure.txt").st_size > 0:
        failure_list = genfromtxt("failure.txt")
        failure_flag = True 
        if type(failure_list) is list:
            failure_list = sort(failure_list)
        else: 
            print('Fractures:', failure_list , 'Failed')
        print('Main process exiting.')
    else:
        failure_flag = False 
        os.remove("failure.txt");
        print('Triangulating Polygons: Complete')
    return failure_flag    


def merge_the_meshes(num_poly, ncpu, n_jobs, visual_mode):
    """Runs the LaGrit Scripts to merge meshes into final mesh 

    Parameters
    ----------
    num_poly (int): Number of Fractures
    npcu (int): Number of Processors
    n_jobs (int): Number of mesh pieces
    visual_mode (bool): True/False for reduced meshing

    Returns
    -------
    None

    Notes
    -----
    None

    """
    print "\nMerging triangulated polygon meshes"

    # should be converted to using multiprocessing 
    for j in range(1, n_jobs + 1):
        pid = os.fork()
        if pid == 0: # clone a child job
            cmd = os.environ['LAGRIT_EXE']+ ' < merge_poly_part_%d.lgi ' \
                + '> log_merge_poly_part%d' 
            subprocess.call(cmd%(j,j), shell = True)
            os._exit(0)
        else:
            print 'Merging part ', j, ' of ', n_jobs 

    # wait for all child processes to complete
    j = 0
    while j < n_jobs:
        (pid, status) = os.waitpid(0,os.WNOHANG)
        if pid > 0:
            print 'Process ' + str(j+1) + ' finished'
            j += 1 

    print("Starting Final Merge")

    subprocess.call(os.environ['LAGRIT_EXE'] +' < merge_rmpts.lgi '\
        + ' > log_merge_all.txt', shell=True) # run remove points
    # Check log_merge_all.txt for LaGriT complete successfully
    if not visual_mode:
        if(os.stat("full_mesh.lg").st_size > 0):
            print("Final Merge Complete")
            print("Merging triangulated polygon meshes: Complete\n")
        else:
            sys.exit("Final Merge Failed")
    else:
        if os.stat("reduced_mesh.inp").st_size > 0:
            print("Final Merge Complete")
            print("Merging triangulated polygon meshes: Complete\n")
        else:
            sys.exit("Final Merge Failed")
