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
from pydfnworks.general.dfntools import *

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
    # genearl functions
    from pydfnworks.general.legal import legal
    from pydfnworks.general.paths import define_paths
    from pydfnworks.general.general_functions import dump_time, print_run_time 
  
    # dfnGen functions 
    from pydfnworks.dfnGen.gen_input import check_input
    from pydfnworks.dfnGen.generator import dfn_gen, make_working_directory, create_network
    from pydfnworks.dfnGen.gen_output import output_report
    from pydfnworks.dfnGen.mesh_dfn import mesh_network
    from pydfnworks.dfnGen.mesh_dfn_helper import inp2gmv 
    
    # dfnFlow
    from pydfnworks.dfnFlow.flow import dfn_flow, create_dfn_flow_links, set_flow_solver, uncorrelated  
    from pydfnworks.dfnFlow.pflotran import lagrit2pflotran, pflotran, inp2vtk_python, parse_pflotran_vtk_python, pflotran_cleanup, write_perms_and_correct_volumes_areas, zone2ex 
    from pydfnworks.dfnFlow.fehm import correct_stor_file, fehm
    from pydfnworks.dfnFlow.mass_balance import effective_perm

    # dfnTrans
    from pydfnworks.dfnTrans.transport import dfn_trans, copy_dfn_trans_files, run_dfn_trans, create_dfn_trans_links, check_dfn_trans_run_files


    # dfnGraph
    from pydfnworks.dfnGraph.dfn2graph import create_graph, k_shortest_paths_backbone, dump_json_graph, load_json_graph, plot_graph, greedy_edge_disjoint, dump_fractures 
    from pydfnworks.dfnGraph.graph_flow import run_graph_flow 
    from pydfnworks.dfnGraph.graph_transport import run_graph_transport 

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

        self.h = "" 

        self.dfnTrans_version= 2.2
        self.freeze = False
        self.legal()
        #options = create_dfn.commandline_options()

 
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
            -gen : string 
                Generator Input File (Mandatory, can be included within the input file)
            -flow : string 
                PFLORAN Input File (Mandatory, can be included within the input file)
            -trans : string
                Transport Input File (Mandatory, can be included within the input file)
            -prune_file : string
                Absolute path to the prune Input File 
            -path : string
                Path to another DFN run that you want to base the current run from 
            -cell : bool
                True/False Set True for use with cell based aperture and permeabuility (Optional, default=False)
    """

    import argparse

    parser = argparse.ArgumentParser(description="Command Line Arguments for dfnWorks")
    parser.add_argument("-name", "--jobname", default="", type=str,
              help="jobname") 
    parser.add_argument("-ncpu", "--ncpu", default=4, type=int, 
              help="Number of CPUs")
    parser.add_argument("-input", "--input_file", default="", type=str,
              help="input file with paths to run files") 
    parser.add_argument("-gen", "--dfnGen", default="", type=str,
              help="Path to dfnGen run file") 
    parser.add_argument("-flow", "--dfnFlow", default="", type=str,
              help="Path to dfnFlow run file") 
    parser.add_argument("-trans", "--dfnTrans", default="", type=str,
              help="Path to dfnTrans run file") 
    parser.add_argument("-path", "--path", default="", type=str,
              help="Path to directory for sub-network runs") 
    parser.add_argument("-cell", "--cell", default=False, action="store_true",
              help="Binary For Cell Based Apereture / Perm")
    parser.add_argument("-prune_file", "--prune_file", default="", type=str, 
              help="Path to prune DFN list file") 
    parser.add_argument("-prune_path", "--prune_path", default="", type=str, 
              help="Path to original DFN files") 
    options = parser.parse_args()
    if options.jobname is "":
        sys.exit("Error: Jobname is required. Exiting.")
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
    print("\n-->Creating DFN class")
    DFN=dfnworks(jobname=options.jobname, ncpu=options.ncpu)

    if options.input_file != "":
        with open(options.input_file) as f:
            for line in f:
                line=line.rstrip('\n')
                line=line.split()

                if line[0].find("dfnGen") == 0:
                    DFN.dfnGen_file = line[1]
                    DFN.local_dfnGen_file = line[1].split('/')[-1]

                elif line[0].find("dfnFlow") == 0:
                    DFN.dfnFlow_file = line[1]
                    DFN.local_dfnFlow_file = line[1].split('/')[-1]

                elif line[0].find("dfnTrans") == 0:
                    DFN.dfnTrans_file = line[1]
                    DFN.local_dfnTrans_file = line[1].split('/')[-1]
    else:   
        if options.dfnGen != "":
            DFN.dfnGen_file = options.dfnGen
            DFN.local_dfnGen_file = options.dfnGen.split('/')[-1]
        elif dfnGen_file != "":
            DFN.dfnGen_file = dfnGen_file  
            DFN.local_dfnGen_file = dfnGen_file.split('/')[-1]
        else:
            sys.exit("ERROR: Input File for dfnGen not provided. Exiting")
        
        if options.dfnFlow != "":
            DFN.dfnFlow_file = options.dfnFlow
            DFN.local_dfnFlow_file = options.dfnFlow.split('/')[-1]
        elif dfnFlow_file != "":
            DFN.dfnFlow_file = dfnFlow_file  
            DFN.local_dfnFlow_file = dfnFlow_file.split('/')[-1]
        else:
            sys.exit("ERROR: Input File for dfnFlow not provided. Exiting")
        
        if options.dfnTrans != "":
            DFN.dfnTrans_file = options.dfnTrans
            DFN.local_dfnTrans_file = options.dfnTrans.split('/')[-1]
        elif dfnTrans_file != "":
            DFN.dfnTrans_file = dfnTrans_file  
            DFN.local_dfnTrans_file = dfnTrans_file.split('/')[-1]
        else:
            sys.exit("ERROR: Input File for dfnTrans not provided. Exiting")

    if options.path != "":
        if not options.path.endswith('/'):
            options.path += os.sep
        DFN.path = options.path 
    else:
        DFN.path = ""

    if options.prune_file != "":
        DFN.prune_file = options.prune_file
    else:
        DFN.prune_file = ""

    if options.cell is True:
        DFN.aper_cell_file = 'aper_node.dat'
        DFN.perm_cell_file = 'perm_node.dat'
    else:
        DFN.aper_file = 'aperture.dat'
        DFN.perm_file = 'perm.dat'

    print("\n-->Creating DFN class: Complete")
    print('Jobname: ', DFN.jobname)
    print('Number of cpus requested: ', DFN.ncpu)
    print('--> dfnGen input file: ',DFN.dfnGen_file)
    print('--> dfnFlow input file: ',DFN.dfnFlow_file)
    print('--> dfnTrans input file: ',DFN.dfnTrans_file)

    print('--> Local dfnGen input file: ',DFN.local_dfnGen_file)
    print('--> Local dfnFlow input file: ',DFN.local_dfnFlow_file)
    print('--> Local dfnTrans input file: ',DFN.local_dfnTrans_file)

    if options.cell is True:
        print('--> Expecting Cell Based Aperture and Permeability')

    print("="*80+"\n")  
    return DFN

