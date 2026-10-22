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
    if flow_solver == "FEHM" or flow_solver == "PFLOTRAN" or flow_solver == "TOUGH":
        self.print_log(f"Using flow solver {flow_solver}")
        self.flow_solver = flow_solver
    else:
        error = f"Error: Unknown flow solver requested {flow_solver}\nCurrently supported flow solvers are FEHM and PFLOTRAN\nExiting dfnWorks\n"
        self.print_log(error, 'error')


def set_perm_cell(self, cell_based=None):
    """ Build the per-cell permeability array self.perm_cell, one value per mesh node in UGE CELLS order.

    Parameters
    ----------
        self : object
            DFN Class

        cell_based : bool or None
            If False, permeability is fracture based: each cell takes the permeability of its fracture, self.perm[material_id - 1].
            If True, permeability is cell based: read from column 2 of self.perm_cell_file.
            If None (default), use self.cell_based_aperture.

    Returns
    ---------
        perm_cell : numpy array
            Permeability of each cell. Also stored as self.perm_cell.

    Notes
    --------
        Shared by the PFLOTRAN and TOUGH writers so both see the same permeability field.
        Fracture based requires self.material_ids (read from materialid.dat during meshing) and self.perm.
    """
    if cell_based is None:
        cell_based = self.cell_based_aperture

    if cell_based:
        self.print_log(f"--> Building cell based permeability from {self.perm_cell_file}")
        if not os.path.isfile(self.perm_cell_file):
            self.print_log(f"Error. Cannot find cell permeability file {self.perm_cell_file}\n", 'error')
        perm_cell = np.genfromtxt(self.perm_cell_file, skip_header=1)[:, 1]
    else:
        self.print_log("--> Building fracture based permeability from material ids")
        if not isinstance(self.material_ids, (list, np.ndarray)):
            self.print_log("Error. material ids are not loaded. Read materialid.dat before building cell permeability\n", 'error')
        material_ids = np.asarray(self.material_ids, dtype=int)
        perm = np.asarray(self.perm)
        if material_ids.min() < 1 or material_ids.max() > len(perm):
            self.print_log(f"Error. material ids range from {material_ids.min()} to {material_ids.max()}, but there are {len(perm)} fracture permeabilities\n", 'error')
        perm_cell = perm[material_ids - 1]

    if len(perm_cell) != self.num_nodes:
        self.print_log(f"Error. Built {len(perm_cell)} cell permeabilities, but the mesh has {self.num_nodes} nodes\n", 'error')

    self.print_log(f"--> Cell permeability: {len(perm_cell)} cells, min {perm_cell.min():0.4e}, max {perm_cell.max():0.4e}")
    self.perm_cell = perm_cell
    return self.perm_cell


def dfn_flow(self, dump_vtk=True, dump_h5=False):
    """ Run the dfnFlow portion of the workflow

    Parameters
    ----------
        self : object
            DFN Class

        dump_vtk : bool
            True - Parse PFLOTRAN VTK output into pflotran_vtk_outputs/ via
                   parse_pflotran_vtk_python (default).
            False - Skip VTK parsing.
        dump_h5 : bool
            True - Parse PFLOTRAN HDF5 output into pflotran_vtk_outputs/ via
                   parse_pflotran_h5. Mesh comes from the .inp via
                   inp2vtk_python; data come from <base>.h5.
            False - Skip HDF5 parsing (default).

    Returns
    ---------

    Notes
    --------
    Information on individual functions is found therein.
    dump_vtk and dump_h5 are independent; both can be True to produce
    parsed output from each source.
    """

    self.print_log('=' * 80)
    self.print_log("dfnFlow Starting")
    self.print_log('=' * 80)

    tic_flow = time()

    if self.flow_solver == "PFLOTRAN":
        self.print_log(f"Using flow solver: {self.flow_solver}")
        self.lagrit2pflotran()

        self.pflotran()

        if dump_vtk:
            self.parse_pflotran_vtk_python()
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
