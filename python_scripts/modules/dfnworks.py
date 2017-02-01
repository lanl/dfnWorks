__author__ = "Jeffrey Hyman and Satish Karra"
__version__ = "2.0"
__maintainer__ = "Jeffrey Hyman and Satish Karra"
__email__ = "jhyman@lanl.gov"

import re, sys, glob
import os
from time import time
from shutil import copy, rmtree, Error 
import numpy as np
import scipy
from scipy.stats import norm, lognorm, powerlaw
from scipy.integrate import odeint 
from dfntools import *
import h5py
import argparse

import matplotlib.pylab as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.mlab as mlab
import meshDFN as mesh
from pylagrit import PyLaGriT

import flow
import generator
import gen_input
import gen_output
import helper
import mesh_helper
import transport

class dfnworks(Frozen):
    """
    Class for DFN Generation and meshing
    """
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
        #self._flow_solver = 'pflotran'
        self._rfield=rfield
        self._dfnTrans_version= 2.0
        self._freeze

    def dfnGen(self):
        '''
        Run the dfnGen workflow. 
        1) make_working_directory: Create a directory with name of job
        2) check_input: Check input parameters and create a clean version of the input file
        3) create_network: Create network. DFNGEN v2.0 is called and creates the network
        4) output_report: Generate a PDF summary of the DFN generation
        5) mesh_network: calls module dfnGen_meshing and runs LaGriT to mesh the DFN
        '''
        tic_gen = time()
        # Create Working directory
        tic = time()
        generator.make_working_directory(self._jobname)
        helper.dump_time(self._jobname, 'Function: make_working_directory', time()- tic) 
    
        # Check input file  
        tic = time()
        gen_input.check_input(self._dfnGen_file, self._jobname)
        helper.dump_time(self._jobname, 'Function: check_input', time() - tic)   
    
        # Create network    
        tic = time()
        generator.create_network(self._local_dfnGen_file, self._jobname)
        helper.dump_time(self._jobname, 'Function: create_network', time() - tic)    
        
        tic = time()
        #output_report()
        helper.dump_time(self._jobname, 'output_report', time() - tic)   
        # Mesh Network

        tic = time()
        mesh_helper.mesh_network(self._jobname, helper.get_num_frac(), self._ncpu)
        helper.dump_time(self._jobname, 'Function: mesh_network', time() - tic)  
        print ('='*80)
        print 'dfnGen Complete'
        print ('='*80)
        print ''
        helper.dump_time(self._jobname, 'Process: dfnGen',time() - tic_gen)  

    def dfnFlow(self):
        ''' dfnFlow
        Run the dfnFlow portion of the workflow.
        1) lagrit2pflotran: takes output from LaGriT and processes it for use in PFLOTRAN
        ''' 
    
        print('='*80)
        print("\ndfnFlow Starting\n")
        print('='*80)

        tic_flow = time()

        tic = time()
        flow.lagrit2pflotran()
        helper.dump_time(self._jobname, 'Function: lagrit2pflotran', time() - tic)   
        
        tic = time()    
        flow.pflotran()
        helper.dump_time(self._jobname, 'Function: pflotran', time() - tic)  

        tic = time()    
        flow.parse_pflotran_vtk()       
        helper.dump_time(self._jobname, 'Function: parse_pflotran_vtk', time() - tic)    
        
        tic = time()    
        flow.pflotran_cleanup()
        helper.dump_time(self._jobname, 'Function: parse_cleanup', time() - tic) 
        helper.dump_time(self._jobname,'Process: dfnFlow',time() - tic_flow)    
    
        print('='*80)
        print("\ndfnFlow Complete\n")
        print('='*80)

    def dfnTrans(self):
        '''dfnTrans
        Copy input files for dfnTrans into working directory and run DFNTrans
        '''
        print('='*80)
        print("\ndfnTrans Starting\n")
        print('='*80)

        # Create Path to DFNTrans   
        try:
            os.symlink(os.environ['DFNTRANS_PATH']+'DFNTrans', './DFNTrans')
        except OSError:
            os.remove('DFNTrans')   
            os.symlink(os.environ['DFNTRANS_PATH']+'DFNTrans', './DFNTrans')
        except:
            sys.exit("Cannot create link to DFNTrans. Exiting Program")
        
        # Copy DFNTrans input file  
        try:
            copy(self._dfnTrans_file, self._local_dfnTrans_file) 
        except Error:
            print("--> Problem copying %s file"%self._local_dfnTrans_file)
            print("--> Trying to delete and recopy") 
            os.remove(self._local_dfnTrans_file)
            copy(self._dfnTrans_file, self._local_dfnTrans_file) 
        except:
            print("--> ERROR: Problem copying %s file"%self._local_dfnTrans_file)
            sys.exit("Unable to replace. Exiting Program")

        tic = time()    
        failure = os.system('./DFNTrans '+self._local_dfnTrans_file)
        helper.dump_time(self._jobname, 'Process: dfnTrans', time() - tic)   
        if failure == 0:
            print('='*80)
            print("\ndfnTrans Complete\n")
            print('='*80)
        else:
            sys.exit("--> ERROR: dfnTrans did not complete\n")

def commandline_options():
    '''Read command lines for use in dfnWorks.
    Options:
    -name : Jobname (Mandatory)
    -ncpu : Number of CPUS (Optional, default=4)

    -gen : Generator Input File (Mandatory, can be included within this file)
    -flow : PFLORAN Input File (Mandatory, can be included within this file)
    -trans: Transport Input File (Mandatory, can be included within this file)

    -cell: True/False Set True for use with cell 
        based aperture and permeabuility (Optional, default=False)
    '''
    parser = argparse.ArgumentParser(description="Command Line Arguments for dfnWorks")
    parser.add_argument("-name", "--jobname", default="", type=str,
              help="jobname") 
    parser.add_argument("-ncpu", "--ncpu", default=4, type=int, 
              help="Number of CPUs")
    parser.add_argument("-input", "--input_file", default="", type=str,
              help="input file with paths to run files") 
    parser.add_argument("-rfield", "--field", default="", type=str,
              help="level of random field") 
    parser.add_argument("-gen", "--dfnGen", default="", type=str,
              help="Path to dfnGen run file") 
    parser.add_argument("-flow", "--dfnFlow", default="", type=str,
              help="Path to dfnFlow run file") 
    parser.add_argument("-trans", "--dfnTrans", default="", type=str,
              help="Path to dfnTrans run file") 
    parser.add_argument("-cell", "--cell", default=False, action="store_true",
              help="Binary For Cell Based Apereture / Perm")

    options = parser.parse_args()
    
    if options.jobname is "":
        sys.exit("Error: Jobname is required. Exiting.")
    return options

def create_dfn(dfnGen_file="", dfnFlow_file="", dfnTrans_file=""):
    '''create_dfn
    Parse command line inputs and input files to create and populate dfnworks class
    '''

    options = commandline_options()
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


