"""
.. file:: lagrit_scripts.py
   :synopsis: create lagrit scripts for meshing dfn using LaGriT 
   :version: 1.0
   :maintainer: Jeffrey Hyman, Carl Gable, Nathaniel Knapp
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import os
from shutil import copy, rmtree
from numpy import genfromtxt, sqrt, cos, arcsin

def create_parameter_mlgi_file(num_poly, h, slope = 2, refine_dist = 0.5):
    """create parameter_mgli_files
    Outputs parameteri.mlgi files used in running LaGriT Scripts
    Inputs:
    num_poly: Number of polygons
    h: meshing length scale
    slope: Slope of coarsening function, default = 2, 
    	set to 0 for uniform mesh resolution
    refine_dist: distance used in coarsing function, default = 0.5,
    """
    
    print("\nCreating parameter*.mlgi files")
    try:
    	os.mkdir('parameters')
    except OSError:
    	rmtree('parameters')	
    	os.mkdir('parameters')

    # Extrude and Translate computation
    # Parameters, delta: buffer zone, amount of h/2 we remove from around line
    # h_extrude hieght of rectangle extruded from line of intersection
    # r_radius: Upper bound on radius of circumscribed circle around rectangle
    # h_trans : amount needed to translate to create delta buffer
    # It's  just a little trig! 
    delta = 0.75
    h_extrude = 0.5*h # upper limit on spacing of points on interssction line
    h_radius = sqrt((0.5*h_extrude)**2 + (0.5*h_extrude)**2)
    h_trans = -0.5*h_extrude + h_radius*cos(arcsin(delta))

    #Go through the list and write out parameter file for each polygon
    #to be an input file for LaGriT
    data = genfromtxt('poly_info.dat')
    for i in range(num_poly):
    	
    	frac_id = str(int(data[i,0]))
    	long_name = str(int(data[i,0]))  	
    	theta = data[i,2]	
    	x1 = data[i,3]	
    	y1 = data[i,4]	
    	z1 = data[i,5]	
    	x2 = data[i,6]	
    	y2 = data[i,7]	
    	z2 = data[i,8]	
    	family = data[i,1]

    	fparameter_name = 'parameters/parameters_' + long_name + '.mlgi'
    	f = open(fparameter_name, 'w')
    	f.write('define / ID / ' + frac_id + '\n')
    	f.write('define / OUTFILE_GMV / mesh_' + long_name + '.gmv\n')
    	f.write('define / OUTFILE_AVS / mesh_' + long_name + '.inp\n')
    	f.write('define / OUTFILE_LG / mesh_' + long_name + '.lg\n')
    	f.write('define / POLY_FILE / poly_' + long_name + '.inp\n')
    	f.write('define / QUAD_FILE / tmp_quad_' + frac_id + '.inp\n')
    	f.write('define / EXCAVATE_FILE / tmp_excavate_' + frac_id + '.inp\n')
    	f.write('define / PRE_FINAL_FILE / tmp_pre_final_'+frac_id + '.inp\n')
    	f.write('define / PRE_FINAL_MASSAGE / tmp_pre_final_massage_' + frac_id +'.gmv\n')
    	
    	f.write('define / H_SCALE / ' + str(h) + '\n')
    	f.write('define / H_EPS / ' + str(h*10**-7) + '\n')
    	f.write('define / H_SCALE2 / ' + str(1.5*h) + '\n')

    	f.write('define / H_EXTRUDE / ' + str(h_extrude) + '\n')
    	f.write('define / H_TRANS / ' + str(h_trans) + '\n')

    	f.write('define / H_PRIME / ' + str(0.8*h) + '\n')
    	f.write('define / H_PRIME2 / ' + str(0.3*h) + '\n')
    	
    	f.write('define / H_SCALE3 / ' + str(3*h) + '\n')
    	f.write('define / H_SCALE8 / ' + str(8*h) + '\n')
    	f.write('define / H_SCALE16 / ' + str(16*h) + '\n')
    	f.write('define / H_SCALE32 / ' + str(32*h) + '\n')
    	f.write('define / H_SCALE64 / ' + str(64*h) + '\n')

    	f.write('define / PURTURB8 / ' + str(8*0.05*h) + '\n')
    	f.write('define / PURTURB16 / ' + str(16*0.05*h) + '\n')
    	f.write('define / PURTURB32 / ' + str(32*0.05*h) + '\n')
    	f.write('define / PURTURB64 / ' + str(64*0.05*h) + '\n')

    	f.write('define / PARAM_A / '+str(slope)+'\n')	
    	f.write('define / PARAM_B / '+str(h*(1-slope*refine_dist))+'\n')	

    	f.write('define / PARAM_A2 / '+str(0.5*slope)+'\n')	
    	f.write('define / PARAM_B2 / '+str(h*(1 - 0.5*slope*refine_dist))+'\n')	
    	
    	f.write('define / THETA  / '+str(theta)+'\n')
    	f.write('define / X1 / '+str(x1)+'\n')
    	f.write('define / Y1 / '+str(y1)+'\n')
    	f.write('define / Z1 / '+str(z1)+'\n')
    	f.write('define / X2 / '+str(x2)+'\n')
    	f.write('define / Y2 / '+str(y2)+'\n')
    	f.write('define / Z2 / '+str(z2)+'\n')
    	f.write('define / family / '+str(family)+'\n')
    	f.write('finish \n')
    	f.flush()
    	f.close()
    print("Creating parameter*.mlgi files: Complete\n")

def create_lagrit_scripts(visual_mode, ncpu, refine_factor=1, production_mode=True): 
    """create_lagrit_scripts
    Creates LaGriT script to be run for each polygon
    Inputs: visual_mode (True / False)
    ncpu: number of cpus
    refine_fractor: used rectangles
    produnction_mode (True/False)
    """

    #Section 2 : Creates LaGriT script to be run for each polygon
    #Switches to control the LaGriT output
    #Network visualization mode True ouputs the triangulated mesh
    #for each fracture without any refinement. The goal is to visualize
    #the network structure instead of outputing the appropriate values
    #for computation

    print("Writing LaGriT Control Files")
    #Go through the list and write out parameter file for each polygon
    #to be an input file for LaGriT

    lagrit_input = """infile %s 
#LaGriT Script
# Name the input files that contain the polygons 
# and lines of intersection. 

define / POLY_FILE / %s 
define / LINE_FILE / %s 
define / OUTPUT_INTER_ID_SSINT / id_tri_node_CPU%d.list

# Define parameters such as: 
# length scale to refine triangular mesh  
# purturbation distance to break symmetry of refined mesh# 

# Read in line and polygon files  
read / POLY_FILE / mo_poly_work
""" 
    if not visual_mode:
    	lagrit_input += """
read / LINE_FILE / mo_line_work 
"""
    #
    # START: Refine the point distribution
    #
    if(refine_factor > 1):
    	lagrit_input += 'extrude / mo_quad_work / mo_line_work / const / H_SCALE8 / volume / 0. 0. 1.  \n'
    	if (refine_factor == 2):
    		lagrit_input += 'refine/constant/imt1/linear/element/1 0 0 /-1.,0.,0./inclusive amr 2  \n'

    	if (refine_factor == 4):
    		lagrit_input += 'refine/constant/imt1/linear/element/1 0 0 /-1.,0.,0./inclusive amr 2  \n'
    		lagrit_input += 'refine/constant/imt1/linear/element/1 0 0 /-1.,0.,0./inclusive amr 2  \n'
    		
    	if (refine_factor == 8):
    		lagrit_input +='refine/constant/imt1/linear/element/1 0 0 /-1.,0.,0./inclusive amr 2  \n'
    		lagrit_input +='refine/constant/imt1/linear/element/1 0 0 /-1.,0.,0./inclusive amr 2  \n'
    		lagrit_input +='refine/constant/imt1/linear/element/1 0 0 /-1.,0.,0./inclusive amr 2  \n'
    		
    	lagrit_input += """ 
grid2grid / tree_to_fe / mo_quad_work / mo_quad_work  
extract/surfmesh/1,0,0/mo_ext_work/mo_quad_work/external 
compute / distance_field / mo_ext_work / mo_line_work / dfield 
pset / pdel_work / attribute / dfield / 1 0 0 / H_SCALE3 / gt 
rmpoint / pset get pdel_work / inclusive 
rmpoint / compress  

cmo / delete / mo_quad_work 
cmo / delete / mo_line_work
cmo / move / mo_line_work / mo_ext_work 
rmpoint / compress  
"""    
    	# END: Refine the point distribution
    	#
    lagrit_input += """
## Triangulate Fracture without point addition 
cmo / create / mo_pts / / / triplane 
copypts / mo_pts / mo_poly_work 
cmo / select / mo_pts 
triangulate / counterclockwise 

cmo / setatt / mo_pts / imt / 1 0 0 / ID 
cmo / setatt / mo_pts / itetclr / 1 0 0 / ID 
resetpts / itp 
cmo / delete / mo_poly_work 
cmo / select / mo_pts 

"""
    if not visual_mode:
    	lagrit_input += """
# Creates a Coarse Mesh and then refines it using the distance field from intersections
massage / H_SCALE64 / H_EPS  / H_EPS
recon 0; smooth;recon 0;smooth;recon 0;smooth;recon 0
resetpts / itp
pset / p_move / attribute / itp / 1 0 0 / 0 / eq
perturb / pset get p_move / PURTURB64 PURTURB64 0.0
recon 0; smooth;recon 0;smooth;recon 0;smooth;recon 0
smooth;recon 0;smooth;recon 0;smooth;recon 0

massage / H_SCALE32 / H_EPS / H_EPS
resetpts / itp
pset / p_move / attribute / itp / 1 0 0 / 0 / eq
perturb / pset get p_move / PURTURB32 PURTURB32 0.0
recon 0; smooth;recon 0;smooth;recon 0;smooth;recon 0
smooth;recon 0;smooth;recon 0;smooth;recon 0

massage / H_SCALE16 / H_EPS  / H_EPS
resetpts / itp
pset / p_move / attribute / itp / 1 0 0 / 0 / eq
perturb / pset get p_move / PURTURB16 PURTURB16 0.0
recon 0; smooth;recon 0;smooth;recon 0;smooth;recon 0
smooth;recon 0;smooth;recon 0;smooth;recon 0

massage / H_SCALE8 / H_EPS / H_EPS
resetpts / itp
pset / p_move / attribute / itp / 1 0 0 / 0 / eq
perturb / pset get p_move / PURTURB8 PURTURB8 0.0
recon 0; smooth;recon 0;smooth;recon 0;smooth;recon 0
smooth;recon 0;smooth;recon 0;smooth;recon 0

cmo/addatt/ mo_pts /x_four/vdouble/scalar/nnodes 
cmo/addatt/ mo_pts /fac_n/vdouble/scalar/nnodes 

# Massage points based on linear function down to h_prime
massage2/user_function2.lgi/H_PRIME/fac_n/1.e-5/1.e-5/1 0 0/strictmergelength 

assign///maxiter_sm/1 
smooth;recon 0;smooth;recon 0;smooth;recon 0

assign///maxiter_sm/10

massage2/user_function.lgi/H_PRIME/fac_n/1.e-5/1.e-5/1 0 0/strictmergelength 
cmo / DELATT / mo_pts / rf_field_name 

# Extrude and excavate the lines of intersection
cmo / select / mo_line_work 

extrude / mo_quad / mo_line_work / const / H_EXTRUDE / volume / 0. 0. 1. 
"""
    	if not production_mode:
    		lagrit_input += """
dump / avs / QUAD_FILE / mo_quad 
cmo / delete / mo_quad 
read / QUAD_FILE / mo_quad 
"""
    	else:
    		lagrit_input += 'cmo / select / mo_quad \n'
    	
    	lagrit_input += """
# Translate extruced lines of intersectino down slightly to excavate 
# nearby points from the mesh 

trans / 1 0 0 / 0. 0. 0. / 0. 0. H_TRANS
hextotet / 2 / mo_tri / mo_quad 
cmo / delete / mo_quad 
addmesh / excavate / mo_excavate / mo_pts / mo_tri

##### DEBUG #####
# If meshing fails, uncomment and rerun the script to get tmp meshes, 
# which are otherwise not output 
#dump / avs2 / tmp_tri.inp / mo_tri / 1 1 1 0
#dump / avs2 / tmp_pts.inp / mo_pts / 1 1 1 0
#dump / avs2 / tmp_excavate.inp / mo_excavate / 1 1 1 0
#finish
#####
 
cmo / delete / mo_tri 
cmo / delete / mo_pts 

# recompute dfield 
cmo / create / mo_final / / / triplane 
copypts / mo_final / mo_excavate  
compute / distance_field / mo_final / mo_line_work / dfield 
cmo / printatt / mo_final / dfield / minmax 
pset / pdel / attribute dfield / 1,0,0 / lt H_PRIME2 
rmpoint / pset,get,pdel / inclusive  
rmpoint / compress  

copypts / mo_final / mo_line_work  

cmo / select / mo_final 
cmo / setatt / mo_final / imt / 1 0 0 / ID 
cmo / setatt / mo_final / itp / 1 0 0 / 0 
cmo / setatt / mo_final / itetclr / 1 0 0 / ID 
# cmo / printatt / mo_final / -xyz- / minmax 
trans/ 1 0 0 / zero / xyz 
cmo / setatt / mo_final / zic / 1 0 0 / 0.0 
cmo / printatt / mo_final / -xyz- / minmax 
connect 

trans / 1 0 0 / original / xyz 
cmo / printatt / mo_final / -xyz- / minmax 

#cmo / delete / mo_line_work 
cmo / delete / mo_excavate
cmo / select / mo_final 
resetpts / itp 

"""
    	if not production_mode:
    		lagrit_input += 'dump / gmv / PRE_FINAL_MASSAGE / mo_final \n'
    	
    	lagrit_input += """
## Massage Mesh Away from Intersection 
pset / pref / attribute / dfield / 1,0,0 / lt / H_EPS 
pset / pregion / attribute / dfield / 1,0,0 / gt / H_SCALE2 
pset / pboundary / attribute / itp / 1,0,0 / eq / 10 
pset / psmooth / not / pregion pref pboundary 
#massage / H_SCALE / 1.e-5 / 1.e-5 / pset get pref / & 
#nosmooth / strictmergelenth

assign///maxiter_sm/1 

smooth / position / esug / pset get psmooth; recon 0; 
smooth / position / esug / pset get psmooth; recon 0; 
smooth / position / esug / pset get psmooth; recon 0; 

assign///maxiter_sm/10
###########################################
# nodes for Intersection / Mesh Connectivity Check 
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
# Output list of intersection nodes with the corrosponding node id number from the triangle mesh

dump / avs2 / OUTPUT_INTER_ID_SSINT / mo_line_work / 0 0 2 0
cmo / delete / mo_line_work

cmo / delete / mo_final_check
# nodes for intersection check over

cmo / select / mo_final 

##### DEBUG
# write out mesh before it is rotate back into its final location
# Useful to compare with meshing workflow if something crashes
#dump / avs2 / tmp_mesh_2D.inp / mo_final / 1 1 1 0 
##### DEBUG
# Rotate facture back into original plane 
rotateln / 1 0 0 / nocopy / X1, Y1, Z1 / X2, Y2, Z2 / THETA / 0.,0.,0.,/  
cmo / printatt / mo_final / -xyz- / minmax 
recon 1 

resetpts / itp 

cmo / addatt / mo_final / unit_area_normal / xyz / vnorm 
cmo / addatt / mo_final / scalar / xnorm ynorm znorm / vnorm 
cmo / DELATT / mo_final / vnorm 

"""
    	# Clean up before output to GMV/AVS
    	if production_mode:
    		lagrit_input += """
cmo / DELATT / mo_final / x_four 
cmo / DELATT / mo_final / fac_n 
cmo / DELATT / mo_final / rf_field_name 
cmo / DELATT / mo_final / xnorm 
cmo / DELATT / mo_final / ynorm 
cmo / DELATT / mo_final / znorm 
cmo / DELATT / mo_final / a_b 
cmo / setatt / mo_final / ipolydat / no 
cmo / modatt / mo_final / icr1 / ioflag / l 
cmo / modatt / mo_final / isn1 / ioflag / l 
    
# Create Family element set
cmo / addatt / mo_final / family_id / vint / scalar / nelements 
cmo / setatt / mo_final / family_id / 1 0 0 / family
    
"""
    	lagrit_input += """
dump / OUTFILE_AVS / mo_final
dump / lagrit / OUTFILE_LG / mo_final
""" 
    else:
    	lagrit_input += """
cmo / setatt / mo_pts / imt / 1 0 0 / ID 
cmo / setatt / mo_pts / itetclr / 1 0 0 / ID 
resetpts / itp 

cmo / setatt / mo_line_work / imt / 1 0 0 / ID 
cmo / setatt / mo_line_work / itetclr / 1 0 0 / ID

addmesh / merge / mo_final / mo_pts / mo_line_work 
cmo / delete / mo_pts 
cmo / delete / mo_line_work 
    
# Create Family element set
cmo / addatt / mo_final / family_id / vint / scalar / nelements 
cmo / setatt / mo_final / family_id / 1 0 0 / family

cmo / select / mo_final 
# Rotate 
rotateln / 1 0 0 / nocopy / X1, Y1, Z1 / X2, Y2, Z2 / THETA / 0.,0.,0.,/ 

cmo / printatt / mo_final / -xyz- / minmax 
cmo / modatt / mo_final / icr1 / ioflag / l 
cmo / modatt / mo_final / isn1 / ioflag / l
dump / lagrit / OUTFILE_LG / mo_final 
"""

    lagrit_input += """
quality 
cmo / delete / mo_final 
cmo / status / brief 
finish
"""

    # Create a different Run file for each CPU
    for i in range(1,ncpu+1):
    	file_name = 'mesh_poly_CPU%d.lgi'%i
    	f = open(file_name, 'w')
    	#Name of parameter Input File
    	fparameter_name = 'parameters_CPU%d.mlgi'%i 
    	fintersection_name = 'intersections_CPU%d.inp'%i
    	fpoly_name = 'poly_CPU%d.inp'%i
    	parameters = (fparameter_name, fpoly_name, fintersection_name, i)
    	f.write(lagrit_input%parameters)
    	f.flush()
    	f.close()
    print 'Writing LaGriT Control Files: Complete'

def create_user_functions():
    """ Create user_function.lgi files for meshing"""

    # user_function.lgi useing PARAM_A and PARAM_B for slope and intercept
    lagrit_input = """
cmo/DELATT/mo_pts/dfield
compute / distance_field / mo_pts / mo_line_work / dfield
math/multiply/mo_pts/x_four/1,0,0/mo_pts/dfield/PARAM_A/
math/add/mo_pts/x_four/1,0,0/mo_pts/x_four/PARAM_B/
cmo/copyatt/mo_pts/mo_pts/fac_n/x_four
finish
"""
    f = open('user_function.lgi', 'w')
    f.write(lagrit_input)
    f.close()

    # user_function2.lgi uses PARAM_A2 and PARAM_B2 for slope and intercept
    lagrit_input = """
cmo/DELATT/mo_pts/dfield
compute / distance_field / mo_pts / mo_line_work / dfield
math/multiply/mo_pts/x_four/1,0,0/mo_pts/dfield/PARAM_A2/
math/add/mo_pts/x_four/1,0,0/mo_pts/x_four/PARAM_B2/
cmo/copyatt/mo_pts/mo_pts/fac_n/x_four
finish
"""
    f = open('user_function2.lgi', 'w')
    f.write(lagrit_input)
    f.close()



def create_merge_poly_files(ncpu, num_poly, visual_mode):
    """
    Section 4 : Create merge_poly file
     Creates a lagrit script that reads in each mesh, appends it to the main mesh, and then deletes that mesh object
     Then duplicate points are removed from the main mesh using EPS_FILTER 
     The points are compressed, and then written in the files full_mesh.gmv, full_mesh.inp, and an FEHM dump is preformed.
    """


    # This needs to be re-written using PyLaGriT so we can check 
    # that the number of dudded points is that which we expect
    print "Writing : merge_poly.lgi"

    part_size = num_poly/ncpu + 1 ###v number of fractures in each part
    endis = range(part_size, num_poly + part_size, part_size) 
    endis[-1] = num_poly

    lagrit_input = """
# Change to read LaGriT
read / lagrit /  %s / mo_%d / binary
cmo / move / mo_%d / mo_final 
define / MO_NAME_FRAC / mo_%d
"""
    if not visual_mode:
    	lagrit_input += """
cmo / addatt / MO_NAME_FRAC / volume / evol_onen
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

    j = 0 # Counter for cpus 
    fout = 'merge_poly_part_1.lgi'
    f = open(fout, 'w')
    for i in range(1,num_poly+1):
    	tmp = 'mesh_'+str(i) +'.lg'

    	f.write(lagrit_input%(tmp,i,i,i,i,i))
    	# if i is the last fracture in the cpu set
    	# move to the next cpu set	
    	if i == endis[j]:
    		f.write(lagrit_input_2%(j+1))
    		f.flush()
    		f.close()
    		
    		j += 1
    		fout = 'merge_poly_part_'+str(j+1)+'.lgi'
    		f = open(fout,'w') 

    f.flush() 
    f.close() 
    os.remove(fout) ###

    ## Write LaGriT file for merge parts of the mesh and remove duplicate points 

    lagrit_input  = """
read / lagrit / part%d.lg / junk / binary
addmesh / merge / mo_all / mo_all / cmo_tmp 
cmo / delete / cmo_tmp 

    """
    f = open('merge_rmpts.lgi','w')
    for j in range(1,len(endis)+1):
    	f.write(lagrit_input%(j))

    # Append meshes complete
    lagrit_input = """ 
# Appending the meshes complete 
# LaGriT Code to remove duplicates and output the mesh
cmo / select / mo_all 
#recon 1
##### JDH #####
##### MAKE H SENSITIVE #######
define / EPS / 1.e-6
define / EPS_FILTER / 1.e-4 
##### MAKE H SENSITIVE #######
pset / pinter / attribute / dfield / 1,0,0 / lt / EPS 
filter / pset get pinter / EPS_FILTER 
pset / pinter / delete
rmpoint / compress 
# SORT can affect a_b attribute
sort / mo_all / index / ascending / ikey / imt xic yic zic 
reorder / mo_all / ikey 
cmo / DELATT / mo_all / ikey
"""
     
    if not visual_mode: 
    	lagrit_input += """
resetpts / itp 
boundary_components 
dump / full_mesh.gmv / mo_all
dump / full_mesh.inp / mo_all
dump / lagrit / full_mesh.lg / mo_all
dump / pflotran / full_mesh / mo_all / nofilter_zero
dump / stor / tri_fracture / mo_all / ascii

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
cmo / modatt / mo_all / pt_gtg / ioflag / l
# Dump out Material ID Dat file
dump / avs2 / materialid.dat / mo_all / 0 0 2 0

cmo / modatt / mo_all / imt1 / ioflag / l
cmo / modatt / mo_all / family_id / ioflag / l
cmo / modatt / mo_all / evol_onen / ioflag / l
# Dump mesh with no attributes for viz
dump / full_mesh_viz.inp / mo_all
"""
    else:
    	lagrit_input += """
cmo / modatt / mo_all / icr1 / ioflag / l
cmo / modatt / mo_all / isn1 / ioflag / l
cmo / modatt / mo_all / itp1 / ioflag / l
dump / reduced_full_mesh.gmv / mo_all 
dump / reduced_full_mesh.inp / mo_all
"""
    lagrit_input += """
quality 
finish
"""
    f.write(lagrit_input)
    f.flush()
    f.close()

    return len(endis)

def define_zones(h, domain):
    """	
    Creates and runs LaGriT script to define domain size
    """	
    eps = h*10**-3
    parameters = (0.5*domain['x'] - eps, -0.5*domain['x'] + eps, \
    	0.5*domain['y'] - eps, -0.5*domain['y'] + eps, \
    	0.5*domain['z'] - eps, -0.5*domain['z'] + eps)

    lagrit_input = '''
read / lagrit / full_mesh.lg / mo_all / binary 
define / XMAX / %e 
define / XMIN / %e 
define / YMAX / %e 
define / YMIN / %e 
define / ZMAX / %e 
define / ZMIN / %e 

pset / top/ attribute / zic / 1,0,0/ gt /ZMAX 
pset / bottom/ attribute/ zic/ 1,0,0/ lt/ZMIN 
pset / left_w / attribute/ xic/ 1,0,0 /lt / XMIN
pset / front_s / attribute/ yic / 1,0,0 / gt/YMAX
pset / right_e / attribute/ xic/1,0,0/ gt/XMAX
pset / back_n / attribute/ yic/ 1,0,0 / lt/YMIN
pset/-all-/ zone / boundary / ascii
finish
'''

    f=open('bound_zones.lgi','w')
    f.write(lagrit_input%parameters)
    f.flush()
    f.close()
    os.system(os.environ['lagrit_dfn']+ " < bound_zones.lgi > boundary_output.txt ")
    
    # copies boundary zone files for PFLOTRAN 
    copy('boundary_bottom.zone','pboundary_bottom.zone')
    copy('boundary_left_w.zone','pboundary_left_w.zone')
    copy('boundary_front_s.zone','pboundary_front_s.zone')
    copy('boundary_right_e.zone','pboundary_right_e.zone')
    copy('boundary_back_n.zone','pboundary_back_n.zone')
    copy('boundary_top.zone','pboundary_top.zone')
    
    fall=open("allboundaries.zone","w")
    #copy all but last 2 lines of boundary_top.zone in allboundaries.zone
    fzone=open("boundary_top.zone","rb")
    lines=fzone.readlines()
    lines=lines[:-2]
    fzone.close() 
    fall.writelines(lines)
    #copy all but frist and last 2 lines of boundary_bottom.zone in allboundaries.zone
    files=['bottom','left_w','front_s','right_e']
    for f in files:
            fzone=open("boundary_%s.zone"%f,"rb")
            lines=fzone.readlines()
            lines=lines[1:-2]
            fzone.close() 
            fall.writelines(lines)
    fzone=open("boundary_back_n.zone","rb")
    lines=fzone.readlines()
    lines=lines[1:]
    fzone.close() 
    fall.writelines(lines)
    fall.close()

    # Remove Left over zone files
    os.remove('boundary_bottom.zone')
    os.remove('boundary_top.zone')
    os.remove('boundary_left_w.zone')
    os.remove('boundary_right_e.zone')
    os.remove('boundary_front_s.zone')
    os.remove('boundary_back_n.zone')def edit_intersection_files(num_poly, keep_list):

    pull_list = list(set(range(1,num_poly+ 1)) - set(keep_list))
    os.chdir('intersections')
    for i in keep_list:
    	filename = 'intersections_%s.inp'%str(i)
    	print '--> Working on: ', filename
    	lagrit_script = 'read / %s / mo1'%filename
    	lagrit_script += '''
pset / pset2remove / attribute / b_a / 1,0,0 / eq / %d
'''%pull_list[0]    
    	for j in pull_list[1:]:
    		lagrit_script += '''
pset / prune / attribute / b_a / 1,0,0 / eq / %d
pset / pset2remove / union / pset2remove, prune
#rmpoint / pset, get, prune
pset / prune / delete
 '''%j
    	lagrit_script += '''
rmpoint / pset, get, pset2remove 
rmpoint / compress

cmo / modatt / mo1 / imt / ioflag / l
cmo / modatt / mo1 / itp / ioflag / l
cmo / modatt / mo1 / isn / ioflag / l
cmo / modatt / mo1 / icr / ioflag / l

cmo / status / brief
dump / intersections_%d_prune.inp / mo1
finish
'''%i
    	
    	file_name = 'prune_intersection.lgi'
    	f = open(file_name, 'w')
    	f.write(lagrit_script)
    	f.flush()
    	f.close()
    	os.system(lagrit_path +  '< prune_intersection.lgi > out.txt')

