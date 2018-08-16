__author__ = "Jeffrey Hyman and Satish Karra"
__version__ = "2.1"
__maintainer__ = "Jeffrey Hyman and Satish Karra"
__email__ = "jhyman@lanl.gov"

import  sys 
import os
from time import time
from dfntools import *
import helper
from integrated import *
from create_run_scripts import * 

class dfnworks(Frozen):
    '''
    Class for DFN Generation and meshing
    
    Attributes:
        * jobname: name of job, also the folder where output files are stored
        * ncpu: number of CPUs used in the job
        * dfnGen file: the name of the dfnGen input file
        * dfnFlow file: the name of the dfnFlow input file
        * local prefix: indicates that the name contains only the most local directory
        * vtk_file: the name of the VTK file
        * inp_file: the name of the INP file
        * uge_file: the name of the UGE file
        * mesh_type: the type of mesh
        * perm_file: the name of the file containing permeabilities 
        * aper_file: the name of the file containing apertures 
        * perm_cell file: the name of the file containing cell permeabilities 
        * aper_cell_file: the name of the file containing cell apertures
        * dfnTrans_version: the version of dfnTrans to use
        * freeze: indicates whether the class attributes can be modified
        * large_network: indicates whether C++ or Python is used for file processing at the bottleneck
        of inp to vtk conversion
    '''
    from generator import dfn_gen
    from flow import dfn_flow
    from transport import dfn_trans
    # Specific functions
    from helper import * # scale, cleanup_files, cleanup_end, commandline_options
    from gen_input import check_input
    from generator import make_working_directory, create_network
    from gen_output import output_report 
    from flow import lagrit2pflotran, pflotran, parse_pflotran_vtk, inp2vtk_python, parse_pflotran_vtk_python, pflotran_cleanup, write_perms_and_correct_volumes_areas, zone2ex, create_dfn_flow_links, uncorrelated, set_flow_solver 
    from flow import correct_stor_file, fehm
    from transport import copy_dfn_trans_files, run_dfn_trans, create_dfn_trans_links
    from meshdfn import mesh_network
    from mesh_dfn_helper import clean_up_files_after_prune, create_mesh_links 
    from legal import legal
    from paths import define_paths
    from dfn2graph import create_graph, k_shortest_paths_backbone, add_perm, dump_json_graph, load_json_graph, plot_graph, greedy_edge_disjoint, dump_fractures 

    def __init__(self, jobname='', local_jobname='',dfnGen_file='',output_file='',local_dfnGen_file='',ncpu='', dfnFlow_file = '', local_dfnFlow_file = '', dfnTrans_file = '', path = '', flow_solver = "PFLOTRAN", inp_file='full_mesh.inp', uge_file='', stor_file='', vtk_file='', mesh_type='dfn', perm_file='', aper_file='',perm_cell_file='',aper_cell_file='', dfnTrans_version ='', num_frac = ''):

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
        options = helper.commandline_options()

def create_dfn(dfnGen_file="", dfnFlow_file="", dfnTrans_file=""):
    '''
    Parse command line inputs and input files to create and populate dfnworks class
    '''
    
    options = helper.commandline_options()
    print("Command Line Inputs:")
    print options
    print("\n-->Creating DFN class")
    dfn = dfnworks(jobname=options.jobname, ncpu=options.ncpu)

    if options.input_file != "":
        with open(options.input_file) as f:
            for line in f:
                line=line.rstrip('\n')
                line=line.split()

                if line[0].find("dfnGen") == 0:
                    dfn.dfnGen_file = line[1]
                    dfn.local_dfnGen_file = line[1].split('/')[-1]

                elif line[0].find("dfnFlow") == 0:
                    dfn.dfnFlow_file = line[1]
                    dfn.local_dfnFlow_file = line[1].split('/')[-1]

                elif line[0].find("dfnTrans") == 0:
                    dfn.dfnTrans_file = line[1]
                    dfn.local_dfnTrans_file = line[1].split('/')[-1]
    else:   
        if options.dfnGen != "":
            dfn.dfnGen_file = options.dfnGen
            dfn.local_dfnGen_file = options.dfnGen.split('/')[-1]
        elif dfnGen_file != "":
            dfn.dfnGen_file = dfnGen_file  
            dfn.local_dfnGen_file = dfnGen_file.split('/')[-1]
        else:
            sys.exit("ERROR: Input File for dfnGen not provided. Exiting")
        
        if options.dfnFlow != "":
            dfn.dfnFlow_file = options.dfnFlow
            dfn.local_dfnFlow_file = options.dfnFlow.split('/')[-1]
        elif dfnFlow_file != "":
            dfn.dfnFlow_file = dfnFlow_file  
            dfn.local_dfnFlow_file = dfnFlow_file.split('/')[-1]
        else:
            sys.exit("ERROR: Input File for dfnFlow not provided. Exiting")
        
        if options.dfnTrans != "":
            dfn.dfnTrans_file = options.dfnTrans
            dfn.local_dfnTrans_file = options.dfnTrans.split('/')[-1]
        elif dfnTrans_file != "":
            dfn.dfnTrans_file = dfnTrans_file  
            dfn.local_dfnTrans_file = dfnTrans_file.split('/')[-1]
        else:
            sys.exit("ERROR: Input File for dfnTrans not provided. Exiting")

    if options.path != "":
        dfn.path = options.path

    if options.cell is True:
        dfn.aper_cell_file = 'aper_node.dat'
        dfn.perm_cell_file = 'perm_node.dat'
    else:
        dfn.aper_file = 'aperture.dat'
        dfn.perm_file = 'perm.dat'

    print("\n-->Creating DFN class: Complete")
    print 'Jobname: ', dfn.jobname
    print 'Number of cpus requested: ', dfn.ncpu 
    print '--> dfnGen input file: ',dfn.dfnGen_file
    print '--> dfnFlow input file: ',dfn.dfnFlow_file
    print '--> dfnTrans input file: ',dfn.dfnTrans_file

    print '--> Local dfnGen input file: ',dfn.local_dfnGen_file
    print '--> Local dfnFlow input file: ',dfn.local_dfnFlow_file
    print '--> Local dfnTrans input file: ',dfn.local_dfnTrans_file

    if options.cell is True:
        print '--> Expecting Cell Based Aperture and Permeability'
    print("="*80+"\n")  

    return dfn

