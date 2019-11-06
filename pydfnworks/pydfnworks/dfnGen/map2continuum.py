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
from pydfnworks.dfnGen import mesh_dfn_helper as mh
import time
import multiprocessing as mp
#import Queue


def map_to_continuum(self, l, orl):
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
    print('=' * 80)
    print("Meshing Continuum Using LaGrit : Starting")
    print('=' * 80)

    if type(orl) is not int or orl < 1:
        error = "ERROR: orl must be positive integer. Exiting"
        sys.stderr.write(error)
        sys.exit(1)

    # Read in normal vectors and points from dfnWorks output
    normal_vectors = np.genfromtxt('normal_vectors.dat', delimiter=' ')

    with open('translations.dat') as old, open('points.dat', 'w') as new:
        old.readline()
        for line in old:
            if not 'R' in line:
                new.write(line)
    points = np.genfromtxt('points.dat', skip_header=0, delimiter=' ')

    num_poly, h, _, _, domain = mh.parse_params_file()

    # Extent of domain
    x0 = 0 - (domain['x'] / 2.0)
    x1 = 0 + (domain['x'] / 2.0)
    y0 = 0 - (domain['y'] / 2.0)
    y1 = 0 + (domain['y'] / 2.0)
    z0 = 0 - (domain['z'] / 2.0)
    z1 = 0 + (domain['z'] / 2.0)

    # Number of cell elements in each direction at coarse level
    nx = domain['x'] / l + 1
    ny = domain['y'] / l + 1
    nz = domain['z'] / l + 1

    if nx * ny * nz > 1e8:
        error = "ERROR: Number of elements > 1e8. Exiting"
        sys.stderr.write(error)
        sys.exit(1)

    print("\nCreating *.lgi files for octree mesh\n")
    try:
        os.mkdir('octree')
    except OSError:
        rmtree('octree')
        os.mkdir('octree')

    lagrit_driver(nx, ny, nz, num_poly, normal_vectors, points)
    lagrit_parameters(orl, x0, x1, y0, y1, z0, z1, nx, ny, nz, h)
    lagrit_build()
    lagrit_intersect()
    lagrit_hex_to_tet()
    lagrit_remove()
    lagrit_run()
    lagrit_strip(num_poly)
    driver_parallel(self, num_poly)


def lagrit_driver(nx, ny, nz, num_poly, normal_vectors, points):
    """ This function creates the main lagrit driver script, which calls all 
    lagrit scripts.

    Parameters
    ----------
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
    j = num_poly + 1
    floop = ""
    for i in range(1, int(num_poly + 2)):
        if j != num_poly + 1:
            xn = normal_vectors[j - 1][0]
            yn = normal_vectors[j - 1][1]
            zn = normal_vectors[j - 1][2]
            xp = points[j - 1][0]
            yp = points[j - 1][1]
            zp = points[j - 1][2]
        floop += """cmo / create / FRACTURE{0} 
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
    eltset / etemp / itetclr / ne / {0}
    cmo / setatt / TETCOPY / itetclr / eltset get etemp / {1}    
    eltset / etemp / delete
    pset / ptemp / delete
    
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
    """.format(j, num_poly + 1, xp, yp, zp, xn, yn, zn)
        j = j - 1

    f_name = 'octree/driver_octree.lgi'
    f = open(f_name, 'w')
    fin = ("""# 
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
loop / do / NTIMES / 0 N_OCTREE_REFINE_M1 1 / loop_end &
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
# NOTE: I commented out the following lines for unknown but seemingly
# important reason
#
#cmo / setatt / mohex2 / itetclr / 1 0 0 / 1
#cmo / setatt / mohex2 / imt     / 1 0 0 / 1
""" + floop + """
#
#dump / avs / tmp_remove_cells.inp / mohex2
#dump / avs / tmp_tet.inp / MOTET
#
interpolate / map / MOTET / itetclr / 1 0 0 / mohex2 / itetclr
compute / distance_field / MOTET / mohex2 / dfield
cmo / select / MOTET
#
# This use of 1.e-8 is fine for now but might cause problems if the
# bounding box of the problem was very small (<1.e-7)
#
pset / pfrac / attribute / dfield / 1 0 0 / le / 1.e-8
cmo / setatt / MOTET / imt / 1 0 0 / 2
cmo / setatt / MOTET / imt / pset get pfrac / 1
#
cmo / modatt / MOTET / itp / ioflag / l
cmo / modatt / MOTET / isn / ioflag / l
cmo / modatt / MOTET / icr / ioflag / l
#
dump / pflotran / full_mesh / MOTET / nofilter_zero
dump / avs2 /         octree_dfn.inp / MOTET
dump / coord  /       octree_dfn     / MOTET
dump / stor /         octree_dfn     / MOTET
dump / zone_imt /     octree_dfn     / MOTET
dump / zone_outside / octree_dfn     / MOTET

define / ZONE / 1
define / FOUT / pboundary_top
pset / top / attribute / zic / 1 0 0 / gt / ZMAX
pset / top / zone / FOUT / ascii / ZONE

define / ZONE / 2
define / FOUT / pboundary_bottom
pset / bottom / attribute / zic / 1 0 0 / lt / ZMIN
pset / bottom / zone / FOUT / ascii / ZONE

define / ZONE / 3
define / FOUT / pboundary_left_w
pset / left_w / attribute / xic / 1 0 0 / lt / XMIN
pset / left_w / zone / FOUT / ascii / ZONE

define / ZONE / 4
define / FOUT / pboundary_front_n
pset / front_n / attribute / yic / 1 0 0 / gt / YMAX
pset / front_n / zone / FOUT / ascii / ZONE

define / ZONE / 5
define / FOUT / pboundary_right_e
pset / right_e / attribute / xic / 1 0 0 / gt / XMAX
pset / right_e / zone / FOUT / ascii / ZONE

define / ZONE / 6
define / FOUT / pboundary_back_s
pset / back_s / attribute / yic / 1 0 0 / lt / YMIN
pset / back_s / zone / FOUT / ascii / ZONE

#
# Work around for getting *.fehnm file
# Do we need this?
#
cmo / setatt / MOTET / itetclr / 1 0 0 / 1
cmo / setatt / MOTET / imt / 1 0 0 / 1
resetpts / itp
dump / fehm        / tmp_tmp_     / MOTET
#
finish
""")
    f.write(fin)
    f.flush()
    f.close()
    print("Creating driver_octree.lgi file: Complete\n")


def lagrit_parameters(orl, x0, x1, y0, y1, z0, z1, nx, ny, nz, h):
    """ This function creates the parameters_octree_dfn.mlgi lagrit script.
    
    Parameters
    ----------
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
    f_name = 'octree/parameters_octree_dfn.mlgi'
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
    print("Creating parameters_octree_dfn.mlgi file: Complete\n")


def lagrit_build():
    """ This function creates the build_octree.mlgi lagrit script.
    
    Parameters
    ----------
        None    

    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    f_name = 'octree/build_octree.mlgi'
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
loop / do / NTIMES / 1 N_OCTREE_REFINE 1 / loop_end &
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
    print("Creating build_octree.mlgi file: Complete\n")


def lagrit_intersect():
    """ This function creates the intersect_refine.mlgi lagrit scripts.
    
    Parameters
    ----------
        None    

    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    f_name = 'octree/intersect_refine.mlgi'
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
    print("Creating intersect_refine.mlgi file: Complete\n")
    f_name = 'octree/intersect_refine_np1.mlgi'
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
    print("Creating intersect_refine_np1.mlgi file: Complete\n")


def lagrit_hex_to_tet():
    """ This function creates the hex_to_tet.mlgi lagrit script.
    
    Parameters
    ----------
        None    

    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    f_name = 'octree/hex_to_tet.mlgi'
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
    print("Creating hex_to_tet.mlgi file: Complete\n")


def lagrit_remove():
    """ This function creates the remove_cells.mlgi lagrit script.
    
    Parameters
    ----------
        None    

    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    f_name = 'octree/remove_cells.mlgi'
    f = open(f_name, 'w')
    fin = """#
# Remove cells from hex mesh based on the level of refinement
# itetlev is the refinement level. Original mesh itetlev=0
#
eltset / edelete / itetlev / eq / NTIMES
rmpoint / element / eltset get edelete
eltset / edelete / release
rmpoint / compress
#
finish
    """
    f.write(fin)
    f.flush()
    f.close()
    print("Creating remove_cells.mlgi file: Complete\n")


def lagrit_run():
    """ This function executes the lagrit scripts. 
    
    Parameters
    ----------
        None    

    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    # Run LaGriT
    os.chdir('octree/')
    if os.path.isfile("../reduced_mesh.inp"):
        os.symlink("../reduced_mesh.inp", "reduced_mesh.inp")
    else:
        error = "ERROR!!! Reduced Mesh not found. Please run mesh_dfn with visual_mode=True.\nExiting"
        sys.stderr.write(error)
        sys.exit(1)

    cmd = os.environ['LAGRIT_EXE'] + '< driver_octree.lgi'
    subprocess.call(cmd, shell=True)


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
    print(node_dict)

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
        with open('ex_area{0}.table'.format(i), 'r') as infile:
            with open('ex_area{0}_2.table'.format(i), 'w') as outfile:
                for j, line in enumerate(infile):
                    if j > 2:
                        outfile.write(line.split()[1])
                        outfile.write("\n")
            outfile.close()
        infile.close()


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
        print(tasks_that_are_done.get())

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
    dump / avs / area_sum{0}.inp / frac 
        
    cmo / delete / mo_vertex
    cmo / delete / frac
    """.format(f_id)
    fin += "finish"
    print(fin)
    f.write(fin)
    f.flush()
    f.close()

    cmd = os.environ['LAGRIT_EXE'] + '< driver{0}.lgi'.format(f_id)
    subprocess.call(cmd, shell=True)


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
