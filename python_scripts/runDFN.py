import os, sys, glob, time
from shutil import copy, rmtree
from numpy import genfromtxt

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
	os.environ['python3_dfn'] = '/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/3.4.1.1/bin/python3'
	os.environ['lagrit_dfn'] = '/n/swdev/LAGRIT/bin/lagrit_lin' 
	os.environ['connect_test'] = '/home/jhyman/dfnWorks/DFN_Mesh_Connectivity_Test/ConnectivityTest'
	os.environ['correct_uge_PATH'] = '/home/jhyman/dfnWorks/dfnWorks-main/C_uge_correct/correct_uge' 

def remove_batch(name):
	''' This function is used to clean up the directory in batch '''
	for fl in glob.glob(name):
		os.remove(fl)	

def make_working_directory(jobname):
    try:
        os.makedir(jobname)
	os.makedir(jobname + '/radii')
	os.makedir(jobname + '/intersections')
	os.makedir(jobname + '/polys')
    except OSError:
	print '\nFolder ', jobname, ' exists'
	keep = raw_input('Do you want to delete it? [yes/no] \n')
	if keep == 'yes':
		print 'Deleting', jobname 
		rmtree(jobname)
		print 'Creating', jobname 
		os.mkdir(jobname)	
		os.makedir(jobname + '/radii')
		os.makedir(jobname + '/intersections')
		os.makedir(jobname + '/polys')
	elif keep == 'no':
		print 'Exiting Program'
		exit() 
	else:
		print 'Unknown Response'
		print 'Exiting Program'
		exit()
	
def check_input(dfnGen_run_file):

	print '--> Checking input file'	
	copy(dfnGen_run_file, 'input.dat')
	try:
		os.system('ln -s ${PYTHON_SCRIPTS}/parse.py ./parse.py')
	except:
		print '\t--> parse.py file already exists'
	try:
		os.system('ln -s ${PYTHON_SCRIPTS}/inputParser.py ./inputParser.py')
	except:
		print '\t--> inputParser.py file already exists'
	os.system('$python_dfn parse.py input.dat')


def dfnGen(jobname, dfnGen_run_file):
	print '--> Running DFNGEN'	
	# copy input file into job folder	
	cmd = '${DFNGENC_PATH}/./main '+ dfnGen_run_file + ' ' + jobname 
	#cmd = '${DFNGENC_PATH}/./main input.dat'
	os.system(cmd)
	if os.path.isfile(jobname+"/params.txt") is False:
		print '--> Generation Failed'
		print '--> Exiting Program'
		exit()
	else:
		print '--> Generation Succeeded'

def mesh_fractures(nCPU):

	print '--> Meshing Fractures'	
	os.system('cp ${PYTHON_SCRIPTS}/mesh_DFN_C++_v2.py ./mesh_DFN_C++_v2.py')
	cmd = '$python_dfn mesh_DFN_C++_v2.py params.txt ' + str(nCPU) 
	os.system(cmd)

def graph_analysis():
	print '--> Running Graph Analysis'
	os.system('cp ${PYTHON_SCRIPTS}/run_prune_v2.py ./run_prune_v2.py')
	cmd = '$python_dfn run_prune_v2.py' 
	os.system(cmd)

def mesh_prune_network(nCPU, keep_list):

	print '--> Meshing Prune Network'
	try:
		os.makedirs('prune_network')
	except OSError:
		rmtree('prune_network')
		os.mkdir('prune_network')
	
	os.chdir('prune_network')
	os.system('ln -s ../params.txt ./')
	os.system('ln -s ../intersections/ ./')
	os.system('ln -s ../polys/ ./')
	os.system('ln -s ../'+keep_list + ' ./' )
	
	os.system('cp ${PYTHON_SCRIPTS}/mesh_prune_DFN.py ./mesh_prune_DFN.py')
	cmd = '$python_dfn mesh_prune_DFN.py params.txt ' + str(nCPU) + ' ' + keep_list 
	os.system(cmd)

	print'--> Editing perm.dat and aperture.dat files'
	keep_list_nodes = genfromtxt(keep_list, dtype = "int")
	perm = genfromtxt('../perm.dat', skip_header = 1)[keep_list_nodes, -1]
	fperm = open('perm.dat', 'w+')
	fperm.write('permeability\n')
	for i in range(len(keep_list_nodes)):
		fperm.write('-%d 0 0 %e %e %e\n'%(7 + i, perm[i], perm[i], perm[i]))	
	fperm.close()	
	
	aperture = genfromtxt('../aperture.dat', skip_header = 1)[keep_list_nodes, -1]
	faperture = open('aperture.dat', 'w+')
	faperture.write('aperture\n')
	for i in range(len(keep_list_nodes)):
		faperture.write('-%d 0 0 %e \n'%(7 + i, aperture[i]))	
	faperture.close()	
	print'--> Editing perm.dat and aperture.dat files complete'

def convert_to_vtk(name):
	
	try:	
		os.system('ln -s ${PYTHON_SCRIPTS}/convert_avs_to_vtk.py ./convert_avs_to_vtk.py')
	except:
		print '\t--> convert_avs_to_vtk.py already exists'
	cmd = '$python_dfn convert_avs_to_vtk.py ' + name + ' ' + name[:-4] + ' binary' 
	os.system(cmd)

def uncorrelated_perm(variance):

	try:	
		os.system('ln -s ${PYTHON_SCRIPTS}/uncorrelated.py ./uncorrelated.py')
	except:
		print '\t--> uncorrelated.py already exists'
	cmd = '$python_dfn uncorrelated.py %f'%variance
	os.system(cmd)

def preprocess():
	print '--> Converting LaGriT output for PFLOTRAN'
	try:
		os.system('ln -s ${PYTHON_SCRIPTS}/driver.py ./driver.py')
		os.symlink('${PYTHON_SCRIPTS}/dfnworks_v3.py', './dfnworks_v3.py')
		os.symlink('${PYTHON_SCRIPTS}/dfntools.py', './dfntools.py')
	except:
		print '\t--> Driver files already exist'
		
	cmd = '$python_dfn driver.py'
	os.system(cmd)

def pflotran(dfnFlow_run_file, nCPU):

	print '--> Running PFLOTRAN' 
	try: 
		copy(dfnFlow_run_file, './dfn_explicit.in')
	except:
		print '\t--> PFLOTRAN input file already exists'
	cmd = '${PETSC_DIR}/${PETSC_ARCH}/bin/mpirun -np %d $PFLOTRAN_DIR/src/pflotran/pflotran -pflotranin dfn_explicit.in'
	os.system(cmd%nCPU)	

def postprocess():
	print '--> Processing PFLOTRAN output' 
	try:
		os.system('ln -s ${PYTHON_SCRIPTS}/postprocess.py ./postprocess.py')
	except:
		print '\t--> postprocess.py file already exists'
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
	try:
		os.system('ln -s ${DFNTRANS_PATH}/DFNTrans .')
	except:
		print '\t--> Link to DFNTRANS already exists'
	try:	
		copy(dfnTrans_run_file, 'PTDFN_control.dat')
	except:
		print '\t--> PTDFN_control.dat file already exists' 
	os.system('./DFNTrans')

if __name__ == "__main__":
	
	dfnGen_run_file = '/home/jhyman/dfnWorks/dfnWorks-main/python_scripts/pl_test.dat'	
	dfnFlow_run_file = '/scratch/nobackup/jhyman/2016-mixing/dfn_explicit.in'
	dfnTrans_run_file = '/scratch/nobackup/jhyman/2016-mixing/PTDFN_control.dat'

	main_time = time.time()
	try: 
		jobname = sys.argv[1]
		nCPU = int(sys.argv[2])
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

	print 'Running Job: ', jobname
	print '--> dfnGen input file: ',dfnGen_run_file
	print '--> dfnFlow input file: ',dfnFlow_run_file
	print '--> dfnTrans input file: ',dfnTrans_run_file
	print ''

	define_paths()
	make_working_directory(jobname)
	# dfnGen
	check_input(dfnGen_run_file)
	
	#dfnGen(jobname, dfnGen_run_file)
	os.chdir(jobname)
	#mesh_fractures(nCPU)
	#preprocess()
	#pflotran(dfnFlow_run_file, nCPU)
	#postprocess()
	#dfnTrans(dfnTrans_run_file)

	### Graph Analysis
	graph_analysis()
	mesh_prune_network(nCPU, 'maxflow.nodes.txt')
	preprocess()
	pflotran(dfnFlow_run_file, nCPU)
	postprocess()
	dfnTrans(dfnTrans_run_file)
#	convert_to_vtk('full_mesh.inp')
	### dfnFlow

	main_elapsed = time.time() - main_time
	print jobname, 'Complete'
	timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
	print timing 


