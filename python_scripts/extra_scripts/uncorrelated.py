import numpy as np
import matplotlib.pyplot as plt 
import os, sys

print 'Creating Transmissivity Fields'

#mu  = float(sys.argv[1]) 
sigma = float(sys.argv[1]) 

print 'Variance: ', sigma

print 'Running un-correlated'
x = np.genfromtxt('aperture.dat', skip_header = 1)
n = len(x)
b = x[0,-1]
n = len(x)
T = (b**3)/12.0
k = T/b

k *= 10**6

print k
print np.log(k)
perm = np.log(k)*np.ones(n) 
perturbation = np.random.normal(0.0, 1.0, n)
perm = np.exp(perm + np.sqrt(sigma)*perturbation) 

aper = (12.0*perm)**0.5


#plt.hist(np.log(perm))
#plt.show()


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

aper_format = np.genfromtxt('aperture.dat', skip_header = 1)

output_filename = 'aperture_' + str(sigma) + '.dat'
f = open(output_filename,'w+')
f.write('aperture\n')
for i in range(n):
	f.write('%d %d %d  %0.5e\n'%(aper_format[i,0], aper_format[i,1], aper_format[i,2], aper[i]))
f.close()

os.remove('aperture.dat')
cmd = 'ln -s ' + output_filename + ' aperture.dat '
os.system(cmd)

#
#perm_format = np.genfromtxt('perm.dat', skip_header = 1)
#new_perm = np.genfromtxt('perm.dat', skip_header = 1)
#for i in range(n):
#	new_perm[i,3] = perm[i] 
#	new_perm[i,4] = new_perm[i,3] 
#	new_perm[i,5] = new_perm[i,3] 
#
output_filename = 'perm_' + str(sigma) + '.dat'
f = open(output_filename,'w+')
f.write('permeability\n')
for i in range(n):
	f.write('-%d 0 0 %0.5e %0.5e %0.5e\n'%(i+7, perm[i], perm[i], perm[i]))
f.close()

os.remove('perm.dat')
cmd = 'ln -s ' + output_filename + ' perm.dat '
os.system(cmd)


