"""
.. module:: prune_mesh_scripts.py
   :synopsis: create lagrit scripts for meshing dfn using LaGriT 
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""
import os, sys
from shutil import copy, move
import subprocess
import numpy as np

from pydfnworks.dfnGen.meshing.mesh_dfn import mesh_dfn_helper as mh


def load_connectivity_file(path):
    connectivity = []
    with open(path + "/dfnGen_output/connectivity.dat", "r") as fp:
        for line in fp.readlines():
            tmp = []
            line = line.split()
            for frac in line:
                tmp.append(int(frac))
            connectivity.append(tmp)
    return connectivity


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

    fractures_to_remove = list(
        set(range(1, self.num_frac + 1)) - set(self.fracture_list))

    # remove symbolic link and setup local intersection directory
    if os.path.isdir(self.jobname + '/intersections'):
        os.unlink(self.jobname + '/intersections')
        os.mkdir(self.jobname + '/intersections')
    else:
        os.mkdir(self.jobname + '/intersections')
    os.chdir(self.jobname + '/intersections')

    ## DEBUGGING ##
    # clean up directory
    #fl_list = glob.glob("*prune.inp")
    #for fl in fl_list:
    #   os.remove(fl)
    ## DEBUGGING ##

    self.print_log("--> Editing Intersection Files")
    connectivity = load_connectivity_file(self.path)
    ## Note this could be easily changed to run in parallel if needed. Just use cf
    for ifrac in self.fracture_list:
        filename = f'intersections_{ifrac}.inp'
        self.print_log(f'--> Working on: {filename}')
        intersecting_fractures = connectivity[ifrac - 1]
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
            for jfrac in pull_list[1:]:
                lagrit_script += f'''
pset / prune / attribute / b_a / 1,0,0 / eq / {jfrac}
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
dump / intersections_{ifrac}_prune.inp / mo1
finish
'''

            lagrit_filename = 'prune_intersection.lgi'
            with open(lagrit_filename, 'w') as f:
                f.write(lagrit_script)
                f.flush()
            mh.run_lagrit_script("prune_intersection.lgi",
                                 f"pruning_{ifrac}.txt",
                                 quiet=True)
            os.remove(filename)
            if os.path.isfile(f"intersections_{ifrac}_prune.inp"):
                move(f"intersections_{ifrac}_prune.inp",
                     f"intersections_{ifrac}.inp")
            else:
                error = f"Error. intersections_{ifrac}_prune.inp file not found.\nExitting Program"
                self.print_log(error, 'error')
        else:
            try:
                copy(self.path + 'intersections/' + filename, filename)
            except:
                pass

    os.chdir(self.jobname)
    self.num_frac = len(self.fracture_list)
    self.print_log("--> Done editting intersection files")


def clean_up_files_after_prune(self, dump_files=True):
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

    self.print_log(f"--> Editing DFN file based on fractures in {self.prune_file}")
    keep_list = np.sort(np.genfromtxt(self.prune_file).astype(int))
    self.poly_info = self.poly_info[keep_list - 1, :]
    self.families = self.families[keep_list - 1]
    self.perm = self.perm[keep_list - 1]
    self.aperture = self.aperture[keep_list - 1]
    # self.material_ids = self.material_ids[keep_list - 1]
    self.radii = self.radii[keep_list - 1, :]
    self.normal_vect = self.normal_vectors[keep_list - 1, :]
    self.centers = self.centers[keep_list - 1, :]
    self.surface_area = self.surface_area[keep_list - 1]

    print(f"--> Modifying DFN properties based on fractures in {self.prune_file}: Complete")


    if dump_files:
        ## this is probably broken, but everything else is in memory now so....
        self.print_log("--> Editing params.txt file")
        fin = open(self.path + '/params.txt')
        try:
            os.unlink('params.txt')
        except:
            pass
        fout = open(self.jobname + 'params.txt', 'w')
        line = fin.readline()
        fout.write('%d\n' % self.num_frac)
        for i in range(7):
            line = fin.readline()
            fout.write(line)
        fin.close()
        fout.close()
        self.print_log("--> Complete")

        self.print_log("--> Editing poly_info.dat file")
        try:
            os.unlink('poly_info.dat')
        except:
            pass

        with open(self.jobname + 'poly_info.dat', 'w') as fp:
            for i in range(self.num_frac):
                fp.write('%d %d %f %f %f %d %f %f %d\n' %
                         (i + 1, self.poly_info[i, 1], self.poly_info[i, 2],
                          self.poly_info[i, 3], self.poly_info[i, 4],
                          self.poly_info[i, 5], self.poly_info[i, 6],
                          self.poly_info[i, 7], self.poly_info[i, 8]))
        self.print_log("--> Complete")

        self.print_log("--> Editing radii_Final.dat file")
        fin = open(self.path + 'dfnGen_output/radii_Final.dat')
        fout = open(self.jobname + 'dfnGen_output/radii_Final.dat', 'w')
        # copy header
        line = fin.readline()
        fout.write(line)
        line = fin.readline()
        fout.write(line)
        fin.close()
        # write radii from remaining fractures
        #np.genfromtxt(self.path + 'radii_Final.dat', skip_header=2)[keep_list - 1, :]
        for i in range(self.num_frac):
            fout.write('%f %f %d\n' %
                       (self.radii[i, 0], self.radii[i, 1], self.radii[i, 2]))
        fout.close()
        self.print_log("--> Complete")

        self.print_log("--> Editing normal_vectors.dat file")
        fin = open(self.path + 'dfnGen_output/normal_vectors.dat')
        fout = open(self.jobname + 'dfnGen_output/normal_vectors.dat', 'w')
        # copy header
        #np.genfromtxt(self.path + 'normal_vectors.dat')[keep_list - 1, :]
        for i in range(self.num_frac):
            fout.write('%f %f %f\n' %
                       (self.normal_vect[i, 0], self.normal_vect[i, 1],
                        self.normal_vect[i, 2]))
        fout.close()
        self.print_log("--> Complete")

        self.print_log("--> Editing translations.dat file")
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
        for i in range(self.num_frac):
            fout.write('%f %f %f\n' %
                       (points[i, 0], points[i, 1], points[i, 2]))
        fout.close()
        self.print_log("--> Complete")

        self.print_log("--> Editing translations.dat file")
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
                for i in range(self.num_frac):
                    fout.write('%f %f %f\n' %
                               (points[i, 0], points[i, 1], points[i, 2]))

        fout = open(self.jobname + 'dfnGen_output/surface_area_Final.dat', 'w')
        fout.write(
            'Fracture Surface Area After Isolated Fracture and Cluster Removal'
        )
        # copy header
        for i in range(self.num_frac):
            fout.write(f'{self.surface_area[i]}\n')
        fout.close()
        self.print_log("--> Complete")

        self.print_log("--> Editing polygons.dat file")
        with open(self.path + 'dfnGen_output/polygons.dat', 'r') as fin:
            header = fin.readline()
            data = fin.read().strip()
            with open('dfnGen_output/polygons.dat', 'w') as fout:
                # new header
                fout.write(f'nPolygons: {self.num_frac}\n')
                for fracture, line in enumerate(data.split('\n')):
                    if fracture - 1 in keep_list:
                        fout.write(line + "\n")

    self.print_log("--> Editing Fracture Files Complete")
