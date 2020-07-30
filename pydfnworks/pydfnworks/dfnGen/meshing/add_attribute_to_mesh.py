"""
.. file:: add_attribute_mesh.py
   :synopsis: Add a node based attribute to a DFN mesh
   :version: 1.0
   :maintainer: Jeffrey Hyman
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import subprocess
from numpy import genfromtxt, zeros, savetxt
import sys
import os

from pydfnworks.dfnGen.meshing.mesh_dfn_helper import run_lagrit_script


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
            name of materialid file produced by large. Normally produced by run_meshing. Can 
    Returns
    ----------
        variable_file_by_node : string
            name of file containing node based values of the variable

    """

    print("--> Making {0} by node file".format(variable))
    values = genfromtxt(variable_file)
    if not os.path.isfile(matid_file):
        error = "ERROR!!! Cannot Located the file '{0}'\nExiting\n"
        sys.stderr.write(error)
        sys.exit(1)
    nodes = genfromtxt(matid_file, skip_header=3).astype(int)
    value_by_node = zeros(len(nodes))
    for i, n in enumerate(nodes):
        value_by_node[i] = values[n - 1]
    variable_file_by_node = "{0}_by_node.dat".format(variable)
    savetxt(variable_file_by_node, value_by_node)
    print("--> Complete")
    return variable_file_by_node


def create_lagrit_script(variable, variable_file, mesh_file_in, mesh_file_out):
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
    print("Making LaGriT script")
    lagrit_script = '''
read / {0} / mo1
cmo / addatt / mo1 / {1} / vdouble / scalar / nnodes
cmo / setatt / mo1 / {1} / 1 0 0 / 1
cmo / readatt / mo1 / {1} / 1, 0, 0 / {2} 
dump / {3} / mo1 
finish
'''.format(mesh_file_in, variable, variable_file, mesh_file_out)

    lagrit_file = "add_{0}_to_mesh.lgi".format(variable)
    fp = open(lagrit_file, "w")
    fp.write(lagrit_script)
    fp.flush()
    fp.close()
    print("Complete")
    return lagrit_file


def add_variable_to_mesh(self,
                         variable,
                         variable_file,
                         mesh_file_in,
                         mesh_file_out=None,
                         cell_based=None):

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
        cell_based : bool
            Set to True if variable_file contains cell-based values, Set to False 
            if variable_file provide fracture based values

    Returns
    ----------
        lagrit_file : string
            Name of LaGriT output file
    """

    if mesh_file_out is None:
        mesh_file_out = mesh_file_in

    if cell_based:
        lagrit_file = create_lagrit_script(variable, variable_file,
                                           mesh_file_in, mesh_file_out)
    else:
        variable_file_by_node = create_variable_file(variable, variable_file)
        lagrit_file = create_lagrit_script(variable, variable_file_by_node,
                                           mesh_file_in, mesh_file_out)
    run_lagrit_script(lagrit_file)

