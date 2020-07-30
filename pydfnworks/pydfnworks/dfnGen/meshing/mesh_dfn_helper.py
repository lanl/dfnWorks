"""
.. module:: mesh_dfn_helper.py
   :synopsis: helper functions for meshing DFN using LaGriT  
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""
import os
import glob
from numpy import genfromtxt, sort
import subprocess


def parse_params_file(quite=False):
    """ Reads params.txt file from DFNGen and parses information

    Parameters
    ---------
        quite : bool
            If True details are not printed to screen, if False they area 

    Returns
    -------
        num_poly: int
            Number of Polygons
        h: float 
            Meshing length scale h
        dudded_points: int 
            Expected number of dudded points in Filter (LaGriT)
        visual_mode : bool
            If True, reduced_mesh.inp is created (not suitable for flow and transport), if False, full_mesh.inp is created  
        domain: dict
             x,y,z domain sizes 
    
    Notes
    -----
        None
    """
    if not quite:
        print("\n--> Parsing  params.txt")
    fparams = open('params.txt', 'r')
    # Line 1 is the number of polygons
    num_poly = int(fparams.readline())
    #Line 2 is the h scale
    h = float(fparams.readline())
    # Line 3 is the visualization mode: '1' is True, '0' is False.
    visual_mode = int(fparams.readline())
    # line 4 dudded points
    dudded_points = int(fparams.readline())

    # Dict domain contains the length of the domain in x,y, and z
    domain = {'x': 0, 'y': 0, 'z': 0}
    #Line 5 is the x domain length
    domain['x'] = (float(fparams.readline()))

    #Line 5 is the x domain length
    domain['y'] = (float(fparams.readline()))

    #Line 5 is the x domain length
    domain['z'] = (float(fparams.readline()))
    fparams.close()

    if not quite:
        print("Number of Polygons: %d" % num_poly)
        print("H_SCALE %f" % h)
        if visual_mode > 0:
            visual_mode = True
            print("Visual mode is on")
        else:
            visual_mode = False
            print("Visual mode is off")
        print(f"Expected Number of dudded points: {dudded_points}")
        print(f"X Domain Size {domain['x']} m")
        print(f"Y Domain Size {domain['y']} m")
        print(f"Z Domain Size {domain['z']} m")
        print("--> Parsing params.txt complete\n")

    return (num_poly, h, visual_mode, dudded_points, domain)


def check_dudded_points(dudded, hard=False):
    """Parses LaGrit log_merge_all.txt and checks if number of dudded points is the expected number

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
    with open("lagrit_logs/log_merge_all.txt", "r") as fp:
        for line in fp.readlines():
            if 'Dudding' in line:
                print(f'--> From LaGriT: {line}')
                try:
                    pts = int(line.split()[1])
                except:
                    pts = int(line.split()[-1])
            if 'RMPOINT:' in line:
                print(f'--> From LaGriT: {line}')
                total_pts = int(line.split()[-1])
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
        print('--> WARNING!!! Number of points removed does not \
            match expected value')
        diff_ratio = float(diff) / float(total_points)
        if diff_ratio < 0.002 or hard == False:
            print(f"However value is small: {diff}")
            print("Proceeding\n")
            return True
        else:
            print('ERROR! Incorrect Number of points removed')
            print(f"Over 1% of node removed {diff_ratio}")
            return False


def cleanup_dir():
    """ Removes meshing files

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

    files_to_remove = [
        'part*', 'log_merge*', 'merge*', 'mesh_poly_CPU*', 'mesh*inp',
        'mesh*lg'
    ]
    for name in files_to_remove:
        for fl in glob.glob(name):
            os.remove(fl)


def output_meshing_report(local_jobname, visual_mode):
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

    f = open(local_jobname + '_mesh_information.txt', 'w')
    f.write('The final mesh of DFN consists of: \n')
    if not visual_mode:
        print(
            "--> Output files for flow calculations are written in : full_mesh.*"
        )

        finp = open('full_mesh.inp', 'r')
        g = finp.readline()
        g = g.split()
        NumElems = int(g.pop(1))
        NumIntNodes = int(g.pop(0))
        f.write(str(NumElems) + ' triangular elements; \n')
        f.write(str(NumIntNodes) + '  nodes / control volume cells; \n')
        finp.close()

        fstor = open('full_mesh.stor', 'r')
        fstor.readline()
        fstor.readline()
        gs = fstor.readline()
        gs = gs.split()
        NumCoeff = int(gs.pop(0))
        f.write(
            str(NumCoeff) +
            ' geometrical coefficients / control volume faces. \n')
        fstor.close()
    else:
        print(
            "--> Output files for visualization are written in : reduced_mesh.inp"
        )
        print("--> Warning!!! Mesh is not suitable for flow and transport.")

        finp = open('reduced_mesh.inp', 'r')
        g = finp.readline()
        g = g.split()
        NumElems = int(g.pop(1))
        NumIntNodes = int(g.pop(0))
        f.write(str(NumElems) + ' triangular elements; \n')
        f.write(str(NumIntNodes) + '  nodes / control volume cells. \n')
        finp.close()
    f.close()


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
    This function should always be run after pruning if flow solution is going to be run
 
    '''

    print("--> Editing DFN file based on fractures in %s" % self.prune_file)
    keep_list = sort(genfromtxt(self.prune_file).astype(int))
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
    poly_info = genfromtxt(self.path + 'poly_info.dat')[keep_list - 1, :]
    try:
        os.unlink('poly_info.dat')
    except:
        pass
    f = open('poly_info.dat', 'w')
    for i in range(num_frac):
        f.write('%d %d %f %f %f %d %f %f %d\n' %
                (i + 1, poly_info[i, 1], poly_info[i, 2], poly_info[i, 3],
                 poly_info[i, 4], poly_info[i, 5], poly_info[i, 6],
                 poly_info[i, 7], poly_info[i, 8]))
    f.close()
    print("--> Complete")

    print("--> Editing perm.dat file")
    perm = genfromtxt(self.path + 'perm.dat', skip_header=1)[keep_list - 1, -1]
    f = open('perm.dat', 'w+')
    f.write('permeability\n')
    for i in range(num_frac):
        f.write('-%d 0 0 %e %e %e\n' % (7 + i, perm[i], perm[i], perm[i]))
    f.close()
    print("--> Complete")

    print("--> Editing aperture.dat file")
    aperture = genfromtxt(self.path + 'aperture.dat',
                          skip_header=1)[keep_list - 1, -1]
    f = open('aperture.dat', 'w+')
    f.write('aperture\n')
    for i in range(num_frac):
        f.write('-%d 0 0 %e \n' % (7 + i, aperture[i]))
    f.close()
    print("--> Complete")

    print("--> Editing radii_Final.dat file")
    fin = open(self.path + 'radii_Final.dat')
    fout = open('radii_Final.dat', 'w')
    # copy header
    line = fin.readline()
    fout.write(line)
    line = fin.readline()
    fout.write(line)
    fin.close()
    # write radii from remaining fractures
    radii = genfromtxt(self.path + 'radii_Final.dat',
                       skip_header=2)[keep_list - 1, :]
    for i in range(num_frac):
        fout.write('%f %f %d\n' % (radii[i, 0], radii[i, 1], radii[i, 2]))
    fout.close()
    print("--> Complete")

    print("--> Editing normal_vectors.dat file")
    fin = open(self.path + 'normal_vectors.dat')
    fout = open('normal_vectors.dat', 'w')
    # copy header
    normal_vect = genfromtxt(self.path + 'normal_vectors.dat')[keep_list -
                                                               1, :]
    for i in range(num_frac):
        fout.write('%f %f %f\n' %
                   (normal_vect[i, 0], normal_vect[i, 1], normal_vect[i, 2]))
    fout.close()
    print("--> Complete")

    print("--> Editing translations.dat file")
    fin = open(self.path + 'translations.dat')
    fout = open('translations.dat', 'w')
    # copy header
    line = fin.readline()
    fout.write(line)
    points = []
    for line in fin.readlines():
        tmp = line.split(' ')
        if tmp[-1] != 'R':
            points.append((float(tmp[0]), float(tmp[1]), float(tmp[2])))
    from numpy import asarray
    points = asarray(points)
    points = points[keep_list - 1, :]
    for i in range(num_frac):
        fout.write('%f %f %f\n' % (points[i, 0], points[i, 1], points[i, 2]))
    fout.close()
    print("--> Complete")

    print("--> Editing Fracture Files Complete")


def create_mesh_links(path):
    ''' Makes symlinks for files in path required for meshing
    
    Parameters
    ----------
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
    print("--> Creating links for meshing from %s" % path)
    files = [
        'params.txt', 'poly_info.dat', 'connectivity.dat', 'left.dat',
        'right.dat', 'front.dat', 'back.dat', 'top.dat', 'bottom.dat', 'polys'
    ]
    for f in files:
        if os.path.isfile(f) or os.path.isdir(f):
            print("Removing %s" % f)
            try:
                rmtree(f)
            except:
                print("Unable to remove %s" % f)
        try:
            os.symlink(path + f, f)
        except:
            print("Unable to make link for %s" % f)
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


def run_lagrit_script(lagrit_file, output_file=None, quite=False):
    """
    Runs LaGriT

    Parameters
    -----------
    ----------
        lagrit_file : string
            Name of LaGriT script to run
        output_file : string
            Name of file to dump LaGriT output
        quite : bool
            If false, information will be printed to screen.

    Returns
    ----------
        failure: int
            If the run was successful, then 0 is returned. 

    """
    if output_file == None:
        cmd = f"{os.environ['LAGRIT_EXE']} < {lagrit_file}"
    else:
        cmd = f"{os.environ['LAGRIT_EXE']} < {lagrit_file} > {output_file}"
    if not quite:
        print(f"--> Running: {cmd}")

    failure = subprocess.call(cmd, shell=True)
    if failure:
        error = f"ERROR running LaGriT on script {lagrit_file}. Exiting Program.\n"
    return failure
