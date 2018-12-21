__author__ = "Jeffrey Hyman and Satish Karra"
__version__ = "2.2"
__maintainer__ = "Jeffrey Hyman and Satish Karra"
__email__ = "jhyman@lanl.gov"

"""
DFN object class. 
"""

import sys 
import os
from time import time
from dfntools import *

class dfnworks(Frozen):
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
    from generator import dfn_gen
    from flow import dfn_flow
    from transport import dfn_trans
    # Specific functions
    from create_dfn_functions import commandline_options
    from dfn2graph import create_graph, k_shortest_paths_backbone, add_perm, dump_json_graph, load_json_graph, plot_graph, greedy_edge_disjoint, dump_fractures 
    from general_functions import dump_time, print_run_time 
   
    from gen_input import check_input
    from generator import make_working_directory, create_network
    from gen_output import output_report

    from flow import create_dfn_flow_links, set_flow_solver, uncorrelated  
    from pflotran import lagrit2pflotran, pflotran, inp2vtk_python, parse_pflotran_vtk_python, pflotran_cleanup, write_perms_and_correct_volumes_areas, zone2ex 
    from fehm import correct_stor_file, fehm

    from transport import copy_dfn_trans_files, run_dfn_trans, create_dfn_trans_links, check_dfn_trans_run_files
    from meshdfn import mesh_network
    from mesh_dfn_helper import clean_up_files_after_prune, create_mesh_links, inp2gmv 
    from legal import legal
    from paths import define_paths
    from mass_balance import effective_perm


    def __init__(self, jobname='', ncpu='', local_jobname='',dfnGen_file='',output_file='',local_dfnGen_file='', dfnFlow_file = '', local_dfnFlow_file = '', dfnTrans_file = '', path = '', prune_file = '', flow_solver = "PFLOTRAN", inp_file='full_mesh.inp', uge_file='', stor_file='', vtk_file='', mesh_type='dfn', perm_file='', aper_file='',perm_cell_file='',aper_cell_file='', dfnTrans_version ='', num_frac = '', h = ''):

        self.jobname = jobname
        self.ncpu = ncpu
        self.local_jobname = self.jobname.split('/')[-1]

        self.dfnGen_file = dfnGen_file
        self.local_dfnGen_file = self.dfnGen_file.split('/')[-1]
        
        self.output_file = self.dfnGen_file.split('/')[-1]
        
        self.dfnFlow_file = dfnFlow_file 
        self.local_dfnFlow_file = self.dfnFlow_file.split('/')[-1]

        self.dfnTrans_file = dfnTrans_file 
        self.local_dfnTrans_file = self.dfnTrans_file.split('/')[-1]

        self.vtk_file = vtk_file
        self.inp_file = inp_file
        self.uge_file = uge_file
        self.mesh_type = mesh_type
        self.perm_file = perm_file
        self.aper_file = aper_file
        self.stor_file = stor_file 
        self.perm_cell_file = perm_cell_file
        self.aper_cell_file = aper_cell_file
        self.flow_solver = flow_solver
        self.dfnTrans_version= 2.2
        self.freeze = False
        self.legal()
        #options = create_dfn.commandline_options()

