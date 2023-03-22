"""
.. module:: mesh_dfn.py
   :synopsis: meshing driver for DFN 
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import os
import sys
import shutil
import timeit

from numpy import genfromtxt, sort
# pydfnworks Modules
from pydfnworks.dfnGen.meshing import mesh_dfn_helper as mh
from pydfnworks.dfnGen.meshing import poisson_driver as lg
from pydfnworks.dfnGen.meshing import run_meshing as run_mesh
from pydfnworks.dfnGen.meshing import general_lagrit_scripts as lgs


def mesh_network(self,
                 uniform_mesh=False,
                 slope=0.2,
                 min_dist=0.5,
                 cleanup=True):
    """
      Mesh fracture network using LaGriT

    Parameters
    ----------
        self : object 
            DFN Class
        prune : bool
            If prune is False, mesh entire network. If prune is True, mesh only fractures in self.prune_file 
        uniform_mesh : bool
            If true, mesh is uniform resolution. If False, mesh is spatially variable            
        production_mode : bool
            If True, all working files while meshing are cleaned up. If False, then working files will not be deleted
        visual_mode : None
            If the user wants to run in a different meshing mode from what is in params.txt, 
            set visual_mode = True/False on command line to override meshing mode
        coarse_factor: float
            Maximum resolution of the mesh. Given as a factor of h
        slope : float
            slope of variable coarsening resolution. 
        min_dist : float 
            Range of constant min-distance around an intersection (in units of h). 
        max_dist : float 
            Range over which the min-distance between nodes increases (in units of h)
        concurrent_samples : int
            number of new candidates sampled around an accepted node at a time.
        grid_size : float
            side length of the occupancy grid is given by H/occupancy_factor
        well_flag : bool
            If well flag is true, higher resolution around the points in 

    Returns
    -------
        None

    Notes
    ------
        1. For uniform resolution mesh, set slope = 0
        2. All fractures in self.prune_file must intersect at least 1 other fracture

    """

    print('=' * 80)
    print("Meshing DFN using LaGriT : Starting")
    print('=' * 80)
    tic = timeit.default_timer()

    mh.setup_meshing_directory()

    ######## Pruning scripts

    #     if prune:
    #         if self.prune_file == "":
    #             error = "ERROR!! User requested pruning in meshing but \
    # did not provide file of fractures to keep.\nExiting program.\n"

    #             sys.stderr.write(error)
    #             sys.exit(1)

    #         self.create_mesh_links(self.path)

    #         if self.visual_mode:
    #             print("\n--> Running in Visual Mode\n")
    #         print(
    #             f"Loading list of fractures to remain in network from {self.prune_file}"
    #         )
    #         fracture_list = sort(genfromtxt(self.prune_file).astype(int))
    #         print(fracture_list)
    #         if not self.visual_mode:
    #             lagrit.edit_intersection_files(self.num_frac, fracture_list,
    #                                            self.path)
    #         self.num_frac = len(fracture_list)

    ######## Pruning scripts

    print("--> Creating scripts for LaGriT meshing")
    lg.create_poisson_user_function_script()
    if uniform_mesh:
        self.slope = 0
    else:
        self.slope = slope
    self.intercept = min_dist * self.h

    digits = len(str(self.num_frac))
    self.fracture_list = range(1, self.num_frac + 1)

    for frac_id in self.fracture_list:
        self.create_lagrit_parameters_file(frac_id, digits)
        if self.visual_mode:
            lg.create_lagrit_reduced_mesh_script(frac_id, digits)
        else:
            lg.create_lagrit_poisson_script(frac_id, digits)

    print("--> Creating scripts for LaGriT meshing: complete")

    # ##### FOR SERIAL DEBUG ######
    # for frac_id in self.fracture_list:
    #     _, msg = run_mesh.mesh_fracture(frac_id, self.visual_mode, self.num_frac)
    #     if msg < 0:
    #         error = f"Fracture {frac_id} failed to mesh properly.\nMsg {msg}.\nExiting Program\n"
    #         sys.stderr.write(error)
    #         sys.exit(msg)
    # # ##### FOR SERIAL DEBUG ######

    # ### Parallel runs
    # if there are more processors than fractures, 
    if self.ncpu > self.num_frac:
        print("--> Warning, more processors than fractures requested.\nResetting ncpu to num_frac")
        self.ncpu = self.num_frac

    if self.mesh_fractures_header():
        error = "One or more fractures failed to mesh properly.\nExiting Program\n"
        sys.stderr.write(error)
        sys.exit(1)
    # ### Parallel runs
    
    self.merge_network()

    if (not self.visual_mode and not self.prune):
        if not mh.check_dudded_points(self.dudded_points):
            mh.cleanup_meshing_files()
            error = "Error!!! Incorrect Number of dudded points.\nExiting Program\n"
            sys.stderr.write(error)
            sys.exit(1)

    if not self.visual_mode:
        lgs.define_zones()

    if self.prune:
        mh.clean_up_files_after_prune(self)

    self.gather_mesh_information()
    elapsed = timeit.default_timer() - tic

    if cleanup:
        mh.cleanup_meshing_files()

    time_sec = elapsed
    time_min = elapsed / 60
    time_hrs = elapsed / 3600

    print("--> Total Time to Mesh Network:")
    print(
        f"--> {time_sec:.2e} seconds\t{time_min:.2e} minutes\t{time_hrs:.2e} hours"
    )
    print()
    print('=' * 80)
    print("Meshing DFN using LaGriT : Complete")
    print('=' * 80)

