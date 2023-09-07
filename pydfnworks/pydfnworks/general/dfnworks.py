__author__ = "Jeffrey Hyman, Satish Karra"
__version__ = "2.7"
__maintainer__ = "Jeffrey Hyman"
__email__ = "jhyman@lanl.gov"
"""
DFN class. 
"""

import os
import sys
import ntpath
from datetime import datetime
from time import time


class DFNWORKS():
    '''
    Class for DFN Generation and meshing
    
    Attributes:
        * jobname: name of job, also the folder where output files are stored
        * ncpu: number of CPUs used in the job
        * dfnGen file: the name of the dfnGen input file
        * dfnFlow file: the name of the dfnFlow input file
        * dfnTrans file: the name of the dfnFlow input file
        * local prefix: indicates that the name contains only the most local directory
        * vtk_file: the name of the VTK file
        * inp_file: the name of the INP file
        * uge_file: the name of the UGE file
        * mesh_type: the type of mesh
        * perm_file: the name of the file containing permeabilities 
        * aper_file: the name of the file containing apertures 
        * perm_cell file: the name of the file containing cell permeabilities 
        * aper_cell_file: the name of the file containing cell apertures
        * freeze: indicates whether the class attributes can be modified
        * h : FRAM length scale 
    '''

    from pydfnworks.general.paths import define_paths, print_paths
    from pydfnworks.general.legal import legal

    from pydfnworks.general.images import failure, success
    from pydfnworks.general.general_functions import dump_time, print_run_time, print_parameters, print_log, go_home, to_pickle, from_pickle

    # dfnGen functions
    import pydfnworks.dfnGen

    from pydfnworks.dfnGen.generation.input_checking.check_input import check_input, print_domain_parameters
    from pydfnworks.dfnGen.generation.generator import dfn_gen, make_working_directory, create_network, parse_params_file, gather_dfn_gen_output, assign_hydraulic_properties, grab_polygon_data
    from pydfnworks.dfnGen.generation.output_report.gen_output import output_report
    from pydfnworks.dfnGen.generation.hydraulic_properties import generate_hydraulic_values, dump_hydraulic_values, dump_aperture, dump_perm, dump_transmissivity, dump_fracture_info, set_fracture_hydraulic_values
    from pydfnworks.dfnGen.generation.stress import stress_based_apertures
    from pydfnworks.dfnGen.generation.input_checking.parameter_dictionaries import load_parameters
    from pydfnworks.dfnGen.generation.input_checking.fracture_family import add_fracture_family, print_family_information
    from pydfnworks.dfnGen.generation.input_checking.add_fracture_family_to_params import write_fracture_families, reorder_fracture_families
    from pydfnworks.dfnGen.generation.input_checking.user_defined_fracture_functions import add_user_fract, add_user_fract_from_file, write_user_fractures_to_file, print_user_fracture_information

    from pydfnworks.dfnGen.meshing.mesh_dfn import mesh_network
    from pydfnworks.dfnGen.meshing.mesh_dfn_helper import inp2gmv, create_mesh_links, inp2vtk_python, gather_mesh_information
    from pydfnworks.dfnGen.meshing.add_attribute_to_mesh import add_variable_to_mesh

    from pydfnworks.dfnGen.meshing.udfm.map2continuum import map_to_continuum
    from pydfnworks.dfnGen.meshing.udfm.map2continuum_helper import in_domain, gather_points
    from pydfnworks.dfnGen.meshing.udfm.upscale import upscale
    from pydfnworks.dfnGen.meshing.udfm.false_connections import check_false_connections
    from pydfnworks.dfnGen.well_package.wells import tag_well_in_mesh, find_well_intersection_points, combine_well_boundary_zones, cleanup_wells, run_find_well_intersection_points, convert_well_to_polyline_avs, well_point_of_intersection, expand_well

    from pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_ecpm import mapdfn_ecpm 
    from pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_tag_cells import mapdfn_tag_cells
    from pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_upscale import mapdfn_upscale
    from pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_effective_perm import mapdfn_effective_perm

    from pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_ecpm import mapdfn_ecpm 
    from pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_tag_cells import mapdfn_tag_cells
    from pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_upscale import mapdfn_upscale

    from pydfnworks.dfnGen.meshing.dfm.mesh_dfm import mesh_dfm

    # dfnFlow
    import pydfnworks.dfnFlow
    from pydfnworks.dfnFlow.flow import dfn_flow, create_dfn_flow_links, set_flow_solver
    from pydfnworks.dfnFlow.pflotran import lagrit2pflotran, pflotran, parse_pflotran_vtk_python, pflotran_cleanup, write_perms_and_correct_volumes_areas, zone2ex, dump_h5_files
    from pydfnworks.dfnFlow.fehm import correct_stor_file, fehm
    from pydfnworks.dfnFlow.mass_balance import effective_perm

    # dfnTrans
    import pydfnworks.dfnTrans
    from pydfnworks.dfnTrans.transport import dfn_trans, copy_dfn_trans_files, run_dfn_trans, create_dfn_trans_links, check_dfn_trans_run_files

    # dfnGraph
    # dfnGraph
    import pydfnworks.dfnGraph
    from pydfnworks.dfnGraph.dfn2graph import create_graph, dump_json_graph, load_json_graph, plot_graph, dump_fractures, add_fracture_source, add_fracture_target
    from pydfnworks.dfnGraph.pruning import k_shortest_paths_backbone, greedy_edge_disjoint, current_flow_threshold
    from pydfnworks.dfnGraph.graph_flow import run_graph_flow, compute_dQ
    from pydfnworks.dfnGraph.graph_transport import run_graph_transport

    def __init__(self,
                 jobname=None,
                 ncpu=4,
                 dfnGen_file=None,
                 dfnFlow_file=None,
                 dfnTrans_file=None,
                 path=None,
                 prune_file=None,
                 flow_solver="PFLOTRAN",
                 inp_file="full_mesh.inp",
                 uge_file="full_mesh.uge",
                 mat_file='materialid.dat',
                 stor_file=None,
                 vtk_file=None,
                 num_nodes=None,
                 mesh_type='dfn',
                 cell_based_aperture=False,
                 store_polygon_data=True,
                 pickle_file=None):
        self.num_frac = int
        self.h = float
        self.visual_mode = bool
        self.dudded_points = int
        self.domain = {'x': 0, 'y': 0, 'z': 0}


        self.aper_cell_file = 'aper_node.dat'
        self.perm_cell_file = 'perm_node.dat'
        self.aper_file = 'aperture.dat'
        self.perm_file = 'perm.dat'

        self.fracture_families = []
        self.user_ell_params = []
        self.user_rect_params = []
        self.user_poly_params = []

        self.polygons = dict

        self.material_ids = float

        self.num_nodes = num_nodes
        self.vtk_file = vtk_file
        self.inp_file = inp_file
        self.uge_file = uge_file
        self.mat_file = mat_file
        self.stor_file = stor_file
        self.flow_solver = flow_solver

        self.cell_based_aperture = cell_based_aperture
        self.path = path
        self.prune_file = prune_file
        self.logging = False
        self.store_polygon_data = store_polygon_data

        ## check is define_paths has been run yet
        if not 'dfnworks_PATH' in os.environ:

            self.define_paths()
            self.legal()

        # try:
        #     os.remove('dfnWorks.log') #Remove the old log file
        #     print("Creating New Log File (dfnWorks.log)")
        #     print("")
        # except:
        #     print("Creating New Log File (dfnWorks.log)")
        #     print("")
        print("\n--> Creating DFN Object: Starting")

        if pickle_file:
            print(f"--> Loading DFN from pickled object file {pickle_file}")
            self.from_pickle(pickle_file)

        if jobname:
            self.jobname = jobname
            self.local_jobname = ntpath.basename(self.jobname)
        else:
            self.jobname = os.getcwd() + os.sep + "output"
            self.local_jobname = "output"

        if dfnGen_file:
            self.dfnGen_file = dfnGen_file
            self.local_dfnGen_file = ntpath.basename(self.dfnGen_file)
            self.output_file = ntpath.basename(self.dfnGen_file)
        else:
            self.dfnGen_file = self.local_jobname + "_dfnGen_input.dat"
            self.local_dfnGen_file = self.local_jobname + "_dfnGen_input.dat"
            self.output_file = self.local_jobname + "_dfnGen_output_file.dat"

        if dfnFlow_file:
            self.dfnFlow_file = dfnFlow_file
            self.local_dfnFlow_file = ntpath.basename(self.dfnFlow_file)
        else:
            self.dfnFlow_file = None
            self.local_dfnFlow_file = None

        if dfnTrans_file:
            self.dfnTrans_file = dfnTrans_file
            self.local_dfnTrans_file = ntpath.basename(self.dfnTrans_file)
        else:
            self.dfnTrans_file = None
            self.local_dfnTrans_file = None

        self.ncpu = ncpu
        self.params, self.mandatory_params = self.load_parameters()

        # if logging:
        #     print("--> Writting output to log file.")
        #     import logging
        #     logging.basicConfig(filename= self.local_jobname + "_run_log.txt", level=logging.DEBUG,
        #             format="%(asctime)s %(message)s")

        self.start_time = time()
        self.print_parameters()
        print("\n--> Creating DFN Object: Complete")


#     def __del__(self):
#         print("=" * 80)
#         print(f"--> {self.local_jobname} completed/exited at {now}")
#         elapsed = time() - self.start_time
#         time_sec = elapsed
#         time_min = elapsed / 60
#         time_hrs = elapsed / 3600

#         print(f"\n--> Total Run Time: {time_sec:.2e} seconds / {time_min:.2e} minutes / {time_hrs:.2e} hours")
#         output = '''
# \t\t\t*********************************************
# \t\t\t*   Thank you for using dfnWorks            *
# \t\t\t*   Learn more at https://dfnworks.lanl.gov *
# \t\t\t*   Contact us at dfnworks@lanl.gov         *
# \t\t\t*********************************************

# '''
#         print(output)


def commandline_options():
    """Read command lines for use in dfnWorks.

    Parameters
    ----------
        None

    Returns
    ---------
        options : argparse function
            command line options

    Notes
    ---------
        Options:
            -name : string
                Path to working directory (Mandatory)
            -ncpu : int
                Number of CPUS (Optional, default=4)
            -input : string
                Input file with paths to run files (Mandatory if the next three options are not specified)
            -prune_file : string
                Absolute path to the prune Input File
            -path : string
                Path to another DFN run that you want to base the current run from
            -cell : bool
                True/False Set True for use with cell based aperture and permeabuility (Optional, default=False)
    """

    import argparse

    parser = argparse.ArgumentParser(
        description="Command Line Arguments for dfnWorks")
    parser.add_argument("-name",
                        "--jobname",
                        default="",
                        type=str,
                        help="jobname")
    parser.add_argument("-ncpu",
                        "--ncpu",
                        default=4,
                        type=int,
                        help="Number of CPUs")
    parser.add_argument("-input",
                        "--input_file",
                        default="",
                        type=str,
                        help="input file with paths to run files")
    parser.add_argument("-path",
                        "--path",
                        default="",
                        type=str,
                        help="Path to directory for sub-network runs")
    parser.add_argument("-cell",
                        "--cell",
                        default=False,
                        action="store_true",
                        help="Binary For Cell Based Apereture / Perm")
    parser.add_argument("-prune_file",
                        "--prune_file",
                        default="",
                        type=str,
                        help="Path to prune DFN list file")
    options = parser.parse_args()
    if options.jobname == "":
        error = "Error: Jobname is required. Exiting.\n"
        sys.stderr.write(error)
        sys.exit(1)
    return options


def create_dfn():
    '''Parse command line inputs and input files to create and populate dfnworks class

    Parameters
    ----------
        None

    Returns
    -------
        DFN : object
            DFN class object populated with information parsed from the command line. Information about DFN class is in dfnworks.py

    Notes
    -----
    None
    '''

    options = commandline_options()
    print("Command Line Inputs:")
    print(options)

    now = datetime.now()

    if options.input_file == "":
        error = "ERROR!!! Input file must be provided.\n"
        sys.stderr.write(error)
        sys.exit(1)
    else:
        print("--> Reading Input from " + options.input_file)

    dfnGen_file = None
    dfnFlow_file = None
    dfnTrans_file = None
    print(f"--> Reading run files from {options.input_file}")
    with open(options.input_file, "r") as f:
        for i, line in enumerate(f.readlines()):
            line = line.rstrip('\n')
            line = line.split()
            try:
                if "dfnGen" in line:
                    dfnGen_file = line[1]
                    print('--> dfnGen input file: ', dfnGen_file)
                elif "dfnFlow" in line:
                    dfnFlow_file = line[1]
                    print('--> dfnFlow input file: ', dfnFlow_file)
                elif "dfnTrans" in line:
                    dfnTrans_file = line[1]
                    print('--> dfnTrans input file: ', dfnTrans_file)
            except:
                error = f"ERROR Reading {options.input_file}\nUnknown line: {line} on line number {i}\n"
                sys.stderr.write(error)
                sys.exit(1)

    if not options.path:
        if not options.path.endswith('/'):
            options.path += os.sep

    DFN = DFNWORKS(jobname=options.jobname,
                   ncpu=options.ncpu,
                   dfnGen_file=dfnGen_file,
                   dfnFlow_file=dfnFlow_file,
                   dfnTrans_file=dfnTrans_file,
                   prune_file=options.prune_file,
                   path=options.path,
                   cell_based_aperture=options.cell)
    return DFN
