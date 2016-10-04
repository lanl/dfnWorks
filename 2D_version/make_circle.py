from numpy import sin, cos, linspace, pi, zeros, sqrt
import matplotlib.pylab as plt

r = 1.0
nPoints = 256 
theta = linspace(0,2*pi,nPoints)
x = zeros(nPoints)
y = zeros(nPoints)

x=(r*cos(theta))
y=(r*sin(theta))
#
#for i in range(nPoints):
#	d = sqrt( (x[i-1] - x[i])**2 + (y[i-1] - y[i])**2 )  
#	print d
#
#print x
#print y
#
fp = open('circle.inp', 'w+')
fp.write('%d %d 2 0 0\n'%(nPoints,nPoints-1))
for i in range(nPoints):
	fp.write('%d %f %f 0\n'%(i+1,x[i],y[i]))
for i in range(nPoints - 1):
	fp.write('%d 1 line %d %d\n'%(i+1,i+1,i+2))
fp.write('2 1 1\n')
fp.write('a_b, integer\n')
fp.write('b_a, integer\n')
for i in range(nPoints):
	fp.write('%d %d %d\n'%(i+1,0,1))
fp.close()



#
#plt.plot(x,y,'o-')
#plt.show()
#
#
