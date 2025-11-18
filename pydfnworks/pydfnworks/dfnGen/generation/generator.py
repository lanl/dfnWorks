import os
import sys
import numpy as np
import shutil
from time import time
import subprocess


def dfn_gen(self, output=True):
    ''' Wrapper script the runs the dfnGen workflow:    
        1) make_working_directory: Create a directory with name of job
        2) check_input: Check input parameters and create a clean version of the input file
        3) create_network: Create network. DFNGEN v2.0 is called and creates the network
        4) output_report: Generate a PDF summary of the DFN generation
        5) mesh_network: calls module dfnGen_meshing and runs LaGriT to mesh the DFN

    Parameters
    ----------
        self :
            DFN object
        
        output : bool
            If True, output pdf will be created. If False, no pdf is made 

    Returns
    -------
        None

    Notes
    -----
        Details of each portion of the routine are in those sections

    '''
    self.print_log('=' * 80)
    self.print_log('dfnGen Starting')
    self.print_log('=' * 80) 
    # Create Working directory
    self.make_working_directory()
    # Check input file
    self.check_input()
    # Create network
    self.create_network()
    if output:
        self.output_report()
    # Mesh Network
    self.mesh_network()
    self.print_log('=' * 80)
    self.print_log('dfnGen Complete')
    self.print_log('=' * 80)


def make_working_directory(self, delete=False):
    ''' Make working directory for dfnWorks Simulation

    Parameters
    ----------
        self :
            DFN object

        delete : bool
            If True, deletes the existing working directory. Default = False

    Returns
    -------
        None

    Notes
    -----
    If directory already exists, user is prompted if they want to overwrite and proceed. If not, program exits. 
    '''

    if not delete:
        try:
            os.mkdir(self.jobname)
        except OSError:
            if os.path.isdir(self.jobname):
                self.print_log(f'Folder {self.jobname} exists')
                keep = input('Do you want to delete it? [yes/no] \n')
                if keep == 'yes' or keep == 'y':
                    self.print_log('Deleting', self.jobname)
                    shutil.rmtree(self.jobname)
                    self.print_log('Creating', self.jobname)
                    os.mkdir(self.jobname)
                elif keep == 'no' or 'n':
                    error = "Not deleting folder. Exiting Program\n"
                    self.print_log(error, 'error')
                    sys.exit(1)
                else:
                    error = "Unknown Response. Exiting Program\n"
                    self.print_log(error, 'error')
                    sys.exit(1)
            else:
                error = f"Unable to create working directory {self.jobname}\n. Please check the provided path.\nExiting\n"
                self.print_log(error, 'error')
                sys.exit(1)
    else:
        if not os.path.isdir(self.jobname):
            os.mkdir(self.jobname)
        else:
            try:
                shutil.rmtree(self.jobname)
                self.print_log(f'--> Creating directory {self.jobname}')
                os.mkdir(self.jobname)
            except:
                error = "Error. deleting and creating directory.\nExiting\n"
                self.print_log(error, 'error')
                sys.stderr.write(error)
                sys.exit(1)

    subdirs = ['dfnGen_output', 'dfnGen_output/radii', 'intersections','polys']
    for subdir in subdirs:
        self.print_log(f"Making subdirectory: {subdir}")
        try:
            os.mkdir(self.jobname + os.sep + subdir)
        except:
            self.print_log(f"Error making subdirectory: {subdir}", 'error')
    os.chdir(self.jobname)
    self.print_log(f"Current directory is now: {os.getcwd()}")
    self.print_log(f"Jobname is {self.jobname}")


def create_network(self):
    ''' Execute dfnGen

    Parameters
    ----------
        self :
            DFN object 

    Returns
    -------
        None

    Notes
    -----
    After generation is complete, this script checks whether the generation of the fracture network failed or succeeded based on the existence of the file params.txt. 
    '''
    self.print_log('--> Running DFNGEN')
    os.chdir(self.jobname)
    cmd = os.environ[
        'DFNGEN_EXE'] + ' ' + 'dfnGen_output/' + self.local_dfnGen_file[:
                                                     -4] + '_clean.dat' + ' ' + self.jobname
    self.print_log(f"Running: >> {cmd}")
    subprocess.call(cmd, shell=True)

    self.print_log("-->Opening dfnGen LogFile...\n")
    with open('dfngen_logfile.txt', 'r') as f:
        self.print_log(f.read())

    self.print_log("-->Opening dfnGen LogFile...\n")
    with open('dfngen_logfile.txt', 'r') as f:
        self.print_log(f.read())

    if os.path.isfile("params.txt"):
        self.gather_dfn_gen_output()
        self.assign_hydraulic_properties()
        self.print_log('-' * 80)
        self.print_log("Generation Succeeded")
        self.print_log('-' * 80)
    else:
        error = f"Error. Unable to find 'params.txt' in current directory {os.getcwd}.\n"
        self.print_log(error, 'error')
        sys.exit(1)
