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
                 min_dist = 0.5,
                 max_dist = 10,
                 max_resolution_factor = 10,
                 well = False,
                 cleanup = True,
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
        min_dist : float
            Defines the minimum distance from the intersections with resolution h/2. This value is the factor of h, distance = min_dist * h
        max_dist : float
            Defines the minimum distance from the intersections with resolution max_resolution * h. This value is the factor of h, distance = max_dist * h
        max_resolution_factor : float
            Maximum factor of the mesh resolultion (max_resolution *h). Depending on the slope of the linear function and size of the fracture, this may not be realized in the mesh. 
        cleanup : bool
            toggle to clean up directory (remove meshing files after a run). Default : True
        strict : bool
            Toggle if a few mesh errors are acceptable. default is true
        quiet : bool
            Toggle to turn on/off verbose information to screen about meshing. Default is true, does not print to screen

    Returns
    -------
        None

    Notes
    ------
        1. All fractures in self.prune_file must intersect at least 1 other fracture

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
    else:
        self.fracture_list = range(1, self.num_frac + 1)

    if well:
        add_well_points_to_line_of_intersection()

    slope,intercept = mh.compute_mesh_slope_and_intercept(self.h, min_dist, max_dist, max_resolution_factor, uniform_mesh)
    digits = len(str(self.num_frac))
    ## Create user resolution function 
    print("--> Creating scripts for LaGriT meshing")
    lg.create_poisson_user_function_script()
    ## make driver files for each function 
    for index, frac_id in enumerate(self.fracture_list):
        self.create_lagrit_parameters_file(frac_id, index + 1, digits, slope, intercept, max_resolution_factor)
        ## Make viz script or regular script
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
    if (not self.visual_mode and not self.prune_file and not self.r_fram):
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

