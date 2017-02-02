def uncorrelated(self, sigma):
		print '--> Creating Uncorrelated Transmissivity Fields'
		print 'Variance: ', sigma
		print 'Running un-correlated'
		x = np.genfromtxt('../aperture.dat', skip_header = 1)[:,-1]
		k = np.genfromtxt('../perm.dat', skip_header = 1)[0,-1]
		n = len(x)

		print np.mean(x)

		perm = np.log(k)*np.ones(n) 
		perturbation = np.random.normal(0.0, 1.0, n)
		perm = np.exp(perm + np.sqrt(sigma)*perturbation) 

		aper = np.sqrt((12.0*perm))
		aper -= np.mean(aper)
		aper += np.mean(x)

		print '\nPerm Stats'
		print '\tMean:', np.mean(perm)
		print '\tMean:', np.mean(np.log(perm))
		print '\tVariance:',np.var(np.log(perm))
		print '\tMinimum:',min(perm)
		print '\tMaximum:',max(perm)
		print '\tMinimum:',min(np.log(perm))
		print '\tMaximum:',max(np.log(perm))

		print '\nAperture Stats'
		print '\tMean:', np.mean(aper)
		print '\tVariance:',np.var(aper)
		print '\tMinimum:',min(aper)
		print '\tMaximum:',max(aper)


		output_filename = 'aperture_' + str(sigma) + '.dat'
		f = open(output_filename,'w+')
		f.write('aperture\n')
		for i in range(n):
			f.write('-%d 0 0 %0.5e\n'%(i + 7, aper[i]))
		f.close()

		cmd = 'ln -s ' + output_filename + ' aperture.dat '
		os.system(cmd)

		output_filename = 'perm_' + str(sigma) + '.dat'
		f = open(output_filename,'w+')
		f.write('permeability\n')
		for i in range(n):
			f.write('-%d 0 0 %0.5e %0.5e %0.5e\n'%(i+7, perm[i], perm[i], perm[i]))
		f.close()

		cmd = 'ln -s ' + output_filename + ' perm.dat '
		os.system(cmd)

def create_dfnTrans_links(self):
    #os.symlink('../params.txt', 'params.txt')
    os.symlink('../allboundaries.zone', 'allboundaries.zone')
    os.symlink('../tri_fracture.stor', 'tri_fracture.stor')
    os.symlink('../poly_info.dat','poly_info.dat')
    #os.symlink(self._jobname+'/*ex', './')

