"""
.. module:: meshdfn.py
   :synopsis: meshing driver for DFN 
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import os
import sys
from time import time
from numpy import genfromtxt, sort

import mesh_dfn_helper as mh 
import lagrit_scripts as lagrit 
import run_meshing as run_mesh 


def mesh_network(self, prune = False,  keep_file = [], production_mode=True, refine_factor=1, slope=2):
    '''
    Mesh fracture network using LaGriT
    '''
    print('='*80)
    print("Meshing Network Using LaGriT : Starting")
    print('='*80)
    
    num_poly, h, visual_mode, dudded_points, domain = mh.parse_params_file()

    if prune:
        print("Loading list of fractures to remain in network from %s"%keep_file)
        fracture_list = sort(genfromtxt(keep_file).astype(int))
        print fracture_list
        lagrit.edit_intersection_files(num_poly, fracture_list)
        num_poly = len(fracture_list)
    else:
        fracture_list = range(1, num_poly + 1)

    # if number of fractures is greater than number of CPUS, 
    # only use num_poly CPUs. This change is only made here, so ncpus
    # is still used in PFLOTRAN
    ncpu = min(self.ncpu, num_poly)
    lagrit.create_parameter_mlgi_file(fracture_list, h, slope=slope)
    lagrit.create_lagrit_scripts(visual_mode, ncpu)
    lagrit.create_user_functions()
    failure = run_mesh.mesh_fractures_header(fracture_list, ncpu, visual_mode, prune)
    if failure:
        mh.cleanup_dir()
        sys.exit("One or more fractures failed to mesh properly.\nExiting Program")

    n_jobs = lagrit.create_merge_poly_files(ncpu, num_poly, fracture_list, h, visual_mode, domain,self.flow_solver)
    run_mesh.merge_the_meshes(num_poly, ncpu, n_jobs, visual_mode)
    
    if (not visual_mode and not prune):    
        if not mh.check_dudded_points(dudded_points):
            mh.cleanup_dir()
            sys.exit("Incorrect Number of dudded points.\nExitingin Program")

    if production_mode:
        mh.cleanup_dir()

    if not visual_mode: 
        lagrit.define_zones()

    mh.output_meshing_report(visual_mode)


if __name__ == "__main__":
    print ('='*80)
    print '''Python Script to parse DFNGEN output and mesh it using LaGriT 

    Last Update August 1 2016 by Jeffrey Hyman
    EES - 16, LANL
    jhyman@lanl.gov
    '''
    #Production mode "ON" outputs the final results for computation, 
    #cleaning up all the temporary attributes needed during refinement.
    #Note that the visualization mode must be "OFF" in order to run
    #in produciton mode. "dfield" can also be turn ON/OFF. 
    #*1: "ON", *0: "OFF". 
    #dfield = 0

    slope = 2
    refine_dist = 0.5

    production_mode = True 
    refine_factor = 1
    ncpu = 4

    os.environ['dfnworks_PATH'] = '/home/jhyman/dfnworks/dfnworks-main/'

    # Executables    
    os.environ['python_dfn'] = '/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/2.4.1/bin/python'
    os.environ['lagrit_dfn'] = '/n/swdev/mesh_tools/lagrit/install-Ubuntu-14.04-x86_64/3.2.0/release/gcc-4.8.4/bin/lagrit'
    os.environ['connect_test'] = os.environ['dfnworks_PATH']+'DFN_Mesh_Connectivity_Test/'

    try:
        python_path = os.environ['python_dfn']
        #python_path = '/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/2.4.1/bin/python'
    except KeyError:
        print 'python_dfn not defined'
        sys.exit(1)    
    try:    
        connectivity_test = os.environ['connect_test']
        #connectivity_test = '/home/jhyman/dfnWorks/DFN_Mesh_Connectivity_Test/ConnectivityTest'
    except KeyError:
        sys.exit('connect_test undefined')    
    
    if (len(sys.argv) == 1):
        filename = 'params.txt'
        print "Number of CPU's to use (default):", ncpu
        print "Reading in file (default):", filename 

    elif (len(sys.argv) == 2):
        filename = sys.argv[1] 
        print "Reading in file:", filename 
        print "Number of CPU's to use (default):", ncpu
        
    elif (len(sys.argv) == 3):
        filename = sys.argv[1] 
        ncpu = int(sys.argv[2])
        print "Reading in file:", filename 
        print "Number of CPU's to use:", ncpu
        

     ## input checking over
    num_poly, h, visual_mode, dudded_points, domain = mh.parse_params_file()

    ncpu=min(ncpu, num_poly)

    lagrit.create_parameter_mlgi_file(num_poly, h)
    lagrit.create_lagrit_scripts(visual_mode, ncpu)
    lagrit.create_user_functions()

    failure = run_mesh.mesh_fractures_header(num_poly, ncpu, visual_mode)

    if failure:
        mh.cleanup_dir()
        sys.exit("One or more fractures failed to mesh properly.\nExiting Program")

    n_jobs = lagrit.create_merge_poly_files(ncpu, num_poly, h, visual_mode, domain)
    run_mesh.merge_the_meshes(num_poly, ncpu, n_jobs, visual_mode)
    
    if not visual_mode:    
        if not mh.check_dudded_points(dudded_points):
#            mh.cleanup_dir()
            sys.exit("Incorrect Number of dudded points.\nExitingin Program")

    if production_mode:
        mh.cleanup_dir()

    if not visual_mode: 
        lagrit.define_zones()

    mh.output_meshing_report(visual_mode)

