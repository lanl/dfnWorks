"""
.. module:: lagrit_scripts.py
   :synopsis: create lagrit scripts for meshing dfn using LaGriT 
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""
import os
import sys
import glob
from shutil import copy, rmtree, move
from numpy import genfromtxt, sqrt, cos, arcsin
import subprocess

from pydfnworks.dfnGen.meshing import mesh_dfn_helper as mh


def edit_intersection_files(num_poly, fracture_list, path):
    """ If pruning a DFN, this function walks through the intersection files
    and removes references to files that are not included in the 
    fractures that will remain in the network.
 
    Parameters
    ---------
        num_poly : int 
            Number of Fractures in the original DFN
        fracture_list :list of int
            List of fractures to keep in the DFN

    Returns
    -------
        None

    Notes
    -----
    1. Currently running in serial, but it could be parallelized
    2. Assumes the pruning directory is not the original directory

    """
    # Make list of connectivity.dat
    connectivity = []
    with open(path + "/dfnGen_output/connectivity.dat", "r") as fp:
        for i in range(num_poly):
            tmp = []
            line = fp.readline()
            line = line.split()
            for frac in line:
                tmp.append(int(frac))
            connectivity.append(tmp)

    fractures_to_remove = list(
        set(range(1, num_poly + 1)) - set(fracture_list))
    
    cwd = os.getcwd()
    if os.path.isdir('intersections'):
        os.unlink('intersections')
        os.mkdir('intersections')
    else:
        os.mkdir('intersections') 

    os.chdir('intersections')

    ## DEBUGGING ##
    # clean up directory
    #fl_list = glob.glob("*prune.inp")
    #for fl in fl_list:
    #   os.remove(fl)
    ## DEBUGGING ##

    print("--> Editing Intersection Files")
    ## Note this could be easily changed to run in parallel if needed. Just use cf
    for i in fracture_list:
        filename = f'intersections_{i}.inp'
        print(f'--> Working on: {filename}')
        intersecting_fractures = connectivity[i - 1]
        pull_list = list(
            set(intersecting_fractures).intersection(set(fractures_to_remove)))
        if len(pull_list) > 0:
            # Create Symlink to original intersection file
            os.symlink(path + 'intersections/' + filename, filename)
            # Create LaGriT script to remove intersections with fractures not in prune_file
            lagrit_script = f"""
read / {filename} / mo1 
pset / pset2remove / attribute / b_a / 1,0,0 / eq / {pull_list[0]}
"""
            for j in pull_list[1:]:
                lagrit_script += f'''
pset / prune / attribute / b_a / 1,0,0 / eq / {j}
pset / pset2remove / union / pset2remove, prune
rmpoint / pset, get, prune
pset / prune / delete
     '''
            lagrit_script += f'''
rmpoint / pset, get, pset2remove 
rmpoint / compress
    
cmo / modatt / mo1 / imt / ioflag / l
cmo / modatt / mo1 / itp / ioflag / l
cmo / modatt / mo1 / isn / ioflag / l
cmo / modatt / mo1 / icr / ioflag / l
    
cmo / status / brief
dump / intersections_{i}_prune.inp / mo1
finish

'''

            lagrit_filename = 'prune_intersection.lgi'
            f = open(lagrit_filename, 'w')
            f.write(lagrit_script)
            f.flush()
            f.close()
            mh.run_lagrit_script("prune_intersection.lgi",
                                 f"out_{i}.txt",
                                 quiet=True)
            os.remove(filename)
            move(f"intersections_{i}_prune.inp", f"intersections_{i}.inp")
        else:
            try:
                copy(path + 'intersections/' + filename, filename)
            except:
                pass
    os.chdir(cwd)


def create_parameter_mlgi_file(fracture_list, h, slope=2.0, refine_dist=0.5):
    """Create parameteri.mlgi files used in running LaGriT Scripts
    
    Parameters
    ----------
        num_poly : int
            Number of polygons
        h : float 
            Meshing length scale
        slope : float 
            Slope of coarsening function, default = 2
        refine_dist : float 
            Distance used in coarsening function, default = 0.5

    Returns
    -------
        None

    Notes
    -----
    Set slope = 0 for uniform mesh
    """

    print("\n--> Creating parameter*.mlgi files")
    try:
        os.mkdir('parameters')
    except OSError:
        rmtree('parameters')
        os.mkdir('parameters')

    # Extrude and Translate computation
    # Parameters, delta: buffer zone, amount of h/2 we remove from around line
    # h_extrude height of rectangle extruded from line of intersection
    # r_radius: Upper bound on radius of circumscribed circle around rectangle
    # h_trans : amount needed to translate to create delta buffer
    # It's  just a little trig!
    delta = 0.75
    h_extrude = 0.5 * h  # upper limit on spacing of points on intersection line
    h_radius = sqrt((0.5 * h_extrude)**2 + (0.5 * h_extrude)**2)
    h_trans = -0.5 * h_extrude + h_radius * cos(arcsin(delta))

    #Go through the list and write out parameter file for each polygon
    #to be an input file for LaGriT
    data = genfromtxt('poly_info.dat')

    for index, i in enumerate(fracture_list):
        # using i - 1 do to python indexing from 0
        # fracture index starts at 1
        frac_id = str(int(data[i - 1, 0]))
        long_name = str(int(data[i - 1, 0]))

        theta = data[i - 1, 2]
        x1 = data[i - 1, 3]
        y1 = data[i - 1, 4]
        z1 = data[i - 1, 5]
        x2 = data[i - 1, 6]
        y2 = data[i - 1, 7]
        z2 = data[i - 1, 8]
        family = data[i - 1, 1]

        fparameter_name = 'parameters/parameters_' + long_name + '.mlgi'
        f = open(fparameter_name, 'w')
        f.write('define / ID / ' + str(index + 1) + '\n')
        f.write('define / OUTFILE_GMV / mesh_' + long_name + '.gmv\n')
        f.write('define / OUTFILE_AVS / mesh_' + long_name + '.inp\n')
        f.write('define / OUTFILE_LG / mesh_' + long_name + '.lg\n')
        f.write('define / POLY_FILE / poly_' + long_name + '.inp\n')
        f.write('define / QUAD_FILE / tmp_quad_' + frac_id + '.inp\n')
        f.write('define / EXCAVATE_FILE / tmp_excavate_' + frac_id + '.inp\n')
        f.write('define / PRE_FINAL_FILE / tmp_pre_final_' + frac_id +
                '.inp\n')
        f.write('define / PRE_FINAL_MASSAGE / tmp_pre_final_massage_' +
                frac_id + '.gmv\n')

        f.write('define / H_SCALE / %e \n' % h)
        f.write('define / H_EPS / %e \n' % (h * 10**-7))
        f.write('define / H_SCALE2 / %e \n' % (1.5 * h))

        f.write('define / H_EXTRUDE / %e \n' % (h_extrude))
        f.write('define / H_TRANS / %f \n' % (h_trans))

        f.write('define / H_PRIME / %e \n' % (0.4 * h))

        # f.write('define / H_SCALE3 / %e \n' % (3.0 * h))
        # f.write('define / H_SCALE8 / %e \n' % (8.0 * h))
        # f.write('define / H_SCALE16 / %e \n' % (16.0 * h))
        # f.write('define / H_SCALE32 / %e \n' % (32.0 * h))
        # f.write('define / H_SCALE64 / %e \n' % (64.0 * h))

        # f.write('define / PERTURB8 / %e \n' % (8 * 0.05 * h))
        # f.write('define / PERTURB16 / %e \n' % (16 * 0.05 * h))
        # f.write('define / PERTURB32 / %e \n' % (32 * 0.05 * h))
        # f.write('define / PERTURB64 / %e \n' % (64 * 0.05 * h))

        # f.write('define / PARAM_A / %f \n' % slope)
        # f.write('define / PARAM_B / %f \n' % (h * (1 - slope * refine_dist)))

        # f.write('define / PARAM_A2 / %f \n' % (0.5 * slope))
        # f.write('define / PARAM_B2 / %f \n' %
        #         (h * (1 - 0.5 * slope * refine_dist)))

        f.write('define / THETA  / %0.12f \n' % theta)
        f.write('define / X1 /  %0.12f \n' % x1)
        f.write('define / Y1 / %0.12f \n' % y1)
        f.write('define / Z1 / %0.12f \n' % z1)
        f.write('define / X2 / %0.12f \n' % x2)
        f.write('define / Y2 / %0.12f \n' % y2)
        f.write('define / Z2 / %0.12f \n' % z2)
        f.write('define / FAMILY / %d \n' % family)
        f.write('finish \n')
        f.flush()
        f.close()


#         lagrit_input = f"""
# define / ID / {index + 1}
# define / OUTFILE_AVS / mesh_{long_name}.inp
# define / OUTFILE_LG / mesh_{long_name}.lg
# define / POLY_FILE / poly_{long_name}.inp

# define / H_SCALE / {h:e}
# define / H_EPS / {h*10**-7:0.12e}
# define / H_SCALE2 / {h*1.5:0.12e}
# define / H_EXTRUDE / {h_extrude:0.12e}
# define / H_TRANS / {h_trans:0.12e}
# define / H_PRIME / {0.8*h:0.12e}

# define / THETA  / {theta:0.12f}
# define / X1 / {x1:0.12f}
# define / Y1 / {y1:0.12f}
# define / Z1 / {z1:0.12f}

# define / X2 / {x2:0.12f}
# define / Y2 / {y2:0.12f}
# define / Z2 / {z2:0.12f}
# define / FAMILY / {family}

# finish

# # """
#         with open(f'parameters/parameters_{long_name}.mlgi', 'w') as fp:
#             fp.write(lagrit_input)
#             fp.flush()
#             fp.close()

    print("--> Creating parameter*.mlgi files: Complete\n")


def create_lagrit_scripts_poisson(fracture_list):
    """ Creates LaGriT script to be mesh each polygon using Poisson-Disc
    sampling method
    
    Parameters
    ---------- 
        fracture_list : list
            list of fracture numbers to be meshed

    Returns
    -------
        None

    Notes
    -----

    """

    #Section 2 : Creates LaGriT script to be run for each polygon
    #Switches to control the LaGriT output
    #Network visualization mode True ouputs the triangulated mesh
    #for each fracture without any refinement. The goal is to visualize
    #the network structure instead of outputing the appropriate values
    #for computation

    print("--> Writing LaGriT Control Files")
    #Go through the list and write out parameter file for each polygon
    #to be an input file for LaGriT

    lagrit_input = """
# This LaGriT Scripts reads in the points generated by the Poisson-Disc
# sampling method. Then it reads in the intersection points generated 
# in dfnGEn. All points in the Poisson-Disc set that are too close to
# the line of intersection are removed. Then the mesh is written out 
# in binary LaGriT and AVS UCD format. 

# LaGriT Parameter file 
infile parameters_{0}.mlgi

# Name of input files that contains the lines of intersection
# and Poisson Points

define / POINT_FILE / points_{0}.xyz
define / LINE_FILE / intersections_{0}.inp

# connectivity file used in mesh checking
define / OUTPUT_INTER_ID_SSINT / id_tri_node_{0}.list

#### READ IN POISSON DISC POINTS

# Create a mesh object named mo_pts
cmo / create / mo_pts / / / triplane

# Read in the three column x,y,z vertex data
cmo / readatt / mo_pts / xic,yic,zic / 1,0,0 / POINT_FILE

# Send some diagnostic output to the screen
cmo / status / brief
cmo / printatt / mo_pts / -xyz- / minmax

# Set imt (integer material type) of all vertices to ID
cmo / setatt / mo_pts / imt / 1 0 0 / ID
# Set itp of all vertices to 0
cmo / setatt / mo_pts / itp / 1 0 0 / 0

# This should not do anything. If there were 2 or more vertices within distance
# epsilon of one another, this would remove all but one. Since the distributions
# should be well behaved, it should not filter/delete any vertices.

filter / 1 0 0
rmpoint / compress
#
# Connect the 2D planar (XY-plane) vertices to create a Delaunay triangular mesh
# with an exterior boundary that is the convex hull of the vertices in mo_pts.
connect
resetpts / itp

# Diagnostic output to the screen on triangle aspect ratio and volume (area)
quality

# Add cell attribute for area and aspect ratio
cmo / addatt / mo_pts / area / tri_area
quality / aspect / y

# Apply two iterations of Laplace smoothing and Lawson flipping to smooth the mesh
# and recover the Delaunay triangulation.
assign///maxiter_sm/ 1                                                           
smooth;recon 0
smooth;recon 1

##### DEBUG #####
# comments out to dump poisson initial triangulation 
# dump / avs2 / output_{0}.inp / mo_pts
##### DEBUG #####

## Read the lines of intersections into mesh object mo_line_work
read / LINE_FILE / mo_line_work

# Extrude the line mesh a distance H_EXTRUDE in the Z direction (vector 0.,0.,1.) to create a quad mesh.
extrude / mo_quad / mo_line_work / const / H_EXTRUDE / volume / 0. 0. 1. 


# Translate extruded lines of intersection down slightly to excavate 
# nearby points from the mesh 

trans / 1 0 0 / 0. 0. 0. / 0. 0. H_TRANS
hextotet / 2 / mo_tri / mo_quad 
cmo / delete / mo_quad
# Remove (excavate) vertices from mo_pts that fall within the circumscribed sphere of any triangle in mo_tri.
# Place the result in mo_excavate. 
addmesh / excavate / mo_excavate / mo_pts / mo_tri

##### DEBUG #####
# If meshing fails, uncomment and rerun the script to get tmp meshes, 
# which are otherwise not output 
#dump / avs2 / tmp_tri.inp / mo_tri / 1 1 1 0
#dump / avs2 / tmp_pts.inp / mo_pts / 1 1 1 0
#dump / avs2 / tmp_excavate.inp / mo_excavate / 1 1 1 0
##### DEBUG #####

cmo / delete / mo_tri 
cmo / delete / mo_pts 

# recompute dfield 
cmo / create / mo_final / / / triplane 
copypts / mo_final / mo_excavate 
# Compute the distance field between the vertices in mo_line_work (fracture intersections)
# and the vertices in mo_final (fracture mesh vertices).
compute / distance_field / mo_final / mo_line_work / dfield 
# Output min/max values of distance field (dfield)
cmo / printatt / mo_final / dfield / minmax 
pset / pdel / attribute dfield / 1,0,0 / lt H_PRIME 
# Delete any vertices with distance field less than H_PRIME
rmpoint / pset,get,pdel / inclusive  
rmpoint / compress  
# Copy the intersection vertices into the fracture mesh mo_final
copypts / mo_final / mo_line_work  

cmo / select / mo_final 
cmo / setatt / mo_final / imt / 1 0 0 / ID 
cmo / setatt / mo_final / itp / 1 0 0 / 0 
# cmo / printatt / mo_final / -xyz- / minmax 
# Translate the vertices so the bounding box is centered on 0,0,0.
trans/ 1 0 0 / zero / xyz 
# Due to slight numerical jitter, all Z values may not be 0. Set them to 0.
cmo / setatt / mo_final / zic / 1 0 0 / 0.0 
cmo / printatt / mo_final / -xyz- / minmax 
# Connect the 2D planar (XY-plane) vertices to create a Delaunay triangular mesh
# with an exterior boundary that is the convex hull of the vertices in mo_final.
connect 
cmo / setatt / mo_final / itetclr / 1 0 0 / ID 
resetpts / itp 
# Translate back to the original coordinates.
trans / 1 0 0 / original / xyz 
cmo / printatt / mo_final / -xyz- / minmax 

#cmo / delete / mo_line_work 
cmo / delete / mo_excavate
cmo / select / mo_final 

## Massage the mesh where vertices are are not on the boundary and
# not within a distance H_EPS of the intersection vertices.
pset / pref / attribute / dfield / 1,0,0 / lt / H_EPS 
pset / pregion / attribute / dfield / 1,0,0 / gt / H_SCALE2 
pset / pboundary / attribute / itp / 1,0,0 / eq / 10 
pset / psmooth / not / pregion pref pboundary 

assign///maxiter_sm/1 
smooth / position / esug / pset get psmooth
recon 0
smooth / position / esug / pset get psmooth
recon 0
smooth / position / esug / pset get psmooth
recon 1
assign///maxiter_sm/10


###########################################
# nodes for Intersection / Mesh Connectivity Check dump
cmo / copy / mo_final_check / mo_final
#
# Define variables that are hard wired for this part of the workflow
define / MO_TRI_MESH_SSINT / mo_tri_tmp_subset
define / MO_LINE_MESH_SSINT / mo_line_tmp_subset
define / ATT_ID_INTERSECTION_SSINT / b_a
define / ATT_ID_SOURCE_SSINT / id_node_global
define / ATT_ID_SINK_SSINT / id_node_tri
#
# Before subsetting the mesh reate a node attribute containing the integer global node number
cmo / set_id / mo_final_check / node / ATT_ID_SOURCE_SSINT
#
# Subset the triangle mesh based on b_a node attribute ne 0
#
cmo / select / mo_final_check
pset / pkeep / attribute / ATT_ID_INTERSECTION_SSINT / 1 0 0 / ne / 0
pset / pall / seq / 1 0 0
pset / pdel / not pall pkeep
rmpoint / pset get pdel / exclusive
rmpoint / compress
#
# Create an integer node attribute in the line mesh to interpolate the triangle node number onto
# 
cmo / addatt / mo_line_work / ATT_ID_SINK_SSINT / vint / scalar / nnodes
interpolate / voronoi / mo_line_work ATT_ID_SINK_SSINT / 1 0 0 / &
                        mo_final_check  ATT_ID_SOURCE_SSINT
#
# Supress AVS output of a bunch of node attributes
#
cmo / modatt / mo_line_work / imt / ioflag / l
cmo / modatt / mo_line_work / itp / ioflag / l
cmo / modatt / mo_line_work / isn / ioflag / l
cmo / modatt / mo_line_work / icr / ioflag / l
cmo / modatt / mo_line_work / a_b / ioflag / l
cmo / modatt / mo_line_work / b_a / ioflag / l
#
# Output list of intersection nodes with the corresponding node id number from the triangle mesh

dump / avs2 / OUTPUT_INTER_ID_SSINT / mo_line_work / 0 0 2 0
cmo / delete / mo_line_work

cmo / delete / mo_final_check
# nodes for intersection check over

cmo / select / mo_final 

##### DEBUG ###### 
# Write out mesh before it is rotate back into its final location
# Useful to compare with meshing work-flow if something crashes
#dump / avs2 / tmp_mesh_2D.inp / mo_final / 1 1 1 0 
##### DEBUG #####

# Rotate fracture back into original plane 
rotateln / 1 0 0 / nocopy / X1, Y1, Z1 / X2, Y2, Z2 / THETA / 0.,0.,0.,/  
cmo / printatt / mo_final / -xyz- / minmax

# Create cell attributes, xnorm, ynorm, znorm, and fill them with the unit normal vector.
cmo / addatt / mo_final / unit_area_normal / xyz / vnorm 
cmo / addatt / mo_final / scalar / xnorm ynorm znorm / vnorm 
cmo / DELATT / mo_final / vnorm

# Create Family element set
cmo / addatt / mo_final / family_id / vint / scalar / nelements 
cmo / setatt / mo_final / family_id / 1 0 0 / FAMILY

# Output mesh in AVS UCD format - required for connectivity checking, is promptly deleted
dump / OUTFILE_AVS / mo_final
# Output mesh in LaGriT binary format. 
dump / lagrit / OUTFILE_LG / mo_final

quality 
cmo / delete / mo_final 
cmo / status / brief 
finish

"""

    if os.path.isdir('lagrit_scripts'):
        rmtree("lagrit_scripts")
        os.mkdir("lagrit_scripts")
    else:
        os.mkdir("lagrit_scripts")

    # Create a different run file for each fracture
    for i in fracture_list:
        file_name = 'lagrit_scripts/mesh_poly_{0}.lgi'.format(i)
        with open(file_name, 'w') as f:
            f.write(lagrit_input.format(i))
            f.flush()
    print('--> Writing LaGriT Control Files: Complete')


def create_lagrit_scripts_reduced_mesh(fracture_list):
    """ Creates LaGriT scripts to create a coarse (non-conforming) 
    mesh of each fracture. 
    
    Parameters
    ---------- 
        fracture_list : list
            list of fracture numbers to be meshed

    Returns
    -------
        None

    Notes
    -----
    """

    #Section 2 : Creates LaGriT script to be run for each polygon
    #Switches to control the LaGriT output
    #Network visualization mode True ouputs the triangulated mesh
    #for each fracture without any refinement. The goal is to visualize
    #the network structure instead of outputing the appropriate values
    #for computation

    print("--> Writing LaGriT Control Files")

    lagrit_input = """

# LaGriT Parameter file 
infile parameters_{0}.mlgi

# Name of input files that contains the boundary of the polygon/fracture 

define / POLY_FILE / poly_{0}.inp

## Triangulate Fracture perimeter without point addition 
read / POLY_FILE / mo_poly_work
cmo / create / mo_pts / / / triplane 
copypts / mo_pts / mo_poly_work 
cmo / select / mo_pts 
triangulate / counterclockwise 

cmo / setatt / mo_pts / imt / 1 0 0 / ID 
cmo / setatt / mo_pts / itetclr / 1 0 0 / ID 
resetpts / itp 
cmo / delete / mo_poly_work 
cmo / select / mo_pts 

# Create Family element set
cmo / addatt / mo_pts / family_id / vint / scalar / nelements 
cmo / setatt / mo_pts / family_id / 1 0 0 / FAMILY

# Rotate 
rotateln / 1 0 0 / nocopy / X1, Y1, Z1 / X2, Y2, Z2 / THETA / 0.,0.,0.,/ 
# Supress AVS output of a icr and isn node attributes
cmo / modatt / mo_pts / icr1 / ioflag / l 
cmo / modatt / mo_pts / isn1 / ioflag / l
cmo / copy/ mo_final /mo_pts
# Output mesh in AVS UCD format and LaGriT binary format.
dump / lagrit / OUTFILE_LG / mo_final 
dump / OUTFILE_AVS / mo_final 
finish

"""

    if os.path.isdir('lagrit_scripts'):
        rmtree("lagrit_scripts")
        os.mkdir("lagrit_scripts")
    else:
        os.mkdir("lagrit_scripts")

    # Create a different run file for each fracture
    for i in fracture_list:
        file_name = f'lagrit_scripts/mesh_poly_{i}.lgi'
        with open(file_name, 'w') as f:
            f.write(lagrit_input.format(i))
            f.flush()
    print('--> Writing LaGriT Control Files: Complete')

    print('--> Writing LaGriT Control Files: Complete')


def create_merge_poly_files(ncpu, num_poly, fracture_list, h, visual_mode,
                            domain, flow_solver):
    """ Creates a LaGriT script that reads in each fracture mesh, appends it to the main mesh, and then deletes that mesh object. Then duplicate points are removed from the main mesh using EPS_FILTER.  The points are compressed, and then written to file.

    Parameters
    ----------
        ncpu : int 
            Number of Processors used for meshing
        fracture_list : list of int
            List of fracture numbers in the DFN
        h : float 
            Meshing length scale
        visual_mode : bool
            If True, reduced_mesh.inp will be output. If False, full_mesh.inp is output
        domain : dict
            Dictionary of x,y,z domain size
        flow_solver : string
            Name of target flow solver (Changes output files)

    Returns
    -------
        n_jobs : int
            number of merge jobs

    Notes
    -----
    1. Fracture mesh objects are read into different part_*.lg files. This allows for merging of the mesh to be performed in batches.  
    """

    print("--> Writing : merge_poly.lgi")
    part_size = int(num_poly / ncpu) + 1  ###v number of fractures in each part
    endis = []
    ii = 0
    for i in fracture_list[:-1]:
        ii += 1
        if ii == part_size:
            endis.append(i)
            ii = 0
    endis.append(fracture_list[-1])
    n_jobs = len(endis)

    lagrit_input = """
# Change to read LaGriT
read / lagrit /  %s / mo_%d / binary
cmo / move / mo_%d / mo_final 
define / MO_NAME_FRAC / mo_%d
"""
    if not visual_mode:
        lagrit_input += """
cmo / addatt / MO_NAME_FRAC / volume / evol_one
math / sum / MO_NAME_FRAC / evol_sum / 1 0 0 / MO_NAME_FRAC / evol_one 
"""
    lagrit_input += """
addmesh / merge / cmo_tmp / cmo_tmp / mo_%d
cmo / delete / mo_%d
"""
    lagrit_input_2 = '#Writing out merged fractures\n'
    if not visual_mode:
        lagrit_input_2 += """
mo / addatt/ cmo_tmp / volume / evol_all
math / sum / cmo_tmp / evol_sum / 1 0 0 / cmo_tmp / evol_all """
    lagrit_input_2 += """ 
cmo select cmo_tmp
dump lagrit part%d.lg cmo_tmp
finish \n 
"""

    j = 0  # Counter for cpus
    fout = 'lagrit_scripts/merge_poly_part_1.lgi'
    f = open(fout, 'w')
    for i in fracture_list:
        tmp = 'mesh_' + str(i) + '.lg'
        f.write(lagrit_input % (tmp, i, i, i, i, i))
        # if i is the last fracture in the cpu set
        # move to the next cpu set
        if i == endis[j]:
            f.write(lagrit_input_2 % (j + 1))
            f.flush()
            f.close()
            j += 1
            fout = 'lagrit_scripts/merge_poly_part_' + str(j + 1) + '.lgi'
            f = open(fout, 'w')

    f.flush()
    f.close()
    os.remove(fout)  ###

    ## Write LaGriT file for merge parts of the mesh and remove duplicate points

    lagrit_input = """
read / lagrit / part%d.lg / junk / binary
addmesh / merge / mo_all / mo_all / cmo_tmp 
cmo / delete / cmo_tmp 
    """
    f = open('lagrit_scripts/merge_rmpts.lgi', 'w')
    for j in range(1, n_jobs + 1):
        f.write(lagrit_input % (j))

    # Append meshes complete
    if not visual_mode:
        lagrit_input = """
# Appending the meshes complete 
# LaGriT Code to remove duplicates and output the mesh
cmo / select / mo_all 
#recon 1
define / EPS / %e 
define / EPS_FILTER / %e 
pset / pinter / attribute / dfield / 1,0,0 / lt / EPS 
#cmo / addatt / mo_all / inter / vint / scalar / nnodes 
#cmo / setatt / mo_all / inter / 1 0 0 / 0 
#cmo / setatt / mo_all / inter / pset, get, pinter / 1 

filterkd / pset get pinter / EPS_FILTER / nocheck
pset / pinter / delete

rmpoint / compress 
# SORT can affect a_b attribute
sort / mo_all / index / ascending / ikey / imt xic yic zic 
reorder / mo_all / ikey 
cmo / DELATT / mo_all / ikey
""" % (h * 10**-5, h * 10**-3)
        lagrit_input += """ 
resetpts / itp 
boundary_components 
#dump / full_mesh.gmv / mo_all
dump / full_mesh.inp / mo_all
dump / lagrit / full_mesh.lg / mo_all
"""
        if flow_solver == "PFLOTRAN":
            print("\n--> Dumping output for %s" % flow_solver)
            lagrit_input += """
dump / pflotran / full_mesh / mo_all / nofilter_zero
dump / stor / full_mesh / mo_all / ascii
    """
        elif flow_solver == "FEHM":
            print("\n--> Dumping output for %s" % flow_solver)
            lagrit_input += """
dump / stor / full_mesh / mo_all / ascii
dump / coord / full_mesh / mo_all 
# matid start at 1, but we need them to start at 7 for FEHM due to zone files
# So we do a little addition
math / add / mo_all / imt1 / 1,0,0 / mo_all / imt1 / 6
dump / zone_imt / full_mesh / mo_all
# and then we subtract 6 back 
math / subtract / mo_all / imt1 / 1,0,0 / mo_all / imt1 / 6
"""
        else:
            print("WARNING!!!!!!!\nUnknown flow solver selection: %s" %
                  flow_solver)
        lagrit_input += """ 
# Dump out Material ID Dat file
cmo / modatt / mo_all / isn / ioflag / l
cmo / modatt / mo_all / x_four / ioflag / l
cmo / modatt / mo_all / fac_n / ioflag / l
cmo / modatt / mo_all / dfield / ioflag / l
cmo / modatt / mo_all / rf_field / ioflag / l
cmo / modatt / mo_all / a_b / ioflag / l
cmo / modatt / mo_all / b_a / ioflag / l
cmo / modatt / mo_all / xnorm / ioflag / l
cmo / modatt / mo_all / ynorm / ioflag / l
cmo / modatt / mo_all / znorm / ioflag / l
cmo / modatt / mo_all / evol_one / ioflag / l
cmo / modatt / mo_all / evol_all / ioflag / l
cmo / modatt / mo_all / numbnd / ioflag / l
cmo / modatt / mo_all / id_numb / ioflag / l
cmo / modatt / mo_all / evol_all / ioflag / l
cmo / modatt / mo_all / itp / ioflag / l
cmo / modatt / mo_all / icr / ioflag / l
cmo / modatt / mo_all / meshid / ioflag / l
cmo / modatt / mo_all / id_n_1 / ioflag / l
cmo / modatt / mo_all / id_n_2 / ioflag / l
cmo / modatt / mo_all / pt_gtg / ioflag / l
# Dump out Material ID Dat file
dump / avs2 / materialid.dat / mo_all / 0 0 2 0

cmo / modatt / mo_all / imt1 / ioflag / l
#cmo / modatt / mo_all / family_id / ioflag / l
cmo / modatt / mo_all / evol_onen / ioflag / l
# Dump mesh with no attributes for viz
dump / full_mesh_viz.inp / mo_all

# Dump out zone files
define / XMAX / %e 
define / XMIN / %e 
define / YMAX / %e 
define / YMIN / %e 
define / ZMAX / %e 
define / ZMIN / %e 

define / ZONE / 1
define / FOUT / boundary_top
pset / top / attribute / zic / 1,0,0/ gt / ZMAX
pset / top / zone / FOUT/ ascii / ZONE

define / ZONE / 2
define / FOUT / boundary_bottom
pset / bottom / attribute / zic / 1,0,0/ lt / ZMIN
pset / bottom / zone / FOUT/ ascii / ZONE

define / ZONE / 3
define / FOUT / boundary_left_w
pset / left_w / attribute/ xic/ 1,0,0 /lt / XMIN
pset / left_w / zone / FOUT/ ascii / ZONE

define / ZONE / 4
define / FOUT / boundary_front_n
pset / front_n / attribute/ yic / 1,0,0 / gt / YMAX
pset / front_n / zone / FOUT/ ascii / ZONE

define / ZONE / 5
define / FOUT / boundary_right_e
pset / right_e / attribute/ xic / 1,0,0/ gt / XMAX
pset / right_e / zone / FOUT/ ascii / ZONE

define / ZONE / 6
define / FOUT / boundary_back_s
pset / back_s / attribute/ yic/ 1,0,0 / lt / YMIN
pset / back_s / zone / FOUT/ ascii / ZONE

"""
        eps = h * 10**-3
        parameters = (0.5*domain['x'] - eps, -0.5*domain['x'] + eps, \
            0.5*domain['y'] - eps, -0.5*domain['y'] + eps, \
            0.5*domain['z'] - eps, -0.5*domain['z'] + eps)

        lagrit_input = lagrit_input % parameters

    else:
        lagrit_input = """
cmo / modatt / mo_all / icr1 / ioflag / l
cmo / modatt / mo_all / isn1 / ioflag / l
cmo / modatt / mo_all / itp1 / ioflag / l
#dump / reduced_mesh.gmv / mo_all 
dump / reduced_mesh.inp / mo_all
"""
    lagrit_input += """
quality 
finish
"""
    f.write(lagrit_input)
    f.flush()
    f.close()

    return n_jobs


def define_zones():
    """Processes zone files for particle tracking. All zone files are combined into allboundaries.zone 
    
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

    fall = open("allboundaries.zone", "w")
    #copy all but last 2 lines of boundary_top.zone in allboundaries.zone
    fzone = open("boundary_top.zone", "r")
    lines = fzone.readlines()
    lines = lines[:-2]
    fzone.close()
    fall.writelines(lines)
    #copy all but frist and last 2 lines of boundary_bottom.zone in allboundaries.zone
    files = ['bottom', 'left_w', 'front_n', 'right_e']
    for f in files:
        fzone = open("boundary_%s.zone" % f, "r")
        lines = fzone.readlines()
        lines = lines[1:-2]
        fzone.close()
        fall.writelines(lines)
    fzone = open("boundary_back_s.zone", "r")
    lines = fzone.readlines()
    lines = lines[1:]
    fzone.close()
    fall.writelines(lines)
    fall.close()
    # copies boundary zone files for PFLOTRAN
    # This can be deleted once we clean up the flow
    move('boundary_bottom.zone', 'pboundary_bottom.zone')
    move('boundary_left_w.zone', 'pboundary_left_w.zone')
    move('boundary_front_n.zone', 'pboundary_front_n.zone')
    move('boundary_right_e.zone', 'pboundary_right_e.zone')
    move('boundary_back_s.zone', 'pboundary_back_s.zone')
    move('boundary_top.zone', 'pboundary_top.zone')

    ## Remove Left over zone files
    #os.remove('boundary_bottom.zone')
    #os.remove('boundary_top.zone')
    #os.remove('boundary_left_w.zone')
    #os.remove('boundary_right_e.zone')
    #os.remove('boundary_front_n.zone')
    #os.remove('boundary_back_s.zone')
