"""
.. module:: mesh_dfn_helper.py
   :synopsis: helper functions for meshing DFN using LaGriT  
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""
import os
import sys
import glob
import shutil
import numpy as np
import subprocess
import pyvtk as pv


def edit_intersection_files(num_poly, fracture_list, path):
    """ If pruning a DFN, this function walks through the intersection files
    and removes references to files that are not included in the 
    fractures that will remain in the network.
 
    Parameters
    ---------
        num_poly : int 
            Number of Fractures in the original DFN
        fracture_list :list of int
            List of fractures to keep in the DFN

    Returns
    -------
        None

    Notes
    -----
    1. Currently running in serial, but it could be parallelized
    2. Assumes the pruning directory is not the original directory

    """
    # Make list of connectivity.dat
    connectivity = []
    with open(path + "/dfnGen_output/connectivity.dat", "r") as fp:
        for i in range(num_poly):
            tmp = []
            line = fp.readline()
            line = line.split()
            for frac in line:
                tmp.append(int(frac))
            connectivity.append(tmp)

    fractures_to_remove = list(
        set(range(1, num_poly + 1)) - set(fracture_list))

    cwd = os.getcwd()
    if os.path.isdir('intersections'):
        os.unlink('intersections')
        os.mkdir('intersections')
    else:
        os.mkdir('intersections')

    os.chdir('intersections')

    ## DEBUGGING ##
    # clean up directory
    #fl_list = glob.glob("*prune.inp")
    #for fl in fl_list:
    #   os.remove(fl)
    ## DEBUGGING ##

    print("--> Editing Intersection Files")
    ## Note this could be easily changed to run in parallel if needed. Just use cf
    for i in fracture_list:
        filename = f'intersections_{i}.inp'
        print(f'--> Working on: {filename}')
        intersecting_fractures = connectivity[i - 1]
        pull_list = list(
            set(intersecting_fractures).intersection(set(fractures_to_remove)))
        if len(pull_list) > 0:
            # Create Symlink to original intersection file
            os.symlink(path + 'intersections/' + filename, filename)
            # Create LaGriT script to remove intersections with fractures not in prune_file
            lagrit_script = f"""
read / {filename} / mo1 
pset / pset2remove / attribute / b_a / 1,0,0 / eq / {pull_list[0]}
"""
            for j in pull_list[1:]:
                lagrit_script += f'''
pset / prune / attribute / b_a / 1,0,0 / eq / {j}
pset / pset2remove / union / pset2remove, prune
rmpoint / pset, get, prune
pset / prune / delete
     '''
            lagrit_script += f'''
rmpoint / pset, get, pset2remove 
rmpoint / compress
    
cmo / modatt / mo1 / imt / ioflag / l
cmo / modatt / mo1 / itp / ioflag / l
cmo / modatt / mo1 / isn / ioflag / l
cmo / modatt / mo1 / icr / ioflag / l
    
cmo / status / brief
dump / intersections_{i}_prune.inp / mo1
finish

'''

            lagrit_filename = 'prune_intersection.lgi'
            f = open(lagrit_filename, 'w')
            f.write(lagrit_script)
            f.flush()
            f.close()
            mh.run_lagrit_script("prune_intersection.lgi",
                                 f"out_{i}.txt",
                                 quiet=True)
            os.remove(filename)
            move(f"intersections_{i}_prune.inp", f"intersections_{i}.inp")
        else:
            try:
                copy(path + 'intersections/' + filename, filename)
            except:
                pass
    os.chdir(cwd)


def check_dudded_points(dudded, hard=False):
    """Parses LaGrit log_merge_all.out and checks if number of dudded points is the expected number

    Parameters
    ---------
        dudded : int 
            Expected number of dudded points from params.txt
        hard : bool
            If hard is false, up to 1% of nodes in the mesh can be missed. If hard is True, no points can be missed. 
    Returns
    ---------
        True/False : bool
            True if the number of dudded points is correct and  False if the number of dudded points is incorrect 
    
    Notes
    -----
    If number of dudded points is incorrect by over 1%, program will exit. 

    """
    print("--> Checking that number of dudded points is correct\n")
    with open("lagrit_logs/log_merge_all.out", "r") as fp:
        for line in fp.readlines():
            if 'Dudding' in line:
                print(f'--> From LaGriT: {line}')
                try:
                    pts = int(line.split()[1])
                except:
                    pts = int(line.split()[-1])
            if 'RMPOINT:' in line:
                print(f'--> From LaGriT: {line}')
                total_points = int(line.split()[-1])
                break

    diff = abs(dudded - pts)
    print(f"--> Expected Number of dudded points: {dudded}")
    print(f"--> Actual Number of dudded points: {pts}")
    print(f"--> Difference between expected and actual dudded points: {diff}")
    if diff == 0:
        print('--> The correct number of points were removed. Onward!\n')
        return True
    elif diff > 0:
        ## compare with total number poins
        print(
            '--> WARNING!!! Number of points removed does not match the expected value'
        )
        diff_ratio = 100 * (float(diff) / float(total_points))
        if diff_ratio < 0.01 and hard == False:
            print(f"--> However value is small: {diff}")
            print("--> Proceeding\n")
            return True
        else:
            print('ERROR! Incorrect Number of points removed')
            print(f"Over 0.01% of nodes removed. Value is {diff_ratio:.2f}")
            return False


def gather_mesh_information(self):
    """ Prints information about the final mesh to file
    
    Parameters
    ----------
        local_jobname : string
            Name of current DFN job (not path) 
    visual_mode : bool
        Determines is reduced_mesh or full_mesh is dumped

    Returns
    -------
        None
   
    Notes
    -----
        None 
"""

    if self.visual_mode:
        with open('reduced_mesh.inp', 'r') as finp:
            header = finp.readline()
            header = header.split()
            self.num_nodes = int(header[0])
        print(
            f"--> The reduced mesh in full_mesh.inp has {self.num_nodes} nodes and {int(header[1])} triangular elements"
        )
    else:
        with open('full_mesh.inp', 'r') as finp:
            header = finp.readline()
            header = header.split()
            self.num_nodes = int(header[0])
        print(
            f"--> The primary mesh in full_mesh.inp has {self.num_nodes} nodes and {int(header[1])} triangular elements"
        )
        ## get material -ids
        self.material_ids = np.genfromtxt('materialid.dat',
                                          skip_header=3).astype(int)
        self.aperture_cell = np.zeros(self.num_nodes)
        self.perm_cell = np.zeros(self.num_nodes)


def clean_up_files_after_prune(self):
    ''' After pruning a DFN to only include the fractures in prune_file this function removes references to those fractures from params.txt, perm.dat, aperature.dat, and poly_info.dat 
    
    Parameters
    ----------
        self : DFN object
         
    Returns
    -------
        None

    Notes
    -----
        This function should always be run after pruning if flow solution is going to be run. 
 
    '''

    print("--> Editing DFN file based on fractures in %s" % self.prune_file)
    keep_list = np.sort(np.genfromtxt(self.prune_file).astype(int))
    num_frac = len(keep_list)

    print("--> Editing params.txt file")
    fin = open(self.path + '/params.txt')
    try:
        os.unlink('params.txt')
    except:
        pass
    fout = open('params.txt', 'w')
    line = fin.readline()
    fout.write('%d\n' % num_frac)
    for i in range(7):
        line = fin.readline()
        fout.write(line)
    fin.close()
    fout.close()
    print("--> Complete")

    print("--> Editing poly_info.dat file")
    poly_info = self.poly_info[
        keep_list -
        1, :]  #np.genfromtxt(self.path + 'poly_info.dat')[keep_list - 1, :]
    try:
        os.unlink('poly_info.dat')
    except:
        pass

    with open('poly_info.dat', 'w') as fp:
        for i in range(num_frac):
            fp.write('%d %d %f %f %f %d %f %f %d\n' %
                     (i + 1, poly_info[i, 1], poly_info[i, 2], poly_info[i, 3],
                      poly_info[i, 4], poly_info[i, 5], poly_info[i, 6],
                      poly_info[i, 7], poly_info[i, 8]))
    self.poly_info = poly_info

    print("--> Complete")

    # print("--> Editing perm.dat file")
    # perm = self.perm  #np.genfromtxt(self.path + 'perm.dat', skip_header=1)[keep_list - 1, -1]
    # f = open('perm.dat', 'w+')
    # f.write('permeability\n')
    # for i in range(num_frac):
    #     f.write('-%d 0 0 %e %e %e\n' % (7 + i, perm[i], perm[i], perm[i]))
    # f.close()
    # print("--> Complete")

    # print("--> Editing aperture.dat file")
    # aperture = self.aperture  #np.genfromtxt(self.path + 'aperture.dat', skip_header=1)[keep_list - 1, -1]
    # f = open('aperture.dat', 'w+')
    # f.write('aperture\n')
    # for i in range(num_frac):
    #     f.write('-%d 0 0 %e \n' % (7 + i, aperture[i]))
    # f.close()
    # print("--> Complete")

    print("--> Editing radii_Final.dat file")
    fin = open(self.path + 'dfnGen_output/radii_Final.dat')
    fout = open('dfnGen_output/radii_Final.dat', 'w')
    # copy header
    line = fin.readline()
    fout.write(line)
    line = fin.readline()
    fout.write(line)
    fin.close()
    # write radii from remaining fractures
    radii = self.radii[
        keep_list -
        1, :]  #np.genfromtxt(self.path + 'radii_Final.dat', skip_header=2)[keep_list - 1, :]
    for i in range(num_frac):
        fout.write('%f %f %d\n' % (radii[i, 0], radii[i, 1], radii[i, 2]))
    fout.close()
    print("--> Complete")

    print("--> Editing normal_vectors.dat file")
    fin = open(self.path + 'dfnGen_output/normal_vectors.dat')
    fout = open('dfnGen_output/normal_vectors.dat', 'w')
    # copy header
    normal_vect = self.normal_vectors[
        keep_list -
        1, :]  #np.genfromtxt(self.path + 'normal_vectors.dat')[keep_list - 1, :]
    for i in range(num_frac):
        fout.write('%f %f %f\n' %
                   (normal_vect[i, 0], normal_vect[i, 1], normal_vect[i, 2]))
    fout.close()
    print("--> Complete")

    print("--> Editing translations.dat file")
    fin = open(self.path + 'dfnGen_output/translations.dat')
    fout = open('dfnGen_output/translations.dat', 'w')
    # copy header
    line = fin.readline()
    fout.write(line)
    points = []
    for line in fin.readlines():
        tmp = line.split(' ')
        if tmp[-1] != 'R':
            points.append((float(tmp[0]), float(tmp[1]), float(tmp[2])))
    points = np.asarray(points)
    points = points[keep_list - 1, :]
    for i in range(num_frac):
        fout.write('%f %f %f\n' % (points[i, 0], points[i, 1], points[i, 2]))
    fout.close()

    print("--> Complete")

    print("--> Editing translations.dat file")
    with open(self.path + 'dfnGen_output/translations.dat', 'r') as fin:
        with open('dfnGen_output/translations.dat', 'w') as fout:
            # copy header
            line = fin.readline()
            fout.write(line)
            points = []
            for line in fin.readlines():
                tmp = line.split(' ')
                if tmp[-1] != 'R':
                    points.append(
                        (float(tmp[0]), float(tmp[1]), float(tmp[2])))
            points = np.asarray(points)
            points = points[keep_list - 1, :]
            for i in range(num_frac):
                fout.write('%f %f %f\n' %
                           (points[i, 0], points[i, 1], points[i, 2]))

    fout = open('dfnGen_output/surface_area_Final.dat', 'w')
    fout.write(
        'Fracture Surface Area After Isolated Fracture and Cluster Removal')
    # copy header
    surface_area = self.surface_area[keep_list - 1]
    for i in range(num_frac):
        fout.write(f'{surface_area[i]}\n')
    fout.close()
    print("--> Complete")

    print("--> Editing polygons.dat file")
    with open(self.path + 'dfnGen_output/polygons.dat', 'r') as fin:
        header = fin.readline()
        data = fin.read().strip()
        with open('dfnGen_output/polygons.dat', 'w') as fout:
            # new header
            fout.write(f'nPolygons: {self.num_frac}')
            for fracture, line in enumerate(data.split('\n')):
                if fracture - 1 in keep_list:
                    fout.write(line + "\n")

    self.families = self.families[keep_list - 1]
    self.perm = self.perm[keep_list - 1]
    self.aperture = self.aperture[keep_list - 1]

    print("--> Editing Fracture Files Complete")


def create_mesh_links(self, path):
    ''' Makes symlinks for files in path required for meshing
    
    Parameters
    ----------
        self : DFN object
        path : string
            Path to where meshing files are located

    Returns
    -------
        None
    
    Notes
    -----
        None

    '''
    import os.path
    from shutil import rmtree
    print(f"--> Creating links for meshing from {path}")
    files = [
        'params.txt',
        'poly_info.dat',
        'polys',
        'intersections',
        'dfnGen_output/connectivity.dat',
        'dfnGen_output/left.dat',
        'dfnGen_output/right.dat',
        'dfnGen_output/front.dat',
        'dfnGen_output/back.dat',
        'dfnGen_output/top.dat',
        'dfnGen_output/fracture_info.dat',
        'dfnGen_output/intersection_list.dat',
        'dfnGen_output/bottom.dat',
    ]
    for filename in files:
        if os.path.isfile(filename) or os.path.isdir(filename):
            print(f"Removing {filename}")
            try:
                rmtree(filename)
            except:
                print(f"Unable to remove {filename}")
        try:
            os.symlink(path + filename, filename)
        except:
            print(f"Unable to make link for {filename}")
            pass
    print("--> Complete")


def inp2gmv(self, inp_file=''):
    """ Convert inp file to gmv file, for general mesh viewer. Name of output file for base.inp is base.gmv

    Parameters
    ----------
        self : object
            DFN Class
        inp_file : str
            Name of inp file if not an attribure of self

    Returns
    ----------
    None

    Notes
    ---------
    """

    if inp_file:
        self.inp_file = inp_file
    else:
        inp_file = self.inp_file

    if inp_file == '':
        error = 'ERROR: inp file must be specified in inp2gmv!\n'
        sys.stderr.write(error)
        sys.exit(1)

    gmv_file = inp_file[:-4] + '.gmv'

    with open('inp2gmv.lgi', 'w') as fid:
        fid.write(f'read / avs / {inp_file} / mo\n')
        fid.write(f'dump / gmv / {gmv_file} / mo\n')
        fid.write('finish \n\n')

    failure = run_lagrit_script('inp2gmv.lgi')

    if failure:
        error = 'ERROR: Failed to run LaGrit to get gmv from inp file!\n'
        sys.stderr.write(error)
        sys.exit(1)
    print("--> Finished writing gmv format from avs format")


def inp2vtk_python(self):
    """ Using Python VTK library, convert inp file to VTK file.  

    Parameters
    ----------
        self : object 
            DFN Class

    Returns
    --------
        None

    Notes
    --------
        For a mesh base.inp, this dumps a VTK file named base.vtk
    """

    if self.flow_solver != "PFLOTRAN":
        error = "ERROR! Wrong flow solver requested\n"
        sys.stderr.write(error)
        sys.exit(1)

    print("--> Using Python to convert inp files to VTK files")
    if self.inp_file:
        inp_file = self.inp_file

    if inp_file == '':
        error = 'ERROR: Please provide inp filename!\n'
        sys.stderr.write(error)
        sys.exit(1)

    if self.vtk_file:
        vtk_file = self.vtk_file
    else:
        vtk_file = inp_file[:-4]
        self.vtk_file = vtk_file + '.vtk'

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
    vtk = pv.VtkData(
        pv.UnstructuredGrid(coord,
                            tetra=elem_list_tetra,
                            triangle=elem_list_tri),
        'Unstructured pflotran grid')

    vtk.tofile(vtk_file)


def run_lagrit_script(lagrit_file, output_file=None, quiet=False):
    """
    Runs LaGriT

    Parameters
    -----------
    ----------
        lagrit_file : string
            Name of LaGriT script to run
        output_file : string
            Name of file to dump LaGriT output
        quiet : bool
            If false, information will be printed to screen.

    Returns
    ----------
        failure: int
            If the run was successful, then 0 is returned. 

    """
    if output_file == None:
        cmd = f"{os.environ['LAGRIT_EXE']} < {lagrit_file} -log {lagrit_file}.log -out {lagrit_file}.out"
    else:
        cmd = f"{os.environ['LAGRIT_EXE']} < {lagrit_file} -log {output_file}.log -out {output_file}.out > {output_file}.dump"
    if not quiet:
        print(f"--> Running: {cmd}")
    failure = subprocess.call(cmd, shell=True)
    if failure:
        error = f"ERROR running LaGriT on script {lagrit_file}. Exiting Program.\n"
        sys.stderr.write(error)
        sys.exit(1)
    else:
        print(f"--> Running LaGriT on script {lagrit_file} successful.\n")
        return failure


def setup_meshing_directory():

    dirs = ["lagrit_scripts", "lagrit_logs"]
    for d in dirs:
        try:
            if os.path.isdir(d):
                shutil.rmtree(d)
            os.mkdir(d)
        except:
            error = f"Unable to make directory {d}"
            sys.stderr.write(error)
            sys.exit(1)


def cleanup_meshing_files():
    """ Removes mesh files and directories 

    Parameters
    ----------
        None

    Returns
    -------
        None

    Notes
    -----
    Only runs if production_mode is True
    """

    batch_files_to_remove = [
        'part*', 'log_merge*', 'merge*', 'mesh_poly_CPU*', 'mesh*inp',
        'mesh*lg'
    ]
    for files in batch_files_to_remove:
        for fl in glob.glob(files):
            os.remove(fl)

    dirs_to_remove = ['lagrit_scripts', 'lagrit_logs']
    for d in dirs_to_remove:
        try:
            shutil.rmtree(d)
        except:
            error = f"Unable to remove directory {d}"
            sys.stderr.write(error)
            sys.exit(1)

    files_to_remove = ['user_resolution.mlgi']
    for filename in files_to_remove:
        try:
            os.remove(filename)
        except:
            error = f"Unable to remove directory {filename}"
            sys.stderr.write(error)
            sys.exit(1)
