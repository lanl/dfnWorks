"""
functions for using pflotran in dfnworks
"""
import os
import subprocess
import h5py
import glob
import shutil
import ntpath
import re
from time import time
import numpy as np
from pathlib import Path



def lagrit2pflotran(self, dim=3, boundary_cell_area=None):
    """Take output from LaGriT and process it for use in PFLOTRAN.

    Calls :func:`zone2ex`, :func:`dump_h5_files`, and :func:`correct_uge_file`,
    forwarding ``dim`` to the latter.

    Parameters
    ----------
        self : object
            DFN Class.
        dim : int
            Problem dimension, ``3`` (default) or ``2``, forwarded to
            :func:`correct_uge_file`.
        boundary_cell_area : double
            Boundary cell area. Defaults to ``None``, in which case ``1 / self.h``
            is used.

    Returns
    -------
        None

    Notes
    -----
        ``correct_uge_file`` sets ``self.uge_file`` to the active mesh, so it does
        not need to be assigned manually after this call.
    """
    if self.flow_solver != "PFLOTRAN":
        self.print_log("Error. Wrong flow solver requested\n", "error")

    self.print_log("=" * 80)
    self.print_log("Starting conversion of files for PFLOTRAN ")

    if self.inp_file == "":
        self.print_log("Error: inp filename not attached to object\n", "error")

    self.uge_file = self.inp_file[:-4] + ".uge"
    if not os.path.isfile(self.uge_file):
        self.print_log("Error. Cannot find uge file\nExiting\n", "error")

    if not boundary_cell_area:
        boundary_cell_area = 1 / self.h

    self.zone2ex(zone_file="all", boundary_cell_area=boundary_cell_area)
    self.dump_h5_files()
    self.correct_uge_file(dim=dim)

    self.print_log("Conversion of files for PFLOTRAN complete")
    self.print_log("=" * 80)


def zone2ex(self, zone_file='', face='', boundary_cell_area=1.e-1):
    """
    Convert zone files from LaGriT into ex format for LaGriT
    
    Parameters
    -----------
        self : object
            DFN Class
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
    self.print_log('*' * 80)
    self.print_log('--> Converting zone files to ex')

    if self.uge_file == '':
        error = 'Error: uge filename not assigned to object yet'
        self.print_log(error, 'error')
    # Opening uge file
    self.print_log('--> Opening uge file')
    with open(self.uge_file, 'r') as fuge:
        # Reading cell ids, cells centers and cell volumes
        line = fuge.readline()
        line = line.split()
        num_cells = int(line[1])

        cell_id = np.zeros(num_cells, 'int')
        cell_coord = np.zeros((num_cells, 3), 'float')
        cell_vol = np.zeros(num_cells, 'float')

        for cells in range(num_cells):
            line = fuge.readline()
            line = line.split()
            cell_id[cells] = int(line.pop(0))
            line = [float(id) for id in line]
            cell_vol[cells] = line.pop(3)
            cell_coord[cells] = line

    self.print_log('--> Finished processing uge file\n')

    # loop through zone files
    if zone_file == 'all':
        zone_files = ['boundary_front_n.zone', 'boundary_back_s.zone', 'boundary_left_w.zone', 'boundary_right_e.zone', 'boundary_top.zone', 'boundary_bottom.zone']
        face_names = ['north', 'south', 'west', 'east', 'top', 'bottom']
    else:
        if zone_file == '':
            error = 'Error: Please provide boundary zone filename!\n'
            self.print_log(error, 'error')
        if face == '':
            error = 'Error: Please provide face name among: top, bottom, north, south, east, west !\n'
            self.print_log(error, 'error')
        zone_files = [zone_file]
        face_names = [face]

    for iface, zone_file in enumerate(zone_files):
        face = face_names[iface]
        # Ex filename
        ex_file = zone_file.strip('zone') + 'ex'

        # Opening the input file
        self.print_log(f'--> Opening zone file: {zone_file}')
        with open(zone_file, 'r') as fzone:
            self.print_log('--> Reading boundary node ids')
            node_array = fzone.read()
            node_array = node_array.split()
            num_nodes = int(node_array[4])
            node_array = np.array(node_array[5:-1], dtype='int')
        self.print_log('--> Finished reading zone file')

        Boundary_cell_area_array = np.zeros(num_nodes, 'float')
        for i in range(num_nodes):
            Boundary_cell_area_array[
                i] = boundary_cell_area  # Fix the area to a large number

        self.print_log('--> Finished calculating boundary connections')
        boundary_cell_coord = [
            cell_coord[cell_id[i - 1] - 1] for i in node_array
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
            error = f'Error: Unknown face provided: {face}. Select one of: top, bottom, east, west, north, south, none'
            self.print_log(error, 'error')
        ## Write out ex files
        with open(ex_file, 'w') as f:
            f.write('CONNECTIONS\t%i\n' % node_array.size)
            for idx, cell in enumerate(boundary_cell_coord):
                f.write(
                    f"{node_array[idx]}\t{cell[0]:.12e}\t{cell[1]:.12e}\t{cell[2]:.12e}\t{Boundary_cell_area_array[idx]:.12e}\n"
                )

        self.print_log(
            f'--> Finished writing ex file {ex_file} corresponding to the zone file: {zone_file} \n'
        )

    self.print_log('--> Converting zone files to ex complete')
    self.print_log('*' * 80)

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
    self.print_log('*' * 80)
    self.print_log("--> Correcting UGE file: Starting")
    if self.flow_solver != "PFLOTRAN":
        error = "Error. Wrong flow solver requested\n"
        self.print_log(error,'error')

    self.print_log("--> Writing Perms and Correct Volume Areas")
    if self.inp_file == '':
        error = 'Error. inp file must be specified.\n'
        self.print_log(error,'error')

    if self.uge_file == '':
        error = 'Error. uge file must be specified.\n'
        self.print_log(error,'error')

    if self.perm_file == '' and self.perm_cell_file == '':
        error = 'Error. perm file must be provide.'
        self.print_log(error,'error')

    if self.aper_file == '' and self.aper_cell_file == '':
        error = 'Error. aperture file must be specified.'
        self.print_log(error,'error')


    # self.print_log("--> Correcting UGE file: Complete")
    # self.print_log('*' * 80)
    # correct_volume_file = os.path.join(self.jobname, "correct_volumes_logfile.log")
    # if os.path.exists(correct_volume_file):
    #     self.print_log(f"--> Printing correct volumes output file:")
    #     self.print_log(f"filename: {correct_volume_file}")
    #     try:
    #         with open(correct_volume_file, 'r') as file:
    #             for line in file:
    #                 self.print_log(line.strip())
    #     except FileNotFoundError:
    #         self.print_log(f"File not found: {correct_volume_file}")
    #     except Exception as e:
    #         self.print_log(f"An error occurred: {e}")

def dump_h5_files(self):
    """ Write permeability values to cell ids and permeability values to dfn_properties.h5 file for pflotran. 

    Parameters
    ----------
        self : object
            DFN Class

    Returns
    ---------
        None

    Notes
    ----------
        Hydraulic properties need to attached to the class prior to running this function. Use DFN.assign_hydraulic_properties() to do so. 
    """
    self.print_log('*' * 80)
    self.print_log("--> Dumping h5 file")
    filename = 'dfn_properties.h5'
    self.print_log(f'--> Opening HDF5 File {filename}')
    with h5py.File(filename, mode='w') as h5file:
        self.print_log('--> Allocating cell index array')
        self.print_log('--> Writing cell indices')
        iarray = np.arange(1, self.num_nodes + 1)
        dataset_name = 'Cell Ids'
        h5dset = h5file.create_dataset(dataset_name, data=iarray)
        self.print_log('--> Creating permeability array')
        self.print_log('--> Note: This script assumes isotropic permeability')
        if self.cell_based_aperture: 
            self.perm_cell = np.genfromtxt(self.perm_cell_file, skip_header = 1)[:,1]
        else: 
            for i in range(self.num_nodes):
                self.perm_cell[i] = self.perm[self.material_ids[i] - 1]
        self.print_log('--> Writting Permeability')
        dataset_name = 'Permeability'
        h5dset = h5file.create_dataset(dataset_name, data=self.perm_cell)

    self.print_log("--> Done writting h5 file")
    self.print_log('*' * 80)

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
        error = "Error! Wrong flow solver requested\n"
        self.print_log(error, 'error')

    try:
        shutil.copy(os.path.abspath(self.dfnFlow_file),
                    os.path.abspath(os.getcwd()))
    except:
        error = "--> Error. Unable to copy PFLOTRAN input file\n"
        self.print_log(error, 'error')

    self.print_log("=" * 80)
    self.print_log("--> Running PFLOTRAN")

    mpirun = os.environ['PETSC_DIR'] + '/' + os.environ[
        'PETSC_ARCH'] + '/bin/mpirun'

    if not (os.path.isfile(mpirun) and os.access(mpirun, os.X_OK)):
        # PETSc did not install MPI. Hopefully, the user has their own MPI.
        mpirun = 'mpirun'

    cmd = mpirun + ' -np ' + str(self.ncpu) + \
          ' ' + os.environ['PFLOTRAN_EXE'] + ' -pflotranin ' + self.local_dfnFlow_file

    self.print_log(f"--> Running: {cmd}")
    subprocess.call(cmd, shell=True)

    if restart:
        try:
            shutil.copy(os.path.abspath(restart_file),
                        os.path.abspath(os.getcwd()))
        except:
            error = "--> ERROR!! Unable to copy PFLOTRAN restart input file\n"
            self.print_log(error, 'error')

        self.print_log("=" * 80)
        self.print_log("--> Running PFLOTRAN")
        cmd = os.environ['PETSC_DIR']+'/'+os.environ['PETSC_ARCH']+'/bin/mpirun -np ' + str(self.ncpu) + \
              ' ' + os.environ['PFLOTRAN_EXE'] + ' -pflotranin ' + ntpath.basename(restart_file)
        self.print_log("Running: %s" % cmd)
        subprocess.call(cmd, shell=True)

    self.print_log('=' * 80)
    self.print_log("--> Running PFLOTRAN Complete")
    self.print_log('=' * 80)
    self.print_log("\n")


def pflotran_cleanup(self, index_start=0, index_finish=1, filename=''):
    """pflotran_cleanup
    Concatenate PFLOTRAN output files and then delete them 
    
    Parameters
    -----------
        self : object 
            DFN Class
        index : int
             If PFLOTRAN has multiple dumps use this to pick which dump is put into cellinfo.dat and darcyvel.dat
        filename : string
            name of file to be concatenated
    Returns 
    ----------
        None

    Notes
    ----------
        Can be run in a loop over all pflotran dumps
    """
    if self.flow_solver != "PFLOTRAN":
        error = "Error. Wrong flow solver requested\n"
        self.print_log(error, 'error')

    if filename == '':
        filename = self.local_dfnFlow_file[:-3]
    else:
        filename = ntpath.basename(filename[:-3])

    self.print_log('--> Processing PFLOTRAN output')

    for index in range(index_start, index_finish + 1):
        cmd = 'cat ' + filename + '-cellinfo-%03d-rank*.dat > cellinfo_%03d.dat' % (
            index, index)
        self.print_log("Running >> %s" % cmd)
        subprocess.call(cmd, shell=True)

        cmd = 'cat ' + filename + '-darcyvel-%03d-rank*.dat > darcyvel_%03d.dat' % (
            index, index)
        self.print_log(f"--> Running >> {cmd}")
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
        self.print_log("--> Warning. Unable to create symlink for darcyvel.dat", 'warning')
    try:
        os.symlink("cellinfo_%03d.dat" % index_finish, "cellinfo.dat")
    except:
        self.print_log("--> Warning. Unable to create symlink for cellinfo.dat")


# Directory that receives the converted PFLOTRAN output (.vtu files + .pvd)
PFLOTRAN_VTU_DIR = 'pflotran_vtu_outputs'

# PFLOTRAN time units -> seconds
_TIME_UNITS_TO_SECONDS = {
    's': 1.0, 'sec': 1.0, 'second': 1.0, 'seconds': 1.0,
    'min': 60.0, 'minute': 60.0, 'minutes': 60.0,
    'h': 3600.0, 'hr': 3600.0, 'hour': 3600.0, 'hours': 3600.0,
    'd': 86400.0, 'day': 86400.0, 'days': 86400.0,
    'w': 604800.0, 'wk': 604800.0, 'week': 604800.0, 'weeks': 604800.0,
    'mo': 2629800.0, 'month': 2629800.0, 'months': 2629800.0,
    'y': 31557600.0, 'yr': 31557600.0, 'year': 31557600.0, 'years': 31557600.0,
}

_SNAPSHOT_NAME = re.compile(r'^(?P<base>.+?)(?P<vel>-vel)?-(?P<idx>\d+)\.vtk$')
_STEP_TIME = re.compile(r'^\s*Step\s+\d+\s+Time=\s*(?P<value>\S+).*\[(?P<unit>[A-Za-z]+)\]')
_VTK_WRITE = re.compile(r'write vtk output file:\s*(?P<name>\S+)')


def _time_to_seconds(value, unit):
    """ Convert a PFLOTRAN time value and unit (e.g. 1.0e2, 'd') to seconds.
    Unknown units are returned unconverted. """
    factor = _TIME_UNITS_TO_SECONDS.get(unit.strip().lower())
    return float(value) * factor if factor else float(value)


def _pflotran_snapshot_times(out_file):
    """ Read the simulation time of every VTK snapshot from a PFLOTRAN log.

    PFLOTRAN writes ``Step N Time= X ... [unit]`` after each time step and
    ``--> write vtk output file: <name>`` whenever it writes a snapshot. Each
    snapshot gets the time of the most recent step before it, or 0 for
    snapshots written before the first step (the initial condition).

    Parameters
    ----------
        out_file : string
            PFLOTRAN screen/log output, normally ``<base>.out``.

    Returns
    -------
        times : dict
            ``{vtk file name: time in seconds}``. Empty if the file is missing.
    """
    times = {}
    if not os.path.isfile(out_file):
        return times
    current = 0.0
    with open(out_file, 'r', errors='replace') as f:
        for line in f:
            m = _STEP_TIME.match(line)
            if m:
                try:
                    current = _time_to_seconds(m.group('value'), m.group('unit'))
                except ValueError:
                    pass
                continue
            m = _VTK_WRITE.search(line)
            if m:
                times[m.group('name')] = current
    return times


def _read_pflotran_vtk_fields(vtk_file, num_values):
    """ Read the SCALARS and VECTORS blocks of a PFLOTRAN legacy VTK file.

    PFLOTRAN writes cell data for its control volumes, which are the nodes of
    the DFN mesh, so each field has one value (or vector) per mesh node.

    Parameters
    ----------
        vtk_file : string
            PFLOTRAN output file, e.g. ``dfn_explicit-001.vtk``.
        num_values : int
            Number of mesh nodes.

    Returns
    -------
        fields : dict
            ``{name: array}``; scalars have shape (n,), vectors (n, 3).
    """
    with open(vtk_file, 'r') as f:
        tokens = f.read().split()
    fields = {}
    i = 0
    while i < len(tokens):
        keyword = tokens[i]
        if keyword in ('SCALARS', 'VECTORS'):
            name, dtype = tokens[i + 1], tokens[i + 2]
            i += 3
            if keyword == 'SCALARS':
                # optional number of components, then optional LOOKUP_TABLE
                if i < len(tokens) and tokens[i].isdigit():
                    i += 1
                if i < len(tokens) and tokens[i] == 'LOOKUP_TABLE':
                    i += 2
                count, shape = num_values, (num_values, )
            else:
                count, shape = 3 * num_values, (num_values, 3)
            values = np.asarray(tokens[i:i + count], dtype=np.float64)
            if values.size != count:
                raise ValueError(f"{vtk_file}: field {name} has {values.size} values, expected {count}")
            if dtype.lower() in ('int', 'long', 'short', 'char', 'unsigned_int'):
                values = values.astype(np.int64)
            fields[name] = values.reshape(shape)
            i += count
        else:
            i += 1
    return fields


def parse_pflotran_vtk(self, binary=True):
    """ Convert PFLOTRAN VTK output into XML VTK (.vtu) files and a ParaView time series (.pvd).

    Parameters
    ----------
        self : object
            DFN Class

        binary : bool
            If True (default), data arrays are base64-encoded binary. If False,
            they are written as ASCII.

    Returns
    --------
        None

    Notes
    --------
        - PFLOTRAN writes ``<base>-NNN.vtk`` files that contain only cell data
          for its control volumes, which are the nodes of the DFN mesh. Each
          snapshot is written to ``pflotran_vtu_outputs/<base>-NNN.vtu`` with
          the mesh from ``self.inp_file`` and the PFLOTRAN fields as point
          data (plus the fracture ``material_id`` as cell data). Velocity files
          (``<base>-vel-NNN.vtk``) are merged into the matching snapshot.
        - ``pflotran_vtu_outputs/<base>.pvd`` lists the snapshots with their
          simulation times in seconds, read from the PFLOTRAN log
          ``<base>.out``. If the log is missing, the snapshot number is used.
          Open the ``.pvd`` file in ParaView.
        - The original PFLOTRAN ``.vtk`` files are removed.
    """
    from pydfnworks.general.vtu_io import read_inp_mesh, write_vtu, write_pvd

    self.print_log('--> Converting PFLOTRAN VTK output to VTU/PVD')
    if self.flow_solver != "PFLOTRAN":
        self.print_log("Error. Wrong flow solver requested\n", 'error')

    base = Path(self.local_dfnFlow_file).stem
    snapshots = {}
    for name in sorted(glob.glob(f"{base}*.vtk")):
        m = _SNAPSHOT_NAME.match(name)
        if not m or m.group('base') != base:
            continue
        snapshots.setdefault(int(m.group('idx')), []).append(name)
    if not snapshots:
        self.print_log(f"--> Warning. No PFLOTRAN VTK files matching {base}-NNN.vtk found", 'warning')
        return

    mesh = read_inp_mesh(self.inp_file)
    num_points = mesh['points'].shape[0]

    times = _pflotran_snapshot_times(f"{base}.out")
    if not times:
        self.print_log(f"--> Warning. {base}.out not found; using snapshot numbers as times in the .pvd file", 'warning')

    os.makedirs(PFLOTRAN_VTU_DIR, exist_ok=True)
    collection = []
    for idx in sorted(snapshots):
        point_data = {}
        for vtk_file in snapshots[idx]:
            self.print_log(f"--> Processing file: {vtk_file}")
            point_data.update(_read_pflotran_vtk_fields(vtk_file, num_points))
        vtu_name = f"{base}-{idx:03d}.vtu"
        write_vtu(os.path.join(PFLOTRAN_VTU_DIR, vtu_name), mesh, point_data=point_data, binary=binary)
        main_file = f"{base}-{idx:03d}.vtk"
        collection.append((times.get(main_file, float(idx)), vtu_name))
        for vtk_file in snapshots[idx]:
            os.remove(vtk_file)

    pvd_file = os.path.join(PFLOTRAN_VTU_DIR, f"{base}.pvd")
    write_pvd(pvd_file, collection)
    self.print_log(f"--> Wrote {len(collection)} snapshots to {PFLOTRAN_VTU_DIR}/; open {pvd_file} in ParaView")
    self.print_log('--> Converting PFLOTRAN VTK output complete')


def parse_pflotran_vtk_python(self, grid_vtk_file=''):
    """ Deprecated. Use :func:`parse_pflotran_vtk`, which writes XML ``.vtu``
    files and a ``.pvd`` time series to ``pflotran_vtu_outputs/``.

    Parameters
    ----------
        self : object
            DFN Class
        grid_vtk_file : string
            Ignored. The mesh is read from ``self.inp_file``.

    Returns
    --------
        None
    """
    self.print_log("--> parse_pflotran_vtk_python is deprecated and now writes .vtu/.pvd files to "
                   f"{PFLOTRAN_VTU_DIR}/. Use DFN.parse_pflotran_vtk() instead.", 'warning')
    if grid_vtk_file:
        self.print_log("--> grid_vtk_file is ignored; the mesh is read from the .inp file", 'warning')
    self.parse_pflotran_vtk()


def _parse_time_group(group_name):
    """ Parse a PFLOTRAN HDF5 time group name.

    PFLOTRAN writes top-level groups like ``'   1 Time  1.00000E+02 d'``.

    Returns
    -------
        (index, time in seconds), or None if the name is not a time group.
    """
    tokens = group_name.strip().split()
    try:
        idx = int(tokens[0])
    except (ValueError, IndexError):
        return None
    seconds = float(idx)
    if len(tokens) >= 3 and tokens[1].lower() == 'time':
        try:
            seconds = _time_to_seconds(tokens[2], tokens[3] if len(tokens) > 3 else 's')
        except ValueError:
            pass
    return idx, seconds


def parse_pflotran_h5(self, h5_file='', binary=True, grid_vtk_file=''):
    """ Convert PFLOTRAN HDF5 output into XML VTK (.vtu) files and a ParaView time series (.pvd).

    Parameters
    ----------
        self : object
            DFN Class
        h5_file : string
            Path to the PFLOTRAN HDF5 output file. If empty, defaults to
            ``<local_dfnFlow_file stem>.h5`` in the current directory.
        binary : bool
            If True (default), data arrays are base64-encoded binary. If False,
            they are written as ASCII.
        grid_vtk_file : string
            Deprecated and ignored. The mesh is read from ``self.inp_file``.

    Returns
    --------
        None

    Notes
    --------
        - Each time group of the HDF5 file (e.g. ``'   1 Time  1.00000E+02 d'``)
          becomes ``pflotran_vtu_outputs/<base>-NNN.vtu``. Every dataset with one
          value per mesh node is written as point data; datasets with three
          values per node are written as vectors. Others are skipped.
        - ``pflotran_vtu_outputs/<base>.pvd`` lists the snapshots with the
          times from the group names, converted to seconds.
    """
    from pydfnworks.general.vtu_io import read_inp_mesh, write_vtu, write_pvd

    self.print_log('--> Converting PFLOTRAN HDF5 output to VTU/PVD')
    if self.flow_solver != "PFLOTRAN":
        self.print_log("Error. Wrong flow solver requested\n", 'error')
    if grid_vtk_file:
        self.print_log("--> grid_vtk_file is deprecated and ignored; the mesh is read from the .inp file", 'warning')

    if not h5_file:
        h5_file = f"{Path(self.local_dfnFlow_file).stem}.h5"
    if not os.path.exists(h5_file):
        self.print_log(f"PFLOTRAN HDF5 file not found: {h5_file}", 'error')
    self.print_log(f"--> Reading HDF5 data from {h5_file}")

    mesh = read_inp_mesh(self.inp_file)
    num_points = mesh['points'].shape[0]
    base = Path(self.local_dfnFlow_file).stem
    os.makedirs(PFLOTRAN_VTU_DIR, exist_ok=True)

    collection = []
    with h5py.File(h5_file, 'r') as h5:
        time_groups = []
        for name in h5.keys():
            if not isinstance(h5[name], h5py.Group):
                continue
            parsed = _parse_time_group(name)
            if parsed is not None:
                time_groups.append((parsed[0], parsed[1], name))
        time_groups.sort(key=lambda x: x[0])
        if not time_groups:
            self.print_log(f"No PFLOTRAN time-step groups found in {h5_file}", 'error')

        for idx, seconds, group_name in time_groups:
            group = h5[group_name]
            point_data = {}
            for dset_name in group.keys():
                dset = group[dset_name]
                if not isinstance(dset, h5py.Dataset):
                    continue
                values = np.asarray(dset[()])
                if values.size == num_points:
                    point_data[dset_name] = values.ravel()
                elif values.size == 3 * num_points:
                    point_data[dset_name] = values.reshape(num_points, 3)
                else:
                    self.print_log(f"Skipping '{dset_name}' in time group {idx}: "
                                   f"size {values.size} does not match {num_points} mesh points")
            vtu_name = f"{base}-{idx:03d}.vtu"
            self.print_log(f"--> Writing {PFLOTRAN_VTU_DIR}/{vtu_name}")
            write_vtu(os.path.join(PFLOTRAN_VTU_DIR, vtu_name), mesh, point_data=point_data, binary=binary)
            collection.append((seconds, vtu_name))

    pvd_file = os.path.join(PFLOTRAN_VTU_DIR, f"{base}.pvd")
    write_pvd(pvd_file, collection)
    self.print_log(f"--> Wrote {len(collection)} snapshots to {PFLOTRAN_VTU_DIR}/; open {pvd_file} in ParaView")
    self.print_log('--> Converting PFLOTRAN HDF5 output complete')

