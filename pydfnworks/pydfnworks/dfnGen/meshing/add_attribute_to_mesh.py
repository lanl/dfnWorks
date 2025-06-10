import subprocess
from numpy import genfromtxt, zeros, savetxt
import sys
import os

from pydfnworks.dfnGen.meshing.mesh_dfn.mesh_dfn_helper import run_lagrit_script
from pydfnworks.general import helper_functions as hf
from pydfnworks.general.logging import local_print_log, print_log 


def create_variable_file(variable, variable_file, matid_file="materialid.dat"):
    """
    Creates a node based file for variables

    Parameters
    -----------
        variable : string
            name of variable
        
        variable_file : string
            name of file containing variable files. Must be a single column where each line corresponds to that fracture number. 
        
        matid_file : string
            name of materialid file produced by large. Normally produced by run_meshing.

    Returns
    ----------
        variable_file_by_node : string
            name of file containing node based values of the variable

    """

    local_print_log(f"--> Making {variable} by node file")
    values = genfromtxt(variable_file, skip_header=0, usecols=(-1))
    if not os.path.isfile(matid_file):
        local_print_log(f"Cannot locate the file '{matid_file}",'error')


    nodes = genfromtxt(matid_file, skip_header=3).astype(int)
    value_by_node = zeros(len(nodes))
    for i, n in enumerate(nodes):
        value_by_node[i] = values[n - 1]
    variable_file_by_node = f"{variable}_by_node.dat"
    savetxt(variable_file_by_node, value_by_node)
    local_print_log("--> Complete")
    return variable_file_by_node


def create_lagrit_append_script(variable, variable_file, mesh_file_in,
                                mesh_file_out):
    """
    Creates a LaGriT script to append the attribute to the mesh 

    Parameters
    -----------
        variable : string
            name of variable
        
        variable_file : string
            name of file containing variable files. Must be a single column where each line corresponds to that node number in the mesh
        
        mesh_file_in : string
            Name of source mesh file
        
        mesh_file_out : string
            Name of Target mesh file
    Returns
    ----------
        lagrit_file : string
            Name of LaGriT output file
    """
    local_print_log("--> Making LaGriT script")
    lagrit_script = f'''
read / {mesh_file_in} / mo1
cmo / addatt / mo1 / {variable} / vdouble / scalar / nnodes
cmo / setatt / mo1 / {variable} / 1 0 0 / 1
cmo / readatt / mo1 / {variable} / 1, 0, 0 / {variable_file} 
dump / {mesh_file_out} / mo1 
finish
'''

    lagrit_file = f"add_{variable}_to_mesh.lgi"
    with open(lagrit_file, "w") as fp:
        fp.write(lagrit_script)
        fp.flush()
    local_print_log("--> Complete")
    return lagrit_file


def add_variable_to_mesh(self,
                         variable,
                         variable_file,
                         mesh_file_in,
                         mesh_file_out=None,
                         node_based=False):
    """
    Adds a variable to the nodes of a mesh. Can be either fracture (material) based 
    or node based. 

    Parameters
    -----------
        self : object
            DFN Class
        
        variable : string
            name of variable
        
        variable_file : string
            name of file containing variable files. Must be a single column where each line corresponds to that node number in the mesh
        
        mesh_file_in : string
            Name of source mesh file
        
        mesh_file_out : string
            Name of Target mesh file.  If no name if provide, mesh_file_in will be used
        
        node_based : bool
            Set to True if variable_file contains node-based values, Set to False 
            if variable_file provide fracture based values

    Returns
    ----------
        lagrit_file : string
            Name of LaGriT output file
    """

    # Check input files
    if not os.path.isfile(variable_file):
        self.print_log(f"Error -- in function 'add_variable_to_mesh'. The file {variable_file} is not in current directory.  Please check the filename.",'error')


    if not os.path.isfile(mesh_file_in):
        self.print_log(
            f"Error -- in function 'add_variable_to_mesh'. The mesh file {mesh_file_in} is not in current directory.  Please check the filename.", "error"
        )

    # if an output mesh file is not provided, set target mesh to be the source mesh.
    if mesh_file_out is None:
        mesh_file_out = mesh_file_in

    self.print_log(
        f"--> Adding attribute in {variable_file} to mesh file {mesh_file_in}.\n--> Output writting into {mesh_file_out}"
    )

    if node_based:
        self.print_log(f"--> Expecting node-based values")
        lagrit_file = create_lagrit_append_script(variable, variable_file,
                                                  mesh_file_in, mesh_file_out)
    else:
        variable_file_by_node = create_variable_file(variable, variable_file)
        lagrit_file = create_lagrit_append_script(variable,
                                                  variable_file_by_node,
                                                  mesh_file_in, mesh_file_out)

    run_lagrit_script(lagrit_file)

    self.print_log(
        f"--> Complete: Adding attribute in {variable_file} to mesh file {mesh_file_in}.\n--> Output writting into {mesh_file_out}"
    )
