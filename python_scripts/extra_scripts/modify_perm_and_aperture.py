from numpy import genfromtxt, sort

keep_list = genfromtxt('maxflow.nodes.txt')
keep_list_nodes = sort(keep_list.astype(int))

print keep_list

print'--> Editing perm.dat and aperture.dat files'
#keep_list_nodes = genfromtxt(keep_list, dtype = "int")
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

