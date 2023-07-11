import os, sys

def setup_output_dir(output_dir, jobname):

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
    
    num_cells = nx*ny*nz
    print(nx,ny,nz,num_cells)
    print(domain['x'] % cell_size, domain['y'] % cell_size, domain['z'] % cell_size )
    if domain['x'] % cell_size + domain['y'] % cell_size + domain['z'] % cell_size > 0:
        error_msg = f"Error: The cell size you've specified, {cell_size} m, does not evenly divide the domain. Domain size: {domain['x']} x {domain['y']} x {domain['z']} m^3."
        sys.stderr.write(error_msg)
        sys.exit(1)

    return domain_origin, nx, ny, nz, num_cells


