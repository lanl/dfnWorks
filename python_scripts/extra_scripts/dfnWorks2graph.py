
def graph_analysis():
	print '--> Running Graph Analysis'
	copy(os.environ['PYTHON_SCRIPTS']+'/run_prune_v2.py ./run_prune_v2.py')
	os.system('$python_dfn run_prune_v2.py') 
	print '--> Running Graph Analysis Complete'

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


