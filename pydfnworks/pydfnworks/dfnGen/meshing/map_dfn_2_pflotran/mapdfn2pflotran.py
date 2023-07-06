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

   Author: Emily Stein (ergiamb@sandia.gov)
           Applied Systems Analysis and Research, 8844
           Sandia National Laboratories

   Date: 07/13/18
   SAND Number: SAND2018-7605 O

   Edited by Teresa Portone (tporton@sandia.gov) 11/2020
   to take arguments.
'''
import os.path as op
import sys, os

sys.path.append(op.abspath(op.dirname(sys.argv[0])))
import numpy as np
from mapdfn import *
from h5py import File
import argparse
from glob import glob


def main(args):
    parser = argparse.ArgumentParser(
        description=
        "This script takes the top-level directory of the dfn and maps it to an ecpm, saving the ecpm files in that directory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "dfn_dir", help="The directory containing the generated dfn files.")
    parser.add_argument("-d",
                        "--cell_size",
                        help="The cell size to use for the meshing.",
                        default=20,
                        type=float)
    parser.add_argument("--meshing_case",
                        help="A case switch for the meshing to be performed. ",
                        choices=['whole_domain', 'repo'],
                        default='whole_domain')
    parser.add_argument("--no_user_defined", help="If passed, strips the 6 user-defined fractures "\
        "out before meshing.", action='store_true' )
    parser.add_argument("--no_correction_factor", help="If passed, stairstep correction not applied to permeability "\
        "out before meshing.", action='store_false' )
    pa = parser.parse_args(args)

    if pa.no_user_defined and (not pa.meshing_case == 'whole_domain'):
        sys.exit("ERROR: filtering out user-defined fractures is only compatible with meshing "\
            "the whole domain.")

    if not op.isdir(pa.dfn_dir):
        sys.exit("ERROR: you must pass a directory as the dfn_dir argument.")

    dfn_dir = op.abspath(pa.dfn_dir) + '/dfnGen_output/'
    if not len(glob(dfn_dir + 'radii_Final.dat')) > 0:
        sys.exit("ERROR: you must pass a directory holding generated DFN files as the "\
            "dfn_dir argument.")
    """ Setting the properties that are shared no matter the meshing case """
    k_background = 1.e-18
    bulk_por = 0.005
    tortuosity_factor = 0.001
    """ Setting the properties that depend on the meshing case """
    # origin of area of map in DFN domain coordinates where (0,0,0) is center of DFN
    # PFLOTRAN takes origin at bottom back corner
    domain_origin = [-500, -500, -500]
    if pa.meshing_case == 'whole_domain':
        out_dir = dfn_dir + 'cpm'
        if pa.no_user_defined: out_dir += '_no_user_defined'
        if not pa.cell_size == 20:
            out_dir += f'/meshed_cell_size_{pa.cell_size}/'
        filenames = {
            'mapEllipses_txt': out_dir + '/mapELLIPSES.txt',
            "mapEllipses_h5": out_dir + '/mapELLIPSES.h5',
            'isotropic_k': out_dir + '/isotropic_k.h5',
            'anisotropic_k': out_dir + '/anisotropic_k.h5',
            'tortuosity': out_dir + '/tortuosity.h5',
            'porosity': out_dir + '/porosity.h5',
            'materials': out_dir + '/materials.h5'
        }
        # Origin of area to map in DFN domain coordinates (0,0,0 is center of DFN)
        origin = domain_origin
        [Lx, Ly, Lz] = [1000, 1000, 1000]
        d = pa.cell_size
        if Lx % d + Ly % d + Lz % d > 0:
            sys.exit(f"ERROR: The cell size you've specified, {d} m, does not evenly "\
                "divide the domain. Domain size: {Lx} x {Ly} x {Lz} m^3.")
        [nx, ny, nz] = [int(Lx / d), int(Ly / d), int(Lz / d)]
    if pa.meshing_case == 'repo':
        sys.exit(
            "ERROR: You haven't updated the origin for the repo for this problem yet!"
        )
        out_dir = dfn_dir + 'cpm_repository'
        if not pa.cell_size == 20:
            out_dir += '/meshed_cell_size_{}'.format(pa.cell_size)
        filenames = {
            'mapEllipses_txt': out_dir + 'mapELLIPSES.txt',
            "mapEllipses_h5": out_dir + '/mapELLIPSES.h5',
            'isotropic_k': out_dir + '/rep_isotropic_k.h5',
            'anisotropic_k': out_dir + '/rep_anisotropic_k.h5',
            'tortuosity': out_dir + '/rep_tortuosity.h5',
            'porosity': out_dir + '/rep_porosity.h5',
            'materials': out_dir + '/rep_materials.h5'
        }
        # Origin of area to map in DFN domain coordinates (0,0,0 is center of DFN)
        origin = [-2000, -350,
                  25.0]  # Set this to the origin of the repo region
        [Lx, Ly, Lz] = [1075, 700,
                        50]  # Set this to the extent of the repo region
        d = pa.cell_size / 3  # scale this appropriately or do a hard setting
        #   if Lx%d + Ly%d + Lz%d > 0:
        #     sys.exit(f"ERROR: The cell size you've specified, {d} m, does not evenly  "\
        #         "divide the domain. Domain size: {Lx} x {Ly} x {Lz} m^3.")
        [nx, ny, nz] = [int(Lx / d), int(Ly / d), int(Lz / d)]
    # this is origin of mapping in cpm domain. (0,0,0) is origin of CPM,
    # though it doesn't have to be)
    h5origin = [x - y for x, y in zip(origin, domain_origin)]

    # Call mapdfn functions
    print('Mapping DFN to grid')
    ellipses = readEllipse(dfn_dir + 'radii_Final.dat',
                           dfn_dir + 'normal_vectors.dat',
                           dfn_dir + 'translations.dat')
    apertures = readApertures(dfn_dir + '../aperture.dat')
    perms = readPerms(dfn_dir + '../perm.dat')
    if pa.no_user_defined:
        ellipses = ellipses[6:]
        apertures = apertures[6:]
        perms = perms[6:]
    fracture = map_dfn(ellipses, origin, nx, ny, nz, d)
    T = findT(apertures, perms)

    print("Creating output directory " + out_dir)
    if not op.exists(out_dir): os.makedirs(out_dir)

    k_iso = permIso(fracture, T, d, k_background)
    if pa.no_correction_factor:
        k_aniso = permAniso(fracture,
                            ellipses,
                            T,
                            d,
                            k_background,
                            out_dir=out_dir,
                            correction_factor=False)
    else:
        k_aniso = permAniso(fracture,
                            ellipses,
                            T,
                            d,
                            k_background,
                            out_dir=out_dir)
    print('Calculating fracture permeability')
    por = porosity(fracture, apertures, d, bulk_por)

    # Fill arrays that will go into PFLOTRAN h5 files.
    # Also write mapELLIPSES.txt for later use.
    # Potentially large file. If you have no use for it, don't write it.
    fout = open(filenames['mapEllipses_txt'], 'w')
    fout.write('#x, y, z, number of fractures, fracture numbers\n')

    #arrays for making PFLOTRAN hf file
    x = np.zeros(nx + 1, '=f8')
    x[nx] = h5origin[0] + nx * d
    y = np.zeros(ny + 1, '=f8')
    y[ny] = h5origin[1] + ny * d
    z = np.zeros(nz + 1, '=f8')
    z[nz] = h5origin[2] + nz * d
    a = np.zeros((nx, ny, nz), '=f8')
    khdf5 = np.zeros((nx, ny, nz), '=f8')
    kx = np.zeros((nx, ny, nz), '=f8')
    ky = np.zeros((nx, ny, nz), '=f8')
    kz = np.zeros((nx, ny, nz), '=f8')
    phdf5 = np.zeros((nx, ny, nz), '=f8')

    print('Writing text file')
    #write mapELLIPSES.txt and fill arrays
    for k in range(nz):
        z[k] = h5origin[2] + k * d
        for j in range(ny):
            y[j] = h5origin[1] + j * d
            for i in range(nx):
                index = i + nx * j + nx * ny * k
                x[i] = h5origin[0] + i * d
                khdf5[i][j][k] = k_iso[index]
                kx[i][j][k] = k_aniso[index][0]
                ky[i][j][k] = k_aniso[index][1]
                kz[i][j][k] = k_aniso[index][2]
                phdf5[i][j][k] = por[index]
                fout.write('%e  %e  %e  %i %e ' %
                           (origin[0] + i * d + d / 2., origin[1] + j * d +
                            d / 2., origin[2] + k * d + d / 2.,
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
    h5grp.attrs['Discretization'] = [d, d, d]
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
    h5grp.attrs['Discretization'] = [d, d, d]
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
    h5grp.attrs['Discretization'] = [d, d, d]
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
    h5grp.attrs['Discretization'] = [d, d, d]
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
    h5grp.attrs['Discretization'] = [d, d, d]
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
    h5grp.attrs['Discretization'] = [d, d, d]
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
        if k_iso[i] == k_background:
            marray[i] = 0
        else:
            marray[i] = 1
    h5dset = materials_group.create_dataset('Cell Ids', data=iarray)
    h5dset = materials_group.create_dataset('Material Ids', data=marray)
    h5file4.close()
    print('Done!')


if __name__ == '__main__':
    main(sys.argv[1:])
