import os
import shutil
import sys

#pydfnworks modules
import pydfnworks.dfnGen.generation.input_checking.helper_functions as hf
from pydfnworks.dfnGen.generation.input_checking.parsing import parse_input
from pydfnworks.dfnGen.generation.input_checking.verifications import verify_params
from pydfnworks.dfnGen.generation.input_checking.write_input_file import dump_params
from pydfnworks.dfnGen.generation.input_checking.add_fracture_family_to_params import write_fracture_families


def print_domain_parameters(self, print_all=False):
    """ Prints domain parameters to screen
    Parameters
    ------------
        self : DFN Class Object
        print_all : bool
            If True, all parameters will be printed to screen, even those without a value. If False (default), only those with a value will be printed to screen.  

    Returns
    ---------
        None

    """
    print()
    print('=' * 80)
    print("--> dfnGen input parameters")
    print('=' * 80)
    print()
    print("{:40s}{:}".format("Name", "Value"))
    print("{:40s}{:}".format("----------------------------",
                             "---------------"))
    #print('-' * 60)
    for key in self.params.keys():
        value = self.params[key]['value']
        if print_all:
            print(f"{key:34s}{value}")
        else:
            if value:
                print(f"Name: {key:34s}Value: {value}")
    print('=' * 80)


def check_input(self, from_file=False):
    """ Checks input file for DFNGen to make sure all necessary parameters are defined. Then writes out a "clean" version of the input file

     Input Format Requirements:  
        * Each parameter must be defined on its own line (separate by newline)
        * A parameter (key) MUST be separated from its value by a colon ':' (ie. --> key: value)
        * Values may also be placed on lines after the 'key'
        * Comment Format:  On a line containing  // or / ``*``, nothing after ``*`` / or // will be processed  but text before a comment will be processed 
    
    Parameters
    ------------
        self : DFN Class Object

    Returns
    ---------
        None

    Notes
    -----
        There are warnings and errors raised in this function. Warning will let you continue while errors will stop the run. Continue past warnings are your own risk. 

        From File feature is no longer maintained. Functions should be removed in the near future.
    """
    print()
    print('=' * 80)
    print("Checking Input File\n")
    ## Needs to be a logic fork here for using input file
    from_file = from_file  #added call to function creat_dfn to set flag, default is false
    if from_file:
        # Copy input file
        if os.path.isfile(self.dfnGen_file):
            try:
                print(f"--> Copying input file: {self.dfnGen_file}")
                shutil.copy(self.dfnGen_file, self.jobname)
                print("--> Copying input file successful")
            except:
                error = f"Unable to copy dfnGen input file to working directory \n{self.dfnGen_file}\n Exiting"
                sys.stderr.write(error)
                sys.exit(1)
        else:
            error = f"Input file \n{self.dfnGen_file} not found\n Exiting"
            sys.stderr.write(error)
            sys.exit(1)
        input_file = self.local_dfnGen_file
        output_file = "dfnGen_output/" + self.local_dfnGen_file[:-4] + '_clean.dat'
        print(f"--> Reading input file: {input_file}")
        self.params = parse_input(input_file)

    else:
        output_file = "dfnGen_output/" + self.local_dfnGen_file[:-4] + '_clean.dat'
        self.params = self.write_fracture_families()
        self.write_user_fractures_to_file()
    print(f"--> Clean output file name: {output_file}")
    verify_params(self.params)
    dump_params(self.params, output_file)
    print("\nChecking Input File Complete")
    print('=' * 80)
    print()
