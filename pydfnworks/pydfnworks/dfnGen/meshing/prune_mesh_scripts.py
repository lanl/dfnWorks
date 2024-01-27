"""
.. module:: prune_mesh_scripts.py
   :synopsis: create lagrit scripts for meshing dfn using LaGriT 
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""
import os, sys
from shutil import copy, move
import subprocess
import numpy as np

from pydfnworks.dfnGen.meshing import mesh_dfn_helper as mh


def edit_intersection_files(self):
    """ If pruning a DFN, this function walks through the intersection files
    and removes references to files that are not included in the 
    fractures that will remain in the network.
 
    Parameters
    ---------
        self.num_frac : int 
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
    with open(self.path + "/dfnGen_output/connectivity.dat", "r") as fp:
        for i in range(self.num_frac):
            tmp = []
            line = fp.readline()
            line = line.split()
            for frac in line:
                tmp.append(int(frac))
            connectivity.append(tmp)

    fractures_to_remove = list(
        set(range(1, self.num_frac + 1)) - set(self.fracture_list))

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
    for i in self.fracture_list:
        filename = f'intersections_{i}.inp'
        print(f'--> Working on: {filename}')
        intersecting_fractures = connectivity[i - 1]
        pull_list = list(
            set(intersecting_fractures).intersection(set(fractures_to_remove)))
        if len(pull_list) > 0:
            # Create Symlink to original intersection file
            os.symlink(self.path + 'intersections/' + filename, filename)
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
            with open(lagrit_filename, 'w') as f:
                f.write(lagrit_script)
                f.flush()
            mh.run_lagrit_script("prune_intersection.lgi",
                                 f"pruning_{i}.txt",
                                 quiet=True)
            os.remove(filename)
            if os.path.isfile(f"intersections_{i}_prune.inp"):
                move(f"intersections_{i}_prune.inp", f"intersections_{i}.inp")
            else:
                error = "Error. intersections_{i}_prune.inp file not found.\nExitting Program"
                sys.stderr.write(error)
                sys.exit(1)
        else:
            try:
                copy(self.path + 'intersections/' + filename, filename)
            except:
                pass
    os.chdir(self.jobname)


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
    fout = open(self.jobname + 'params.txt', 'w')
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

    with open(self.jobname + 'poly_info.dat', 'w') as fp:
        for i in range(num_frac):
            fp.write('%d %d %f %f %f %d %f %f %d\n' %
                     (i + 1, poly_info[i, 1], poly_info[i, 2], poly_info[i, 3],
                      poly_info[i, 4], poly_info[i, 5], poly_info[i, 6],
                      poly_info[i, 7], poly_info[i, 8]))
    self.poly_info = poly_info
    print("--> Complete")

    print("--> Editing radii_Final.dat file")
    fin = open(self.path + 'dfnGen_output/radii_Final.dat')
    fout = open(self.jobname + 'dfnGen_output/radii_Final.dat', 'w')
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
    fout = open(self.jobname + 'dfnGen_output/normal_vectors.dat', 'w')
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
    fin = open(self.path + 'dfnGen_output/translations.dat', 'r')
    fout = open(self.jobname + 'dfnGen_output/translations.dat', 'w')
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
        with open(self.jobname + 'dfnGen_output/translations.dat',
                  'w') as fout:
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

    fout = open(self.jobname + 'dfnGen_output/surface_area_Final.dat', 'w')
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
