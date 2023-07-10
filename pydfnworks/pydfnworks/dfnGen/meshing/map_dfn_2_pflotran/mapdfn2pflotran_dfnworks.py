'''
   mapdfn2pflotran.py

   Call methods in mapdfn.py to take output of dfnWorks-Version2.0, create
   equivalent continuous porous medium representation, and write parameters
   (permeability, porosity, tortuosity) to files for use with PFLOTRAN.

   Usage: Edit values for origin, nx, ny, nz, d, k_background, bulk_por,
          tortuosity factor, and h5origin.
          Paths and filenames are hardwired and may also need to be checked.
          As written, they assume script is being called from a subdirectory.
          Then: python mapdfn2pflotran.py

   Dependencies: mapdfn.py
                 numpy
                 h5py

   Author: 

   Date: 07/13/18
   SAND Number: SAND2018-7605 O

'''
import os.path as op
import sys, os
import math as m
import pydfnworks.dfnGen.meshing.map_dfn_2_pflotran.transformations as tr
import time 

import numpy as np
from h5py import File


def get_porosity(fracture, apertures, d, bulk_por):
    '''Calculate fracture porosity for each cell of ECPM intersected by
     one or more fractures. Simplifying assumptions: 1) each fracture crosses
     the cell parallel to cell faces, 2) each fracture completely crosses the cell.
     Assign bulk porosity to cells not intersected by fractures.
     Return numpy array of porosity for each cell in the ECPM domain.

     fracture = numpy array containing number of fractures in each cell, list of fracture numbers in each cell
     apertures = list containing aperture of each fracture
     d = float length of cell side
     bulk_por = float bulk porosity (which would normally be larger than fracture porosity)
  '''

    t0 = time.time()
    ncell = fracture.shape[0]
    porosity = np.zeros((ncell), '=f8')
    for i in range(ncell):
        if fracture[i][0] == 0:
            porosity[i] = bulk_por
        else:  #there are fractures in this cell
            for j in range(1, fracture[i][0] + 1):
                fracnum = fracture[i][j]
                porosity[i] += apertures[
                    fracnum -
                    1] / d  #aperture is 0 indexed, fracture numbers are 1 indexed

    t1 = time.time()
    print('Time spent in porosity() = %f.' % (t1 - t0))

    return porosity

def perm_iso(fracture, T, cell_size, k_background):
    '''Calculate isotropic permeability for each cell of ECPM intersected by
     one or more fractures. Sums fracture transmissivities and divides by 
     cell length (d) to calculate cell permeability.
     Assign background permeability to cells not intersected by fractures.
     Returns numpy array of isotropic permeability for each cell in the ECPM.

     fracture = numpy array containing number of fractures in each cell, list of fracture numbers in each cell
     T = [] containing intrinsic transmissivity for each fracture
     d = length of cell sides
     k_background = float background permeability for cells with no fractures in them
  '''
    t0 = time.time()
    ncell = fracture.shape[0]
    k_iso = np.full((ncell), k_background, '=f8')
    for i in range(ncell):
        if fracture[i][0] != 0:
            for j in range(1, fracture[i][0] + 1):
                fracnum = fracture[i][j]
                k_iso[i] += T[
                    fracnum -
                    1] / cell_size  #T is 0 indexed, fracture numbers are 1 indexed

    t1 = time.time()
    print('Time spent in permIso() = %f.' % (t1 - t0))

    return k_iso

def perm_aniso(num_frac,
               fracture,
               ellipses,
               T,
               cell_size,
               k_background,
               LUMP = False,
               out_dir='./',
               correction_factor=True):
    '''Calculate anisotropic permeability tensor for each cell of ECPM
     intersected by one or more fractures. Discard off-diagonal components
     of the tensor. Assign background permeability to cells not intersected
     by fractures.
     Return numpy array of anisotropic permeability (3 components) for each 
     cell in the ECPM.

     fracture = numpy array containing number of fractures in each cell, list of fracture numbers in each cell
     ellipses = [{}] containing normal and translation vectors for each fracture
     T = [] containing intrinsic transmissivity for each fracture
     d = length of cell sides
     k_background = float background permeability for cells with no fractures in them
  '''
    #quick error check
    ellipseT = np.zeros((num_frac, 3), '=f8')
    fullTensor = []
    T_local = np.zeros((3, 3), dtype=np.float)
    t0 = time.time()
    #calculate transmissivity tensor in domain coordinates for each ellipse
    for f in range(num_frac):
        normal = ellipses[f]['normal']
        direction = np.cross(normal, [0, 0, 1])
        angle = np.arccos(normal[2])
        M = tr.rotation_matrix(angle, direction)
        Transpose = np.transpose(M[:3, :3])
        T_local[0, 0] = T[f]
        T_local[1, 1] = T[f]
        #permeability = 0 in local z direction of fracture
        T_domain = np.dot(np.dot(M[:3, :3], T_local), Transpose)
        ellipseT[f][0:3] = [T_domain[0, 0], T_domain[1, 1], T_domain[2, 2]]
        fullTensor.append(T_domain)
    t1 = time.time()
    print('time spent calculating fracture transmissivity %f' % (t1 - t0))

    #in case you were wondering what those off-diagonal terms are:
    t0 = time.time()
    #fout=file('Ttensor.txt','w')
    fout = open(out_dir + 'Ttensor.txt', 'w')
    for f in range(len(fullTensor)):
        fout.write(str(fullTensor[f]))
        fout.write('\n\n')
    fout.close()
    t1 = time.time()
    print('time spent writing fracture transmissivity %f' % (t1 - t0))

    #calculate cell effective permeability by adding fracture k to background k
    t0 = time.time()
    ncells = fracture.shape[0]
    # maxfrac = fracture.shape[1]
    k_aniso = np.full((ncells, 3), k_background, '=f8')
    for i in range(ncells):
        if fracture[i][0] != 0:
            for j in range(1, fracture[i][0] + 1):
                fracnum = fracture[i][j]
                if LUMP:  #lump off diagonal terms
                    #because symmetrical doesn't matter if direction of summing is correct, phew!
                    k_aniso[i][0] += np.sum(fullTensor[fracnum - 1][0, :3]) / cell_size
                    k_aniso[i][1] += np.sum(fullTensor[fracnum - 1][1, :3]) / cell_size
                    k_aniso[i][2] += np.sum(fullTensor[fracnum - 1][2, :3]) / cell_size
                else:  #discard off diagonal terms (default)
                    #ellipseT is 0 indexed, fracture numbers are 1 indexed
                    k_aniso[i][0] += ellipseT[fracnum - 1][
                        0] / cell_size  
                    k_aniso[i][1] += ellipseT[fracnum - 1][1] / cell_size
                    k_aniso[i][2] += ellipseT[fracnum - 1][2] / cell_size

            if correction_factor:
                #correction factor Sweeney et al. 2019 from upscale.py

                min_n1 = 1e6
                min_n2 = 1e6
                min_n3 = 1e6

                for j in range(1, fracture[i][0] + 1):
                    fracnum = fracture[i][j]
                    normal = ellipses[fracnum - 1]['normal']
                    n1_temp = normal[0]
                    theta1_t = m.degrees(m.acos(n1_temp)) % 90
                    if abs(theta1_t - 45) <= min_n1:
                        theta1 = theta1_t
                        min_n1 = theta1_t
                    n2_temp = normal[1]
                    theta2_t = m.degrees(m.acos(n2_temp)) % 90
                    if abs(theta2_t - 45) <= min_n2:
                        theta2 = theta2_t
                        min_n2 = theta2_t
                    n3_temp = normal[2]
                    theta3_t = m.degrees(m.acos(n3_temp)) % 90
                    if abs(theta3_t - 45) <= min_n3:
                        theta3 = theta3_t
                        min_n3 = theta3_t

                sl = (2 * 2**(1. / 2) - 1) / -45.0
                b = 2 * 2**(1. / 2)

                cf_x = sl * abs(theta1 - 45) + b
                cf_y = sl * abs(theta2 - 45) + b
                cf_z = sl * abs(theta3 - 45) + b

                k_aniso[i][0] *= cf_x
                k_aniso[i][1] *= cf_y
                k_aniso[i][2] *= cf_z

            ########
    t1 = time.time()
    print(f'Time spent summing cell permeabilities {t1 - t0}')

    return k_aniso

def setup_output_dir(output_dir):

    print(f"--> Creating output directory {output_dir}")
    if not op.exists(output_dir):
        os.makedirs(output_dir)
        os.chdir(output_dir)
    filenames = {
        'mapEllipses_txt': output_dir + '/mapELLIPSES.txt',
        "mapEllipses_h5": output_dir + '/mapELLIPSES.h5',
        'isotropic_k': output_dir + '/isotropic_k.h5',
        'anisotropic_k': output_dir + '/anisotropic_k.h5',
        'tortuosity': output_dir + '/tortuosity.h5',
        'porosity': output_dir + '/porosity.h5',
        'materials': output_dir + '/materials.h5'
    }
    return filenames

def setup_domain(domain,cell_size):
    domain_origin = [
        -1 * domain['x'] / 2, -1 * domain['y'] / 2, -1 * domain['z'] / 2
    ]
    print(domain_origin)
    # Origin of area to map in DFN domain coordinates (0,0,0 is center of DFN)
    [nx, ny, nz] = [
        int(domain['x'] / cell_size),
        int(domain['y']  / cell_size),
        int(domain['z']  / cell_size)
        ]
    
    print(nx,ny,nz)
    print(domain['x'] % cell_size, domain['y'] % cell_size, domain['z'] % cell_size )
    if domain['x'] % cell_size + domain['y'] % cell_size + domain['z'] % cell_size > 0:
        error_msg = f"Error: The cell size you've specified, {cell_size} m, does not evenly divide the domain. Domain size: {domain['x']} x {domain['y']} x {domain['z']} m^3."
        sys.stderr.write(error_msg)
        sys.exit(1)

    return domain_origin, nx, ny, nz 

def get_perms_and_porosity(self, ellipses, origin, nx, ny, nz, cell_size, matrix_perm,
                           matrix_porosity, correction_factor, out_dir):

    # Call mapdfn functions
    print('Mapping DFN to grid')
    fractures = self.map_dfn( origin, nx, ny, nz, cell_size)
    # This really isn't a transmissivity. It doesn't have the right units. 
    ###
    T = self.apertures * self.perm
    k_iso = perm_iso(fractures, T, cell_size, matrix_perm)

    k_aniso = perm_aniso(fractures,
        ellipses,
        T,
        cell_size,
        matrix_perm,
        out_dir,
        correction_factor)
        
    print('Calculating fracture permeability')
    porosity = get_porosity(fractures, self.aperture, cell_size,
                            matrix_porosity)

    return fractures, k_iso, k_aniso, porosity


def write_h5_files(origin, domain_origin, filenames, nx, ny, nz, cell_size,
                fracture, k_iso, k_aniso, porosity, matrix_perm, tortuosity_factor):

    h5origin = [x - y for x, y in zip(origin, domain_origin)]

    # Fill arrays that will go into PFLOTRAN h5 files.
    # Also write mapELLIPSES.txt for later use.
    # Potentially large file. If you have no use for it, don't write it.
    
    fout = open(filenames['mapEllipses_txt'], 'w')
    fout.write('#x, y, z, number of fractures, fracture numbers\n')

    #arrays for making PFLOTRAN hf file
    x = np.zeros(nx + 1, '=f8')
    x[nx] = h5origin[0] + nx * cell_size
    y = np.zeros(ny + 1, '=f8')
    y[ny] = h5origin[1] + ny * cell_size
    z = np.zeros(nz + 1, '=f8')
    z[nz] = h5origin[2] + nz * cell_size
    a = np.zeros((nx, ny, nz), '=f8')
    khdf5 = np.zeros((nx, ny, nz), '=f8')
    kx = np.zeros((nx, ny, nz), '=f8')
    ky = np.zeros((nx, ny, nz), '=f8')
    kz = np.zeros((nx, ny, nz), '=f8')
    phdf5 = np.zeros((nx, ny, nz), '=f8')

    print('Writing text file')
    #write mapELLIPSES.txt and fill arrays
    for k in range(nz):
        z[k] = h5origin[2] + k * cell_size
        for j in range(ny):
            y[j] = h5origin[1] + j * cell_size
            for i in range(nx):
                index = i + nx * j + nx * ny * k
                x[i] = h5origin[0] + i * cell_size
                khdf5[i][j][k] = k_iso[index]
                kx[i][j][k] = k_aniso[index][0]
                ky[i][j][k] = k_aniso[index][1]
                kz[i][j][k] = k_aniso[index][2]
                phdf5[i][j][k] = porosity[index]
                fout.write('%e  %e  %e  %i %e ' %
                           (origin[0] + i * cell_size + cell_size / 2.,
                            origin[1] + j * cell_size + cell_size / 2.,
                            origin[2] + k * cell_size + cell_size / 2.,
                            fracture[index][0], k_iso[index]))
                if (fracture[index][0]) != 0:
                    a[i][j][k] = fracture[index][
                        1]  #color by the first fracture number in the list
                    for c in range(1, fracture[index][0] + 1):
                        fout.write(' ' + str(fracture[index][c]))
                else:
                    a[i][j][k] = 0  #color it zero
                    fout.write(' ' + str(fracture[index][1]))  #?
                fout.write('\n')
    fout.close()

    # Write same information to mapELLIPSES.h5. This file can be opened in Paraview
    # by chosing "PFLOTRAN file" as the format.
    print('Writing .h5 file for viz')
    h5file = File(filenames['mapEllipses_h5'], 'w')
    dataset_name = 'Coordinates/X [m]'
    h5dset = h5file.create_dataset(dataset_name, data=x)
    dataset_name = 'Coordinates/Y [m]'
    h5dset = h5file.create_dataset(dataset_name, data=y)
    dataset_name = 'Coordinates/Z [m]'
    h5dset = h5file.create_dataset(dataset_name, data=z)

    dataset_name = 'Time:  0.00000E+00 y/Perm'
    hfdset = h5file.create_dataset(dataset_name, data=khdf5)
    dataset_name = 'Time:  0.00000E+00 y/Fracture'
    h5dset = h5file.create_dataset(dataset_name, data=a)
    dataset_name = 'Time:  0.00000E+00 y/PermX'
    h5dset = h5file.create_dataset(dataset_name, data=kx)
    dataset_name = 'Time:  0.00000E+00 y/PermY'
    h5dset = h5file.create_dataset(dataset_name, data=ky)
    dataset_name = 'Time:  0.00000E+00 y/PermZ'
    h5dset = h5file.create_dataset(dataset_name, data=kz)
    dataset_name = 'Time:  0.00000E+00 y/Porosity'
    hfdset = h5file.create_dataset(dataset_name, data=phdf5)

    h5file.close()

    # Write isotropic permeability to a gridded dataset for use with PFLOTRAN.
    print('Writing .h5 file for isotropic permeability field')
    h5file2 = File(filenames['isotropic_k'], 'w')
    # 3d uniform grid
    h5grp = h5file2.create_group('Permeability')
    # 3D will always be XYZ where as 2D can be XY, XZ, etc. and 1D can be X, Y or Z
    h5grp.attrs['Dimension'] = np.string_('XYZ')
    # based on Dimension, specify the uniform grid spacing
    h5grp.attrs['Discretization'] = [cell_size, cell_size, cell_size]
    # again, depends on Dimension
    h5grp.attrs['Origin'] = h5origin
    # leave this line out if not cell centered.  If set to False, it will still
    # be true (issue with HDF5 and Fortran)
    h5grp.attrs['Cell Centered'] = [True]
    h5grp.attrs['Interpolation Method'] = np.string_('Step')
    h5grp.create_dataset(
        'Data', data=khdf5)  #does this matter that it is also called data?
    h5file2.close()

    # Write porosity as a gridded dataset for use with PFLOTRAN.
    print('And also porosity as a gridded dataset')
    h5file2 = File(filenames['porosity'], 'w')
    # 3d uniform grid
    h5grp = h5file2.create_group('Porosity')
    # 3D will always be XYZ where as 2D can be XY, XZ, etc. and 1D can be X, Y or Z
    h5grp.attrs['Dimension'] = np.string_('XYZ')
    # based on Dimension, specify the uniform grid spacing
    h5grp.attrs['Discretization'] = [cell_size, cell_size, cell_size]
    # again, depends on Dimension
    h5grp.attrs['Origin'] = h5origin
    # leave this line out if not cell centered.  If set to False, it will still
    # be true (issue with HDF5 and Fortran)
    h5grp.attrs['Cell Centered'] = [True]
    h5grp.attrs['Interpolation Method'] = np.string_('Step')
    h5grp.create_dataset('Data', data=phdf5)
    h5file2.close()

    # Write tortuosity as a gridded dataset for use with PFLOTRAN.
    print('And also tortuosity as a gridded dataset')
    h5file2 = File(filenames['tortuosity'], 'w')
    # 3d uniform grid
    h5grp = h5file2.create_group('Tortuosity')
    # 3D will always be XYZ where as 2D can be XY, XZ, etc. and 1D can be X, Y or Z
    h5grp.attrs['Dimension'] = np.string_('XYZ')
    # based on Dimension, specify the uniform grid spacing
    h5grp.attrs['Discretization'] = [cell_size, cell_size, cell_size]
    # again, depends on Dimension
    h5grp.attrs['Origin'] = h5origin
    # leave this line out if not cell centered.  If set to False, it will still
    # be true (issue with HDF5 and Fortran)
    h5grp.attrs['Cell Centered'] = [True]
    h5grp.attrs['Interpolation Method'] = np.string_('Step')
    h5grp.create_dataset('Data', data=tortuosity_factor / phdf5)
    h5file2.close()

    # Write anisotropic permeability as a gridded dataset for use with PFLOTRAN.
    print('and anisotropic k')
    h5file3 = File(filenames['anisotropic_k'], 'w')
    # 3d uniform grid
    h5grp = h5file3.create_group('PermeabilityX')
    # 3D will always be XYZ where as 2D can be XY, XZ, etc. and 1D can be X, Y or Z
    h5grp.attrs['Dimension'] = np.string_('XYZ')
    # based on Dimension, specify the uniform grid spacing
    h5grp.attrs['Discretization'] = [cell_size, cell_size, cell_size]
    # again, depends on Dimension
    h5grp.attrs['Origin'] = h5origin
    # leave this line out if not cell centered.  If set to False, it will still
    # be true (issue with HDF5 and Fortran)
    h5grp.attrs['Cell Centered'] = [True]
    h5grp.attrs['Interpolation Method'] = np.string_('Step')
    h5grp.create_dataset(
        'Data', data=kx)  #does this matter that it is also called data?

    # 3d uniform grid
    h5grp = h5file3.create_group('PermeabilityY')
    # 3D will always be XYZ where as 2D can be XY, XZ, etc. and 1D can be X, Y or Z
    h5grp.attrs['Dimension'] = np.string_('XYZ')
    # based on Dimension, specify the uniform grid spacing
    h5grp.attrs['Discretization'] = [cell_size, cell_size, cell_size]
    # again, depends on Dimension
    h5grp.attrs['Origin'] = h5origin
    # leave this line out if not cell centered.  If set to False, it will still
    # be true (issue with HDF5 and Fortran)
    h5grp.attrs['Cell Centered'] = [True]
    h5grp.attrs['Interpolation Method'] = np.string_('Step')
    h5grp.create_dataset(
        'Data', data=ky)  #does this matter that it is also called data?

    # 3d uniform grid
    h5grp = h5file3.create_group('PermeabilityZ')
    # 3D will always be XYZ where as 2D can be XY, XZ, etc. and 1D can be X, Y or Z
    h5grp.attrs['Dimension'] = np.string_('XYZ')
    # based on Dimension, specify the uniform grid spacing
    h5grp.attrs['Discretization'] = [cell_size, cell_size, cell_size]
    # again, depends on Dimension
    h5grp.attrs['Origin'] = h5origin
    # leave this line out if not cell centered.  If set to False, it will still
    # be true (issue with HDF5 and Fortran)
    h5grp.attrs['Cell Centered'] = [True]
    h5grp.attrs['Interpolation Method'] = np.string_('Step')
    h5grp.create_dataset(
        'Data', data=kz)  #does this matter that it is also called data?
    h5file3.close()

    # Write materials.h5 to inactivate non-fracture cells in PFLOTRAN.
    print('Write material id file for inactivating matrix cells')
    h5file4 = File(filenames['materials'], 'w')
    materials_group = h5file4.create_group('Materials')
    iarray = np.zeros((nx * ny * nz), '=i4')
    marray = np.zeros((nx * ny * nz), '=i4')
    for i in range(nx * ny * nz):
        iarray[i] = i + 1
        if k_iso[i] == matrix_perm:
            marray[i] = 0
        else:
            marray[i] = 1
    h5dset = materials_group.create_dataset('Cell Ids', data=iarray)
    h5dset = materials_group.create_dataset('Material Ids', data=marray)
    h5file4.close()


def map_dfn_2_pflotran(self,
                    mat_perm,
                    mat_porosity,
                    cell_size,
                    tortuosity_factor =  0.001,
                    correction_factor=True,
                    output_dir="ecpm"):
    """ This script takes the top-level directory of the dfn and maps it to an ecpm, saving the ecpm files in that directory
  
  Parameters
  -----------------
    self : dfnWorks object
      
    cell_size : float
      The cell size (meters) to use for the meshing. Default: 20

    meshing_case : string 
      A case switch for the meshing to be performed. 

    user_defined : boolean
      If passed, strips the 6 user-defined fractures out before meshing. 

    correction_factor : boolean
      Apply stairstep correction from EDFM to  not applied to permeability

    
  Returns
  -----------------
    None

  Authors
  -----------------
    Emily Stein (ergiamb@sandia.gov)
    Applied Systems Analysis and Research, 8844
    Sandia National Laboratories
  
    Edited by Teresa Portone (tporton@sandia.gov) 11/2020 to take arguments.

    Rosie Leone 

    Jeffrey Hyman 07/2023 - Integration with pydfnWorks 

  Notes
  -----------------


  """

    filenames = setup_output_dir(output_dir)

    domain_origin, nx, ny, nz  = setup_domain(self.domain, cell_size)

    fractures, k_iso, k_aniso, porosity = self.get_perms_and_porosity(domain_origin, nx, ny, nz, cell_size, mat_perm, mat_porosity, correction_factor)

    write_h5_files(origin, domain_origin, filenames, nx, ny, nz, cell_size,
                fractures, k_iso, k_aniso, porosity, mat_perm, tortuosity_factor)