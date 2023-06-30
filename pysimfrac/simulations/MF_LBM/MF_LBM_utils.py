from subprocess import run
from os import mkdir
from shutil import copy, move
from copy import deepcopy as cp

import numpy as np
import pickle


def create_folder(folder_name):
    """Create a new folder with the given name if it does not already exist
    
    Parameters
    ----------
        folder_name (str): 
            Name of the folder to create.

    Returns
    -------
        None

    Notes
    -----
        This function uses the `mkdir` function from the `os` module to create a new folder with the specified name.
        If the folder already exists, it raises a `FileExistsError` which is caught and ignored in this function.
    
    """
    try:
        mkdir(folder_name)
    except FileExistsError:
        pass


def replace_word(file, old_word, new_word):
    """Replace occurrences of a word in a file with a new word
    
    Parameters
    ----------
    file : str
        Path to the file.
    old_word : str
        The word to replace.
    new_word : str
        The new word to use.

    Returns
    -------
        None

    Notes
    -----
        This function reads the content of the file, replaces all occurrences of `old_word` with `new_word`,
        and writes the modified content back to the file.
    
    """
    f = open(file, 'r')
    filedata = f.read()
    f.close()

    newdata = filedata.replace(old_word, new_word)

    f = open(file, 'w')
    f.write(newdata)
    f.close()


class write_MFLBM:
    """Class for writing MFLBM configuration files"""

    def __init__(
        self,
        simfrac_obj,
        mu_1=0.4,
        mu_2=0.4,
        sigma=0.03,
        theta=45,
        Ca_num=1e-4,
        ntime_visual=20000,
        buffer_layers=10,
        gpus=1,
        num_hrs=14,
        num_mins='00',
        allocation=None,
    ):
        """Initialize the write_MFLBM class
        
        Parameters
        ----------
            self : simfrac object 
            simfrac_obj : simfrac object 
            mu_1 : float, 
                Fluid 1 viscosity (default is 0.4).
            mu_2 : float, 
                Fluid 2 viscosity (default is 0.4).
            sigma : float, 
                Surface tension (default is 0.03).
            theta : int, 
                Theta value (default is 45).
            Ca_num : float, 
                Capillary number (default is 1e-4).
            ntime_visual : int,
                Visual time (default is 20000).
            buffer_layers : int,
                Number of buffer layers (default is 10).
            gpus : int,
                Number of GPUs (default is 1).
            num_hrs : int, 
                Number of hours (default is 14).
            num_mins : str,
                Number of minutes (default is '00').
            allocation : None or str
                Allocation information (default is None).

        Returns
        -------
            None

        Notes
        -----
            This constructor initializes the write_MFLBM class. It creates a new folder for the simulation, copies necessary files,
            and writes the configuration files based on the provided parameters.
        """
        
        # Create a folder named 'sims' if it doesn't exist
        create_folder('sims')
        
        #create a new simulation folder
        self.folder_num = self.create_new_folder()
        self.folder_path = f'sims/frac_{self.folder_num}'

        self.my_frac = cp(simfrac_obj)

        # set the simulation properties
        self.mu_1 = mu_1
        self.mu_2 = mu_2
        self.ntime_visual = ntime_visual
        self.sigma = sigma
        self.theta = theta
        self.Ca_num = Ca_num
        self.buffer_layers = buffer_layers
        self.gpus = gpus
        self.num_mins = num_mins
        self.num_hrs = num_hrs
        self.allocation = allocation
        
        #transpose the fracture.  MF_LBM must displace fluid in the z direction
        frac_3D = 1 - np.transpose(simfrac_obj.frac_3D, (2, 0, 1))
        self.frac_dims = frac_3D.shape

        #create simulation subfolders
        create_folder(f'{self.folder_path}/out1.output')
        create_folder(f'{self.folder_path}/out2.checkpoint')
        create_folder(f'{self.folder_path}/out3.field_data')
        create_folder(f'{self.folder_path}/output')

        # Copy necessary data files
        self.copy_data()

        # Write geometry file
        self.write_geom(frac_3D)

        # Write input_parameter.txt, path_info.txt, and job_status.txt
        self.write_input1()
        self.write_input2(lbm_loc='dummylbmloc')
        self.write_input3()

        # Update simulation_control.txt file with simulation parameters
        self.edit_inputs()
        
        # Dump simulation pickle
        self.save_pickle()
        
        # Dump fracture pickle
        with open(f'{self.folder_path}/surf_frac_object.pk', 'wb') as f:
            pickle.dump(simfrac_obj, f, protocol=pickle.HIGHEST_PROTOCOL)

    def create_new_folder(self):
        """Create a new folder for the simulation
        
        Parameters
        -------
            self : simfrac object
            
        Returns
        -------
            int : i
                Number of the created folder.

        Notes
        -----
            This function tries to create a new folder by incrementing the folder number until it finds a number
            that doesn't conflict with an existing folder. It returns the number of the created folder.
        """
        for i in range(10000000000):
            try:
                mkdir(f'sims/frac_{i}')
                break
            except FileExistsError:
                continue
        return i

    def write_geom(self, frac):
        """Write the geometry file for the simulation
        
        Parameters
        ----------
            self : simfrac object
            frac : ndarray
                3D array representing the geometry.

        Returns
        -------
            None

        Notes
        -----
            This function writes the geometry file (frac.dat) by flattening the `frac` array and appending its shape.
            The resulting data is saved in text format using `np.savetxt`.
        """
        tofile = np.append([*frac.shape], frac.flatten('F'))
        np.savetxt(f'{self.folder_path}/frac.dat', tofile, fmt='%.0f')

    def write_input1(self):
        """Write input_parameter.txt file for the simulation
        
        Returns
        -------
            None

        Notes
        -----
            This function writes the input_parameter.txt file by writing various parameters to it.
        """
        with open(f'{self.folder_path}/input_parameter.txt', 'w') as f:
            f.write('wall_file_path:\n')
            f.write('frac.dat\n')
            f.write(f'{self.buffer_layers},{self.buffer_layers}   !buffer layers\n')
            f.write('0       ! crop the original domain option: 0-not crop; 1-crop\n')
            f.write('120.5, 120.5, 120.5  !crop center (only when crop_option=1)\n')
            f.write('160, 160, 160     !cropped domain size, not including buffer zone (only when crop_option=1)\n')

    def write_input2(self, lbm_loc):
        """Write path_info.txt file for the simulation
        
        Parameters
        ----------
            self : simfrac object            
            lbm_loc : str
                Location of the MF_LBM executable.

        Returns
        -------
            None

        Notes
        -----
            This function writes the path_info.txt file by writing the location of the LBM executable and other parameters to it.
        """
        with open(f'{self.folder_path}/path_info.txt', 'w') as f:
            f.write('# executable location\n')
            f.write(f'{lbm_loc}\n')
            f.write('# geometry file\n')
            f.write('frac.dat\n')
            f.write('# preprocessed boundary nodes info file of the corresponding above geometry file (if geometry_preprocess_cmd = 1)\n')
            f.write('placeholder\n')

    def write_input3(self):
        """Write job_status.txt file for the simulation
        Parameters
        -------
            self : simfrac object
        
        Returns
        -------
            None

        Notes
        -----
            This function writes the job_status.txt file with the status "new_simulation".
        """
        with open(f'{self.folder_path}/job_status.txt', 'w') as f:
            f.write('new_simulation')

    def copy_data(self):
        """Copy template files to the simulation folder
        
        Parameters
        -------
            self : simfrac object
                
        Returns
        -------
            None

        Notes
        -------
            This function copies template files from the "templates" directory to the simulation folder.
        """
        #a.out is created through the compilation of readwritefortran.f90
        #see MP_LBM/README.md for more info.
        
        copy('templates/a.out', f'{self.folder_path}')
        copy('templates/simulation_control.txt', f'{self.folder_path}')


    def edit_inputs(self):
        """Edit the input files with the simulation parameters
        Parameters
        -------
            self : simfrac object
        
        Returns
        -------
            None

        Notes
        -----
            This function updates the content of 'simulation_control.txt' file using the specified simulation parameters.
        """
        replace_word(f'{self.folder_path}/Slurm', 'JOBNAME', f"frac_{self.folder_num}")

        print(self.frac_dims)
        replace_word(f'{self.folder_path}/simulation_control.txt',
                     'lattice_dimensions 256,256,100',
                     f"lattice_dimensions {self.frac_dims[0]},{self.frac_dims[1]},{self.frac_dims[2]+self.buffer_layers*2}")

        replace_word(f'{self.folder_path}/simulation_control.txt',
                     'excluded_layers 10,10',
                     f"excluded_layers {self.buffer_layers},{self.buffer_layers}")

        replace_word(f'{self.folder_path}/simulation_control.txt',
                     'fluid1_viscosity 0.4',
                     f"fluid1_viscosity {self.mu_1}")

        replace_word(f'{self.folder_path}/simulation_control.txt',
                     'fluid2_viscosity 0.4',
                     f"fluid2_viscosity {self.mu_2}")

        replace_word(f'{self.folder_path}/Slurm',
                     'time=9:00:00',
                     f"time={self.num_hrs}:{self.num_mins}:00")

        replace_word(f'{self.folder_path}/simulation_control.txt',
                     'surface_tension 0.03',
                     f"surface_tension {self.sigma}")

        replace_word(f'{self.folder_path}/simulation_control.txt',
                     'theta 45',
                     f"theta {self.theta}")

        replace_word(f'{self.folder_path}/simulation_control.txt',
                     'capillary_number 100d-5',
                     f"capillary_number {self.Ca_num}")

        replace_word(f'{self.folder_path}/simulation_control.txt',
                     'ntime_visual 20000',
                     f"ntime_visual {self.ntime_visual}")

    def save_pickle(self):
        """Save a pickle file with the simulation parameters
        
        Parameters
        -------
            self : simfrac object
        
        Returns
        -------
            None

        Notes
        -----
            This function saves a pickle file with the simulation parameters for future reference.
        """
        with open(f'{self.folder_path}/sim_parameters.pkl', 'wb') as f:
            pickle.dump(
                {
                    'folder_num': self.folder_num,
                    'mu_1': self.mu_1,
                    'mu_2': self.mu_2,
                    'ntime_visual': self.ntime_visual,
                    'sigma': self.sigma,
                    'theta': self.theta,
                    'Ca_num': self.Ca_num,
                    'buffer_layers': self.buffer_layers,
                    'gpus': self.gpus,
                    'num_mins': self.num_mins,
                    'num_hrs': self.num_hrs,
                    'allocation': self.allocation,
                },
                f,
                protocol=pickle.HIGHEST_PROTOCOL,
            )
