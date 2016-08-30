
def remove_batch(name):
	''' This function is used to clean up the directory in batch '''
	for fl in glob.glob(name):
		os.remove(fl)	

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


