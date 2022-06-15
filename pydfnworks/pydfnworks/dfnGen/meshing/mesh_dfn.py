"""
.. module:: mesh_dfn.py
   :synopsis: meshing driver for DFN 
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import os
import sys
from numpy import genfromtxt, sort
# pydfnworks Modules
from pydfnworks.dfnGen.meshing import mesh_dfn_helper as mh
from pydfnworks.dfnGen.meshing import lagrit_scripts_poisson_disc as lagrit
from pydfnworks.dfnGen.meshing import run_meshing as run_mesh
from pydfnworks.dfnGen.meshing.poisson_disc.poisson_functions import single_fracture_poisson, dump_poisson_params


def mesh_network(self,
                 prune=False,
                 uniform_mesh=False,
                 production_mode=True,
                 coarse_factor=8,
                 slope=0.1,
                 min_dist=1,
                 max_dist=40,
                 concurrent_samples=10,
                 grid_size=10,
                 well_flag=False):
    ''' Mesh fracture network using LaGriT

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

    '''

    print('=' * 80)
    print("Meshing DFN using LaGriT : Starting")
    print('=' * 80)

    if uniform_mesh:
        slope = 0  # Setting slope = 0, results in a uniform mesh

    if prune:
        if self.prune_file == "":
            error = "ERROR!! User requested pruning in meshing but \
did not provide file of fractures to keep.\nExiting program.\n"

            sys.stderr.write(error)
            sys.exit(1)

        self.create_mesh_links(self.path)
        if self.visual_mode:
            print("\n--> Running in Visual Mode\n")
        print(
            f"Loading list of fractures to remain in network from {self.prune_file}"
        )
        fracture_list = sort(genfromtxt(self.prune_file).astype(int))

        if not self.visual_mode:
            lagrit.edit_intersection_files(self.num_frac, fracture_list, self.path)
        self.num_frac = len(fracture_list)

    else:
        fracture_list = range(1, self.num_frac)

    # if number of fractures is greater than number of CPUS,
    # only use num_poly CPUs. This change is only made here, so ncpus
    # is still used in PFLOTRAN
    ncpu = min(self.ncpu, self.num_frac)

    print('=' * 80)
    if self.visual_mode:
        print("\n--> Running in Visual Mode\n")
    else:
        print("\n--> Running in Full Meshing Mode\n")
    print('=' * 80)

    lagrit.create_parameter_mlgi_file(fracture_list, self.h, slope=slope)
    if self.visual_mode:
        lagrit.create_lagrit_scripts_reduced_mesh(fracture_list)
    else:

        # Check for well points well.
        if well_flag:
            if not os.path.isfile("well_points.dat"):
                error = "ERROR!!! Well flag is set to True in DFN.mesh_network(), but file 'well_points.dat' cannot be found.\nPlease run DFN.find_well_intersection_points() for each well prior to meshing\nOr set well_flag = False\nExiting Program\n"
                sys.stderr.write(error)
                sys.exit(1)

        dump_poisson_params(self.h, coarse_factor, slope, min_dist, max_dist,
                            concurrent_samples, grid_size, well_flag)

        lagrit.create_lagrit_scripts_poisson(fracture_list)
    ##### FOR SERIAL DEBUG ######
    #     for f in fracture_list:
    #         run_mesh.mesh_fracture(f, visual_mode, len(fracture_list))
    # exit()

    print('=' * 80)

    failure = run_mesh.mesh_fractures_header(fracture_list, ncpu, self.visual_mode, self.h)
    if failure:
        mh.cleanup_dir()
        error = "One or more fractures failed to mesh properly.\nExiting Program\n"
        sys.stderr.write(error)
        sys.exit(1)

    n_jobs = lagrit.create_merge_poly_files(ncpu, self.num_frac, fracture_list, self.h,
                                            self.visual_mode, self.domain,
                                            self.flow_solver)

    run_mesh.merge_the_meshes( self.num_frac, ncpu, n_jobs, self.visual_mode)

    if (not self.visual_mode and not prune):
        if not mh.check_dudded_points(self.dudded_points):
            mh.cleanup_dir()
            error = "ERROR!!! Incorrect Number of dudded points.\nExiting Program\n"
            sys.stderr.write(error)
            sys.exit(1)

    if production_mode:
        mh.cleanup_dir()

    if not self.visual_mode:
        lagrit.define_zones()

    if prune:
        mh.clean_up_files_after_prune(self)

    mh.output_meshing_report(self.local_jobname, self.visual_mode)
    print('=' * 80)
    print("Meshing DFN using LaGriT : Complete")
    print('=' * 80)
