"""
.. file:: meshdfn.py
   :synopsis: meshing driver for DFN 
   :version: 1.0
   :maintainer: Jeffrey Hyman, Carl Gable, Nathaniel Knapp
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import os
import sys
from time import time

import mesh_dfn_helper as mh 
import lagrit_scripts as lagrit 
import run_meshing as run_mesh 

def mesh_network(self, production_mode=True, refine_factor=1, slope=2):
    '''
    Mesh Fracture Network using ncpus and lagrit
    meshing file is separate file: dfnGen_meshing.py
    '''
    print('='*80)
    print("Meshing Network Using LaGriT : Starting")
    print('='*80)
    
    num_poly, h, visual_mode, dudded_points, domain = mh.parse_params_file()

    lagrit.create_parameter_mlgi_file(num_poly, h, slope=slope)

    lagrit.create_lagrit_scripts(visual_mode, self._ncpu)
    lagrit.create_user_functions()

    failure = run_mesh.mesh_fractures_header(num_poly, self._ncpu, visual_mode)

    if failure:
        mesh.cleanup_dir()
        sys.exit("One or more fractures failed to mesh properly.\nExiting Program")

    n_jobs = lagrit.create_merge_poly_files(self._ncpu, num_poly, visual_mode)

    run_mesh.merge_the_meshes(num_poly, self._ncpu, n_jobs, visual_mode)
    
    if not visual_mode:    
        if not mh.check_dudded_points(dudded_points):
            mh.cleanup_dir()
            sys.exit("Incorrect Number of dudded points.\nExitingin Program")

    if production_mode:
        mh.cleanup_dir()

    if not visual_mode: 
        lagrit.define_zones(h,domain)

    mh.output_meshing_report(visual_mode)


if __name__ == "__main__":
    print ('='*80)
    os.system("date")
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

    os.environ['DFNWORKS_PATH'] = '/home/nknapp/dfnworks-main/'

    # Executables    
    os.environ['python_dfn'] = '/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/2.4.1/bin/python'
    os.environ['lagrit_dfn'] = '/n/swdev/mesh_tools/lagrit/install-Ubuntu-14.04-x86_64/3.2.0/release/gcc-4.8.4/bin/lagrit'
    os.environ['connect_test'] = os.environ['DFNWORKS_PATH']+'/DFN_Mesh_Connectivity_Test/ConnectivityTest'

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
        print "Number of CPU's to use (default):", ncpu
    
    elif (len(sys.argv) == 2):
        ncpu = int(sys.argv[1])
        print "Number of CPU's to use:", ncpu
    

    ## input checking over
    ## input checking over
    num_poly, h, visual_mode, dudded_points, domain = mh.parse_params_file()

    lagrit.create_parameter_mlgi_file(num_poly, h)

    lagrit.create_lagrit_scripts(visual_mode, ncpu)
    lagrit.create_user_functions()

    failure = run_mesh.mesh_fractures_header(num_poly, ncpu, visual_mode)

    if failure:
        mesh.cleanup_dir()
        sys.exit("One or more fractures failed to mesh properly.\nExiting Program")

    n_jobs = lagrit.create_merge_poly_files(ncpu, num_poly, visual_mode)

    run_mesh.merge_the_meshes(num_poly, ncpu, n_jobs, visual_mode)
    
    if not visual_mode:    
        if not mh.check_dudded_points(dudded_points):
            mh.cleanup_dir()
            sys.exit("Incorrect Number of dudded points.\nExitingin Program")

    if production_mode:
        mh.cleanup_dir()

    if not visual_mode: 
        lagrit.define_zones(h,domain)

    mh.output_meshing_report(visual_mode)

