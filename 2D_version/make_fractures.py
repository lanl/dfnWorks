import numpy as np
import matplotlib.pylab as plt

class fracture(object):
	x0 = 0
	x1 = 0
	y0 = 0
	y1 = 0
	m = 0
	length = 0
	def __init__(self): 
		self._x0 = '' 
		self._y0 = '' 
		self._x1= '' 
		self._y1 = ''
		self._m = '' 
		self._length = '' 
		self._family = -1 
	
def sample_location(domain, length, m):
	a = -0.5*domain 
	b = 0.5*domain 
	x0,y0 = a + (b-a)*np.random.rand(2)
	x1 = x0 + np.sqrt( (length)**2 / ( 1 + m**2)) 
	y1 = m*(x1 - x0) + y0
	return (x0,y0,x1,y1)

num_frac = 10
domain = 10.0
domainBuffer = 0.5*domain
d_half  = 0.5*domain

print 'Number of Fractures:', num_frac

fractures = []

xc = []
yc = []

for i in range(num_frac):
	tmp = fracture()
	if i%2 == 0:
		tmp.m = 1
		tmp.family = 1
	else:
		tmp.m = -1
		tmp.family = 2
	tmp.length = 2.0
	tmp.x0, tmp.y0, tmp.x1, tmp.y1 = sample_location(domain + domainBuffer, tmp.length, tmp.m)
	
	xc.append(0.5*(tmp.x0 + tmp.x1))
	yc.append(0.5*(tmp.y0 + tmp.y1))

	plt.plot([tmp.x0, tmp.x1], [tmp.y0, tmp.y1])
	fractures.append(tmp)

plt.axis([-0.5*domain, 0.5*domain, -0.5*domain, 0.5*domain])
plt.show()



#plt.hist(xc)
#plt.hist(yc)
#plt.show()

print 'Writing out Coordinates'
f = open('fractures.dat','w+')
f.write('nRectangles: %d\n'%(num_frac+1))
f.write('Coordinates:\n')
coords = '{%f, %f, %f} {%f, %f, %f} {%f, %f, %f} {%f, %f, %f}'
tmp = coords%(-d_half,-d_half,0,d_half,-d_half,0, \
	d_half,d_half,0,-d_half,d_half,0)
f.write('%s\n'%tmp)
for i in range(num_frac):
	x0 = fractures[i].x0
	x1 = fractures[i].x1
	y0 = fractures[i].y0
	y1 = fractures[i].y1
	tmp = coords%(x0,y0,-1.1, x1,y1, -1.1, x1,y1, 1.1,x0,y0,1.1)
	f.write('%s\n'%tmp)
f.close()



