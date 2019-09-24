"""
.. module:: upscale.py
   :synopsis: Generates PFLOTRAN or FEHM input from octree refined continuum mesh
.. moduleauthor:: Matthew Sweeney <msweeney2796@lanl.gov>

"""

import os
import numpy as np
import sys
import subprocess
import shutil
import h5py
from pydfnworks.dfnGen import mesh_dfn_helper as mh
import time
import math as m
import glob


def upscale(self, mat_perm, mat_por):
    """ Generate permeabilities and porosities based on output of map2continuum.

    Parameters
    ----------
        self : object
            DFN Class 
        mat_perm : float 
            Matrix permeability (in m^2)
        mat_por: float
            Matrix porosity

    Returns
    -------
        perm_fehm.dat : text file
            Contains permeability data for FEHM input
        rock_fehm.dat : text file
            Contains rock properties data for FEHM input
        mesh_permeability.h5 : h5 file
            Contains permeabilites at each node for PFLOTRAN input
        mesh_porosity.h5 : h5 file
            Contains porosities at each node for PFLOTRAN input               
        
    Notes
    -----
        None

    """

    print('=' * 80)
    print("Generating permeability and porosity for octree mesh: Starting")
    print('=' * 80)

    os.symlink("../params.txt", "params.txt")
    num_poly, _, _, _, domain = mh.parse_params_file()

    # Bring in all the relevant data
    os.symlink("../aperture.dat", "aperture.dat")
    os.symlink("../normal_vectors.dat", "normal_vectors.dat")

    aperture = np.genfromtxt('aperture.dat', skip_header=1)[:, -1]
    normal_vectors = np.genfromtxt('normal_vectors.dat', delimiter=' ')

    if self.flow_solver == "FEHM":
        with open("perm_fehm.dat", "w") as f:
            f.write("perm\n")
        with open("rock_fehm.dat", "w") as g:
            g.write("rock\n")

    # Make dictionary w/ cell IDs (keys) and intersecting fractures, areas  (values)
    for i in range(1, num_poly + 1):
        if i == 1:
            with open('frac1.inp', 'r') as f:
                line = f.readline().strip().split()
                num_nodes = int(float(line[0]))
                num_cells = int(float(line[1]))
                f_dict = {}
                perm_var = np.zeros(num_nodes, 'float')
                por_var = np.zeros(num_nodes, 'float')
                cv_vol = np.zeros(num_nodes, 'float')
                iarray = np.zeros(num_nodes, '=i4')
                frac_vol = np.zeros(num_nodes, 'float')
                permX = np.zeros(num_nodes, 'float')
                permY = np.zeros(num_nodes, 'float')
                permZ = np.zeros(num_nodes, 'float')
            f.close()
        with open('frac{0}.inp'.format(i), 'r') as f:
            with open('area_sum{0}.inp'.format(i), 'r') as g:
                for j in range(num_nodes):
                    f.readline()
                    g.readline()
                f.readline()
                g.readline()
                for j in range(num_cells):
                    f.readline()
                    g.readline()
                f.readline()
                f.readline()
                f.readline()
                g.readline()
                g.readline()
                g.readline()
                g.readline()
                g.readline()
                g.readline()
                g.readline()
                for j in range(num_nodes):
                    fline = f.readline().strip().split()
                    gline = g.readline().strip().split()
                    iarray[j] = int(float(gline[0]))
                    if int(float(gline[1])) != (num_poly + 1):
                        f_dict.setdefault(j + 1, []).append(
                            (i, float(gline[6])))
            g.close()
        f.close()

    with open('full_mesh.uge', 'r') as f:
        f.readline()
        for j in range(num_nodes):
            fline = f.readline().strip().split()
            cv_vol[j] = float(fline[4])
    f.close()

    # Populate permeability and porosity arrays here
    for i in range(1, num_nodes + 1):
        if i in f_dict:

            # Get porosity:
            for j in range(len(f_dict[i])):
                # Calculate total volume of fractures in cv cell i
                frac_vol[i -
                         1] += aperture[f_dict[i][j][0] - 1] * f_dict[i][j][1]
            por_var[i - 1] = frac_vol[i - 1] / cv_vol[i - 1]
            if por_var[i - 1] == 0:
                por_var[i - 1] = mat_por
            if por_var[i - 1] > 1.0:
                por_var[i - 1] = 1.0

            # Get permeability:
            perm_tensor = np.zeros([3, 3])
            phi_sum = 0
            for j in range(len(f_dict[i])):
                phi = (aperture[f_dict[i][j][0] - 1] *
                       f_dict[i][j][1]) / cv_vol[i - 1]
                if phi > 1.0:
                    phi = 1.0
                phi_sum += phi
                if phi_sum > 1.0:
                    phi_sum = 1.0
                b = aperture[f_dict[i][j][0] - 1]
                # Construct tensor Omega
                Omega = np.zeros([3, 3])
                n1 = normal_vectors[f_dict[i][j][0] - 1][0]
                n2 = normal_vectors[f_dict[i][j][0] - 1][1]
                n3 = normal_vectors[f_dict[i][j][0] - 1][2]
                Omega[0][0] = (n2)**2 + (n3)**2
                Omega[0][1] = -n1 * n2
                Omega[0][2] = -n3 * n1
                Omega[1][0] = -n1 * n2
                Omega[1][1] = (n3)**2 + (n1)**2
                Omega[1][2] = -n2 * n3
                Omega[2][0] = -n3 * n1
                Omega[2][1] = -n2 * n3
                Omega[2][2] = (n1)**2 + (n2)**2
                perm_tensor += (phi * (b)**2 * Omega)
            perm_tensor *= 1. / 12

            # Calculate eigenvalues
            permX[i - 1] = np.linalg.eigvals(perm_tensor)[0]
            permY[i - 1] = np.linalg.eigvals(perm_tensor)[1]
            permZ[i - 1] = np.linalg.eigvals(perm_tensor)[2]

            # Arithmetic average of matrix perm
            permX[i - 1] += (1 - phi_sum) * mat_perm
            permY[i - 1] += (1 - phi_sum) * mat_perm
            permZ[i - 1] += (1 - phi_sum) * mat_perm

            # Correction factor

            # Actual value doesn't matter here, just needs to be high
            min_n1 = 1e6
            min_n2 = 1e6
            min_n3 = 1e6

            # See Sweeney et al. 2019 Computational Geoscience
            for j in range(len(f_dict[i])):
                n1_temp = normal_vectors[f_dict[i][j][0] - 1][0]
                theta1_t = m.degrees(m.acos(n1_temp)) % 90
                if abs(theta1_t - 45) <= min_n1:
                    theta1 = theta1_t
                    min_n1 = theta1_t
                n2_temp = normal_vectors[f_dict[i][j][0] - 1][1]
                theta2_t = m.degrees(m.acos(n2_temp)) % 90
                if abs(theta2_t - 45) <= min_n2:
                    theta2 = theta2_t
                    min_n2 = theta2_t
                n3_temp = normal_vectors[f_dict[i][j][0] - 1][2]
                theta3_t = m.degrees(m.acos(n3_temp)) % 90
                if abs(theta3_t - 45) <= min_n3:
                    theta3 = theta3_t
                    min_n3 = theta3_t

            sl = (2 * 2**(1. / 2) - 1) / -45.0
            b = 2 * 2**(1. / 2)

            cf_x = sl * abs(theta1 - 45) + b
            cf_y = sl * abs(theta2 - 45) + b
            cf_z = sl * abs(theta3 - 45) + b

            permX[i - 1] *= cf_x
            permY[i - 1] *= cf_y
            permZ[i - 1] *= cf_z

            # Correct 0 perm if exists
            if permX[i - 1] == 0:
                permX[i - 1] += mat_perm
            if permY[i - 1] == 0:
                permY[i - 1] += mat_perm
            if permZ[i - 1] == 0:
                permZ[i - 1] += mat_perm
            perm_var[i - 1] = max(permX[i - 1], permY[i - 1], permZ[i - 1])
        else:
            # Assign matrix properties
            por_var[i - 1] = mat_por
            perm_var[i - 1] = mat_perm

            # Note these aren't needed if not using anisotropic perm
            permX[i - 1] = mat_perm
            permY[i - 1] = mat_perm
            permZ[i - 1] = mat_perm

        if self.flow_solver == "FEHM":
            with open("perm_fehm.dat", "a") as f:
                f.write(
                    str(i) + " " + str(i) + " " + "1" + " " +
                    str(perm_var[i - 1]) + " " + str(perm_var[i - 1]) + " " +
                    str(perm_var[i - 1]) + "\n")
            with open("rock_fehm.dat", "a") as g:
                g.write(
                    str(i) + " " + str(i) + " " + "1" + " " + "2165." + " " +
                    "931." + " " + str(por_var[i - 1]) + "\n")

    # Need an extra space at end for FEHM
    if self.flow_solver == "FEHM":
        with open("perm_fehm.dat", "a") as f:
            f.write("\n")
        with open("rock_fehm.dat", "a") as g:
            g.write("\n")

    if self.flow_solver == "PFLOTRAN":
        perm_filename = 'mesh_permeability.h5'
        poros_filename = 'mesh_porosity.h5'

        h5file = h5py.File(perm_filename, mode='w')
        dataset_name = 'Cell Ids'
        h5dset = h5file.create_dataset(dataset_name, data=iarray)

        dataset_name = 'Permeability'
        h5dset = h5file.create_dataset(dataset_name, data=perm_var)

        #dataset_name = 'Perm_X'
        #h5dset = h5file.create_dataset(dataset_name, data = permX)

        #dataset_name = 'Perm_Y'
        #h5set = h5file.create_dataset(dataset_name, data = permY)

        #dataset_name = 'Perm_Z'
        #h5set = h5file.create_dataset(dataset_name, data = permZ)
        h5file.close()

        h5file = h5py.File(poros_filename, mode='w')
        dataset_name = 'Cell Ids'
        h5dset = h5file.create_dataset(dataset_name, data=iarray)

        dataset_name = 'Porosity'
        h5dset = h5file.create_dataset(dataset_name, data=por_var)
        h5file.close()

        upscale_cleanup()


def upscale_cleanup():
    files_to_remove = [
        "area*", "build*", "driver*", "ex*", "frac*", "hex*", "intersect*",
        "log*", "out*", "parame*", "remove*", "time*", "tmp*"
    ]
    for name in files_to_remove:
        for fl in glob.glob(name):
            os.remove(fl)
