def mesh_network(self, ncpu = ''):
	'''
	Mesh Fracture Network using ncpus and lagrit
	meshing file is seperate file: dfnGen_meshing.py
	'''
	print('='*80)
	print("Meshing Network Using LaGriT : Starting")
	print('='*80)
	production_mode = True 
	refine_factor = 1	
	
	nPoly, h, visualMode, dudded_points,domain = mesh.parse_params_file()
	self._num_frac = nPoly
	tic2 = time()

	mesh.create_parameter_mlgi_file(nPoly, h)

	mesh.create_lagrit_scripts(production_mode, self._ncpu, refine_factor, visualMode)

	failure = mesh.mesh_fractures_header(nPoly, self._ncpu, visualMode)
	self.dump_time('Process: Meshing Fractures', time() - tic2)
	if failure > 0:
		mesh.cleanup_dir()
		sys.exit("One or more fractures failed to mesh properly.\nExiting Program")

	
	tic2 = time()
	n_jobs = mesh.create_merge_poly_files(self._ncpu, nPoly, visualMode)

	mesh.merge_the_meshes(nPoly, self._ncpu, n_jobs, visualMode)
	self.dump_time('Process: Merging the Mesh', time() - tic2)	

	if(visualMode == False):	
		if (mesh.check_dudded_points(dudded_points) == False):
			cleanup_dir()
			sys.exit("Incorrect Number of dudded points.\nExitingin Program")

	if production_mode == True:
		mesh.cleanup_dir()

	if(visualMode == False): 
		mesh.define_zones(h,domain)

	mesh.output_meshing_report(visualMode)
	print ('='*80)
	if(visualMode==False):
		print("Meshing Network Using LaGriT Complete")
	if(visualMode==True):
		sys.exit("Meshing Visual Mode Network Using LaGriT Complete\n"+'='*80)
	print ('='*80)

