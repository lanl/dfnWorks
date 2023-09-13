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
from pydfnworks.general import helper_functions as hf
from pydfnworks.dfnGen.meshing import mesh_dfn_helper as mh
from pydfnworks.dfnGen.meshing import poisson_driver as lg
from pydfnworks.dfnGen.meshing import run_meshing as run_mesh
from pydfnworks.dfnGen.meshing import general_lagrit_scripts as lgs


def mesh_network(self,
                 uniform_mesh=False,
                 slope=0.3,
                 min_dist = 0.1,
                 max_dist = 10,
                 cleanup=True,
                 strict = True,
                 quiet = True
                 ):
    """
      Mesh fracture network using LaGriT

    Parameters
    ----------
        self : object 
            DFN Class
        uniform_mesh : bool
            toggle for uniform or variable mesh. Default : False 
        slope : float
            slope of variable coarsening resolution. 
        cleanup : bool
            toggle to clean up directory (remove meshing files after a run). Default : True

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
    if self.prune_file:
        print(
            f"Loading list of fractures to remain in network from {self.prune_file}"
        )
        self.fracture_list = sort(genfromtxt(self.prune_file).astype(int))
        print("--> Retaining Fractures: ")
        print(self.fracture_list)
        print("\n")
        if self.path:
            self.create_mesh_links(self.path)
        else:
            hf.print_error("User requested pruning in meshing but did not provide path for main files.")

        if not self.visual_mode:
            self.edit_intersection_files()
    ######## Pruning scripts

    print("--> Creating scripts for LaGriT meshing")
    lg.create_poisson_user_function_script()
    if uniform_mesh:
        self.slope = 0
    else:
        self.slope = slope

    ## check for self consistency of meshing parameters
    if min_dist >= max_dist:
        hf.print_error(f"min_dist greater than or equal to max_dist.\nmin_dist : {min_dist}\nmax_dist : {max_dist}")
    self.intercept = min_dist * self.h

    if not self.prune_file:
        self.fracture_list = range(1, self.num_frac + 1)

    digits = len(str(self.num_frac))
    for index, frac_id in enumerate(self.fracture_list):
        self.create_lagrit_parameters_file(frac_id, index + 1, digits, max_dist)
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
        hf.print_warning("More processors than fractures requested.\nResetting ncpu to num_frac")
        self.ncpu = self.num_frac

    if self.mesh_fractures_header(quiet):
        hf.print_error("One or more fractures failed to mesh properly.")

    # ### Parallel runs 
    self.merge_network()

    ## checking and clean up
    if (not self.visual_mode and not self.prune_file):
        if not mh.check_dudded_points(self.dudded_points):
            mh.cleanup_meshing_files()
            if strict:
                hf.print_error("Incorrect Number of dudded points removed.")

    if not self.visual_mode:
        lgs.define_zones()

    self.gather_mesh_information()
    
    if self.prune_file:
        self.clean_up_files_after_prune()
  
    if cleanup:
        mh.cleanup_meshing_files()
        
    elapsed = timeit.default_timer() - tic
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

