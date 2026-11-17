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
        self.print_log(f"Using flow solver {flow_solver}")
        self.flow_solver = flow_solver
    else:
        error = f"Error: Unknown flow solver requested {flow_solver}\nCurrently supported flow solvers are FEHM and PFLOTRAN\nExiting dfnWorks\n"
        self.print_log(error, 'error')


def dfn_flow(self, dump_vtu=True, dump_h5=False, dump_vtk=None):
    """ Run the dfnFlow portion of the workflow

    Parameters
    ----------
        self : object
            DFN Class

        dump_vtu : bool
            If True (default), convert PFLOTRAN's VTK output into XML .vtu
            files and a .pvd time series in pflotran_vtu_outputs/ with
            parse_pflotran_vtk. If False, skip the conversion.

        dump_h5 : bool
            If True, convert PFLOTRAN's HDF5 output (<base>.h5) into .vtu/.pvd
            files in pflotran_vtu_outputs/ with parse_pflotran_h5. The deck
            must request HDF5 output. If False (default), skip it.

        dump_vtk : bool
            Deprecated name of dump_vtu.

    Returns
    ---------

    Notes
    --------
    Information on individual functions is found therein.
    Both converters write <base>-NNN.vtu and <base>.pvd, so if dump_vtu and
    dump_h5 are both True the HDF5 conversion overwrites the VTK one.
    Open pflotran_vtu_outputs/<base>.pvd in ParaView.
    """
    if dump_vtk is not None:
        self.print_log("--> dfn_flow(dump_vtk=...) is deprecated; use dump_vtu", 'warning')
        dump_vtu = dump_vtk

    self.print_log('=' * 80)
    self.print_log("dfnFlow Starting")
    self.print_log('=' * 80)

    tic_flow = time()

    if self.flow_solver == "PFLOTRAN":
        self.print_log(f"Using flow solver: {self.flow_solver}")
        self.lagrit2pflotran()

        self.pflotran()

        if dump_vtu:
            self.parse_pflotran_vtk()
        if dump_h5:
            self.parse_pflotran_h5()
        self.pflotran_cleanup()

    elif self.flow_solver == "FEHM":
        self.print_log(f"Using flow solver: {self.flow_solver}")
        self.correct_stor_file()
        self.fehm()

    delta_time = time() - tic_flow
    self.dump_time('Process: dfnFlow', delta_time)

    self.print_log('=' * 80)
    self.print_log("dfnFlow Complete")
    self.print_log(f"Time Required for dfnFlow {delta_time} seconds\n")
    self.print_log('=' * 80)


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

    #path = self.jobname + '/../'
    self.print_log(f"Creating symbolic links for dfnFlow from {path}")
    files = [
        'full_mesh.uge', 'full_mesh.inp', 'full_mesh_vol_area.uge',
        'materialid.dat', 'full_mesh.stor', 'full_mesh_material.zone',
        'full_mesh.fehmn', 'allboundaries.zone', 'boundary_bottom.zone',
        'boundary_top.zone', 'boundary_back_s.zone',
        'boundary_front_n.zone', 'boundary_left_w.zone',
        'boundary_right_e.zone', 'perm.dat', 'aperture.dat', 'params.txt'
    ]
    for f in files:
        try:
            os.symlink(path + f, f)
        except:
            self.print_log(f"--> Unable to create link for{f}")
