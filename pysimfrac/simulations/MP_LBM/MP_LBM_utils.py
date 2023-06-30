from subprocess import run
import os
from os import mkdir
from shutil import copy, move
from argparse import Namespace

import pandas as pd
import numpy as np

import pickle
from copy import copy as cp

from skimage import measure
from scipy.ndimage import distance_transform_edt as edist




def read_permeability():
    """
    Reads the permeability value from the data file 'frac.txt'. 

    The function retrieves the permeability value, which is expected to be found after the first 
    equal sign ('=') and before the substring '\nName' on the fourth line from the end of the file.

    It uses the pandas library to read and handle the data file. If the permeability value cannot be 
    converted to a float or if the file 'frac.txt' cannot be found, exceptions will be raised.
    
    Parameters
    -----------
        None
        
    Returns
    --------
        perm : float
            The permeability value parsed from 'frac.txt'.

    Notes
    ------
        None
    
    Raises
    -------
        ValueError
            If the permeability value is not a valid float.
        FileNotFoundError
            If 'frac.txt' cannot be found.
    """
    # Read the data file using pandas
    file = pd.read_csv('frac.txt', header=None)

    # Find the index of the first equal sign in the last fourth line
    ind1 = str(file.iloc[-4]).find('=')+2
    # Find the index of the substring '\nName' in the last fourth line
    ind2 = str(file.iloc[-4]).find('\nName')

    # Extract the permeability value from the string between the two indices and convert it to float
    perm = float(str(file.iloc[-4])[ind1:ind2])
    return perm





def check_lbm_install():
    """
    Checks whether the MPLBM software has been installed. 

    The function verifies the presence of the 'permeability' file in the 'lbm_light/src/1-phase_LBM/' directory. 
    If the file is not present, it indicates that the LBM software is not installed and raises a 
    NotImplementedError. If the file is present, it prints a message to the console to indicate that the 
    LBM installation was found.

    Parameters
    -----------
        None

    Returns
    --------
        None
        
    Raises
    -------
        NotImplementedError
            If the 'permeability' file cannot be found in the 'lbm_light/src/1-phase_LBM/' directory, suggesting that 
            the LBM software has not been installed.

    Notes
    ------
        The function makes use of the 'os' library to interact with the operating system.

    Examples
    --------
        >>> check_lbm_install()
        LBM installation was found
    """
    if not os.path.isfile('lbm_light/src/1-phase_LBM/permeability'):
        raise NotImplementedError('\nLBM has not been installed\n')
    else:
        print('\nLBM installation was found\n')
   
    


def create_folder(folder_name):
    """
    Creates a new folder with a given name.

    The function attempts to create a new directory with the specified name. If a directory with the 
    same name already exists, the function will not create a new directory and will not raise any errors.

    Parameters
    -----------
        folder_name : str
            The name of the folder to be created. 

    Returns
    -------
        None
        
    Raises
    -------
        FileExistsError
            If a directory with the specified name already exists. This error is caught internally and 
            does not interrupt the program execution.

    Notes
    ------
        The function uses the 'os' library function 'mkdir' to create the new directory.

    """
    try:
        mkdir(folder_name)
    except FileExistsError:
        pass
   
    
        
    
def replace_word(file, old_word, new_word):
    """
    Replaces occurrences of a word in a file with a new word.

    The function reads the contents of the specified file, replaces all occurrences of 'old_word' 
    with 'new_word', and overwrites the file with the new contents. If the file does not exist or 
    cannot be read, a FileNotFoundError will be raised. If the file cannot be written to, an 
    OSError may be raised.

    Parameters
    ----------
        file : str
            The path of the file in which the word will be replaced.
        old_word : str
            The word to be replaced.
        new_word : str
            The word to replace 'old_word' with.

    Returns
    --------
        None
        
    Raises
    ------
        FileNotFoundError
            If the specified file does not exist or cannot be read.
        OSError
            If the file cannot be written to.

    Notes
    -----
        None 

    """
    
    f = open(file,'r')
    filedata = f.read()
    f.close()
    
    newdata = filedata.replace(old_word, new_word)
    
    f = open(file,'w')
    f.write(newdata)
    f.close()

    
    
    
def create_single_phase_input_file(input_file_name, geom_name, domain_size, periodic, io_folders, sim_settings, save_vtks):
    """
    Creates an XML input file for a single phase flow simulation based on given parameters.

    The function uses the provided parameters to write the settings for a single phase flow simulation 
    into an XML file. If a file with the specified name already exists, it will be overwritten.

    Parameters
    ----------
        input_file_name : str
            The name of the input file to create. If it already exists, it will be overwritten.
        geom_name : str
            The name of the .dat file that contains the entire geometry. Do not include the ".dat" extension.
        domain_size : list
            The size (in voxels) of the simulation domain, provided as a list of the form [x, y, z].
        periodic : list
            Determines whether the simulation should be periodic in the x, y, and z directions. This should be a list of three strings, either "True" or "False".
        io_folders : list
            A list containing the paths to the input and output folders, in that order.
        sim_settings : list
            A list containing the number of geometries/simulations, pressure, maximum number of iterations, and convergence, in that order.
        save_vtks : str
            Determines whether to save VTK files for the medium and velocity. This should be a string, either "True" or "False".

    Returns
    --------
        None
        
    Notes
    -----
        The function uses Python's built-in 'open' function to create and write to the XML file.

    Examples
    --------
        >>> create_single_phase_input_file('input.xml', 'geometry', [100, 100, 100], ['True', 'False', 'True'], ['input/', 'output/'], [5, 0.02, 2000, 0.0001], 'True')
        # This will create 'input.xml' with the specified settings.
    
    """
    # Parse geometry inputs
    x_size, y_size, z_size = domain_size
    periodic_x, periodic_y, periodic_z = periodic

    # Parse I/O inputs
    input_folder, output_folder = io_folders

    # Parse simulation inputs
    num_geoms_or_sims, pressure, max_iter, convergence = sim_settings

    # Open the input file, creating it if necessary
    with open(input_file_name, 'w') as file:
        file.write('<?xml version="1.0" ?>\n\n')  # Write XML header

        # Write the geometry settings to the file
        file.write('<geometry>\n')
        file.write(f'\t<file_geom> {geom_name} </file_geom>\n')
        file.write(f'\t<size> <x> {x_size} </x> <y> {y_size} </y> <z> {z_size} </z> </size>\n')
        file.write(f'\t<per> <x> {periodic_x} </x> <y> {periodic_y} </y> <z> {periodic_z} </z> </per>\n')
        file.write('</geometry>\n\n')

        # Write the I/O settings to the file
        file.write('<folder>\n')
        file.write(f'\t<in_f> {input_folder} </in_f>\n')
        file.write(f'\t<out_f> {output_folder} </out_f>\n')
        file.write('</folder>\n\n')

        # Write the simulation settings to the file
        file.write('<simulations>\n')
        file.write(f'\t<num> {num_geoms_or_sims} </num>\n')
        file.write(f'\t<press> {pressure} </press>\n')
        file.write(f'\t<iter> {max_iter} </iter>\n')
        file.write(f'\t<conv> {convergence} </conv>\n')
        file.write(f'\t<vtk_out> {save_vtks} </vtk_out>\n')
        file.write('</simulations>')

    


def create_geom_edist(rock, args):
    """
    Modifies a given rock matrix, calculates its Euclidean distance, creates a geometry file based on the 
    modified matrix and returns it.

    This function primarily modifies an input rock matrix according to several configuration options provided 
    in the 'args' parameter, calculates the Euclidean distance for the modified matrix, and writes it to a .dat 
    file. Additionally, the function ensures that all the boundary conditions have bounding box nodes, and it 
    pads the matrix if the 'num_slices' argument is provided.

    Parameters
    ----------
        rock : np.array
            The input rock matrix to be modified.
        args : argparse.Namespace
            An object containing various configuration options. This includes the 'swapXZ', 'scale_2', 'add_mesh', 
            'num_slices', 'print_size' and 'name' flags, and 'loc' directory path.

    Returns
    -------
        erock : np.array
            The modified rock matrix after the Euclidean distance calculation.

    Raises
    ------
        NotImplementedError
            If the 'scale_2' or 'add_mesh' features are attempted to be used as they are not yet implemented.

    Notes
    -----
        The function uses numpy's 'transpose', 'pad' and 'tofile' functions, as well as a custom 'edist' function 
        for Euclidean distance calculation.

    Examples
    --------
        >>> import numpy as np
        >>> import argparse
        >>> rock = np.array([[[0, 1, 0], [1, 0, 1], [0, 1, 0]], [[1, 0, 1], [0, 1, 0], [1, 0, 1]], [[0, 1, 0], [1, 0, 1], [0, 1, 0]]])
        >>> args = argparse.Namespace(swapXZ=False, scale_2=False, add_mesh=False, num_slices=2, print_size=True, name='geom', loc='./')
        >>> mod_rock = create_geom_edist(rock, args)
    """
    # If the 'swapXZ' flag is set, transpose the rock matrix accordingly
    if args.swapXZ:
        rock = rock.transpose([2, 1, 0])

    # If the 'scale_2' flag is set, raise an error as this feature is not yet implemented
    if args.scale_2:
        raise NotImplementedError('Feature not yet implemented')

    # Calculate the Euclidean distance for the rock matrix
    erock = edist(rock)
    
    # Ensure all the BCs have BB nodes
    erock[0,:,:] = erock[:,0,:] = erock[:,:,0] = 1
    erock[-1,:,:] = erock[:,-1,:] = erock[:,:,-1] = 1
    
    # Reopen the pores
    erock[rock==0] = 0
    
    # Get the final matrix with values [0,1,2]
    erock[(erock > 0) * (erock < 2)] = 1
    erock[erock > 1] = 2
    
    # If the 'add_mesh' flag is set, raise an error as this feature is not yet implemented
    if args.add_mesh:
        raise NotImplementedError('Feature not yet implemented')
    
    # If the 'num_slices' argument is provided, pad the 'erock' array accordingly
    if args.num_slices:
        erock = np.pad(erock, [(args.num_slices, args.num_slices), (0, 0), (0, 0)])
    
    # Determine the geometry name based on the 'print_size' flag
    if args.print_size:
        size = erock.shape
        geom_name = f'{args.name}_{size[0]}_{size[1]}_{size[2]}'
    else:
        geom_name = args.name
    
    # Modify the 'erock' array's data type and values for final output
    erock = erock.astype(np.int16)
    erock[erock==0] = 2608
    erock[erock==1] = 2609
    erock[erock==2] = 2610
    
    # Write the 'erock' array to a .dat file
    erock.flatten().tofile(f'{args.loc}/input/{geom_name}.dat')
    
    return erock




def erase_regions(rock):
    """
    Identifies and erases isolated regions within a given rock matrix.

    The function employs the `label` function from the skimage.measure module to detect connected components 
    in the input rock matrix. Isolated regions are identified as those components which are not connected to 
    the main body of the matrix (where the corresponding element in the labeled matrix is greater than 1). 
    These regions are then removed (set to 0) from the rock matrix.

    Parameters
    ----------
        rock : np.array
            The input rock matrix to be processed.

    Returns
    -------
        rock : np.array
            The modified rock matrix with isolated regions removed.

    Notes
    -----
        The function uses skimage.measure's 'label' function for connected components detection. The background 
        is set to 1, and connectivity is set to 1 to consider only orthogonally adjacent points. 

    Examples
    --------
    >>> import numpy as np
    >>> rock = np.array([[[0, 1, 0], [1, 0, 1], [0, 1, 0]], [[1, 0, 1], [0, 1, 0], [1, 0, 1]], [[0, 1, 0], [1, 0, 1], [0, 1, 0]]])
    >>> mod_rock = erase_regions(rock)
    """
    # Use the measure.label function from the skimage.measure module to identify connected components in the rock matrix
    # Here, the background is set to 1, and connectivity is set to 1 to consider only orthogonally adjacent points
    blobs_labels = measure.label(rock, background=1, connectivity=1)
    
    # Erase all isolated regions within the rock matrix
    # This is done by setting all elements in 'rock' that are part of an isolated region (where the corresponding element in 'blobs_labels' is greater than 1) to 0
    rock[blobs_labels > 1] = 0
    
    return rock




class write_MPLBM():
    """
    This class encapsulates methods to set up, manage and execute an MPLBM (MultiPhase Lattice Boltzmann Method) 
    simulation. It uses provided or default settings to create the necessary files and directories, write geometry,
    write inputs, and execute the simulation. 
    """

    def __init__(self, frac_obj, buffer_layers=2, cpus=4, num_hrs=14, allocation=None):
    """
    Initializes the write_MPLBM class
    
    Parameters
    ----------
        frac_obj : object
            An object containing a fracture object.
        buffer_layers : int, optional
            The number of empty slices at the beginning and end of the domain for pressure boundary conditions. 
            Defaults to 2.
        cpus : int, optional
            The number of CPUs to be used in the simulation. Defaults to 4.
        num_hrs : int, optional
            The number of hours the simulation should run. Defaults to 14.
        allocation : str, optional
            A specific allocation for the simulation. Defaults to None.

    Returns
    --------
        None
    
    Notes
    -----
        The class initializes by defining the source location of LBM (Lattice Boltzmann Method), creating required
        directories, copying the surface fraction object, and pre-processing the 3D fracture to generate an efficient 
        geometry for simulation. It also writes a shell script to run the simulation.

        The class includes methods to create new folders, write geometry, write various input files, copy necessary 
        data, edit inputs, and save the configuration as a pickle file for future reference. 
    """ 
        
        # Location of LBM source file
        lbm_loc = '../../lbm_light/src/1-phase_LBM/permeability'
        
        # Define geometry namespace
        geom = Namespace()
        name = 'frac'
        geom.name = name
        geom.print_size = True
        geom.add_mesh = False
        geom.num_slices = buffer_layers
        geom.swapXZ = True              
        geom.scale_2 = False                  
        
        # Create required directories
        create_folder('sims')
        self.folder_num = self.create_new_folder()
        self.folder_path = f'sims/frac_{self.folder_num}'
        create_folder(f'{self.folder_path}/input')
        
        # Assign folder path to geom.loc
        geom.loc = self.folder_path
        
        # Copy the surface fraction object and remove 'frac_3D' to reduce pickle size
        self.my_frac = cp(frac_obj)
        del self.my_frac.frac_3D
        
        self.buffer_layers = buffer_layers
        self.cpus = cpus
        self.num_hrs = num_hrs
        self.allocation = allocation
    
        # Preprocess the 3D fracture and generate an efficient geometry for simulation
        frac_3D = 1 - np.transpose(frac_obj.frac_3D, (2, 0, 1))
        frac_3D = erase_regions(frac_3D)
        frac_3D = create_geom_edist(frac_3D, geom)
        
        # Create input file
        frac_size = frac_3D.shape
        input_file_name = f"{self.folder_path}/{name}.xml"
        geom_name = f'{geom.name}_{frac_size[0]}_{frac_size[1]}_{frac_size[2]}'
        domain_size = [frac_size[0], frac_size[1], frac_size[2]]
        periodic = ["false", "false", "false"]
        
        create_folder(f'{self.folder_path}/output')
        
        io_folders = ['input/', 'output/']
        num_sims = 1
        sim_pressure = 0.0005
        sim_max_iter = 1000000
        sim_convergence = 0.0001
        sim_settings = [num_sims, sim_pressure, sim_max_iter, sim_convergence]
        save_vtks = "true"
        create_single_phase_input_file(input_file_name, geom_name, domain_size, periodic, io_folders, sim_settings, save_vtks)
        
        # Write shell script to run the simulation
        np.savetxt(f'{self.folder_path}/run_{name}.sh', [f'mpirun -n {cpus} {lbm_loc} {name}.xml > {name}.txt'], fmt='%s') 


    def create_new_folder(self):
        """
        Creates a new simulation directory in the 'sims' folder. It searches through numbered folders 
        'frac_i' (i ranging from 0 to 9999999999) and creates the first one that doesn't already exist.

        Parameters
        ----------
            None

        Returns
        -------
            i : int
                The number 'i' of the newly created folder.

        Notes
        ------
            None
        
        """
        
        for i in range(10000000000):
            try:
                mkdir(f'sims/frac_{i}')
                break
            except FileExistsError:
                continue
        return i
    

    def write_geom(self, frac):
        """
        Writes the 3D fracture geometry to a .dat file.

        The function first appends the shape of the input 'frac' array to the flattened 'frac' array, 
        then saves this information to a .dat file in the current simulation's directory.

        Parameters
        ----------
            frac : np.array
                The 3D fracture geometry to be written.

        Returns
        -------
            None

        Notes
        ------
            None
        
        """
        tofile = np.append([*frac.shape], frac.flatten('F'))
        np.savetxt(f'{self.folder_path}/frac.dat', tofile, fmt='%.0f')
    
   

    def save_pickle(self):
        """
        Saves the current instance of the write_MPLBM class as a pickled object.
        
        Parameters
        -----------
            None

        Returns
        -------
            None
            
        Raises
        ------
            PicklingError
                If the pickling process encounters an object that it cannot serialize.

        Notes
        ------
            None
        """
    

        with open(f'{self.folder_path}/lbm_config.pk', 'wb') as f:
            pickle.dump(self, f, protocol = pickle.HIGHEST_PROTOCOL) 
               


