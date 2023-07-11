import os, sys


def setup_output_dir(output_dir, jobname):
    """ Create ECPM output directory

    Parameters
    ----------------
        output_dir : string
            relative path name of output directory. 

    Returns
    ------------
        filenames : dict
            Dictionary of h5 filenames 

    Notes
    ------------
        The name is combined with DFN.jobname to be an absolute path DFN.jobname + / + output_dir
    """
    print(f"--> Creating output directory {output_dir}")
    output_dir = jobname + os.sep + output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        os.chdir(output_dir)
    filenames = {
        "mapdfn": output_dir + '/mapdfn.h5',
        'isotropic_k': output_dir + '/isotropic_k.h5',
        'anisotropic_k': output_dir + '/anisotropic_k.h5',
        'tortuosity': output_dir + '/tortuosity.h5',
        'porosity': output_dir + '/porosity.h5',
        'materials': output_dir + '/materials.h5'
    }

    return filenames


def setup_domain(domain, cell_size):
    """ Initialize domain and discretization

    Parameters
    -----------------
        domain : dictionary
            Domain size in x, y, z from DFN object
        cell_size : float
            Hexahedron cell size

    Returns
    -----------------
        domain_origin : list 
            min_x, min_y, min_z values of domain
        nx : int
            Number of cells in x direction 
        ny : int
            Number of cells in y direction
        nz : int
            Number of cells in z direction 
        num_cells : int 
            Total number of cells in the domain

    Notes
    -----------------
        Does not work for non-integer cells size
    
    
    
    """
    print("--> Computing discrete domain parameters")
    domain_origin = [
        -1 * domain['x'] / 2, -1 * domain['y'] / 2, -1 * domain['z'] / 2
    ]
    # Origin of area to map in DFN domain coordinates (0,0,0 is center of DFN)
    [nx, ny, nz] = [
        int(domain['x'] / cell_size),
        int(domain['y'] / cell_size),
        int(domain['z'] / cell_size)
    ]

    num_cells = nx * ny * nz

    if domain['x'] % cell_size + domain['y'] % cell_size + domain[
            'z'] % cell_size > 0:
        error_msg = f"Error: The cell size you've specified, {cell_size} m, does not evenly divide the domain. Domain size: {domain['x']} x {domain['y']} x {domain['z']} m^3."
        sys.stderr.write(error_msg)
        sys.exit(1)
    print(f"--> Hexahedron edge length {cell_size} m")
    print(f"--> Domain is {nx} x {ny} x {ny} cells. ")
    print(f"--> Total number of cells {num_cells}\n")
    return domain_origin, nx, ny, nz, num_cells
