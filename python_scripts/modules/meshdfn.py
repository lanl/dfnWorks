"""
.. file:: meshdfn.py
   :synopsis: meshing driver for DFN 
   :version: 1.0
   :maintainer: Jeffrey Hyman, Carl Gable, Nathaniel Knapp
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import os
import sys
from mesh_dfn_helper import *
from lagrit_scripts import *
from run_meshing import *

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

	production_mode = True 
	refine_factor = 1
	ncpu = 4

	os.environ['DFNWORKS_PATH'] = '/home/nknapp/dfnworks-main/'

	# Executables	
	os.environ['python_dfn'] = '/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/2.4.1/bin/python'
	os.environ['lagrit_dfn'] = '/n/swdev/mesh_tools/lagrit/install-Ubuntu-14.04-x86_64/3.2.0/release/gcc-4.8.4/bin/lagrit'
	os.environ['connect_test'] = os.environ['DFNWORKS_PATH']+'/DFN_Mesh_Connectivity_Test/ConnectivityTest'

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
		sys.exit('connect_test undefined')	
	
	if (len(sys.argv) == 1):
		print "Number of CPU's to use (default):", ncpu
	
	elif (len(sys.argv) == 2):
		ncpu = int(sys.argv[1])
		print "Number of CPU's to use:", ncpu
	

	## input checking over
	num_poly, h, visual_mode, dudded_points, domain = parse_params_file()

	create_parameter_mlgi_file(num_poly, h)

	create_lagrit_scripts(visual_mode, ncpu)

	failure = mesh_fractures_header(num_poly, ncpu, visual_mode)

	if failure:
		cleanup_dir()
		sys.exit("One or more fractures failed to mesh properly.\nExiting Program")

	n_jobs = create_merge_poly_files(ncpu, num_poly, visual_mode)

	merge_the_meshes(num_poly, ncpu, n_jobs, visual_mode)
	
	if not visual_mode:	
		if not check_dudded_points(dudded_points):
			cleanup_dir()
			sys.exit("Incorrect Number of dudded points.\nExitingin Program")

	if production_mode:
		cleanup_dir()

	if not visual_mode: 
		define_zones(h,domain)

	output_meshing_report(visual_mode)
	os.system("date")
	print ('='*80)
