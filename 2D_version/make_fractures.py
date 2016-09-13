import numpy as np
from fracture_class import *
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
domain = 2.0
domainBuffer = 0.5*domain 

print 'Number of Fractures:', num_frac

fractures = []
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

	plt.plot([tmp.x0, tmp.x1], [tmp.y0, tmp.y1])
	fractures.append(tmp)

plt.axis([-0.5*domain, 0.5*domain, -0.5*domain, 0.5*domain])

plt.show()





