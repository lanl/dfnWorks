import os
import numpy as np
from pydfnworks.general import helper_functions as hf


def create_poisson_user_function_script():

    lagrit_script = f"""
 
read / avs / INTERSECTION / MO_INTERSECTIONS

compute / distance_field / MO_H_FIELD / MO_INTERSECTIONS / dfield

math/multiply/MO_H_FIELD/h_field_att/1,0,0/MO_H_FIELD/dfield/SLOPE/

math/add/MO_H_FIELD/h_field_att/1,0,0/MO_H_FIELD/h_field_att/PARAM_B/

math / floor /   MO_H_FIELD / h_field_att / 1 0 0 / &
                 MO_H_FIELD / h_field_att / H_SCALE

math / ceiling / MO_H_FIELD / h_field_att / 1 0 0 / &
                 MO_H_FIELD / h_field_att / MAX_H_SCALE
 
cmo / delete / mo_line_pts
finish
    """

    with open("user_resolution.mlgi", "w") as fp:
        fp.write(lagrit_script)
        fp.flush()


def grab_z_value(fracture_id):

    with open(f'polys/poly_{fracture_id}.inp', 'r') as fp:
        _ = fp.readline()
        line = fp.readline().split()
        z_value = line[-1]
    return z_value


def create_lagrit_parameters_file(self, fracture_id, index, digits, slope,
                                  intercept, max_resolution_factor):

    ## while h is th key paramter, the intersecctions are meshed at h/2
    local_h = 0.5 * self.h

    # Extrude and Translate computation
    # Parameters, delta: buffer zone, amount of h/2 we remove from around line
    # h_extrude height of rectangle extruded from line of intersection
    # r_radius: Upper bound on radius of circumscribed circle around rectangle
    # h_trans : amount needed to translate to create delta buffer
    # It's  just a little trig!
    delta = 0.75
    # h_extrude = 2*self.h # upper limit on spacing of points on intersection line
    h_extrude = 2 * local_h  # upper limit on spacing of points on intersection line
    h_radius = np.sqrt((0.5 * h_extrude)**2 + (0.5 * h_extrude)**2)
    h_trans = -0.6 * h_extrude + h_radius * np.cos(np.arcsin(delta))

    theta = self.poly_info[fracture_id - 1, 2]
    x1 = self.poly_info[fracture_id - 1, 3]
    y1 = self.poly_info[fracture_id - 1, 4]
    z1 = self.poly_info[fracture_id - 1, 5]
    x2 = self.poly_info[fracture_id - 1, 6]
    y2 = self.poly_info[fracture_id - 1, 7]
    z2 = self.poly_info[fracture_id - 1, 8]
    family = self.poly_info[fracture_id - 1, 1]

    z_value_save = grab_z_value(fracture_id)

    lagrit_script = f"""

## Build header / Parameters
define / POLYGON / poly_{fracture_id}.inp
define / INTERSECTION / intersections_{fracture_id}.inp
define / MO_INTERSECTIONS / mo_line_pts
define / MO_H_FIELD / mo_poi_h_field
define / OUTFILE_LG / mesh_{fracture_id:0{digits}d}.lg 
define / OUTFILE_AVS / mesh_{fracture_id:0{digits}d}.inp
define / OUTPUT_INTER_ID_SSINT / id_tri_node_{fracture_id:0{digits}d}.list

define / H_SCALE /  {local_h}
define / MAX_H_SCALE / {max_resolution_factor*local_h}
define / H_EXTRUDE / {h_extrude}
define / H_TRANS / {h_trans}
define / H_EPS / {local_h * 10**-7:0.12e}
define / H_SCALE2 / {1.5*local_h:0.12e}
define / H_PRIME / {0.8 * local_h: 0.12e}
define / H_PRIME2 / {0.3 * local_h: 0.12e}

define / ID / {index}
define / THETA / {theta:0.12f} 
define / X1 / {x1:0.12f} 
define / Y1 / {y1:0.12f} 
define / Z1 / {z1:0.12f} 
define / X2 / {x2:0.12f} 
define / Y2 / {y2:0.12f} 
define / Z2 / {z2:0.12f} 
define / FAMILY / {family}
define / ZVALUE_SAVE / {z_value_save}

# Y = Ax + B
# Slope
define / SLOPE / {slope}
# Intersect
define / PARAM_B / {intercept} 
finish 

"""

    with open(f'lagrit_scripts/parameters_{fracture_id:0{digits}d}.mlgi',
              "w") as fp:
        fp.write(lagrit_script)
        fp.flush()


def create_lagrit_poisson_script(fracture_id, digits):

    lagrit_script = f"""

infile parameters_{fracture_id:0{digits}d}.mlgi

## Read in polygon boundary and create points and mesh using Poisson Disc Sampling 

read / avs / POLYGON / mo_polygon
cmo / printatt / mo_polygon / -xyz- / minmax

createpts / poisson_disk / 2d_polygon / mo_poisson_pts / mo_polygon &
      / H_SCALE / connect / user_resolution.mlgi

cmo / printatt / mo_poisson_pts / -xyz- / minmax
## move everything to z = 0
cmo/setatt / mo_poisson_pts / zic /1 0 0 / 0  

quality / edge_min / y

cmo / status / brief
cmo / delete / mo_polygon

### Conforming meshing starting #####

# read in intersection file  
read / INTERSECTION / mo_line_work
cmo / select / mo_line_work
cmo/setatt / mo_line_work / zic /1 0 0 / 0  

# extrude the line 
extrude / mo_quad / mo_line_work / const / H_EXTRUDE / volume / 0. 0. 1. 

# Translate extruded lines of intersection down slightly to excavate 
# nearby points from the mesh 
trans / 1 0 0 / 0. 0. 0. / 0. 0. H_TRANS
hextotet / 2 / mo_tri / mo_quad 
cmo / delete / mo_quad
# Remove (excavate) vertices from mo_pts that fall within the circumscribed sphere of any triangle in mo_tri.
# Place the result in mo_excavate. 
addmesh / excavate / mo_excavate / mo_poisson_pts / mo_tri
cmo / create / mo_final / / / triplane 
copypts / mo_final / mo_excavate 

### connect the mesh 
connect 


## Read the lines of intersections into mesh object mo_line_work
cmo / status / brief 

cmo / select / mo_line_work
## set mo line work to z = 0
# cmo / setatt / mo_line_work / zic / 1 0 0 / 0.0 

# Extrude the line mesh a distance H_EXTRUDE in the Z direction (vector 0.,0.,1.) to create a quad mesh.
extrude / mo_quad / mo_line_work / const / H_EXTRUDE / volume / 0. 0. 1. 

# Translate extruded lines of intersection down slightly to excavate 
# nearby points from the mesh 
trans / 1 0 0 / 0. 0. 0. / 0. 0. H_TRANS
hextotet / 2 / mo_tri / mo_quad 
cmo / delete / mo_quad
# Remove (excavate) vertices from mo_pts that fall within the circumscribed sphere of any triangle in mo_tri.
# Place the result in mo_excavate. 

addmesh / excavate / mo_excavate / mo_poisson_pts / mo_tri

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

cmo / printatt / mo_final / -xyz- / minmax 


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
cmo / setatt / mo_final / zic / 1 0 0 / ZVALUE_SAVE 



##### DEBUG #####
# If meshing fails, uncomment and rerun the script to get tmp meshes, 
# which are otherwise not output 
# dump / avs2 / tmp_tri.inp / mo_tri / 1 1 1 0
# dump / avs2 / tmp_pts.inp / mo_poisson_pts / 1 1 1 0
# dump / avs2 / tmp_excavate.inp / mo_excavate / 1 1 1 0
##### DEBUG #####



cmo / delete / mo_poisson_pts 
cmo / delete / mo_excavate
cmo / delete / mo_tri
cmo / select / mo_final 

cmo / status / brief 

#########################################################
## Do we still need this? Think we have this in poisson disk
## driver, correct? 
#########################################################
# ## Massage the mesh where vertices are are not on the boundary and
# # not within a distance H_EPS of the intersection vertices.
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
#########################################################


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


############ nodes for intersection check over

##### DEBUG ###### 
# Write out mesh before it is rotate back into its final location
# Useful to compare with meshing work-flow if something crashes
# dump / avs2 / tmp_mesh_2D.inp / mo_final / 1 1 1 0 
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
    with open(f"lagrit_scripts/mesh_poly_{fracture_id:0{digits}d}.lgi",
              "w") as fp:
        fp.write(lagrit_script)
        fp.flush()


def create_lagrit_reduced_mesh_script(fracture_id, digits):
    """ Creates LaGriT scripts to create a coarse (non-conforming) 
    mesh of each fracture. 
    
    Parameters
    ---------- 

    Returns
    -------
        None

    Notes
    -----
    """

    lagrit_input = f"""
# Name of input files that contains the boundary of the polygon/fracture 
infile parameters_{fracture_id:0{digits}d}.mlgi

## Triangulate Fracture perimeter without point addition 
read / POLYGON / mo_poly_work
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
# dump / OUTFILE_AVS / mo_final 
finish

"""

    with open(f'lagrit_scripts/mesh_poly_{fracture_id:0{digits}d}.lgi',
              'w') as f:
        f.write(lagrit_input)
        f.flush()
