import numpy as np
from h5py import File
import itertools
import time


def create_h5_arrays(nx, ny, nz, cell_size, k_iso, k_aniso, matrix_perm,
                     porosity, cell_fracture_id, matrix_on, h5origin):
    """ Converts values into arrays to be dumped into h5 files

    Parameters
    ------------------
        nx : int 

        ny : int 

        nz : int 

        cell_size : int

        k_iso : float 

        k_aniso 

    Returns
    ------------------


    Notes
    ------------------

     
    
    """

    # h5origin = [x - y for x, y in zip(domain_origin, domain_origin)]
    # h5origin = [0, 0, 0]
    # arrays for PFLOTRAN hf files
    x = np.zeros(nx + 1, '=f8')
    x[nx] = h5origin[0] + nx * cell_size
    y = np.zeros(ny + 1, '=f8')
    y[ny] = h5origin[1] + ny * cell_size
    z = np.zeros(nz + 1, '=f8')
    z[nz] = h5origin[2] + nz * cell_size
    fracture_id = np.zeros((nx, ny, nz), '=f8')
    khdf5 = np.zeros((nx, ny, nz), '=f8')
    kx = np.zeros((nx, ny, nz), '=f8')
    ky = np.zeros((nx, ny, nz), '=f8')
    kz = np.zeros((nx, ny, nz), '=f8')
    phdf5 = np.zeros((nx, ny, nz), '=f8')

    index_set = itertools.product(range(nz), range(ny), range(nx))
    for k, j, i in index_set:
        # complute xyz coords
        x[i] = h5origin[0] + i * cell_size
        y[j] = h5origin[1] + j * cell_size
        z[k] = h5origin[2] + k * cell_size
        # compute linear index
        index = i + nx * j + nx * ny * k
        # convert linear index to 3D arrays
        khdf5[i][j][k] = k_iso[index]
        kx[i][j][k] = k_aniso[index][0]
        ky[i][j][k] = k_aniso[index][1]
        kz[i][j][k] = k_aniso[index][2]
        phdf5[i][j][k] = porosity[index]
        if len(cell_fracture_id[index]) > 0:
            fracture_id[i][j][k] = cell_fracture_id[index][
                0] + 1  # color by the first fracture number in the list (+1 is becuase fracture indices start at 0)
        else:
            fracture_id[i][j][k] = 0  # color it zero

    # compute indicator arrays for material properties
    idx_array = np.zeros((nx * ny * nz), '=i4')
    mat_array = np.zeros((nx * ny * nz), '=i4')
    for i in range(nx * ny * nz):
        idx_array[i] = i + 1
        if not matrix_on:
            if k_iso[i] == matrix_perm:
                mat_array[i] = 0
            else:
                mat_array[i] = 1
        else:
            mat_array[i] = 1

    return x, y, z, fracture_id, khdf5, kx, ky, kz, phdf5, idx_array, mat_array


def write_h5_files(filenames, nx, ny, nz, cell_size, cell_fracture_id, k_iso,
                   k_aniso, porosity, matrix_perm, tortuosity_factor, matrix_on, h5origin):
    """ Write informaiton into h5 files for pflotran run. 

    Parameters
    ----------------



    Returns
    ------------



    Notes
    -----------
        * All files are writting into the output_dir. 
        * mapdfn.h5 can be opened in Paraview by chosing "PFLOTRAN file" format. This file contains all material, porosity, and permeability information
    
    """
    #x, y, z, material_id, khdf5, kx, ky, kz, phdf5, h5origin, idx_array, mat_array = create_h5_arrays(
    #    origin, domain_origin, nx, ny, nz, cell_size, k_iso, k_aniso,
    #    matrix_perm, porosity, cell_fracture_id)

    x, y, z, material_id, khdf5, kx, ky, kz, phdf5, idx_array, mat_array = create_h5_arrays(
        nx, ny, nz, cell_size, k_iso, k_aniso, matrix_perm, porosity,
        cell_fracture_id, matrix_on, h5origin)
    print("** Dumping h5 files **")
    t0 = time.time()

    print(f"--> Writting {filenames['mapdfn']} file for viz")
    with File(filenames['mapdfn'], 'w') as h5file:
        dataset_name = 'Coordinates/X [m]'
        h5dset = h5file.create_dataset(dataset_name, data=x)
        dataset_name = 'Coordinates/Y [m]'
        h5dset = h5file.create_dataset(dataset_name, data=y)
        dataset_name = 'Coordinates/Z [m]'
        h5dset = h5file.create_dataset(dataset_name, data=z)
        dataset_name = 'Time:  0.00000E+00 y/Perm'
        hfdset = h5file.create_dataset(dataset_name, data=khdf5)
        dataset_name = 'Time:  0.00000E+00 y/Fracture'
        h5dset = h5file.create_dataset(dataset_name, data=material_id)
        dataset_name = 'Time:  0.00000E+00 y/PermX'
        h5dset = h5file.create_dataset(dataset_name, data=kx)
        dataset_name = 'Time:  0.00000E+00 y/PermY'
        h5dset = h5file.create_dataset(dataset_name, data=ky)
        dataset_name = 'Time:  0.00000E+00 y/PermZ'
        h5dset = h5file.create_dataset(dataset_name, data=kz)
        dataset_name = 'Time:  0.00000E+00 y/Porosity'
        hfdset = h5file.create_dataset(dataset_name, data=phdf5)

    # Write isotropic permeability to a gridded dataset for use with PFLOTRAN.
    print(
        f"--> Writing isotropic permeability into {filenames['isotropic_k']} as a gridded dataset"
    )
    with File(filenames['isotropic_k'], 'w') as h5file2:
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
        h5grp.attrs['Space Interpolation Method'] = np.string_('Step')
        h5grp.create_dataset(
            'Data', data=khdf5)  #does this matter that it is also called data?

    # Write porosity as a gridded dataset for use with PFLOTRAN.
    print(
        f"--> Writting porosity into {filenames['porosity']} as a gridded dataset"
    )
    with File(filenames['porosity'], 'w') as h5file2:
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
        h5grp.attrs['Space Interpolation Method'] = np.string_('Step')
        h5grp.create_dataset('Data', data=phdf5)

    # Write tortuosity as a gridded dataset for use with PFLOTRAN.
    print(
        f"--> Writting tortuosity into {filenames['tortuosity']} as a gridded dataset"
    )
    with File(filenames['tortuosity'], 'w') as h5file2:
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
        h5grp.attrs['Space Interpolation Method'] = np.string_('Step')
        h5grp.create_dataset('Data', data=tortuosity_factor / phdf5)

    # Write anisotropic permeability as a gridded dataset for use with PFLOTRAN.
    print(
        f"--> Writting anisotropic permeability into {filenames['anisotropic_k']} as a gridded dataset"
    )
    with File(filenames['anisotropic_k'], 'w') as h5file3:
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
        h5grp.attrs['Space Interpolation Method'] = np.string_('Step')
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
        h5grp.attrs['Space Interpolation Method'] = np.string_('Step')
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
        h5grp.attrs['Space Interpolation Method'] = np.string_('Step')
        h5grp.create_dataset(
            'Data', data=kz)  #does this matter that it is also called data?

    # Write materials.h5 to inactivate non-fracture cells in PFLOTRAN.
    print(
        f"--> Writting material id into {filenames['materials']} file for inactivating matrix cells"
    )
    with File(filenames['materials'], 'w') as h5file4:
        materials_group = h5file4.create_group('Materials')
        h5dset = materials_group.create_dataset('Cell Ids', data=idx_array)
        h5dset = materials_group.create_dataset('Material Ids', data=mat_array)
    t1 = time.time()
    print(
        f'** Writting h5 files complete. Time required : {t1 - t0:0.2f} seconds **\n'
    )
