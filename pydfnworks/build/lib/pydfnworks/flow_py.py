
def inp2vtk_python(self, inp_file=''):
    import pyvtk as pv
    """ Using Python VTK library, convert inp file to VTK file.  then change name of CELL_DATA to POINT_DATA.
    """
    if self._inp_file:
        inp_file = self._inp_file
    else:
        self._inp_file = inp_file

    if inp_file == '':
        sys.exit('ERROR: Please provide inp filename!')

    if self._vtk_file:
        vtk_file = self._vtk_file
    else:
        vtk_file = inp_file[:-4]
        self._vtk_file = vtk_file + '.vtk'

    print("--> Reading inp data")

    with open(inp_file, 'r') as f:
        line = f.readline()
        num_nodes = int(line.strip(' ').split()[0])
        num_elems = int(line.strip(' ').split()[1])

        coord = np.zeros((num_nodes, 3), 'float')
        elem_list_tri = []
        elem_list_tetra = []

        for i in range(num_nodes):
            line = f.readline()
            coord[i, 0] = float(line.strip(' ').split()[1])
            coord[i, 1] = float(line.strip(' ').split()[2])
            coord[i, 2] = float(line.strip(' ').split()[3])

        for i in range(num_elems):
            line = f.readline().strip(' ').split()
            line.pop(0)
            line.pop(0)
            elem_type = line.pop(0)
            if elem_type == 'tri':
                elem_list_tri.append([int(i) - 1 for i in line])
            if elem_type == 'tet':
                elem_list_tetra.append([int(i) - 1 for i in line])

    print('--> Writing inp data to vtk format')

    vtk = pv.VtkData(pv.UnstructuredGrid(coord, tetra=elem_list_tetra, triangle=elem_list_tri),
                     'Unstructured pflotran grid')
    vtk.tofile(vtk_file)


def parse_pflotran_vtk_python(self, grid_vtk_file=''):
    """ Replace CELL_DATA with POINT_DATA in the VTK output."""
    print '--> Parsing PFLOTRAN output'
    if grid_vtk_file:
        self._vtk_file = grid_vtk_file
    else:
        self.inp2vtk_python()

    grid_file = self._vtk_file
    
    files = glob.glob('*-[0-9][0-9][0-9].vtk')
    with open(grid_file, 'r') as f:
        grid = f.readlines()[3:]

    out_dir = 'parsed_vtk'
    for line in grid:
        if 'POINTS' in line:
            num_cells = line.strip(' ').split()[1]

    for file in files:
        with open(file, 'r') as f:
            pflotran_out = f.readlines()[4:]
        pflotran_out = [w.replace('CELL_DATA', 'POINT_DATA ') for w in pflotran_out]
        header = ['# vtk DataFile Version 2.0\n',
                  'PFLOTRAN output\n',
                  'ASCII\n']
        filename = out_dir + '/' + file
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'w') as f:
            for line in header:
                f.write(line)
            for line in grid:
                f.write(line)
            f.write('\n')
            f.write('\n')
            if 'vel' in file:
                f.write('POINT_DATA\t ' + num_cells + '\n')
            for line in pflotran_out:
                f.write(line)
    print '--> Parsing PFLOTRAN output complete'