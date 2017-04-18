# particles initial positions are defined randomly all over the DFN domain.
# Code uses lagrit to calculate the shortest distances from particle's 
# initial positions to fractures cells, outputs the cells ID.
from sys import *
from string import *
from array import *
import os
import time
import sys
import numpy
import random

os.system("date")
print "--- Run LaGriT script to find closest node to a randomly seed particle ---"
if len(sys.argv) < 2:
    sys.exit('ERROR: Usage - python findclosenode.py [inp_filename][number of particles]')
inp_file = sys.argv[1]
numberpart = sys.argv[2]
lagritpath = '/home/quanb/src/my_lagrit/src/mylagrit'

print ' Read avs file of the mesh to define DFN domain size '

fcoord=open('ParticleInitCoordR.dat','w')
fcoord.write( str(int(numberpart))+'\n')

# read avs file to define DFN domain's coordinates 
f=open('domainattr.lgi','w')
f.write('read / avs / '+inp_file+' / mo \n')
f.write("\n")
f.write("cmo/ printatt / mo/ -xyz-/minmax \n")
f.write("\n")
f.write("finish \n")
f.write("\n")
f.flush()
f.close()
os.system(lagritpath + " <domainattr.lgi >printxyz.out")

#  read data from lagrit output file 
fil=open('printxyz.out','r')
for line in fil:
	k=line.split()
	for word in line.split():
		if word=='xic':
			xmin=float(k[1])
			xmax=float(k[2])
		if word=='yic':
			ymin=float(k[1])
			ymax=float(k[2])
		if word=='zic':
			zmin=float(k[1])
			zmax=float(k[2])

fil.close()

print ' Seed a particle randomly in the domain and write output file ParticleInitCoordR.dat'
particle=[[0.0, 0.0, 0.0, 0.0]]
for i in range(int(numberpart)):
	xp=random.uniform(xmin,xmax)
	yp=random.uniform(ymin,ymax)
	zp=random.uniform(zmin,zmax) 
        particle.append([xp,yp,zp])
        fcoord.write(str(xp)+'	'+str(yp)+'	'+str(zp)+' \n')
        
fcoord.flush()
fcoord.close()


f=open('definedist.lgi','w')
f.write("read / avs / "+str(inp_file)+" / mo2 \n")
f.write("\n")
f.write('cmo / create/ mo1  \n')
f.write('cmo/readatt/ mo1/ xic, yic, zic/ 1,0,0 / ParticleInitCoordR.dat  \n')
f.write('cmo / set_id/mo2 / node/ n_num \n')
f.write('cmo / addatt/mo1 /idnum/ VINT/scalar / nnodes  \n')
f.write('interpolate/voronoi/mo1,idnum/1 0 0/mo2,n_num  \n')
f.write('dump / avs2/ClosestNodeR.inp / mo1/0 0 1 0  \n')

f.write("finish \n")
f.write("\n")
f.flush()
f.close()
os.system(lagritpath + " <definedist.lgi >distance.out")


