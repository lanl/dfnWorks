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


def mesh_network(self, prune=False, production_mode=True, refine_factor=1, slope=2):
    ''' Mesh fracture network using LaGriT

    Parameters
    ---------
    DFN Class
    prune (bool): If prune is False, mesh entire network. If prune is True, mesh only fractures in self.prune_file 
    production_mode (bool): If True, all working files while meshing are cleaned up. If False, then working files will not be deleted
    refine_factor (float): determines distance for mesh refine meant (default=1)
    slope (float): slope of piecewise linear function determining rate of coarsening. 

    Returns
    -------
    None

    Notes
    ------
    1. For uniform resolution mesh, set slope = 0
    2. All fractures in self.prune_file must intersect at least 1 other fracture

    '''
    print('='*80)
    print("Meshing Network Using LaGriT : Starting")
    print('='*80)
    
    if prune:
        if self.prune_file== "":
            sys.exit("ERROR!! User requested pruning in meshing but \
did not provide file of fractures to keep.\nExiting program.")

        mh.create_mesh_links(self.path)
        num_poly, h, visual_mode, dudded_points, domain = mh.parse_params_file()

        print("Loading list of fractures to remain in network from %s"%self.prune_file)
        fracture_list = sort(genfromtxt(self.prune_file).astype(int))
        print fracture_list
        
        lagrit.edit_intersection_files(num_poly, fracture_list)
        num_poly = len(fracture_list)
    else:
        num_poly, h, visual_mode, dudded_points, domain = mh.parse_params_file()
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
            sys.exit("ERROR!!! Incorrect Number of dudded points.\
\nExitingin Program")

    if production_mode:
        mh.cleanup_dir()

    if not visual_mode: 
        lagrit.define_zones()

    if prune:
        mh.clean_up_files_after_prune(self.prune_file,self.path)        
    
    mh.output_meshing_report(self.local_jobname,visual_mode)
    print("--> Meshing Complete")

