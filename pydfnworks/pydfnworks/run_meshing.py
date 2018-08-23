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

def mesh_fracture(fracture_id, visual_mode, num_poly, prune):
    """Child function for parallelized meshing of fractures"""

    t = time.time()
    p = mp.current_process()
    print 'Fracture ', fracture_id, '\tstarting on ', p.name, '\n' 
    a, cpu_id = p.name.split("-")
    cpu_id = int(cpu_id)
   
    # Create Symbolic Links 
    os.symlink("polys/poly_%d.inp"%fracture_id, "poly_CPU%d.inp"%cpu_id)    
    os.symlink("parameters/parameters_%d.mlgi"%fracture_id,\
        "parameters_CPU%d.mlgi"%cpu_id)
   
    if prune:
        os.symlink('intersections/intersections_%d_prune.inp'%fracture_id,\
            'intersections_CPU%d.inp'%cpu_id)
    else:
        os.symlink('intersections/intersections_%d.inp'%fracture_id,\
            'intersections_CPU%d.inp'%cpu_id)

    cmd = os.environ['lagrit_dfn']+ ' < mesh_poly_CPU%d.lgi' \
         + ' > lagrit_logs/log_lagrit_%d'
    subprocess.call(cmd%(cpu_id,fracture_id), shell = True)

    if not visual_mode:
        cmd_check = os.environ['connect_test'] + 'ConnectivityTest' \
        + ' intersections_CPU%d.inp' \
        + ' id_tri_node_CPU%d.list ' \
        + ' mesh_%d.inp' \
        + ' %d'
        cmd_check = cmd_check%(cpu_id,cpu_id,fracture_id,fracture_id)
        failure = subprocess.call(cmd_check, shell = True)
        if failure > 0:
            print("MESH CHECKING HAS FAILED!!!!")
            print 'Fracture number ', fracture_id, '\trunning on ', p.name, '\n'

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
            os.remove('id_tri_node_CPU' + str(cpu_id) + '.list')
        except: 
            print 'Could not remove id_tri_node_CPU' + str(cpu_id) + '.list'
        try:
            os.remove('mesh_' + str(fracture_id) + '.inp')
        except:
            print 'Could not remove mesh' + str(cpu_id) + '.inp'
    else:
        failure = 0

    # Remove old links and files
    try:
        os.remove('poly_CPU' + str(cpu_id) + '.inp')
    except:
        print 'Could not remove poly_CPU' + str(cpu_id) + '.inp'
    try: 
        os.remove('intersections_CPU' + str(cpu_id) + '.inp')
    except:
        print 'Could not remove intersections_CPU' + str(cpu_id) + '.inp'
    try:
        os.remove('parameters_CPU' + str(cpu_id) + '.mlgi')
    except:
        print 'Could not remove parameters_CPU' + str(cpu_id) + '.mlgi'
    elapsed = time.time() - t

    if failure > 0:
        print 'Fracture ', fracture_id, ' out of ',  num_poly, ' complete, but mesh checking failed' 
        sys.exit("Exiting Program")
    else:
        print 'Fracture ', fracture_id, 'out of ',  num_poly, ' complete' 
        print 'Time for meshing: %0.2f seconds\n'%elapsed

def worker(work_queue, visual_mode, num_poly, prune):
    """ Worker function for parallelized meshing """    
    try:
        for fracture_id in iter(work_queue.get, 'STOP'):
            mesh_fracture(fracture_id, visual_mode, num_poly, prune)
    except: 
        #print('Error on Fracture ',fracture_id)
        pass
    return True

def mesh_fractures_header(fracture_list, ncpu, visual_mode, prune):
    """ Header function for Parallel meshing of fractures
    
    Creates a queue of fracture numbers ranging form 1, num_poly
    
    Each fractures is meshed using mesh_fracture called within the
    worker function.

    If any fracture fails to mesh properly, then a folder is created with 
    that fracture information and the fracture number is written into
    failure.txt.

    Returns:
        * True: If failure.txt is empty meaning all fractures meshed correctly
        * False: If failure.txt is not empty, then at least one fracture failed.  

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
            visual_mode, len(fracture_list), prune))
        p.daemon = True
        p.start()        
        processes.append(p)
        work_queue.put('STOP')

    for p in processes:
        p.join()

    elapsed = time.time() - t_all
    print 'Total Time to Mesh Network: %0.2f seconds'%elapsed
    elapsed /= 60.
    print '--> %0.2f Minutes'%elapsed

    if os.stat("failure.txt").st_size > 0:
        failure_list = genfromtxt("failure.txt")
        failure_flag = True 
        if type(failure_list) is list:
            failure_list = sort(failure_list)
        else: 
            print 'Fractures:', failure_list , 'Failed'
        print 'Main process exiting.'
    else:
        failure_flag = False 
        os.remove("failure.txt");
        print 'Triangulating Polygons: Complete'
    return failure_flag    


def merge_the_meshes(num_poly, ncpu, n_jobs, visual_mode):
    """ 
     Merges all the meshes together, deletes duplicate points, 
        dumps the .gmv and fehm files
    """
    print "\nMerging triangulated polygon meshes"

    # should be converted to using multiprocessing 
    for j in range(1, n_jobs + 1):
        pid = os.fork()
        if pid == 0: # clone a child job
            cmd = os.environ['lagrit_dfn']+ ' < merge_poly_part_%d.lgi ' \
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

    subprocess.call(os.environ['lagrit_dfn'] +' < merge_rmpts.lgi '\
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
