import sys
import os
import time
import sys
sys.path = ['/home/jhyman/Code/python/PyVTK-0.4.85']+sys.path
if sys.version[:3]=='1.5':
    from lib152 import *
else:
    from lib import *


def read_avs(input_file):            #Read in avs meshfile for node, cell data.
	nodelist = [] 
	conn_list = [] 
	cell_list = [] 
	node_attributes = []
	node_attribute_label = []
	node_attribute_unit = []

	cell_attributes = []	
	cell_attribute_label = []	
	cell_attribute_unit = []	

	cell_type_list = []
	mat_id = []

	infile = open(input_file)     
	ln = infile.readline()
	N = int(ln.strip().split()[0])                  # number nodes
	print 'There are ', N, 'nodes'
	N_cell = int(ln.strip().split()[1])               # number cells
	print 'There are ', N_cell, 'cells'
	N_att = int(ln.strip().split()[2])                  # number node based attributes
	print 'There are ', N_att, 'node based attributes'
	N_cell_att = int(ln.strip().split()[3])               # number cells
	print 'There are ', N_cell_att, 'cell based attributes'

	print '\nReading in Node Locations'
	# Read in Point Locations
	for i in range(N):                                              # FOR each node
		nd = infile.readline().strip().split()  # read line
		nodelist.append(([float(nd[1]),float(nd[2]),float(nd[3])]))

	print '\nReading in Cell Information'
	# Read in cell information 
	for i in range(N_cell): # FOR each cell
		cell = infile.readline().strip().split()
		mat_id.append(int(cell[1]))	
		cell_type = cell[2]	
		cell = [cell[0],] + cell[3:]
		cell = [int(celli) - 1 for celli in cell]
		cell_list.append([cell[0], cell_type])
		conn_list.append(cell[1:])

		if cell_type not in cell_type_list:
			cell_type_list.append(cell_type)

	if len(cell_type_list) > 1:
		print 'Just a heads up, this is a hybrid mesh'

	if N_att > 0:
		print '\nReading in Node Based Attributes'	
		# Node Based Attributes
		nd_att = infile.readline().strip().split()  # read line
		for i in range(int(nd_att[0])):
			nd = infile.readline().strip().split(',')  # read line
			node_attribute_label.append(nd[0])
			node_attribute_unit.append(nd[1].lstrip())

		for i in range(N):                                              # FOR each node
			nd = infile.readline().strip().split()  # read line
			ii = 1
			tmp_nd_att = []
			# parse node based attributes based on size, takes care of vectors.
			for j in range(int(nd_att[0])):
				curr_att = [] 
				for k in range(int(nd_att[j+1])):
					curr_att.append(float(nd[ii]))		
					ii += 1
				tmp_nd_att.append(curr_att)
			node_attributes.append(tmp_nd_att)	
	
	if N_cell_att > 0:
		print '\nReading in Cell Based Attributes'	
		# Cell Based Attributes
		cell_att = infile.readline().strip().split()  # read line
		# Number of cell based attributes, size of each attributes
		
		# Read in labels and units for each cell based attribute
		for i in range(int(cell_att[0])):
			cell = infile.readline().strip().split(',')  # read line
			cell_attribute_label.append(cell[0])
			cell_attribute_unit.append(cell[1].lstrip())

		# read and parse each cell based attribute	
		for i in range(N_cell): # FOR each node
			cell = infile.readline().strip().split()  # read line
			ii = 1
			tmp_cell_att = []
			# parse based on size of each attribute
			for j in range(int(cell_att[0])):
				curr_att = [] 
				for k in range(int(cell_att[j+1])):
					curr_att.append(float(cell[ii]))		
					ii += 1
				tmp_cell_att.append(curr_att)
			cell_attributes.append(tmp_cell_att)	
	
	infile.close()
	
	return (nodelist, cell_list, conn_list, node_attribute_label, 
		node_attribute_unit, node_attributes, cell_attributes,
		cell_attribute_label, cell_attribute_unit, mat_id)

if __name__ == "__main__":
	start_time = time.time()
	try: 
		input_file = sys.argv[1]
		output_file = sys.argv[2]
		output_style = sys.argv[3]
	except:
		print 'Usage:', sys.argv[0], '[input_file][output_file][output_style (ascii/binary/both)'; sys.exit(1)

	print 'Converting ', input_file, 'from avs to vtk\n'

	nodelist, cell_list, conn_list, node_attribute_label, node_attribute_unit, node_attributes, cell_attributes, cell_attribute_label, cell_attribute_unit, mat_id = read_avs(input_file)

	print '\nSorting Element types\n'
	# Sort Elements
	vertex_list = []
	poly_vertex_list = []
	line_list = []
	poly_line_list = []
	triangle_list = []
	triangle_strip_list = []
	polygon_list = []
	pixel_list = []
	quad_list = []
	tetra_list = []
	voxel_list = []
	hex_list = []
	wedge_list = []
	pyramid_list = []

	for i,cell_list in enumerate(cell_list):
		if cell_list[1] == 'vertex':
			vertex_list.append(conn_list[i])
		elif cell_list[1] == 'poly_vertex':
			poly_vertex_list.append(conn_list[i])
		elif cell_list[1] == 'line':
			line_list.append(conn_list[i]) 
		elif cell_list[1] == 'poly_line':
			poly_line_list.append(conn_list[i]) 
		elif cell_list[1] == 'tri':
			triangle_list.append(conn_list[i])
		elif cell_list[1] == 'tri_strip':
			triangle_strip_list.append(conn_list[i])
		elif cell_list[1] == 'polygon':
			polygon_list.append(conn_list[i])
		elif cell_list[1] == 'pixel':
			pixel_list.append(conn_list[i])
		elif cell_list[1] == 'quad':
			quad_list.append(conn_list[i])
		elif cell_list[1] == 'tet':
			tetra_list.append(conn_list[i])
		elif cell_list[1] == 'voxel':
			voxel_list.append(conn_list[i])
		elif cell_list[1] == 'hex':
			hex_list.append(conn_list[i])
		elif cell_list[1] == 'prism':
			wedge_list.append(conn_list[i])
		elif cell_list[1] == 'pyr':
			pyramid_list.append(conn_list[i])

	print 'Creating VTK format'
	# Create VTK
	vtk = VtkData(\
		UnstructuredGrid(nodelist,
		vertex = vertex_list,
		poly_vertex = poly_vertex_list, 
		line = line_list,
		poly_line = poly_line_list,
		triangle = triangle_list,
		triangle_strip = triangle_strip_list, 
		polygon = polygon_list,
		quad = quad_list,
		tetra = tetra_list,
		voxel = voxel_list, 
		hexahedron = hex_list,
		wedge = wedge_list,
		pyramid = pyramid_list), 
		output_file)

	# Pass in point data
	for i,N_att in enumerate(node_attribute_label):
		if node_attribute_unit[i] != 'integer' and node_attribute_unit[i] != 'real': 
			tmp_name = N_att + ' (' +node_attribute_unit[i] +')' 	
		else:
			tmp_name = N_att 
		curr_att = []
		
		for N_att_list in node_attributes:
			curr_att.append(N_att_list[i])

		if N_att == 'vect':
			vtk.point_data.append(Vectors(curr_att, name = tmp_name)) 
		else:
			vtk.point_data.append(Scalars(curr_att, name = tmp_name)) 

	# Pass in Cell Data
	for i,cell_att in enumerate(cell_attribute_label):
		if cell_attribute_unit[i] != 'integer' and cell_attribute_unit[i] != 'real': 
			tmp_name = cell_att + ' (' +cell_attribute_unit[i] +')' 	
		else:
			tmp_name = cell_att 
		curr_att = []
		for cell_att_list in cell_attributes:
			curr_att.append(cell_att_list[i])
		vtk.cell_data.append(Scalars(curr_att, name = tmp_name)) 

	# If there are cells, pass in material ID
	if len(mat_id) > 0:
		vtk.cell_data.append(Scalars(mat_id, name = 'Material Id')) 
	print 'Done Creating VTK format\n'

	print '\nDumping VTK Files: '+ output_file + '.vtk'
	if output_style == 'ascii':
		print '\tWritting ASCII format'
		vtk.tofile(output_file)
	elif output_style == 'binary':
		print '\tWritting binary format'
		vtk.tofile(output_file + '_b','binary')
	elif output_style == 'both':
		print '\tWritting ASCII and binary format'
		vtk.tofile(output_file)
		vtk.tofile(output_file + '_b','binary')
	else : 
		print '\tUnrecognized Format Request'
		print '\tWritting ASCII and binary format'
		vtk.tofile(output_file)
		vtk.tofile(output_file + '_b','binary')

	print '\nConversion Complete \n\nTime Taken for Conversion'
	total_time = time.time() - start_time
	print('--- %s seconds ---' % str(total_time))
	print('--- %s minutes---' % str(total_time/60.0))
	print('--- %s hours ---' % str(total_time/(60.**2)))
	print '\n\n\n'
