#!/n/lkcal_linux/bin/python2.7
########## this version merges meshes in parallel 
# Python Code to take the output from mathematica and convert the data into a grid DFN
#
# Usage (default): meshDFN
# Default input file: params.txt
# Default number of processors N_CPU: 4
# Default refine_factor: 1
#
# Optional Argument List
# 2 Argument
# Usage: meshDFN filename N_CPU
#		Default file name: params.txt
#		Default N_CPU: 4 (integer)
# 3 Argument
# Usage: meshDFN filename N_CPU refine_factor
#		Default file name: params.txt
#		Default N_CPU: 4 (integer)
#		Default refine_factor: 1 (integer, allowable values, 1, 2, 4, 8)
#
# Jeffrey Hyman
# EES-16 LANL
# jhyman@lanl.gov
# Command Line Input is the params.txt file output from mathematica
# params.txt needs to be f the format
# nPoly  		Number of polygons in the Set
# h			Built in Length Scale
# 1 THETA X1 Y1 Z1 X2 Y2 Z2  
# 2
# ...
# nPoly THETA X1 Y1 Z1 X2 Y2 Z2

# Where  THETA = angle of rotation to correct polygons
# and a line about which the polygon needs to be rotated is described by the line 
# (X1,Y1,Z1) and (X2, Y2,Z2)

# This script combines the files:
#	create_params.py
#	create_mesh_poly.py
#	create_lagrit_input.py
#	create_merge_poly.py
#	run_lagrit.py
#	runs lagrit < mergepoly.lgi
# Output files are meshi.gmv, meshi.inp, full_mesh.gmv and full_mesh.inp
# individual polygons and merges them into one .inp and .gmv in lagrit
#
# Set up to run triangulation of each fracture polygon in parallel. Set N_CPU to number
# of jobs to run in parallel.

from string import *
import os, sys, glob, time
from numpy import genfromtxt, sort, sqrt, cos, arcsin
from shutil import copy, rmtree
from pylagrit import PyLaGriT
import multiprocessing as mp 

def remove_batch(name):
	''' This function is used to clean up the directory in batch '''
	for fl in glob.glob(name):
		os.remove(fl)	

def parse_params_file():
	''' Read in params.txt file and parse information'''
	print "\nParse Params.txt: Starting"
	fparams = open('params.txt', 'r')
	# Line 1 is the number of polygons
	nPoly = int(fparams.readline())

	print "Number of Polygons:", nPoly

	#Line 2 is the h scale
	h = float(fparams.readline())
	print "H_SCALE", h
		
	# Line 3 is the visualization mode: '1' is on, '0' is off.
	visualMode = int(fparams.readline())
	print 'Visual Mode: ', visualMode

	# line 4 dudded points
	dudded_points = int(fparams.readline())
	print "Expected Number of duded points: ", dudded_points
	fparams.close()
	
	print "Parse Params.txt: Complete\n"
	return(nPoly, h, visualMode, dudded_points)
	
def create_parameter_mlgi_file(nPoly,h, slope = 2, refine_dist = 0.5):
	
	#Section 2 : Outputs parameteri.mlgi files used in running LaGriT Script
	print "\nCreating parameteri.mlgi files"
	os.system('rm -rf parameters')
	os.mkdir('parameters')
	# Extrude and Translate computation
	# Parameters, delta: buffer zone, amount of h/2 we remove from around line
	# h_extrude hieght of rectangle extruded from line of intersection
	# r_radius: Upper bound on radius of circumscribed circle around rectangle
	# h_trans : amount needed to translate to create delta buffer
	# It's all trig to work it out! 
	delta = 0.75
	h_extrude = 0.5*h # upper limit on spacing of points on interssction line
	h_radius = sqrt((0.5*h_extrude)**2 + (0.5*h_extrude)**2)
	h_trans = -0.5*h_extrude + h_radius*cos(arcsin(delta))

	#Go through the list and write out parameter file for each polygon
	#to be an input file for LaGriT
	data = genfromtxt('poly_info.dat') #, skip_header = 1)
	for i in range(nPoly):
		
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
		#f.write('define / PARAM_A / '+str(0.0)+'\n')	
		f.write('define / PARAM_B / '+str(h*(1-slope*refine_dist))+'\n')	

		f.write('define / PARAM_A2 / '+str(0.5*slope)+'\n')	
		#f.write('define / PARAM_A2 / '+str(0.0)+'\n')	
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

	print "Creating parameteri.mlgi files: Complete\n"

def create_lagrit_scripts(production_mode, N_CPU, refine_factor, visualMode): 

	#########################################
	#Section 2 : Creates LaGriT script to be run for each polygon

	#Switches to control the LaGriT output
	#Network visualization mode "ON" ouputs the triangulated mesh
	#for each fracture without any refinement. The goal is to visualize
	#the network structure instead of outputing the appropriate values
	#for computation

	print "Writing LaGriT Control Files"
	#Go through the list and write out parameter file for each polygon
	#to be an input file for LaGriT

	lagrit_input = '''infile %s 
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
''' 
	if(visualMode == 0):
		lagrit_input += '''
read / LINE_FILE / mo_line_work 
'''
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
			
		lagrit_input += ''' 
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
'''	
		# END: Refine the point distribution
		#
	lagrit_input += '''
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

'''
	if(visualMode == 0):
		lagrit_input += '''
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
'''
		if (production_mode == 0):
			lagrit_input += '''
dump / avs / QUAD_FILE / mo_quad 
cmo / delete / mo_quad 
read / QUAD_FILE / mo_quad 
'''
		else:
			lagrit_input += 'cmo / select / mo_quad \n'
		
		lagrit_input += '''
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

'''
		if (production_mode == 0):
			lagrit_input += 'dump / gmv / PRE_FINAL_MASSAGE / mo_final \n'
		
		lagrit_input += '''
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

'''
		# Clean up before output to GMV/AVS
		if (production_mode == 1):
			lagrit_input += '''
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
	
'''
		lagrit_input += '''
dump / OUTFILE_AVS / mo_final
dump / lagrit / OUTFILE_LG / mo_final
''' 
	else:
		lagrit_input += '''
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
'''

	lagrit_input += '''
quality 
cmo / delete / mo_final 
cmo / status / brief 
finish
'''

	# Create a different Run file for each CPU
	for i in range(1,N_CPU+1):
		file_name = 'mesh_poly_CPU' + str(i) + '.lgi'
		f = open(file_name, 'w')
		#Name of parameter Input File
		fparameter_name = 'parameters_CPU' + str(i) + '.mlgi' 
		fintersection_name = 'intersections_CPU' + str(i) + '.inp'
		fpoly_name = 'poly_CPU' + str(i) + '.inp'
		parameters = (fparameter_name, fpoly_name, fintersection_name,i)
		f.write(lagrit_input%parameters)
		f.flush()
		f.close()

	## Create user_function.lgi file
	lagrit_input = '''
cmo/DELATT/mo_pts/dfield
compute / distance_field / mo_pts / mo_line_work / dfield
math/multiply/mo_pts/x_four/1,0,0/mo_pts/dfield/PARAM_A/
math/add/mo_pts/x_four/1,0,0/mo_pts/x_four/PARAM_B/
cmo/copyatt/mo_pts/mo_pts/fac_n/x_four
finish
'''
	f = open('user_function.lgi', 'w')
	f.write(lagrit_input)
	f.close()

	## Create user_function.lgi file
	lagrit_input = '''
cmo/DELATT/mo_pts/dfield
compute / distance_field / mo_pts / mo_line_work / dfield
math/multiply/mo_pts/x_four/1,0,0/mo_pts/dfield/PARAM_A2/
math/add/mo_pts/x_four/1,0,0/mo_pts/x_four/PARAM_B2/
cmo/copyatt/mo_pts/mo_pts/fac_n/x_four
finish
'''
	f = open('user_function2.lgi', 'w')
	f.write(lagrit_input)
	f.close()


	print 'Writing LaGriT Control Files: Complete'

def mesh_fracture(fracture_id, visualMode,nPoly):

	'''Child Function for Parallized Meshing of Fractures'''
	t = time.time()
	p = mp.current_process()
	print 'Fracture ', fracture_id, '\tstarting on ', p.name, '\n' 
	a, cpu_id = p.name.split("-")
	cpu_id = int(cpu_id)
	
	cmd = 'ln -s polys/poly_%d.inp poly_CPU%d.inp'
	os.system(cmd%(fracture_id,cpu_id))

	cmd = 'ln -s parameters/parameters_%d.mlgi '\
		 + 'parameters_CPU%d.mlgi'
	os.system(cmd%(fracture_id,cpu_id))

	cmd = 'ln -s intersections/intersections_%d.inp '\
		 + 'intersections_CPU%d.inp'
	os.system(cmd%(fracture_id,cpu_id))

	cmd = os.environ['lagrit_dfn']+ ' < mesh_poly_CPU%d.lgi' \
		 + ' > lagrit_logs/log_lagrit_%d'
	os.system(cmd%(cpu_id,fracture_id))

	if(visualMode == 0):
		cmd_check = os.environ['connect_test']+ ' intersections_CPU%d.inp' \
		+ ' id_tri_node_CPU%d.list ' \
		+ ' mesh_%d.inp'
		cmd_check = cmd_check%(cpu_id,cpu_id,fracture_id)
		failure = os.system(cmd_check)
		if failure > 0:
			print("MESH CHECKING HAS FAILED!!!!")
			print 'Fracture number ', fracture_id, '\trunning on ', p.name, '\n'

			with open("failure.txt", "a") as failure_file:
			    failure_file.write("%d\n"%fracture_id)

			folder = 'failure_'+str(fracture_id)
			os.mkdir(folder)
			copy('mesh_'+str(fracture_id)+'.inp', folder + '/')
			copy('poly_CPU'+str(cpu_id)+'.inp', folder + '/')
			copy('id_tri_node_CPU'+str(cpu_id)+'.list', folder + '/')
			copy('intersections_CPU'+str(cpu_id)+'.inp',  folder +'/')	
			copy('lagrit_logs/log_lagrit_'+str(fracture_id),  folder +'/')
			copy('parameters_CPU' + str(cpu_id) + '.mlgi', folder +'/')	
			copy('mesh_poly_CPU' + str(cpu_id) + '.lgi', folder + '/')	
			copy('user_function.lgi', folder +'/')	
		try:
			os.remove('id_tri_node_CPU' + str(cpu_id) + '.list')
		except: 
			print 'Could not remove id_tri_node_CPU' + str(cpu_id) + '.list'
		try:
			os.remove('mesh_' + str(fracture_id) + '.inp')
		except:
			print 'Could not remove mesh' + str(cpu_id) + '.inp'
 	else:
		failure = 0

	# Remove old links and files
	try:
		os.remove('poly_CPU' + str(cpu_id) + '.inp')
	except:
		print 'Could not remove poly_CPU' + str(cpu_id) + '.inp'
	try: 
		os.remove('intersections_CPU' + str(cpu_id) + '.inp')
	except:
		print 'Could not remove intersections_CPU' + str(cpu_id) + '.inp'
	try:
		os.remove('parameters_CPU' + str(cpu_id) + '.mlgi')
	except:
		print 'Could not remove parameters_CPU' + str(cpu_id) + '.mlgi'

	elapsed = time.time() - t
	
	print 'Fracture ', fracture_id, 'out of ',  nPoly, ' complete' 
	print 'Time for meshing: %0.2f seconds\n'%elapsed

def worker(work_queue, done_queue, visualMode, nPoly):
	try:
		for fracture_id in iter(work_queue.get, 'STOP'):
			mesh_fracture(fracture_id, visualMode, nPoly)
			#done_queue.put("Fracture %d Complete" % fracture_id)
	except: 
		#done_queue.put('Error on Fracture ',fracture_id)
		print('Error on Fracture ',fracture_id)
	return True

def mesh_fractures_header(nPoly, N_CPU, visualMode):
 
	t_all = time.time()
	print "\nTriangulate Polygons:", nPoly
 	try:
		rmtree('lagrit_logs')
	except OSError:
		pass
	remove_batch('rm -rf failure*')
	os.mkdir('lagrit_logs')

	f = open('failure.txt', 'w')
	f.close()
	# If the number of processors is greater than the number of 
	# polygons, reset N_CPU
	if ( N_CPU > nPoly):
		N_CPU = nPoly

	print("Meshing using %d CPUS"%N_CPU)

	fracture_list = range(1, nPoly + 1)
	work_queue = mp.Queue()   # reader() reads from queue
	done_queue = mp.Queue()   # reader() reads from queue
	processes = []

	for i in fracture_list:
		work_queue.put(i)

	for i in xrange(N_CPU):
		p = mp.Process(target=worker, args= (work_queue, done_queue, visualMode, nPoly))
		p.daemon = True
		p.start()        
		processes.append(p)
		work_queue.put('STOP')

	for p in processes:
		p.join()

	done_queue.put('STOP')
#
#	# Check for Errors in Parallell Meshing, if they exists, 
#	# Attempt to mesh those fractures again
#	redo = []
#	for status in iter(done_queue.get, 'STOP'):
#		print status
#		line = status.split()
#		if line[0] == 'Error':
#			redo.append(int(status.split()[-1]))
#
#	while len(redo) > 0:
#		print("Re-meshing the following fractures:")
#		print redo		
#		if (N_CPU > len(redo)):
#			N_CPU = len(redo) 
#
#		print("Meshing using %d CPUS"%N_CPU)
#
#		work_queue = mp.Queue()   # reader() reads from queue
#		done_queue = mp.Queue()   # reader() reads from queue
#		processes = []
#
#		for i in redo:
#			work_queue.put(i)
#
#		for i in xrange(N_CPU):
#			p = mp.Process(target=worker, args= (work_queue, done_queue, visualMode, nPoly))
#			p.daemon = True
#			p.start()        
#			processes.append(p)
#			work_queue.put('STOP')
#		
#		for p in processes:
#			p.join()
#
#		done_queue.put('STOP')
#
#		redo = []
#		for status in iter(done_queue.get, 'STOP'):
#			print status
#			if status.split()[0] =='Error':
#				redo.append(status.split()[-1])
#	# Checking over
	
	elapsed = time.time() - t_all
	print 'Total Time to Mesh Network: %0.2f seconds'%elapsed
	elapsed /= 60.
	print '--> %0.2f Minutes'%elapsed

	if os.stat("failure.txt").st_size > 0:
		failure_list = genfromtxt("failure.txt")
		failure_flag = 1
		if type(failure_list) is list:
			failure_list = sort(failure_list)
		else: 
			print 'Fractures:', failure_list , 'Failed'
		print 'Main process exiting.'
	else:
		failure_flag = 0
		os.remove("failure.txt");
		print 'Triangulating Polygons: Complete'
	return failure_flag	


def create_merge_poly_files(N_CPU, nPoly, visualMode):
	'''
	Section 4 : Create merge_poly file
	 Creates a lagrit script that reads in each mesh, appends it to the main mesh, and then deletes that mesh object
	 Then duplicate points are removed from the main mesh using EPS_FILTER 
	 The points are compressed, and then written in the files full_mesh.gmv, full_mesh.inp, and an FEHM dump is preformed.
	'''


	# This needs to be re-written using PyLaGriT so we can check 
	# that the number of dudded points is that which we expect
	print "Writing : merge_poly.lgi"

	part_size = nPoly/N_CPU + 1 ###v number of fractures in each part
	endis = range(part_size, nPoly + part_size, part_size) 
	endis[-1] = nPoly

	lagrit_input = '''
# Change to read LaGriT
read / lagrit /  %s / mo_%d / binary
cmo / move / mo_%d / mo_final 
define / MO_NAME_FRAC / mo_%d
'''
	if (visualMode == 0):
		lagrit_input += '''
cmo / addatt / MO_NAME_FRAC / volume / evol_onen
math / sum / MO_NAME_FRAC / evol_sum / 1 0 0 / MO_NAME_FRAC / evol_one 
''' 
	lagrit_input += '''
addmesh / merge / cmo_tmp / cmo_tmp / mo_%d
cmo / delete / mo_%d
'''
	lagrit_input_2 = '#Writing out merged fractures\n' 
	if (visualMode == 0):
		lagrit_input_2 += '''
mo / addatt/ cmo_tmp / volume / evol_all
math / sum / cmo_tmp / evol_sum / 1 0 0 / cmo_tmp / evol_all '''
	lagrit_input_2 += ''' 
cmo select cmo_tmp
dump lagrit part%d.lg cmo_tmp
finish \n 
'''

	j = 0 # Counter for cpus 
	fout = 'merge_poly_part_1.lgi'
	f = open(fout, 'w')
	for i in range(1, nPoly + 1):
		tmp = 'mesh_' + str(i)  + '.lg'

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
	os.system('rm ' + fout) ###

	## Write LaGriT file for merge parts of the mesh and remove duplicate points 

	lagrit_input  = '''
read / lagrit / part%d.lg / junk / binary
addmesh / merge / mo_all / mo_all / cmo_tmp 
cmo / delete / cmo_tmp 

	'''
	f = open('merge_rmpts.lgi','w')
	for j in range(1,len(endis)+1):
		f.write(lagrit_input%(j))

	# Append meshes complete
	lagrit_input = ''' 
# Appending the meshes complete 
# LaGriT Code to remove duplicates and output the mesh
cmo / select / mo_all 
#recon 1
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
'''
	 
	if(visualMode == 0): 
		lagrit_input += '''
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
'''
	else:
		lagrit_input += '''
cmo / modatt / mo_all / icr1 / ioflag / l
cmo / modatt / mo_all / isn1 / ioflag / l
cmo / modatt / mo_all / itp1 / ioflag / l
dump / reduced_full_mesh.gmv / mo_all 
dump / reduced_full_mesh.inp / mo_all
'''
	lagrit_input += '''
quality 
finish
'''
	f.write(lagrit_input)
	f.flush()
	f.close()

	return len(endis)


def merge_the_meshes(nPoly, N_CPU, n_jobs, visualMode):
	''' Section 6 : Merge the Meshes
	 Merges all the meshes together, deletes duplicate points, 
		dumps the .gmv and fehm files
	'''
	print "\nMerging triangulated polygon meshes"

	for j in range(1, n_jobs + 1):
		pid = os.fork()
		if pid == 0: # clone a child job
			cmd = os.environ['lagrit_dfn']+' < merge_poly_part_%d.lgi > log_merge_poly_part%d' 
			os.system(cmd%(j,j))
			os._exit(0)
		else:
			print 'Merging part ', j, ' of ', n_jobs 

	# wait for all child processes to complete
	j = 0
	while j < n_jobs:
		(pid, status) = os.waitpid(0,os.WNOHANG)
		if pid > 0:
			print 'Process ' + str(j+1) + ' finished'
			j += 1 

	print("Starting Final Merge")
	os.system(os.environ['lagrit_dfn'] +' < merge_rmpts.lgi > log_merge_all.txt') # run remove points
	# Check log_merge_all.txt for LaGriT complete successfully
	if visualMode == 0:
		if os.stat("full_mesh.lg").st_size > 0:
			print("Final Merge Complete")
			print("Merging triangulated polygon meshes: Complete\n")
		else:
			sys.exit("Final Merge Failed")
	else:
		if os.stat("reduced_full_mesh.inp").st_size > 0:
			print("Final Merge Complete")
			print("Merging triangulated polygon meshes: Complete\n")
		else:
			sys.exit("Final Merge Failed")
		

def check_dudded_points(dudded):
	print "Checking that number of Dudded points is correct"
        datafile = file('log_merge_all.txt')
        for line in datafile:
            if 'Dudding' in line:
		print 'From LaGriT: '
		print line
		break
	pts = int(line.split()[1])
	if pts == dudded:
		print 'Correct Number of points removed \n'
		return True
	else:
		print 'ERROR! Incorrect Number of points removed'
		print 'Expected Number ', dudded
		return False
	

def cleanup_dir():
	#########################################
	#Section 5 : Create Clean up file
	# Creates a python script to remove the files mesh_polyi.lgi, parametersi.mlgi, merge_poly.lgi, and run_lagrit.py
	# The individual meshes, meshi.gmv and meshi.inp are NOT removed. 
	# Remove merge_poly.lgi
	remove_batch("part*")
	remove_batch("log_merge*")
	remove_batch("merge*")
	remove_batch("mesh_poly_CPU*")
	remove_batch("mesh*inp")
	remove_batch("mesh*lg")

def redefine_zones_old():

	'''Section 8 : redefine zones 
	Creates lagrit script to define domain size
'''
	lagrit_input = '''
read / lagrit / full_mesh.lg / mo_all / binary 
cmo / printatt / mo_all / -xyz- / minmax 
finish

	'''
	f=open('domainattr.lgi','w')
	f.write(lagrit_input) 
	f.flush()
	f.close()
	os.system(os.environ['lagrit_dfn']+ " < domainattr.lgi > printxyz.out")
	# python script to read data from lagrit output file 
	fil = open('printxyz.out','r')
	for line in fil:
		k=line.split()
		for word in line.split():
			if word == 'xic':
				x_min = float(k[1])
				x_max = float(k[2])
			if word=='yic':
				y_min = float(k[1])
				y_max = float(k[2])
			if word=='zic':
				z_min = float(k[1])
				z_max = float(k[2])

	fil.close()
	#lagrit scripts to create new zone files: boundary zones

	eps = h*0.001
	
	parameters = (x_max - eps, x_min + eps, y_max - eps, \
			 y_min + eps, z_max - eps, z_min + eps)
	lagrit_input = '''
read / gmv / full_mesh.gmv / mo
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
	os.system("cp boundary_bottom.zone pboundary_bottom.zone")
	os.system("cp boundary_left_w.zone pboundary_left_w.zone")
	os.system("cp boundary_front_s.zone pboundary_front_s.zone")
	os.system("cp boundary_right_e.zone pboundary_right_e.zone")
	os.system("cp boundary_back_n.zone pboundary_back_n.zone")
	os.system("cp boundary_top.zone pboundary_top.zone")
	for i in range(0,2):
		os.system("sed -i '$d' boundary_top.zone ")
		os.system("sed -i '$d' boundary_bottom.zone ")
		os.system("sed -i '$d' boundary_left_w.zone ")
		os.system("sed -i '$d' boundary_front_s.zone ")
		os.system("sed -i '$d' boundary_right_e.zone ")

	os.system("sed -i '1d' boundary_bottom.zone ")
	os.system("sed -i '1d' boundary_left_w.zone ")
	os.system("sed -i '1d' boundary_front_s.zone ")
	os.system("sed -i '1d' boundary_right_e.zone ")
	os.system("sed -i '1d' boundary_back_n.zone ")
	os.system("cat boundary_top.zone boundary_bottom.zone boundary_left_w.zone boundary_front_s.zone boundary_right_e.zone   boundary_back_n.zone  > allboundaries.zone ")


def redefine_zones(h):
	'''
	Section 8 : redefine zones 
	runs PyLaGriT to identify boundary nodes
	'''

	pl = PyLaGriT(lagrit_exe = os.environ['lagrit_dfn'], verbose = False)
	print '--> Identifying Boundary Nodes'
	eps = h*10**-3
	#eps = 0.5*h
	print '--> Reading in Mesh'	
	mo = pl.read('full_mesh.lg')
	print '--> Complete'
	print '--> Tagging Boundary Nodes'

	# Order for psets in terms of cube directions
	# DO NOT TOUCH THIS!	
	ptop = mo.pset_attribute('zic', mo.zmax - eps, 'gt',name='top')
	pbottom = mo.pset_attribute('zic', mo.zmin + eps, 'lt', name = 'bottom')
	pleft_w = mo.pset_attribute('xic', mo.xmin + eps, 'lt', name = 'left_w')
	pfront_s = mo.pset_attribute('yic', mo.ymax - eps, 'gt', name = 'front_s')
	pright_e = mo.pset_attribute('xic', mo.xmax - eps, 'gt', name = 'right_e')
	pback_n = mo.pset_attribute('yic', mo.ymin + eps, 'lt', name = 'back_n')
	# DO NOT TOUCH THIS!	

	print'--> Complete'

	print '--> Dumping Boundary Nodes'
	mo.dump_pset('boundary', 'zone')
	print '--> Complete'
	
	# copies boundary zone files for PFLOTRAN 
	copy('boundary_bottom.zone','pboundary_bottom.zone')
	copy('boundary_left_w.zone','pboundary_left_w.zone')
	copy('boundary_front_s.zone','pboundary_front_s.zone')
	copy('boundary_right_e.zone','pboundary_right_e.zone')
	copy('boundary_back_n.zone','pboundary_back_n.zone')
	copy('boundary_top.zone','pboundary_top.zone')
	
	# edits zone files to concatenate for dfnTrans
	for i in range(2):
		os.system("sed -i '$d' boundary_top.zone ")
		os.system("sed -i '$d' boundary_bottom.zone ")
		os.system("sed -i '$d' boundary_left_w.zone ")
		os.system("sed -i '$d' boundary_front_s.zone ")
		os.system("sed -i '$d' boundary_right_e.zone ")
	os.system("sed -i '1d' boundary_bottom.zone ")
	os.system("sed -i '1d' boundary_left_w.zone ")
	os.system("sed -i '1d' boundary_front_s.zone ")
	os.system("sed -i '1d' boundary_right_e.zone ")
	os.system("sed -i '1d' boundary_back_n.zone ")
	os.system("cat boundary_top.zone boundary_bottom.zone boundary_left_w.zone boundary_front_s.zone boundary_right_e.zone   boundary_back_n.zone  > allboundaries.zone ")

def output_meshing_report(visualMode):

	f = open('finalmesh.txt','w')
	f.write('The final mesh of DFN consists of: \n')
	if(visualMode == 0): 
		print "Output files for FEHM calculations are written in :"
		print "--> full_mesh.gmv"
		print "--> full_mesh.inp"
		print "--> tri_fracture.stor"

		finp=open('full_mesh.inp','r')
		g = finp.readline()
		g = g.split()
		NumElems = int(g.pop(1))
		NumIntNodes = int(g.pop(0))
		f.write(str(NumElems)+' triangular elements; \n')
		f.write(str(NumIntNodes)+'  nodes / control volume cells; \n')
		finp.close()
		
		fstor=open('tri_fracture.stor','r')
		fstor.readline()
		fstor.readline()
		gs = fstor.readline()
		gs = gs.split()
		NumCoeff = int(gs.pop(0))
		f.write(str(NumCoeff)+' geometrical coefficients / control volume faces. \n')
		fstor.close()
	else:
		print "Output files for visualization are written in :"
		print "--> reduced_full_mesh.gmv"
		print "--> reduced_full_mesh.inp"
		finp=open('reduced_full_mesh.inp','r')
		g = finp.readline()
		g = g.split()
		NumElems = int(g.pop(1))
		NumIntNodes = int(g.pop(0))
		f.write(str(NumElems)+' triangular elements; \n')
		f.write(str(NumIntNodes)+'  nodes / control volume cells. \n')
		finp.close()
	f.close()

############# MAIN ###############
if __name__ == "__main__":
	print ('='*80)
	os.system("date")
	print '''Python Script to parse DFNGEN output and mesh it using LaGriT 

	Last Update August 1 2016 by Jeffrey Hyman
	EES - 16, LANL
	jhyman@lanl.gov
	'''
	#Production mode "ON" outputs the final results for computation, 
	#cleaning up all the temporary attributes needed during refinement.
	#Note that the visualization mode must be "OFF" in order to run
	#in produciton mode. "dfield" can also be turn ON/OFF. 
	#*1: "ON", *0: "OFF". 
	#dfield = 0

	slope = 2
	refine_dist = 0.5

	production_mode = 1
	refine_factor = 1
	N_CPU = 4

	try:
		python_path = os.environ['python_dfn']
		#python_path = '/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/2.4.1/bin/python'
	except KeyError:
		print 'python_dfn not defined'
		sys.exit(1)	
	try:	
		connectivity_test = os.environ['connect_test']
		#connectivity_test = '/home/jhyman/dfnWorks/DFN_Mesh_Connectivity_Test/ConnectivityTest'
	except KeyError:
		print 'connect_test undefined'
		sys.exit(1)	
	try:
		pl = PyLaGriT(lagrit_exe = os.environ['lagrit_dfn'], verbose = False)
	except KeyError:
		print 'PyLaGrit not found'
		sys.exit(1)	

	if (len(sys.argv) == 1):
		print "Number of CPU's to use (default):", N_CPU
	
	elif (len(sys.argv) == 2):
		N_CPU = int(sys.argv[1])
		print "Number of CPU's to use:", N_CPU
	

	## input checking over
	
	nPoly, h, visualMode, dudded_points  = parse_params_file()

	create_parameter_mlgi_file(nPoly, h)

	create_lagrit_scripts(production_mode, N_CPU, refine_factor, visualMode)

	failure = mesh_fractures_header(nPoly, N_CPU)

	if failure > 0:
		cleanup_dir()
		print 'Exiting Program'
		sys.exit(1)

	n_jobs = create_merge_poly_files(N_CPU, nPoly, visualMode)

	merge_the_meshes(nPoly, N_CPU, n_jobs, visualMode)
	if(visualMode == 0):	
		if (check_dudded_points(dudded_points) == False):
			cleanup_dir()
			sys.exit(1)

	if production_mode > 0:
		cleanup_dir()

	if(visualMode == 0): 
		redefine_zones(h)
		#redefine_zones_old()
	output_meshing_report(visualMode)
	os.system("date")
	print ('='*80)
