"""
functions for using pflotran in dfnworks
"""
import os
import subprocess
import sys
import h5py
import glob
import shutil
import ntpath
from time import time
import numpy as np


def lagrit2pflotran(self):
    """  Takes output from LaGriT and processes it for use in PFLOTRAN.
    Calls the functuon write_perms_and_correct_volumes_areas() and zone2ex
   
    Parameters    
    --------------
        self : object
            DFN Class 

    Returns
    --------
        None

    Notes
    --------
        None
    
    """
    if self.flow_solver != "PFLOTRAN":
        error = "ERROR! Wrong flow solver requested\n"
        sys.stderr.write(error)
        sys.exit(1)

    print('=' * 80)
    print("Starting conversion of files for PFLOTRAN ")
    print('=' * 80)

    if self.inp_file == '':
        error = 'ERROR: Please provide inp filename!\n'
        sys.stderr.write(error)
        sys.exit(1)

    # Check if UGE file was created by LaGriT, if it does not exists, exit
    self.uge_file = self.inp_file[:-4] + '.uge'
    if not os.path.isfile(self.uge_file):
        error = 'ERROR!!! Cannot find .uge file\nExiting\n'
        sys.stderr.write(error)
        sys.exit(1)

    self.write_perms_and_correct_volumes_areas()
    self.zone2ex(zone_file='all')
    print('=' * 80)
    print("Conversion of files for PFLOTRAN complete")
    print('=' * 80)
    print("\n\n")


def zone2ex(self,
            uge_file='',
            zone_file='',
            face='',
            boundary_cell_area=1.e-1):
    """
    Convert zone files from LaGriT into ex format for LaGriT
    
    Parameters
    -----------
        self : object
            DFN Class
        uge_file : string
            Name of uge file
        zone_file : string
            Name of zone file
        Face : Face of the plane corresponding to the zone file
        zone_file : string
            Name of zone file to work on. Can be 'all' processes all directions, top, bottom, left, right, front, back
        boundary_cell_area : double 
            should be a large value relative to the mesh size to force pressure boundary conditions. 

    Returns
    ----------
    None

    Notes
    ----------
    the boundary_cell_area should be a function of h, the mesh resolution
    """

    print('--> Converting zone files to ex')

    if self.uge_file == '':
        error = 'ERROR: Please provide uge filename!\n'
        sys.stderr.write(error)
        sys.exit(1)

    # Opening uge file
    print('\n--> Opening uge file')
    fuge = open(self.uge_file, 'r')

    # Reading cell ids, cells centers and cell volumes
    line = fuge.readline()
    line = line.split()
    NumCells = int(line[1])

    Cell_id = np.zeros(NumCells, 'int')
    Cell_coord = np.zeros((NumCells, 3), 'float')
    Cell_vol = np.zeros(NumCells, 'float')

    for cells in range(NumCells):
        line = fuge.readline()
        line = line.split()
        Cell_id[cells] = int(line.pop(0))
        line = [float(id) for id in line]
        Cell_vol[cells] = line.pop(3)
        Cell_coord[cells] = line
    fuge.close()

    print('--> Finished with uge file\n')

    # loop through zone files
    if zone_file == 'all':
        zone_files = ['pboundary_front_n.zone', 'pboundary_back_s.zone', 'pboundary_left_w.zone', \
                        'pboundary_right_e.zone', 'pboundary_top.zone', 'pboundary_bottom.zone']
        face_names = ['north', 'south', 'west', 'east', 'top', 'bottom']
    else:
        if zone_file == '':
            error = 'ERROR: Please provide boundary zone filename!\n'
            sys.stderr.write(error)
            sys.exit(1)
        if face == '':
            error = 'ERROR: Please provide face name among: top, bottom, north, south, east, west !\n'
            sys.stderr.write(error)
            sys.exit(1)
        zone_files = [zone_file]
        face_names = [face]

    for iface, zone_file in enumerate(zone_files):
        face = face_names[iface]
        # Ex filename
        ex_file = zone_file.strip('zone') + 'ex'

        # Opening the input file
        print('--> Opening zone file: ', zone_file)
        fzone = open(zone_file, 'r')
        fzone.readline()
        fzone.readline()
        fzone.readline()

        # Read number of boundary nodes
        print('--> Calculating number of nodes')
        num_nodes = int(fzone.readline())
        Node_array = np.zeros(num_nodes, 'int')
        # Read the boundary node ids
        print('--> Reading boundary node ids')

        if (num_nodes < 10):
            g = fzone.readline()
            node_array = g.split()
            # Convert string to integer array
            node_array = [int(id) for id in node_array]
            Node_array = np.asarray(node_array)
        else:
            for i in range(int(num_nodes / 10 + (num_nodes % 10 != 0))):
                g = fzone.readline()
                node_array = g.split()
                # Convert string to integer array
                node_array = [int(id) for id in node_array]
                if (num_nodes - 10 * i < 10):
                    for j in range(num_nodes % 10):
                        Node_array[i * 10 + j] = node_array[j]
                else:
                    for j in range(10):
                        Node_array[i * 10 + j] = node_array[j]
        fzone.close()
        print('--> Finished with zone file')

        Boundary_cell_area = np.zeros(num_nodes, 'float')
        for i in range(num_nodes):
            Boundary_cell_area[
                i] = boundary_cell_area  # Fix the area to a large number

        print('--> Finished calculating boundary connections')
        boundary_cell_coord = [
            Cell_coord[Cell_id[i - 1] - 1] for i in Node_array
        ]
        epsilon = self.h * 10**-3

        if (face == 'top'):
            boundary_cell_coord = [[cell[0], cell[1], cell[2] + epsilon]
                                   for cell in boundary_cell_coord]
        elif (face == 'bottom'):
            boundary_cell_coord = [[cell[0], cell[1], cell[2] - epsilon]
                                   for cell in boundary_cell_coord]
        elif (face == 'north'):
            boundary_cell_coord = [[cell[0], cell[1] + epsilon, cell[2]]
                                   for cell in boundary_cell_coord]
        elif (face == 'south'):
            boundary_cell_coord = [[cell[0], cell[1] - epsilon, cell[2]]
                                   for cell in boundary_cell_coord]
        elif (face == 'east'):
            boundary_cell_coord = [[cell[0] + epsilon, cell[1], cell[2]]
                                   for cell in boundary_cell_coord]
        elif (face == 'west'):
            boundary_cell_coord = [[cell[0] - epsilon, cell[1], cell[2]]
                                   for cell in boundary_cell_coord]
        elif (face == 'well'):
            boundary_cell_coord = [[cell[0], cell[1], cell[2] + epsilon]
                                   for cell in boundary_cell_coord]
        elif (face == 'none'):
            boundary_cell_coord = [[cell[0], cell[1], cell[2]]
                                   for cell in boundary_cell_coord]
        else:
            error = 'ERROR: unknown face. Select one of: top, bottom, east, west, north, south.\n'
            sys.stderr.write(error)
            sys.exit(1)
        ## Write out ex files
        with open(ex_file, 'w') as f:
            f.write('CONNECTIONS\t%i\n' % Node_array.size)
            for idx, cell in enumerate(boundary_cell_coord):
                f.write(
                    f"{Node_array[idx]}\t{cell[0]:.12e}\t{cell[1]:.12e}\t{cell[2]:.12e}\t{Boundary_cell_area[idx]:.12e}\n"
                )

        print(
            f'--> Finished writing ex file {ex_file} corresponding to the zone file: {zone_file} \n'
        )
    print('--> Converting zone files to ex complete')


def write_perms_and_correct_volumes_areas(self):
    """ Write permeability values to perm_file, write aperture values to aper_file, and correct volume areas in uge_file 

    Parameters
    ----------
        self : object
            DFN Class

    Returns
    ---------
        None

    Notes
    ----------
    Calls executable correct_uge
    """
    if self.flow_solver != "PFLOTRAN":
        error = "ERROR! Wrong flow solver requested\n"
        sys.stderr.write(error)
        sys.exit(1)

    print("--> Writing Perms and Correct Volume Areas")
    if self.inp_file == '':
        error = 'ERROR: inp file must be specified!\n'
        sys.stderr.write(error)
        sys.exit(1)

    if self.uge_file == '':
        error = 'ERROR: uge file must be specified!\n'
        sys.stderr.write(error)
        sys.exit(1)

    if self.perm_file == '' and self.perm_cell_file == '':
        error = 'ERROR: perm file must be specified!\n'
        sys.stderr.write(error)
        sys.exit(1)

    if self.aper_file == '' and self.aper_cell_file == '':
        error = 'ERROR: aperture file must be specified!\n'
        sys.stderr.write(error)
        sys.exit(1)

    t = time()
    # Make input file for C UGE converter
    with open("convert_uge_params.txt", "w") as fp:
        fp.write(f"{self.inp_file}\n")
        fp.write(f"{self.mat_file}\n")
        fp.write(f"{self.uge_file}\n")
        fp.write(f"{self.uge_file[:-4]}_vol_area.uge\n")
        if self.aper_cell_file:
            fp.write(f"{self.aper_cell_file}\n")
            fp.write("1\n")
        else:
            fp.write(f"{self.aper_file}\n")
            fp.write("-1\n")

    ## dump aperture file
    self.dump_aperture(self.aper_file, format='fehm')
    ## execute convert uge C code
    cmd = os.environ['CORRECT_UGE_EXE'] + ' convert_uge_params.txt'
    failure = subprocess.call(cmd, shell=True)
    if failure > 0:
        error = 'ERROR: UGE conversion failed\nExiting Program\n'
        sys.stderr.write(error)
        sys.exit(1)
    elapsed = time() - t
    print(
        f'--> Time elapsed for UGE file conversion: {elapsed:0.3f} seconds\n')

    filename = 'dfn_properties.h5'
    print(f'--> Writing HDF5 File {filename}')

    if not self.cell:
        h5file = h5py.File(filename, mode='w')
        print('--> Beginning writing to HDF5 file')
        print('--> Allocating cell index array')
        iarray = np.zeros(self.num_nodes, '=i4')
        print('--> Writing cell indices')
        # add cell ids to file
        for i in range(self.num_nodes):
            iarray[i] = i + 1
        dataset_name = 'Cell Ids'
        h5dset = h5file.create_dataset(dataset_name, data=iarray)

        print('--> Allocating permeability array')
        perm = np.zeros(self.num_nodes, '=f8')

        print('--> Note: this script assumes isotropic permeability')
        perm = np.zeros(self.num_nodes, '=f8')
        # use material id index to assigned node based permeabilities
        for i in range(self.num_nodes):
            j = self.materialid[i] - 1
            perm[i] = self.perm[j]

        dataset_name = 'Permeability'
        h5dset = h5file.create_dataset(dataset_name, data=perm)

        h5file.close()
        print("--> Done writing permeability to h5 file")

    else:
        filename = 'dfn_properties.h5'
        h5file = h5py.File(filename, mode='w')

        print('--> Beginning writing to HDF5 file')
        print('--> Allocating cell index array')
        iarray = np.zeros(self.num_nodes, '=i4')
        print('--> Writing cell indices')
        # add cell ids to file
        for i in range(self.num_nodes):
            iarray[i] = i + 1
        dataset_name = 'Cell Ids'
        h5dset = h5file.create_dataset(dataset_name, data=iarray)
        print('--> Allocating permeability array')
        perm = np.zeros(self.num_nodes, '=f8')
        print('--> reading permeability data')
        print('--> Note: this script assumes isotropic permeability')
        f = open(self.perm_cell_file, 'r')
        f.readline()
        perm_list = []
        while True:
            h = f.readline()
            h = h.split()
            if h == []:
                break
            h.pop(0)
            perm_list.append(h)

        perm_list = [float(perm[0]) for perm in perm_list]

        dataset_name = 'Permeability'
        h5dset = h5file.create_dataset(dataset_name, data=perm_list)
        f.close()

        h5file.close()
        print('--> Done writing permeability to h5 file')


def pflotran(self, transient=False, restart=False, restart_file=''):
    """ Run PFLOTRAN. Copy PFLOTRAN run file into working directory and run with ncpus

    Parameters
    ----------
        self : object
            DFN Class
        transient : bool
            Boolean if PFLOTRAN is running in transient mode
        restart : bool
            Boolean if PFLOTRAN is restarting from checkpoint
        restart_file : string
            Filename of restart file

    Returns
    ----------
        None

    Notes
    ----------
    Runs PFLOTRAN Executable, see http://www.pflotran.org/ for details on PFLOTRAN input cards
    """
    if self.flow_solver != "PFLOTRAN":
        error = "ERROR! Wrong flow solver requested\n"
        sys.stderr.write(error)
        sys.exit(1)

    try:
        shutil.copy(os.path.abspath(self.dfnFlow_file),
                    os.path.abspath(os.getcwd()))
    except:
        error = "--> ERROR!! Unable to copy PFLOTRAN input file\n"
        sys.stderr.write(error)
        sys.exit(1)

    print("=" * 80)
    print("--> Running PFLOTRAN")

    mpirun = os.environ['PETSC_DIR'] + '/' + os.environ[
        'PETSC_ARCH'] + '/bin/mpirun'
    if not (os.path.isfile(mpirun) and os.access(mpirun, os.X_OK)):
        # PETSc did not install MPI. Hopefully, the user has their own MPI.
        mpirun = 'mpirun'

    cmd = mpirun + ' -np ' + str(self.ncpu) + \
          ' ' + os.environ['PFLOTRAN_EXE'] + ' -pflotranin ' + self.local_dfnFlow_file

    print("Running: %s" % cmd)
    subprocess.call(cmd, shell=True)

    if restart:
        try:
            shutil.copy(os.path.abspath(restart_file),
                        os.path.abspath(os.getcwd()))
        except:
            error = "--> ERROR!! Unable to copy PFLOTRAN restart input file\n"
            sys.stderr.write(error)
            sys.exit(1)

        print("=" * 80)
        print("--> Running PFLOTRAN")
        cmd = os.environ['PETSC_DIR']+'/'+os.environ['PETSC_ARCH']+'/bin/mpirun -np ' + str(self.ncpu) + \
              ' ' + os.environ['PFLOTRAN_EXE'] + ' -pflotranin ' + ntpath.basename(restart_file)
        print("Running: %s" % cmd)
        subprocess.call(cmd, shell=True)

    print('=' * 80)
    print("--> Running PFLOTRAN Complete")
    print('=' * 80)
    print("\n")


def pflotran_cleanup(self, index_start=0, index_finish=1, filename=''):
    """pflotran_cleanup
    Concatenate PFLOTRAN output files and then delete them 
    
    Parameters
    -----------
        self : object 
            DFN Class
        index : int
             If PFLOTRAN has multiple dumps use this to pick which dump is put into cellinfo.dat and darcyvel.dat
    Returns 
    ----------
        None

    Notes
    ----------
        Can be run in a loop over all pflotran dumps
    """
    if self.flow_solver != "PFLOTRAN":
        error = "ERROR! Wrong flow solver requested\n"
        sys.stderr.write(error)
        sys.exit(1)

    if filename == '':
        filename = self.local_dfnFlow_file[:-3]
    else:
        filename = ntpath.basename(filename[:-3])

    print('--> Processing PFLOTRAN output')

    for index in range(index_start, index_finish + 1):
        cmd = 'cat ' + filename + '-cellinfo-%03d-rank*.dat > cellinfo_%03d.dat' % (
            index, index)
        print("Running >> %s" % cmd)
        subprocess.call(cmd, shell=True)

        cmd = 'cat ' + filename + '-darcyvel-%03d-rank*.dat > darcyvel_%03d.dat' % (
            index, index)
        print("Running >> %s" % cmd)
        subprocess.call(cmd, shell=True)

        #for fl in glob.glob(self.local_dfnFlow_file[:-3]+'-cellinfo-000-rank*.dat'):
        #    os.remove(fl)
        #for fl in glob.glob(self.local_dfnFlow_file[:-3]+'-darcyvel-000-rank*.dat'):
        #    os.remove(fl)

        for fl in glob.glob(filename + '-cellinfo-%03d-rank*.dat' % index):
            os.remove(fl)
        for fl in glob.glob(filename + '-darcyvel-%03d-rank*.dat' % index):
            os.remove(fl)
    try:
        os.symlink("darcyvel_%03d.dat" % index_finish, "darcyvel.dat")
    except:
        print("--> WARNING!!! Unable to create symlink for darcyvel.dat")
    try:
        os.symlink("cellinfo_%03d.dat" % index_finish, "cellinfo.dat")
    except:
        print("--> WARNING!!! Unable to create symlink for cellinfo.dat")


def parse_pflotran_vtk_python(self, grid_vtk_file=''):
    """ Adds CELL_DATA to POINT_DATA in the VTK output from PFLOTRAN.
    Parameters
    ----------
        self : object 
            DFN Class
        grid_vtk_file : string
            Name of vtk file with mesh. Typically local_dfnFlow_file.vtk

    Returns
    --------
        None

    Notes
    --------
    If DFN class does not have a vtk file, inp2vtk_python is called
    """
    print('--> Parsing PFLOTRAN output with Python')

    if self.flow_solver != "PFLOTRAN":
        error = "ERROR! Wrong flow solver requested\n"
        sys.stderr.write(error)
        sys.exit(1)

    if grid_vtk_file:
        self.vtk_file = grid_vtk_file
    else:
        self.inp2vtk_python()

    grid_file = self.vtk_file

    files = glob.glob('*-[0-9][0-9][0-9].vtk')
    files.sort()

    with open(grid_file, 'r') as f:
        grid = f.readlines()[3:]

    out_dir = 'parsed_vtk'

    for line in grid:
        if 'POINTS' in line:
            num_cells = line.strip(' ').split()[1]

    for file in files:
        print(f"--> Processing file: {file}")
        with open(file, 'r') as f:
            pflotran_out = f.readlines()[4:]
        pflotran_out = [
            w.replace('CELL_DATA', 'POINT_DATA ') for w in pflotran_out
        ]
        header = [
            '# vtk DataFile Version 2.0\n', 'PFLOTRAN output\n', 'ASCII\n'
        ]
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
        os.remove(file)
    print('--> Parsing PFLOTRAN output complete')
