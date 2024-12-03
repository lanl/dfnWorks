"""
.. module:: map2continuum.py 
   :synopsis: Produce octree-refined continuum mesh replacing dfn 
.. moduleauthor:: Matthew Sweeney <msweeney2796@lanl.gov>

"""

import os
import sys
import subprocess
import shutil
import numpy as np
from pydfnworks.dfnGen.meshing.mesh_dfn import mesh_dfn_helper as mh
from pydfnworks.general.logging import local_print_log
import time
import multiprocessing as mp
import pickle


def map_to_continuum(self, l, orl, path="./", dir_name="octree"):
    """ This function generates an octree-refined continuum mesh using the
    reduced_mesh.inp as input.  To generate the reduced_mesh.inp, one must 
    turn visualization mode on in the DFN input card.

    Parameters
    ----------
        self : object
            DFN Class
        l : float
            Size (m) of level-0 mesh element in the continuum mesh
        orl : int
            Number of total refinement levels in the octree
        path : string
            path to primary DFN directory
        dir_name : string
            name of directory where the octree mesh is created
    
    Returns
    -------
        None

    Notes
    -----
        octree_dfn.inp : Mesh file
            Octree-refined continuum mesh 
        fracX.inp : Mesh files
            Octree-refined continuum meshes, which contain intersection areas 
    
    """
    self.print_log('=' * 80)
    self.print_log("Meshing Continuum Using LaGrit : Starting")
    self.print_log('=' * 80)

    if type(orl) is not int or orl < 1:
        error = "ERROR: orl must be positive integer. Exiting"
        self.print_log(error, 'critical')
        sys.stderr.write(error)
        sys.exit(1)

    # Extent of domain
    x0 = 0 - (self.domain['x'] / 2.0)
    x1 = 0 + (self.domain['x'] / 2.0)
    y0 = 0 - (self.domain['y'] / 2.0)
    y1 = 0 + (self.domain['y'] / 2.0)
    z0 = 0 - (self.domain['z'] / 2.0)
    z1 = 0 + (self.domain['z'] / 2.0)

    # Number of cell elements in each direction at coarse level
    nx = self.domain['x'] / l + 1
    ny = self.domain['y'] / l + 1
    nz = self.domain['z'] / l + 1

    if nx * ny * nz > 1e8:
        error = "Error: Number of elements too large (> 1e8). Exiting"
        self.print_log(error, 'critical')
        sys.stderr.write(error)
        sys.exit(1)

    self.print_log("\nCreating *.lgi files for octree mesh\n")
    try:
        os.mkdir(dir_name)
        os.mkdir(dir_name + os.sep + "lagrit_scripts")
        os.mkdir(dir_name + os.sep + "lagrit_logs")
    except OSError:
        shutil.rmtree(dir_name)
        os.mkdir(dir_name)
        os.mkdir(dir_name + os.sep + "lagrit_scripts")
        os.mkdir(dir_name + os.sep + "lagrit_logs")


    ## gather points on polygons
    points = self.gather_points()
    if self.num_frac == 1:
        self.normal_vectors = np.array([self.normal_vectors])



    center = [self.params['domainCenter']['value'][0],self.params['domainCenter']['value'][1], self.params['domainCenter']['value'][2]] 
    translate_mesh(center,[0,0,0])

    lagrit_driver(dir_name, nx, ny, nz, self.num_frac, self.normal_vectors,points, center)

    #lagrit_driver(dir_name, nx, ny, nz, self.num_frac, self.normal_vectors,
    #              self.centers)

    lagrit_parameters(dir_name, orl, x0, x1, y0, y1, z0, z1, nx, ny, nz,
                      self.h)
    lagrit_build(dir_name)
    lagrit_intersect(dir_name)
    lagrit_hex_to_tet(dir_name)
    lagrit_remove(dir_name)
    lagrit_run(self, self.num_frac, path, dir_name)
    lagrit_strip(self.num_frac)
    driver_parallel(self, self.num_frac)
    build_dict(self, self.num_frac, delete_files=True)
    dir_cleanup()
    ## set object variable name
    self.inp_file = "octree_dfn.inp" 
    translate_mesh([0,0,0], center)


def translate_mesh(x1, x2):
    """
    Moves reduced_mesh.inp from center at x1 to x2 

    Parameters
    ---------------
        x1 : list
            floats x-0, y-1, z-2 - current center

        x2 : list
            floats x-0, y-1, z-2 - requisted center 
    Returns
    --------------
        None 

    """

    lagrit_script = f"""
read / avs / reduced_mesh.inp / MODFN
trans / 1 0 0 / {x1[0]} {x1[1]} {x1[2]} / {x2[0]} {x2[1]} {x2[2]}
dump / reduced_mesh.inp / MODFN
finish
"""
    with open('translate_mesh.lgi', 'w') as fp:
        fp.write(lagrit_script)
        fp.flush()
    mh.run_lagrit_script("translate_mesh.lgi")

def lagrit_driver(dir_name, nx, ny, nz, num_poly, normal_vectors, points, center):
    """ This function creates the main lagrit driver script, which calls all 
    lagrit scripts.

    Parameters
    ----------
        dir_name : string
            Name of working directory
        ni : int
            Number of cells in each direction
        num_poly : int
            Number of fractures
        normal_vectors : array
            Array containing normal vectors of each fracture
        points : array
            Array containing a point on each fracture

    Returns
    -------
        None

    Notes
    -----
        None
    
    """
    xn, yn, zn, xp, yp, zp = 0, 0, 0, 0, 0, 0
    j = num_poly
    floop = ""
    for i in range(1, int(num_poly + 1)):
        xn = normal_vectors[j - 1][0]
        yn = normal_vectors[j - 1][1]
        zn = normal_vectors[j - 1][2]
        xp = points[j - 1][0]
        yp = points[j - 1][1]
        zp = points[j - 1][2]
        floop = """read / avs / mohex2.inp / mohex2 
    cmo / DELATT / mohex2 / if_int
    read / avs / MOTET_np1.inp / MOTET_np1
    read / avs / MOTET.inp / MOTET
    read / avs / reduced_mesh.inp / MODFN
    cmo / create / FRACTURE{0} 
    cmo / copy / FRACTURE{0} / MODFN
    cmo / select / FRACTURE{0}
    pset / pdel / attribute imt / 1 0 0 / ne / {0}
    rmpoint pset, get, pdel
    rmpoint compress
    resetpts itp
    pset / pdel / delete
    eltset / edel / itetclr / ne / {0}
    rmpoint element eltset, get, edel
    rmpoint compress
    resetpts itp
    eltset / edel / delete
    
    intersect_elements / mohex2 / FRACTURE{0} / if_int
    eltset / erefine / if_int / ne / 0
    pset / pinter / eltset erefine

    cmo / create / temp{0}
    cmo / copy / temp{0} / mohex2
    cmo / select / temp{0}
    pset / pdel / if_int / 1 0 0 / eq / 0
    rmpoint, pset, get, pdel
    rmpoint compress
    resetpts itp
    pset / pdel / delete
    eltset / edel / if_int / eq / 0
    rmpoint element eltset, get, edel
    rmpoint compress
    resetpts itp
    eltset / edel / delete    
    cmo / setatt / temp{0} / itetclr / 1 0 0 / {0}
    cmo / setatt / temp{0} / imt / 1 0 0 / {0}
    
    cmo / create / TETCOPY
    cmo / copy / TETCOPY / MOTET
    cmo / select / TETCOPY
    interpolate / map / TETCOPY / itetclr / 1 0 0 / temp{0} / itetclr
    compute / distance_field / TETCOPY / temp{0} /dfield
    cmo / select / TETCOPY
    pset / pfrac / attribute / dfield / 1 0 0 / le / 1.e-8
    cmo / setatt / TETCOPY / imt / 1 0 0 / {1}
    cmo / setatt / TETCOPY / imt / pset get pfrac / {0}
    
    cmo / set_id / MOTET_np1 / element / id_cell
    cmo / set_id / MOTET_np1 / node / id_vertex

    extract / plane / ptnorm / &
    {2} {3} {4} / &
    {5} {6} {7} / &
    1 0 0 / moext / MOTET_np1
    cmo / status / brief

    createpts / median
    cmo / DELATT / moext / id_cell
    cmo / DELATT / moext / id_parent
    dump / avs2 / ex_xyz{0}.table / moext 0 0 0 1
    
    cmo / addatt /  moext / volume / area_tri
    cmo / DELATT / moext / xmed
    cmo / DELATT / moext / ymed
    cmo / DELATT / moext / zmed
    dump / avs2 / ex_area{0}.table / moext 0 0 0 1
    cmo / delete / moext

    cmo / select / TETCOPY
    cmo / DELATT / TETCOPY / icr1
    cmo / DELATT / TETCOPY / itp1
    cmo / DELATT / TETCOPY / isn1
 
    dump / avs2 / frac{0}.inp / TETCOPY  
    cmo / delete / temp{0}   
    cmo / delete / TETCOPY
 
    cmo / select / mohex2
    cmo / setatt / mohex2 / itetclr / eltset get erefine / {0}
    cmo / setatt / mohex2 / imt / pset get pinter / {0}
    eltset / erefine / delete
    pset / pinter / delete
    cmo / DELATT / mohex2 / if_int
    cmo / delete / FRACTURE{0}
    finish
    """.format(j, num_poly + 1, xp, yp, zp, xn, yn, zn)
        f_name = f'{dir_name}/driver_frac{j}.lgi'
        f = open(f_name, 'w')
        f.write(floop)
        f.flush()
        f.close()
        j = j - 1

    f_name = f'{dir_name}/driver_octree_start.lgi'
    f = open(f_name, 'w')
    fin = (f"""# 
# LaGriT control files to build an octree refined hex mesh with refinement
# based on intersection of hex mesh with a DFN triangulation mesh
#
# driver_octree.lgi
#   parameters_octree_dfn.mlgi
#   build_octree.mlgi
#       intersect_refine.mlgi
#   hex_to_tet.mlgi
#   remove_cells.mlgi
#
# Define some parameters
#
infile parameters_octree_dfn.mlgi
#
# Read in DFN mesh
#
read / FTYPE / FNAME / MODFN
cmo / printatt / MODFN / -xyz- / minmax
#
# Octree refined orthogonal mesh based on intersection with DFN mesh
#
infile build_octree.mlgi
#
# Identify cells in hex mesh that are intersected by DFN mesh
#
# This is the last pass through intersect_elements in order to figure out
# which cells in the fully refined hex mesh are intersected by the dfn mesh
#
intersect_elements / MOHEX / MODFN / if_int
eltset / einter / if_int / ne / 0
pset / pinter / eltset einter
#
# Use the itetclr(cell) and imt(vertex) attribute to hold the information
#
cmo / setatt / MOHEX / itetclr / 1 0 0 / 1
cmo / setatt / MOHEX / itetclr / eltset get einter / 2
cmo / setatt / MOHEX / imt / 1 0 0 / 1
cmo / setatt / MOHEX / imt / pset get pinter / 2
#
# Output final hex mesh
#
#dump / avs2 / tmp_hex_refine.inp / MOHEX
#
# Same as above but for np1 hex mesh
#
intersect_elements / MOHEX_np1 / MODFN / if_int
eltset / einter / if_int / ne / 0
pset / pinter / eltset einter
#
# See above
#
cmo / setatt / MOHEX_np1 / itetclr / 1 0 0 / 1
cmo / setatt / MOHEX_np1 / itetclr / eltset get einter / 2
cmo / setatt / MOHEX_np1 / imt / 1 0 0 / 1
cmo / setatt / MOHEX_np1 / imt / pset get pinter / 2
#dump / avs2 / tmp_hex_np1_refine.inp / MOHEX_np1
#
# Convert the hex mesh to a tet mesh
#
infile hex_to_tet.mlgi
#
# Modify the hex data structure from a full octree data structure
# to one in which only the highest level of refined hex is maintained
# and all parent cells are stripped out of the data structure
#
grid2grid / tree_to_fe / mohex2 / MOHEX
#dump / avs / octree_hex_mesh.inp / MOHEX
#
cmo / delete / MOHEX
cmo / select / mohex2
#
# Remove all but the most refined hex cells
#
loop / do / NTIMEs / 0 N_OCTREE_REFINE_M1 1 / loop_end &
infile remove_cells.mlgi
#
cmo / select / mohex2
cmo / DELATT / mohex2 / if_int
intersect_elements / mohex2 / MODFN / if_int
cmo / select / mohex2
eltset / edelete / if_int / eq / 0
rmpoint / element / eltset get edelete
eltset / edelete / release
rmpoint / compress
#
dump / avs / mohex2.inp / mohex2 
dump / avs / MOTET_np1.inp / MOTET_np1
dump / avs / MOTET.inp / MOTET
#
cmo / select / MOTET
#
#
cmo / modatt / MOTET / itp / ioflag / l
cmo / modatt / MOTET / isn / ioflag / l
cmo / modatt / MOTET / icr / ioflag / l
# #

define / ZONE / 1
define / FOUT / boundary_top
pset / top / attribute / zic / 1 0 0 / gt / ZMAX
pset / top / zone / FOUT / ascii / ZONE

define / ZONE / 2
define / FOUT / boundary_bottom
pset / bottom / attribute / zic / 1 0 0 / lt / ZMIN
pset / bottom / zone / FOUT / ascii / ZONE

define / ZONE / 3
define / FOUT / boundary_left_w
pset / left_w / attribute / xic / 1 0 0 / lt / XMIN
pset / left_w / zone / FOUT / ascii / ZONE

define / ZONE / 4
define / FOUT / boundary_front_n
pset / front_n / attribute / yic / 1 0 0 / gt / YMAX
pset / front_n / zone / FOUT / ascii / ZONE

define / ZONE / 5
define / FOUT / boundary_right_e
pset / right_e / attribute / xic / 1 0 0 / gt / XMAX
pset / right_e / zone / FOUT / ascii / ZONE

define / ZONE / 6
define / FOUT / boundary_back_s
pset / back_s / attribute / yic / 1 0 0 / lt / YMIN
pset / back_s / zone / FOUT / ascii / ZONE

           
trans / 1 0 0 / 0. 0. 0. / {center[0]}, {center[1]}, {center[2]} 

           
dump / pflotran / full_mesh / MOTET / nofilter_zero
dump / avs2 /         octree_dfn.inp / MOTET
dump / coord  /       octree_dfn     / MOTET
dump / stor /         octree_dfn     / MOTET
dump / zone_imt /     octree_dfn     / MOTET
dump / zone_outside / octree_dfn     / MOTET
finish
""")
    f.write(fin)
    f.flush()
    f.close()
    local_print_log("Creating driver_octree_start.lgi file: Complete\n")


def lagrit_parameters(dir_name, orl, x0, x1, y0, y1, z0, z1, nx, ny, nz, h):
    """ This function creates the parameters_octree_dfn.mlgi lagrit script.
    
    Parameters
    ----------
        dir_name : string
            Name of working directory
        orl : int
            Number of total refinement levels in the octree
        i0, i1 : float
            Extent of domain in x, y, z directions   
        ni : int
            Number of cells in each direction
    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    f_name = f'{dir_name}/parameters_octree_dfn.mlgi'
    f = open(f_name, 'w')
    fin = """# 
# Define some parameters
#
# Input DFN mesh
#
define / FTYPE / avs
define / FNAME / reduced_mesh.inp
#
define / MOHEX / mohex
define / MOTET / motet
# 
# Set AMR refinement. 123 means refine in x,y,z directions
# See LaGriT refine command for more options
#
define / REFINE_AMR / 123
#
    """
    f.write(fin)
    eps = h * 10**-3
    f.write('define / N_OCTREE_REFINE /    %d \n' % orl)
    f.write('define / N_OCTREE_REFINE_M1 / %d \n' % (orl - 1))
    f.write('define / N_OCTREE_np1 / %d \n' % (orl + 1))
    f.write('define / N_OCTREE_np1_M1 / %d \n' % (orl))
    f.write('define / X0 /  %0.12f \n' % x0)
    f.write('define / X1 /  %0.12f \n' % x1)
    f.write('define / Y0 / %0.12f \n' % y0)
    f.write('define / Y1 /  %0.12f \n' % y1)
    f.write('define / Z0 /  %0.12f \n' % z0)
    f.write('define / Z1 /  %0.12f \n' % z1)
    f.write('define / XMAX / %0.12f \n' % (x1 - eps))
    f.write('define / XMIN / %0.12f \n' % (x0 + eps))
    f.write('define / YMAX / %0.12f \n' % (y1 - eps))
    f.write('define / YMIN / %0.12f \n' % (y0 + eps))
    f.write('define / ZMAX / %0.12f \n' % (z1 - eps))
    f.write('define / ZMIN / %0.12f \n' % (z0 + eps))
    f.write('define / NX / %d \n' % nx)
    f.write('define / NY / %d \n' % ny)
    f.write('define / NZ / %d \n' % nz)
    f.write('finish\n')
    f.flush()
    f.close()
    local_print_log("Creating parameters_octree_dfn.mlgi file: Complete\n")


def lagrit_build(dir_name):
    """ This function creates the build_octree.mlgi lagrit script.
    
    Parameters
    ----------
        dir_name : string
            name of working directory    

    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    f_name = f'{dir_name}/build_octree.mlgi'
    f = open(f_name, 'w')
    fin = """cmo / create / MOHEX / / / hex
createpts / brick / xyz / NX NY NZ / X0 Y0 Z0 / X1 Y1 Z1 / 1 1 1
cmo / setatt / MOHEX / imt / 1 0 0 / 1
cmo / setatt / MOHEX / itetclr / 1 0 0 / 1
resetpts / itp
# 
# Print to screen and logfiles the extents of the hex mesh and dfn mesh
#
cmo / printatt / MOHEX / -xyz- / minmax
cmo / select / MODFN
cmo / printatt / MODFN / -xyz- / minmax
#
# Generate copy of hex mesh for upscaling
#
cmo / copy / MOHEX_np1 / MOHEX
#
# Loop through steps to intersect dfn mesh (MODFN) with hex mesh (MOHEX)
# and refine hex mesh based on cell intersections. Loop through 
# N_OCTREE_REFINE times
#
loop / do / NTIMEs / 1 N_OCTREE_REFINE 1 / loop_end &
infile intersect_refine.mlgi
# 
# See above - except do it once additional time ("np1")
#
loop / do / NTIMEs / 1 N_OCTREE_np1 1 / loop_end &
infile intersect_refine_np1.mlgi
#
finish
    """
    f.write(fin)
    f.flush()
    f.close()
    local_print_log("Creating build_octree.mlgi file: Complete\n")


def lagrit_intersect(dir_name):
    """ This function creates the intersect_refine.mlgi lagrit scripts.
    
    Parameters
    ----------
        dir_name : string
            name of working directory    

    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    f_name = f'{dir_name}/intersect_refine.mlgi'
    f = open(f_name, 'w')
    fin = """#
# Compute mesh to mesh intersection and refine hex mesh
#
intersect_elements / MOHEX / MODFN / if_int
eltset / erefine / if_int / ne / 0
pset / prefine / eltset erefine
#
# If one wants anisotropic mesh refinement, then the 
# variable REFINE_AMR can be set in parameters_octree_dfn.mlgi
#
refine/constant/imt1/linear/element/pset,get,prefine/ &
    -1.,0.,0./exclusive/amr REFINE_AMR
#
# Clean up eltset, pset, and if_int attribute
#
eltset / erefine / delete
pset   / prefine / delete
cmo / DELATT / MOHEX / if_int
#
# Print out diagnostics
#
quality
cmo / status / brief
#
finish
    """
    f.write(fin)
    f.flush()
    f.close()
    local_print_log("Creating intersect_refine.mlgi file: Complete\n")
    f_name = f'{dir_name}/intersect_refine_np1.mlgi'
    f = open(f_name, 'w')
    fin = """#
# For comments see intersect_refine.mlgi
#
intersect_elements / MOHEX_np1 / MODFN / if_int
eltset / erefine / if_int / ne / 0
pset / prefine / eltset erefine
refine/constant/imt1/linear/element/pset,get,prefine/ &
-1.,0.,0./exclusive/amr REFINE_AMR
#
eltset / erefine / delete
pset   / prefine / delete
cmo / DELATT / MOHEX_np1 / if_int
#
quality
cmo / status / brief
#
finish
    """
    f.write(fin)
    f.flush()
    f.close()
    local_print_log("Creating intersect_refine_np1.mlgi file: Complete\n")


def lagrit_hex_to_tet(dir_name):
    """ This function creates the hex_to_tet.mlgi lagrit script.
    
    Parameters
    ----------
        dir_name : string
            name of working directory 

    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    f_name = f'{dir_name}/hex_to_tet.mlgi'
    f = open(f_name, 'w')
    fin = """#
# Convert the octree hex mesh to tet mesh by connecting the
# octree vertex collection to a Delaunay mesh 
#
cmo / create / MOTET
copypts / MOTET / MOHEX
cmo / select / MOTET
filter 1 0 0
rmpoint / compress
cmo / setatt / MOTET / imt / 1 0 0 / 1
cmo / setatt / MOTET / itp / 1 0 0 / 0
#
# Sort and reorder the nodes based on coordinates
#
sort / MOTET / index / ascending / ikey / xic yic zic
reorder / MOTET / ikey
cmo / DELATT / MOTET / ikey
#
# Connect
#
connect / noadd
cmo / setatt / MOTET / itetclr / 1 0 0 / 1
resetpts / itp
#
# Do the same for np1 mesh
#
cmo / create / MOTET_np1
copypts / MOTET_np1 / MOHEX_np1
cmo / select / MOTET_np1
filter 1 0 0 
rmpoint / compress
cmo / setatt / MOTET_np1 / imt / 1 0 0 / 1
cmo / setatt / MOTET_np1 / itp / 1 0 0 / 0
#
# See above
#
sort / MOTET_np1 / index / ascending / ikey / xic yic zic
reorder / MOTET_np1 / ikey
cmo / DELATT / MOTET_np1 / ikey
#
connect / noadd
cmo / setatt / MOTET_np1 / itetclr / 1 0 0 / 1
resetpts / itp
#
finish
    """
    f.write(fin)
    f.flush()
    f.close()
    local_print_log("Creating hex_to_tet.mlgi file: Complete\n")


def lagrit_remove(dir_name):
    """ This function creates the remove_cells.mlgi lagrit script.
    
    Parameters
    ----------
        dir_name : string
            name of working directory 

    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    f_name = f'{dir_name}/remove_cells.mlgi'
    f = open(f_name, 'w')
    fin = """#
# Remove cells from hex mesh based on the level of refinement
# itetlev is the refinement level. Original mesh itetlev=0
#
eltset / edelete / itetlev / eq / NTIMEs
rmpoint / element / eltset get edelete
eltset / edelete / release
rmpoint / compress
#
finish
    """
    f.write(fin)
    f.flush()
    f.close()
    local_print_log("Creating remove_cells.mlgi file: Complete\n")


def lagrit_run(self, num_poly, path, dir_name):
    """ This function executes the lagrit scripts. 
    
    Parameters
    ----------
        path : string
            path to primary DFN directory
        dir_name : string
            name of directory where the octree mesh is created       

    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    # Run LaGriT
    os.chdir(dir_name)

    if os.path.isfile(path + "reduced_mesh.inp"):
        os.symlink(path + "reduced_mesh.inp", "reduced_mesh.inp")
    elif os.path.isfile(path + "../" + "reduced_mesh.inp"):
        os.symlink(path + "../" + "reduced_mesh.inp", "reduced_mesh.inp")
    else:
        error = "Error. Reduced Mesh not found. Please run mesh_dfn with visual_mode=True.\nExiting"
        self.print_log(error, 'critical')


    mh.run_lagrit_script("driver_octree_start.lgi")

    driver_interpolate_parallel(self, num_poly)


def lagrit_strip(num_poly):
    """ This function strips and replaces the headers of the files, which is 
    needed to assign the fracture areas to a mesh object.
    
    Parameters
    ----------
        num_poly : int
            Number of fractures

    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    node_dict = {}
    for i in range(1, num_poly + 1):
        with open('ex_xyz{0}.table'.format(i), 'r') as infile:
            for k, l in enumerate(infile):
                pass
            node_dict.setdefault(i, []).append(k - 4)


#    print(node_dict)

    for i in range(1, num_poly + 1):
        with open('ex_xyz{0}.table'.format(i), 'r') as infile:
            with open('ex_xyz{0}_2.inp'.format(i), 'w') as outfile:
                for j, line in enumerate(infile):
                    if j == 0:
                        outfile.write("{0} 0 0 0 0\n".format(node_dict[i][0]))
                    elif j > 4:
                        outfile.write(line)
            outfile.close()
        infile.close()
        os.remove(f"ex_xyz{i}.table")
        with open('ex_area{0}.table'.format(i), 'r') as infile:
            with open('ex_area{0}_2.table'.format(i), 'w') as outfile:
                for j, line in enumerate(infile):
                    if j > 2:
                        outfile.write(line.split()[1])
                        outfile.write("\n")
            outfile.close()
        infile.close()
        os.remove(f"ex_area{i}.table")


def driver_interpolate_parallel(self, num_poly):
    """ This function drives the parallelization of the area sums upscaling.
    
    Parameters
    ----------
        self : object
            DFN Class
        num_poly : int
            Number of fractures

    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    frac_index = range(1, int(num_poly + 1))
    number_of_task = len(frac_index)
    number_of_processes = self.ncpu
    tasks_to_accomplish = mp.Queue()
    tasks_that_are_done = mp.Queue()
    processes = []

    for i in range(number_of_task):
        tasks_to_accomplish.put(i + 1)

    # Creating processes
    for w in range(number_of_processes):
        p = mp.Process(target=worker_interpolate,
                       args=(tasks_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()
        tasks_to_accomplish.put('STOP')

    for p in processes:
        p.join()

    while not tasks_that_are_done.empty():
        self.print_log(tasks_that_are_done.get())

    return True


def driver_parallel(self, num_poly):
    """ This function drives the parallelization of the area sums upscaling.
    
    Parameters
    ----------
        self : object
            DFN Class
        num_poly : int
            Number of fractures

    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    frac_index = range(1, int(num_poly + 1))
    number_of_task = len(frac_index)
    number_of_processes = self.ncpu
    tasks_to_accomplish = mp.Queue()
    tasks_that_are_done = mp.Queue()
    processes = []

    for i in range(number_of_task):
        tasks_to_accomplish.put(i + 1)

    # Creating processes
    for w in range(number_of_processes):
        p = mp.Process(target=worker,
                       args=(tasks_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()
        tasks_to_accomplish.put('STOP')

    for p in processes:
        p.join()

    while not tasks_that_are_done.empty():
        self.print_log(tasks_that_are_done.get())

    return True


def upscale_parallel(f_id):
    """ Generates lagrit script that makes mesh files with area sums. 
    
    Parameters
    ----------
        f_id : int
            Fracture index
    
    Returns
    -------
        None

    Notes
    -----
        None        

    """
    fname = 'driver{0}.lgi'.format(f_id)
    fin = ""
    f = open(fname, 'w')
    fin += """read / avs / ex_xyz{0}_2.inp / mo_vertex
    cmo / addatt / mo_vertex / area_tri / vdouble / scalar / nnodes
    cmo / readatt / mo_vertex / area_tri / 1 0 0 / ex_area{0}_2.table

    read / avs / frac{0}.inp / frac
    cmo / addatt / frac / area_sum / vdouble / scalar / nnodes

    upscale / sum / frac, area_sum / 1 0 0 / mo_vertex, area_tri

    cmo / DELATT / frac / itp1
    cmo / DELATT / frac / icr1
    cmo / DELATT / frac / isn1 
    cmo / DELATT / frac / dfield 

    dump / avs / area_sum{0}.table / frac / 0 0 2 0
        
    cmo / delete / mo_vertex
    cmo / delete / frac
    """.format(f_id)
    fin += "finish"
    #print(fin)
    f.write(fin)
    f.flush()
    f.close()

    mh.run_lagrit_script(
        f"driver{f_id}.lgi",
        f"lagrit_logs/driver{f_id}",
    )
    # Delete files
    os.remove(f"ex_xyz{f_id}_2.inp")
    os.remove(f"ex_area{f_id}_2.table")
    os.remove(f"frac{f_id}.inp")
    shutil.copy(f"driver{f_id}.lgi", "lagrit_scripts")
    os.remove(f"driver{f_id}.lgi")


def worker(tasks_to_accomplish, tasks_that_are_done):
    """ Worker function for python parallel. See multiprocessing module 
    documentation for details.

    Parameters
    ----------
        tasks_to_accomplish : ?
            Processes still in queue 
        tasks_that_are_done : ?
            Processes complete

    Notes
    -----
        None
 
    """
    try:
        for f_id in iter(tasks_to_accomplish.get, 'STOP'):
            upscale_parallel(f_id)
    except:
        pass
    return True


def worker_interpolate(tasks_to_accomplish, tasks_that_are_done):
    """ Worker function for python parallel. See multiprocessing module 
    documentation for details.

    Parameters
    ----------
        tasks_to_accomplish : ?
            Processes still in queue 
        tasks_that_are_done : ?
            Processes complete

    Notes
    -----
        None
 
    """
    try:
        for f_id in iter(tasks_to_accomplish.get, 'STOP'):
            interpolate_parallel(f_id)
    except:
        pass
    return True


def interpolate_parallel(f_id):
    mh.run_lagrit_script(f"driver_frac{f_id}.lgi",
                         f"lagrit_logs/driver_frac{f_id}")
    shutil.copy(f"driver_frac{f_id}.lgi", "lagrit_scripts")
    os.remove(f"driver_frac{f_id}.lgi")


def build_dict(self, num_poly, delete_files):
    f_dict = {}
    for i in range(1, num_poly + 1):
        imts = np.genfromtxt(f"area_sum{i}.table", skip_header=4)[:, 0]
        area_sums = np.genfromtxt(f"area_sum{i}.table", skip_header=4)[:, 1]
        for j in range(len(imts)):
            if int(float(imts[j])) != (num_poly + 1) and float(
                    area_sums[j]) > 0:
                f_dict.setdefault(j + 1, []).append((i, float(area_sums[j])))
        if delete_files:
            os.remove(f"area_sum{i}.table")
    p_out = open("connections.p", "wb")
    pickle.dump(f_dict, p_out, pickle.HIGHEST_PROTOCOL)
    p_out.close()


def dir_cleanup():
    os.rename("build_octree.mlgi", "lagrit_scripts/build_octree.mlgi")
    os.rename("driver_octree_start.lgi",
              "lagrit_scripts/driver_octree_start.lgi")
    os.rename("driver_octree_start.lgi.log",
              "lagrit_logs/driver_octree_start.lgi.log")
    os.rename("driver_octree_start.lgi.out",
              "lagrit_logs/driver_octree_start.lgi.out")
    os.rename("hex_to_tet.mlgi", "lagrit_scripts/hex_to_tet.mlgi")
    os.rename("parameters_octree_dfn.mlgi",
              "lagrit_scripts/parameters_octree_dfn.mlgi")
    os.rename("remove_cells.mlgi", "lagrit_scripts/remove_cells.mlgi")
    os.rename("intersect_refine.mlgi", "lagrit_scripts/intersect_refine.mlgi")
    os.rename("intersect_refine_np1.mlgi",
              "lagrit_scripts/intersect_refine_np1.mlgi")
    os.remove("mohex2.inp")
    os.remove("MOTET.inp")
    os.remove("MOTET_np1.inp")
