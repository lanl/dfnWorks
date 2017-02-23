__author__ = "Jeffrey Hyman and Satish Karra"
__version__ = "2.0"
__maintainer__ = "Jeffrey Hyman and Satish Karra"
__email__ = "jhyman@lanl.gov"

import  sys 
import os
from time import time
from dfntools import *
import helper

class DFNWORKS(Frozen):
    """  Class for DFN Generation and meshing
    
    Attributes:
        _jobname (str): name of job, also the folder where output files are stored
        _ncpu (int): number of CPUs used in the job
        _dfnGen_file (str): the name of the dfnGen input file
        _dfnFlow_file (str): the name of the dfnFlow input file
        _local prefix: indicates that the name contains only the most local directory
        _vtk_file (str): the name of the VTK file
        _inp_file (str): the name of the INP file
        _uge_file (str): the name of the UGE file
        _mesh_type (str): the type of mesh
        _perm_file (str): the name of the file containing permeabilities (JDH_TODO)
        _aper_file (str): the name of the file containing apertures (JDH_TODO)
        _perm_cell_file (str): the name of the file containing cell permeabilities 
        _aper_cell_file (str): the name of the file containing cell apertures
        _rfield (str): JDH_TODO
        _dfnTrans_version (str): the version of dfnTrans to use
        _freeze (object): indicates whether the class attributes can be modified
    """
    from generator import dfnGen
    from flow import dfnFlow
    from transport import dfnTrans
    # Specific functions

    from gen_input import check_input
    from generator import make_working_directory, create_network
    from gen_output import output_report 
    from flow import lagrit2pflotran, pflotran, parse_pflotran_vtk, parse_pflotran_vtk_python, pflotran_cleanup, write_perms_and_correct_volumes_areas, zone2ex, inp2vtk_python
    from transport import copy_dfnTrans_files, run_dfnTrans
    from meshdfn import mesh_network

    from legal import legal

    def __init__(self, jobname='', local_jobname='',dfnGen_file='',output_file='',local_dfnGen_file='',ncpu='', dfnFlow_file = '', local_dfnFlow_file = '', dfnTrans_file = '', inp_file='full_mesh.inp', uge_file='', vtk_file='', mesh_type='dfn', perm_file='', aper_file='',rfield='',perm_cell_file='',aper_cell_file='', dfnTrans_version ='', num_frac = ''):

        self._jobname = jobname
        self._ncpu = ncpu
        self._local_jobname = self._jobname.split('/')[-1]

        self._dfnGen_file = dfnGen_file
        self._local_dfnGen_file = self._dfnGen_file.split('/')[-1]
        
        self._output_file = self._dfnGen_file.split('/')[-1]
        
        self._dfnFlow_file = dfnFlow_file 
        self._local_dfnFlow_file = self._dfnFlow_file.split('/')[-1]

        self._dfnTrans_file = dfnTrans_file 
        self._local_dfnTrans_file = self._dfnTrans_file.split('/')[-1]

        self._vtk_file = vtk_file
        self._inp_file = inp_file
        self._uge_file = uge_file
        self._mesh_type = mesh_type
        self._perm_file = perm_file
        self._aper_file = aper_file
        self._perm_cell_file = perm_cell_file
        self._aper_cell_file = aper_cell_file
        self._rfield=rfield
        self._dfnTrans_version= 2.0
        self._freeze

        self.legal()

def create_dfn(dfnGen_file="", dfnFlow_file="", dfnTrans_file=""):
    '''
    Parse command line inputs and input files to create and populate dfnworks class
    '''

    options = helper.commandline_options()
    print("Command Line Inputs:")
    print options
    print("\n-->Creating DFN class")
    dfn = DFNWORKS(jobname=options.jobname, ncpu=options.ncpu)

    if options.input_file != "":
        with open(options.input_file) as f:
            for line in f:
                line=line.rstrip('\n')
                line=line.split()

                if line[0].find("dfnGen") == 0:
                    dfn._dfnGen_file = line[1]
                    dfn._local_dfnGen_file = line[1].split('/')[-1]

                elif line[0].find("dfnFlow") == 0:
                    dfn._dfnFlow_file = line[1]
                    dfn._local_dfnFlow_file = line[1].split('/')[-1]

                elif line[0].find("dfnTrans") == 0:
                    dfn._dfnTrans_file = line[1]
                    dfn._local_dfnTrans_file = line[1].split('/')[-1]
    else:   
        if options.dfnGen != "":
            dfn._dfnGen_file = options.dfnGen
        elif dfnGen_file != "":
            dfn._dfnGen_file = dfnGen_file  
        else:
            sys.exit("ERROR: Input File for dfnGen not provided. Exiting")
        
        if options.dfnFlow != "":
            dfn._dfnFlow_file = options.dfnFlow
        elif dfnFlow_file != "":
            dfn._dfnFlow_file = dfnFlow_file  
        else:
            sys.exit("ERROR: Input File for dfnFlow not provided. Exiting")
        
        if options.dfnTrans != "":
            dfn._dfnTrans_file = options.dfnTrans
        elif dfnTrans_file != "":
            dfn._dfnTrans_file = dfnTrans_file  
        else:
            sys.exit("ERROR: Input File for dfnTrans not provided. Exiting")

    if options.cell is True:
        dfn._aper_cell_file = 'aper_node.dat'
        dfn._perm_cell_file = 'perm_node.dat'
    else:
        dfn._aper_file = 'aperture.dat'
        dfn._perm_file = 'perm.dat'

    if options.field != '':
        dfn._rfield = options.field 


    print("\n-->Creating DFN class: Complete")
    print 'Jobname: ', dfn._jobname
    print 'Number of cpus requested: ', dfn._ncpu 
    print '--> dfnGen input file: ',dfn._dfnGen_file
    print '--> dfnFlow input file: ',dfn._dfnFlow_file
    print '--> dfnTrans input file: ',dfn._dfnTrans_file
    if options.cell is True:
        print '--> Expecting Cell Based Aperture and Permeability'
    print("="*80+"\n")  

    return dfn

