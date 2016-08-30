import os, sys, glob, time
from shutil import copy, rmtree
from numpy import genfromtxt

from dfnWorks import *

def define_paths():
	os.environ['PETSC_DIR']='/home/satkarra/src/petsc-git/petsc-for-pflotran'
	os.environ['PETSC_ARCH']='/Ubuntu-14.04-nodebug'
	os.environ['PFLOTRAN_DIR']='/home/satkarra/src/pflotran-dev-Ubuntu-14.04/'
	
	os.environ['DFNGENC_PATH']='/home/jhyman/dfnWorks/DFNGen/DFNC++Version'
	os.environ['DFNTRANS_PATH']='/home/nataliia/DFNWorks_UBUNTU/ParticleTracking'
	os.environ['PYTHONPATH']='/home/satkarra/src'
	os.environ['PYTHON_SCRIPTS'] = '/home/jhyman/dfnWorks/dfnWorks-main/python_scripts'

	# Executables	
	os.environ['python_dfn'] = '/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/2.4.1/bin/python'
	os.environ['lagrit_dfn'] = '/n/swdev/LAGRIT/bin/lagrit_lin' 
	os.environ['connect_test'] = '/home/jhyman/dfnWorks/DFN_Mesh_Connectivity_Test/ConnectivityTest'
	os.environ['correct_uge_PATH'] = '/home/jhyman/dfnWorks/dfnWorks-main/C_uge_correct/correct_uge' 
	
	os.environ['PYLAGRIT']='/home/jhyman/pylagrit/src'


if __name__ == "__main__":
	
	dfnGen_run_file = '/home/jhyman/dfnWorks/dfnWorks-main/sample_inputs/pl_test.dat'	
	dfnFlow_run_file = '/scratch/nobackup/jhyman/2016-mixing/dfn_explicit.in'
	dfnTrans_run_file = '/scratch/nobackup/jhyman/2016-mixing/PTDFN_control.dat'
	
	main_time = time.time()
	# Command lines: argv[1] = jobname, argv[2] = number of cpus. 
	# Command line is overloaded, so argv[3], argv[4], argv[5] 
	# can be dfnGen, dfnFlow, and dfnTrans control files. 
	try: 
		jobname = sys.argv[1]
		ncpu = int(sys.argv[2])
	except:
		print 'Not enough input parameters'
		print 'Usage:', sys.argv[0], '[jobname][nCPU]'; sys.exit(1)
	if len(sys.argv) == 4:
		dfnGen_run_file = sys.argv[3] 
	elif len(sys.argv) == 5:
		dfnGen_run_file = sys.argv[3] 
		dfnFlow_run_file = sys.argv[4] 
	elif len(sys.argv) == 6:
		dfnGen_run_file = sys.argv[3] 
		dfnFlow_run_file = sys.argv[4] 
		dfnTrans_run_file = sys.argv[5] 

	# Create DFN object
	dfn = dfnworks(jobname = jobname, input_file = dfnGen_run_file, ncpu = ncpu, pflotran_file = dfnFlow_run_file, dfnTrans_file = dfnTrans_run_file)

	print 'Running Job: ', jobname
	print 'Number of cpus requested: ', ncpu 
	print '--> dfnGen input file: ',dfnGen_run_file
	print '--> dfnFlow input file: ',dfnFlow_run_file
	print '--> dfnTrans input file: ',dfnTrans_run_file
	print ''


	define_paths()

	dfn.dfnGen()
	#dfn.dfnFlow()
#	dfn.dfnTrans()

	main_elapsed = time.time() - main_time
	print jobname, 'Complete'
	timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
	print timing 


