import os
import networkx as nx
from networkx.algorithms.flow.shortestaugmentingpath import *
from networkx.algorithms.flow.edmondskarp import *
from networkx.algorithms.flow.preflowpush import *
import numpy as np
import os.path

def create_adjacency_matrix(num_frac, version):
	''' Create adjacency Matrix using intersection files'''
	if os.path.isfile('adjac') == False: 	
		print 'Creating Adjac'

		if version < 2:
			A = np.zeros((num_frac,num_frac), dtype=np.int)
			a = np.genfromtxt('intersections.inp', skip_header = 1)[:,-2] - 1
			b = np.genfromtxt('intersections.inp', skip_header = 1)[:,-1] - 1

			for i in range(len(a)):
				A[int(a[i]), int(b[i])] = 1
		else:
			A = np.zeros((num_frac,num_frac), dtype=np.int)
			for i in range(1, num_frac + 1):
				filename = 'intersections/intersections_%d.inp'%i
				fin = open(filename)
				header = fin.readline()
				header = header.split()
				num_points = int(header[0])
				num_elem = int(header[1])
				fin.close()
				skip = 1 + num_points + num_elem + 3
				b = np.genfromtxt(filename, skip_header = skip)[:,-1] - 1 
				b = np.unique(b)
				for j in b:
					A[i - 1,j] = 1

		f = open('adjac', 'w')
		for i in range(num_frac):
			for j in range(num_frac):
				f.write('%d\n'%A[i,j])
		f.close()

		print 'Adjac Built'

def dump_boundary_nodes(domain):

	print '--> Identify Boundary Fractures Using LaGriT'

	lagrit_script = '''
read / full_mesh.inp / mo
define / XMAX / %e 
define / XMIN / %e 
define / YMAX / %e 
define / YMIN / %e 
define / ZMAX / %e 
define / ZMIN / %e 

pset / top / attribute / zic / 1,0,0/ gt /ZMAX 
pset / bottom/ attribute/ zic/ 1,0,0/ lt/ZMIN 
pset / front_s / attribute/ yic / 1,0,0 / gt/YMAX
pset / right_e / attribute/ xic/1,0,0/ gt/XMAX
pset / left_w / attribute/ xic / 1,0,0/ lt/XMIN
pset / back_n / attribute/ yic/ 1,0,0 / lt/YMIN
'''

	wall = '''

cmo/ copy / mo_tag / mo 
cmo / select / mo_tag
pset/ no_tag / not / %s 
rmpoint / pset, get, no_tag 
rmpoint/compress 
cmo / modatt / mo_tag / itp / ioflag / x
cmo / modatt / mo_tag / icr / ioflag / x
cmo / modatt / mo_tag / isn / ioflag / x
cmo / modatt / mo_tag / numbnd / ioflag / x
cmo / modatt / mo_tag / id_numb / ioflag / x
cmo / modatt / mo_tag / dfield / ioflag / x
cmo / modatt / mo_tag / b_a / ioflag / x
dump / avs2 / %s / mo_tag / 0 0 2 0
 
'''

	lagrit_script += wall%('right_e', 'right')
	lagrit_script += wall%('left_w', 'left')
	lagrit_script += wall%('top', 'top')
	lagrit_script += wall%('bottom', 'bottom')
	lagrit_script += wall%('back_n', 'back')
	lagrit_script += wall%('front_s', 'front')
	lagrit_script += 'finish \n'
	names = ['right', 'left', 'top', 'bottom', 'front', 'back']

	lagrit_file = 'dump_boundary_mat_new.lgi'
	f = open(lagrit_file, 'w')
	walls = domain/2.0
	eps = 10**-3*walls
	eps_walls = walls - eps
	edge = (eps_walls, -1.0*eps_walls,  eps_walls, -1.0*eps_walls, eps_walls, -1.0*eps_walls)

	f.write(lagrit_script%edge)
	f.flush()
	f.close()
	cmd = '/n/swdev/LAGRIT/bin/lagrit_lin < ' + lagrit_file
	os.system(cmd) 

	for n in names:
		data = np.genfromtxt(n, skip_header = 3)
		data = np.unique(data)
		np.savetxt(n+'.txt', data, delimiter=',') 

def run_max_flow(inflow_nodes, outflow_nodes):

	print 'Running Max Flow'
	inflow = np.genfromtxt(inflow_nodes) - 1
	outflow = np.genfromtxt(outflow_nodes) - 1
	inflow = list(inflow)
	outflow = list(outflow)

	data = np.genfromtxt('adjac')
	n = int(np.sqrt(len(data)))
	A = data.reshape(n,n)
	G = nx.from_numpy_matrix(A)
	for (u,v,d) in G.edges(data=True):
	    d['capacity'] = 1

	G.add_node('s')
	G.add_node('t')
	G.add_edges_from(zip(['s']*(len(inflow)),inflow),capacity=1)
	G.add_edges_from(zip(outflow,['t']*(len(outflow))),capacity=1)
	# maximum flow
	#v,d = nx.maximum_flow(G,'s','t',flow_func=shortest_augmenting_path)
	v,d = nx.maximum_flow(G,'s','t',flow_func=edmonds_karp)
	# print("maxflow",v)
	#v,d = nx.maximum_flow(G,'s','t',flow_func=preflow_push) # broken?
	maxflow_edges = [(u,v) for (u,v) in G.edges() if d[u][v] > 0 or d[v][u] > 0]
	max_flow_graph = nx.Graph(maxflow_edges)
	max_flow_graph.remove_node('s')
	max_flow_graph.remove_node('t')
	backbone = []
	for n in max_flow_graph:
#		print int(n)+1	
		backbone.append(int(n) +1)
#	print backbone
	print 'Number of Fractures in backbone: %', len(backbone)
	backbone = np.sort(backbone)
	np.savetxt('maxflow.nodes.txt', backbone, fmt = '%d')
	print 'Max Flow Complete'

def run_current_flow(inflow_nodes, outflow_nodes):
	print 'Running Current Flow'
	inflow = np.genfromtxt(inflow_nodes) - 1
	outflow = np.genfromtxt(outflow_nodes) - 1
	inflow = list(inflow)
	outflow = list(outflow)


	data = np.genfromtxt('adjac')
	n = int(np.sqrt(len(data)))
	A = data.reshape(n,n)
	G = nx.from_numpy_matrix(A)
	for (u,v,d) in G.edges(data=True):
	    d['capacity'] = 1
	
	# current flow
	G.add_node('s')
	G.add_node('t')
	G.add_edges_from(zip(['s']*(len(inflow)),inflow),capacity=1)
	G.add_edges_from(zip(outflow,['t']*(len(outflow))),capacity=1)
	cf = nx.edge_current_flow_betweenness_centrality_subset(G,sources=['s'],targets=['t'],weight='capacity')
	currentflow_edges = [(u,v) for (u,v),d in cf.items() if d > 10**-15]
	current_flow_graph = nx.Graph(currentflow_edges)
	current_flow_graph.remove_node('s')
	current_flow_graph.remove_node('t')
	backbone = []
	for n in current_flow_graph:
		backbone.append(int(n) +1)
	print 'Number of Fractures in backbone: ', len(backbone)
	np.savetxt('currentflow.nodes.txt', backbone)
	
	print 'Current Flow Complete '

def prune_mesh(backbone, num_frac):


	print 'Extracting backbone based on ', backbone

	output_file = backbone[:-10] + '_mesh.inp'
	keep_list = np.genfromtxt(backbone)

	# Fractures to keep at tagged with itetclr = M
	M = num_frac + 1

	lagrit_script = '''
define / M / %d
read / avs / full_mesh.inp / mo
cmo / select / mo
# Creat new Element based att for saving itet color
cmo / addatt / mo / itetclr_save / vint / scalar / nelements
# Copy itetclr for saving
cmo / copyatt / mo / mo / itetclr_save / itetclr
'''%M
	lagrit_script += '''
# Find Fractures with Mat ID in keep list
eltset / ereset / itetclr / eq / %d
# Tag Fractures in Keep list with mat id = M
cmo / setatt / mo / itetclr / eltset get ereset / M 
eltset / ereset / delete
'''%(keep_list[0])
	for i in keep_list[1:]:
		lagrit_script += '''
eltset / ereset / itetclr /eq / %d
cmo / setatt / mo / itetclr / eltset get ereset / M 
eltset / ereset / delete
'''%(i)
	lagrit_script += '''
# Remove all fractures with mat id != M, those not in keep list
rmmat / M / element / exclusive
rmpoint / compress
# recolor fractures with original mat ID
cmo / copyatt / mo / mo / itetclr / itetclr_save
cmo / DELATT / mo / itetclr_save
cmo / status / brief
dump / avs2 / %s / mo
finish
'''%output_file

	lagrit_file = 'prune_dfn.lgi'
	f = open(lagrit_file, 'w')
	f.write(lagrit_script)
	f.flush()
	f.close()
	cmd = '/n/swdev/LAGRIT/bin/lagrit_lin < ' + lagrit_file
	os.system(cmd)

	cmd = 'python2.7 /home/jhyman/Code/python/convert_avs_to_vtk.py %s %s binary'%(output_file, output_file[:-4])
	os.system(cmd)

	print backbone, ' nodes mesh output as ', output_file

if __name__ == "__main__":
	
	inflow = 'right.txt'
	outflow = 'left.txt'
	domain = 20 
	version = 2

	# Get Number of Fractures
	f = open('params.txt')
	num_frac = int(f.readline())
	f.close()

	create_adjacency_matrix(num_frac, version)
	dump_boundary_nodes(domain)
	run_max_flow(inflow, outflow)
	#prune_mesh('maxflow.nodes.txt', num_frac)

#	run_current_flow(inflow, outflow)
	#prune_mesh('currentflow.nodes.txt', num_frac)

	print 'All Done, Goodbye'


