# This script demonstrates the creation of multiple multiphase fracture
# simulations utlizing the MF_LBM simulator.  Please see README.md for
# more information

import os  
from subprocess import run  
from MF_LBM_utils import write_MFLBM  
from simfrac import SimFrac  

# Create a SimFrac object with specified parameters
myfrac = SimFrac(h=1.0, lx=512, ly=128, method="spectral")

# Create 3 fractures with different seeds
for i in range(1, 4):
    # Set parameters for the SimFrac object
    myfrac.params['aniso']['value'] = 0.0
    myfrac.params['H']['value'] = 0.75
    myfrac.params['roughness']['value'] = 4
    myfrac.params['mismatch']['value'] = 0.25
    myfrac.params['lambda_0']['value'] = 0.6
    myfrac.params['model']['value'] = 'smooth'
    myfrac.params['seed']['value'] = i
    
    # Create the fracture
    myfrac.create_fracture()

    # Set the mean aperture of the fracture
    myfrac.set_mean_aperture(15) 

    # Voxelize the fracture with a padding of 5 voxels    
    myfrac.voxelize(solid_voxels=5)  

    # Compute the autocorrelation function
    myfrac.compute_acf()  

    # List of capillary numbers
    cas = [1e-2, 1e-3, 1e-4]  
    
    # Create MF LBM simulation folders for each fracture and capillary number
    for j in cas:
        lbm = write_MFLBM(
            simfrac_obj=myfrac,
            mu_1=0.04,
            mu_2=0.04,
            sigma=0.03,
            theta=45,
            Ca_num=j,
            buffer_layers=10,
            gpus=4,
            num_hrs=1,
            allocation=None,
        )
        
        # Change the current working directory to the simulation folder
        os.chdir(f'./{lbm.folder_path}')
        
        # After compiling readwritefortran.f90 separately to create a.out
        # Run the fortran executable to create the input geometry
        run('./a.out')
        
        # After compiling MF_LBM provide the path to executable and run simulation
        run('srun -n 1 /PATH/TO/EXECUTABLE/MF_LBM.gpu')
              
        # Change the current working directory back to the parent directory
        os.chdir(f'../../')
