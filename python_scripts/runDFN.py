import os, sys, glob, time
from shutil import copy, rmtree

def define_paths():
	os.environ['PETSC_DIR']='/home/satkarra/src/petsc-git/petsc-for-pflotran'
	os.environ['PETSC_ARCH']='/Ubuntu-14.04-nodebug'
	os.environ['PFLOTRAN_DIR']='/home/satkarra/src/pflotran-dev-Ubuntu-14.04/'
	
	os.environ['DFNGENC_PATH']='/home/jhyman/dfnWorks/DFNGen/DFNC++Version'
	os.environ['DFNTRANS_PATH']='/home/nataliia/DFNWorks_UBUNTU/ParticleTracking'
	os.environ['PYTHONPATH']='/home/satkarra/src'
	os.environ['PYTHON_SCRIPTS'] = '/home/jhyman/dfnWorks/dfnworks-main/python_scripts'

	# Executables	
	os.environ['python_dfn'] = '/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/2.4.1/bin/python'
	os.environ['python3_dfn'] = '/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/3.4.1.1/bin/python3'
	os.environ['lagrit_dfn'] = '/n/swdev/LAGRIT/bin/lagrit_lin' 
	os.environ['connect_test'] = '/home/jhyman/dfnWorks/DFN_Mesh_Connectivity_Test/ConnectivityTest'
	os.environ['correct_uge_PATH'] = '/home/jhyman/dfnWorks/dfnworks-main/C_uge_correct/correct_uge' 

def remove_batch(name):
	''' This function is used to clean up the directory in batch '''
	for fl in glob.glob(name):
		os.remove(fl)	

def make_working_directory(jobname):
    try:
        os.makedirs(jobname)
    except OSError:
	print '\nFolder ', jobname, ' exists'
	keep = raw_input('Do you want to delete it? yes/no \n')
	if keep == 'yes':
		print 'Deleting', jobname 
		rmtree(jobname)
		print 'Creating', jobname 
		os.mkdir(jobname)	
	elif keep == 'no':
		print 'Exiting Program'
		exit() 
	else:
		print 'Unknown Response'
		print 'Exiting Program'
		exit()	
def check_input(dfnGen_run_file):
	
	copy(dfnGen_run_file, 'input.dat')
	os.system('ln -s ${PYTHON_SCRIPTS}/parse.py ./parse.py')
	os.system('ln -s ${PYTHON_SCRIPTS}/inputParser.py ./inputParser.py')
	os.system('$python3_dfn parse.py input.dat')


def dfnGen(jobname, dfnGen_run_file):
	print '--> Running DFNGEN'	
	# copy input file into job folder	
	cmd = '${DFNGENC_PATH}/./main '+ dfnGen_run_file + ' ' + jobname 
	#cmd = '${DFNGENC_PATH}/./main input.dat'
	os.system(cmd)
	if os.path.isfile("params.txt") is False:
		print '--> Generation Failed'
		print '--> Exiting Program'
		exit()
	else:
		print '--> Generation Succeeded'

def mesh_fractures(nCPU):
	print '--> Meshing Fractures'	
	copy('/home/jhyman/dfnWorks/dfnworks-main/python_scripts/mesh_DFN_C++_v2.py','.')
	#cmd = '$python_dfn mesh_DFN_C++_v2.py params.txt ' + str(nCPU) 
	cmd = '$python_dfn mesh_DFN_C++_v2.py params.txt ' + str(nCPU) + '> meshing_output.txt'
	os.system(cmd)

def uncorrelated_perm(variance):
	
	os.system('ln -s ${PYTHON_SCRIPTS}/uncorrelated.py ./uncorrelated.py')
	cmd = '$python_dfn uncorrelated.py %f'%variance
	os.system(cmd)

def preprocess():
	print '--> Converting LaGriT output for PFLOTRAN'
	os.system('ln -s ${PYTHON_SCRIPTS}/driver.py ./driver.py')
	os.symlink('${PYTHON_SCRIPTS}/dfnworks_v3.py', './dfnworks_v3.py')
	os.symlink('${PYTHON_SCRIPTS}/dfntools.py', './dfntools.py')
	
	cmd = '$python_dfn driver.py'
	os.system(cmd)

def pflotran(dfnFlow_run_file, nCPU):

	print '--> Running PFLOTRAN' 
	copy(dfnFlow_run_file, './dfn_explicit.in')

	cmd = '${PETSC_DIR}/${PETSC_ARCH}/bin/mpirun -np %d $PFLOTRAN_DIR/src/pflotran/pflotran -pflotranin dfn_explicit.in'
	os.system(cmd%nCPU)	

def postprocess():
	print '--> Processing PFLOTRAN output' 
	os.system('ln -s ${PYTHON_SCRIPTS}/postprocess.py ./postprocess.py')
	cmd ='$python_dfn postprocess.py'
	os.system(cmd)

	cmd = 'cat dfn_explicit-cellinfo-001-rank*.dat > cellinfo.dat'
	os.system(cmd)
	cmd = 'cat dfn_explicit-darcyvel-001-rank*.dat > darcyvel.dat' 
	os.system(cmd)

	remove_batch('dfn_explicit-cellinfo*.dat')
	remove_batch('dfn_explicit-darcyvel*.dat')

def dfnTrans(dfnTrans_run_file):
	print '--> Running dfnTrans'	
	os.system('ln -s ${DFNTRANS_PATH}/DFNTrans .')
	copy(dfnTrans_run_file, 'PTDFN_control.dat')
	os.system('./DFNTrans')

if __name__ == "__main__":
	main_time = time.time()
	try: 
		jobname = sys.argv[1]
		nCPU = int(sys.argv[2])
	except:
		print 'Not enough input parameters'
		print 'Usage:', sys.argv[0], '[jobname][nCPU]'; sys.exit(1)

	dfnGen_run_file = '/home/jhyman/dfnWorks/dfnworks-main/python_scripts/multi_rect.dat'	
	dfnFlow_run_file = '/scratch/nobackup/jhyman/2016-mixing/dfn_explicit.in'
	dfnTrans_run_file = '/scratch/nobackup/jhyman/2016-mixing/PTDFN_control.dat'
	
	print 'Running Job: ', jobname
	print '--> dfnGen input file: ',dfnGen_run_file
	print '--> dfnFlow input file: ',dfnFlow_run_file
	print '--> dfnTrans input file: ',dfnTrans_run_file

	define_paths()
	make_working_directory(jobname)
	os.chdir(jobname)
	# dfnGen

	check_input(dfnGen_run_file)
#	dfnGen(jobname, dfnGen_run_file)
#	mesh_fractures(nCPU)
#	### dfnFlow
#	uncorrelated_perm(0)
#	preprocess()
#	pflotran(dfnFlow_run_file, nCPU)
#	postprocess()
#	# dfnTrans
#	#dfnTrans(dfnTrans_run_file)
#
#	main_elapsed = time.time() - main_time
#	print jobname, 'Complete'
#	timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
#	print(timing) 


