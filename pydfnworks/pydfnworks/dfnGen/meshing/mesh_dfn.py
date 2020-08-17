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
                 slope=0.05,
                 max_dist=10,
                 min_dist=1,
                 concurrent_samples=10,
                 grid_size=100,
                 visual_mode=None):
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
        slope : float 
            Slope of piecewise linear function determining rate of coarsening. 
        visual_mode : None
            If the user wants to run in a different meshing mode from what is in params.txt, set visual_mode = True/False on command line to override meshing mode

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

        mh.create_mesh_links(self.path)
        num_poly, h, params_visual_mode, dudded_points, domain = mh.parse_params_file(
        )
        if visual_mode == None:
            visual_mode = params_visual_mode

        print(
            f"Loading list of fractures to remain in network from {self.prune_file}"
        )
        fracture_list = sort(genfromtxt(self.prune_file).astype(int))
        print(fracture_list)
        if not visual_mode:
            lagrit.edit_intersection_files(num_poly, fracture_list, self.path)
        num_poly = len(fracture_list)

    else:
        num_poly, h, params_visual_mode, dudded_points, domain = mh.parse_params_file(
        )
        if visual_mode == None:
            visual_mode = params_visual_mode

        fracture_list = range(1, num_poly + 1)

    # if number of fractures is greater than number of CPUS,
    # only use num_poly CPUs. This change is only made here, so ncpus
    # is still used in PFLOTRAN
    ncpu = min(self.ncpu, num_poly)

    print('=' * 80)
    lagrit.create_parameter_mlgi_file(fracture_list, h, slope=slope)
    if visual_mode:
        lagrit.create_lagrit_scripts_reduced_mesh(ncpu)
    else:
        dump_poisson_params(h,
                            A=slope,
                            R=max_dist,
                            F=min_dist,
                            concurrent_samples=concurrent_samples,
                            grid_size=grid_size)

        lagrit.create_lagrit_scripts_poisson(fracture_list)
        
    print('=' * 80)

    failure = run_mesh.mesh_fractures_header(fracture_list, ncpu, visual_mode,
                                             h)
    if failure:
        mh.cleanup_dir()
        error = "One or more fractures failed to mesh properly.\nExiting Program\n"
        sys.stderr.write(error)
        sys.exit(1)

    n_jobs = lagrit.create_merge_poly_files(ncpu, num_poly, fracture_list, h,
                                            visual_mode, domain,
                                            self.flow_solver)

    run_mesh.merge_the_meshes(num_poly, ncpu, n_jobs, visual_mode)

    if (not visual_mode and not prune):
        if not mh.check_dudded_points(dudded_points):
            mh.cleanup_dir()
            error = "ERROR!!! Incorrect Number of dudded points.\nExiting Program\n"
            sys.stderr.write(error)
            sys.exit(1)

    if production_mode:
        mh.cleanup_dir()

    if not visual_mode:
        lagrit.define_zones()

    if prune:
        mh.clean_up_files_after_prune(self)

    mh.output_meshing_report(self.local_jobname, visual_mode)
    print('=' * 80)
    print("Meshing DFN using LaGriT : Complete")
    print('=' * 80)
