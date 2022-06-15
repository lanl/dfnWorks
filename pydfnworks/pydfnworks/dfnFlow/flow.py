import os
import subprocess
import sys
import glob
import shutil
from time import time
import numpy as np


def set_flow_solver(self, flow_solver):
    """Sets flow solver to be used 
       
    Parameters
    ----------
        self : object
            DFN Class
        flow_solver: string  
            Name of flow solver. Currently supported flow sovlers are FEHM and PFLOTRAN

    Returns
    ---------

    Notes
    --------
    Default is PFLOTRAN 

"""
    if flow_solver == "FEHM" or flow_solver == "PFLOTRAN":
        print("Using flow solver %s" % flow_solver)
        self.flow_solver = flow_solver
    else:
        error = "ERROR: Unknown flow solver requested %s\nCurrently supported flow solvers are FEHM and PFLOTRAN\nExiting dfnWorks\n" % flow_solver
        sys.stderr.write(error)
        sys.exit(1)


def dfn_flow(self, dump_vtk=True):
    """ Run the dfnFlow portion of the workflow
       
    Parameters
    ----------
        self : object
            DFN Class
        dump_vtk : bool
            True - Write out vtk files for flow solutions 
            False  - Does not write out vtk files for flow solutions 
 
    Returns
    ---------

    Notes
    --------
    Information on individual functions is found therein 
    """

    print('=' * 80)
    print("dfnFlow Starting")
    print('=' * 80)

    tic_flow = time()

    if self.flow_solver == "PFLOTRAN":
        print("Using flow solver: %s" % self.flow_solver)
        tic = time()
        self.lagrit2pflotran()
        self.dump_time('Function: lagrit2pflotran', time() - tic)

        tic = time()
        self.pflotran()
        self.dump_time('Function: pflotran', time() - tic)

        if dump_vtk:
            tic = time()
            self.parse_pflotran_vtk_python()
            self.dump_time('Function: parse_pflotran_vtk', time() - tic)
        tic = time()
        self.pflotran_cleanup()
        self.dump_time('Function: pflotran_cleanup', time() - tic)

        tic = time()

    elif self.flow_solver == "FEHM":
        print("Using flow solver: %s" % self.flow_solver)
        tic = time()
        self.correct_stor_file()
        self.fehm()
        self.dump_time('Function: FEHM', time() - tic)

    delta_time = time() - tic_flow
    self.dump_time('Process: dfnFlow', delta_time)

    print('=' * 80)
    print("dfnFlow Complete")
    print("Time Required for dfnFlow %0.2f seconds\n" % delta_time)
    print('=' * 80)


def create_dfn_flow_links(self, path='../'):
    """ Create symlinks to files required to run dfnFlow that are in another directory. 

    Parameters
    ---------
        self : object
            DFN Class
        path : string 
            Absolute path to primary directory. 
   
    Returns
    --------
        None

    Notes
    -------
        1. Typically, the path is DFN.path, which is set by the command line argument -path
        2. Currently only supported for PFLOTRAN
    """
    files = [
        'full_mesh.uge', 'full_mesh.inp', 'full_mesh_vol_area.uge',
        'full_mesh.stor', 'full_mesh_material.zone', 'full_mesh.fehmn',
        'allboundaries.zone', 'pboundary_bottom.zone', 'pboundary_top.zone',
        'pboundary_back_s.zone', 'pboundary_front_n.zone',
        'pboundary_left_w.zone', 'pboundary_right_e.zone'
    ]
    for f in files:
        try:
            os.symlink(path + f, f)
        except:
            print("--> Error Creating link for %s" % f)
