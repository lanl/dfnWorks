import os
import sys
from datetime import datetime
from time import time
import subprocess
import io
import logging
import random
import select
import subprocess
import sys

import numpy as np

from pydfnworks.general.logging import local_print_log


def check_input_paths(self):

    self.print_log("* Checking input paths: Starting")

    if not self.jobname.endswith(os.sep):
       self.jobname += os.sep 

    if self.path:
        if not self.path.endswith(os.sep):
            self.path += os.sep

    if self.prune_file:
        if not os.path.isfile(self.prune_file):
            self.print_log(f'Prune file path is not valid:\n{self.prune_file}\n', 'error')

    if self.dfnFlow_file:
        if not os.path.isfile(self.dfnFlow_file):
            self.print_log(f'dfnFlow file path is not valid:\n{self.dfnFlow_file}\n', 'error')

    if self.dfnTrans_file:
        if not os.path.isfile(self.dfnTrans_file):
            self.print_log(f'dfnTrans control file path  is not valid:\n{self.dfnTrans_file}\n', 'error') 

    if self.pickle_filename:
        if not os.path.isfile(self.pickle_filename):
            self.print_log(f'Pickle file path is not valid:\n{self.pickle_filename}\n', 'error')

    self.print_log("* Checking input paths: Complete")

def set_seed(self, seed=None):
    ''' Initialize the pydfnworks pseudorandom number generators (NumPy and the
    Python random module) from the DFN seed.

    Parameters
    -----------------
        self : object
            DFN Class

        seed : int
            Seed to initialize the generators with. If None (default), the value
            of self.params['seed']['value'] is used.

    Returns
    -------------
        seed : int
            The seed the generators were initialized with.

    Notes
    -------------
        1. Randomness on the Python side of dfnWorks (hydraulic property
        distributions, Poisson-disc meshing, plot sub-sampling) is drawn from
        these two global generators, so seeding them makes those values
        reproducible from run to run.

        2. Following the dfnGen convention, a seed of 0 means "seed off the
        clock", i.e. produce a unique realization. In that case a seed is drawn
        from system entropy and reported, so the pydfnworks-side values can be
        reproduced later by setting DFN.params['seed']['value'] to the reported
        number.

        3. This does not change the seed used by the dfnGen executable. That
        seed is read from the input file written by check_input().
    '''
    if seed is None:
        seed = self.params['seed']['value']
    seed = int(seed)

    if seed < 0:
        self.print_log(
            f"Error. seed must be non-negative. Value provided: {seed}",
            'error')

    if seed == 0:
        # dfnGen convention: 0 means seed off the clock (unique realization).
        # Draw one explicitly so the values used can be reported and repeated.
        seed = random.SystemRandom().randint(1, 2**32 - 1)
        self.print_log(
            "--> seed is 0, pydfnworks random number generators are seeded off the clock"
        )
        self.print_log(
            f"--> Set DFN.params['seed']['value'] = {seed} to reproduce these values"
        )
    else:
        self.print_log(
            f"--> Initializing pydfnworks random number generators with seed {seed}"
        )

    np.random.seed(seed)
    random.seed(seed)
    self.seed = seed
    return seed


def call_executable(self, command):
    ''' Calls subprocess.run to call compiled executables like dfnGen, PFLOTRAN, LaGriT, etc.

    Parameters
    -----------------
        self : object
                DFN Class

        command : string
            command to execute

    Returns
    -------------
        None

    '''
    print(f"Executing {command}")
    subprocess.call(command, shell = True)


def print_parameters(self):
    ''' Prints parameters

    Parameters
    -----------------
        self : object
                DFN Class

    Returns
    -------------
        None

    '''
    self.print_log("=" * 80 + "\n")
    self.print_log(f"--> Jobname: {self.jobname}")
    self.print_log(f"--> Local Jobname: {self.local_jobname}")

    self.print_log(f"--> Number of Processors Requested: {self.ncpu}")
    if self.dfnGen_file:
        self.print_log(f"--> dfnGen filename : {self.dfnGen_file}")
        self.print_log(f"--> Local dfnGen filename : {self.local_dfnGen_file}")
    if self.dfnFlow_file:
        self.print_log(f"--> dfnFlow filename : {self.dfnFlow_file}")
        self.print_log(f"--> Local dfnFlow filename : {self.local_dfnFlow_file}")
    if self.dfnTrans_file:
        self.print_log(f"--> dfnTrans filename : {self.dfnTrans_file}")
        self.print_log(f"--> Local dfnTrans filename : {self.local_dfnTrans_file}")
    self.print_log("=" * 80 + "\n")

def go_home(self):
    os.chdir(self.jobname)
    self.print_log(f"--> Current directory is {os.getcwd()}")

def dump_time(self, function_name, time):
    '''Write run time for a funcion to the jobname_run_time.txt file

    Parameters
    ----------
        self : object
            DFN Class
        
        function_name : string
            Name of function that was timed
        
        time : float
            Run time of function in seconds

    Returns
    ----------
        None

    Notes
    ---------
    While this function is working, the current formulation is not robust through the entire workflow
    '''
    run_time_file = self.jobname + os.sep + self.local_jobname + "_run_time.txt"
    # Check if time file exists, if not create it
    if not os.path.isfile(run_time_file):
        f = open(run_time_file, "w")
        f.write("Runs times for " + self.local_jobname + "\n")
    else:
        f = open(run_time_file, "a")
    # Write Time
    if time < 60.0:
        f.write(function_name + " : %0.2f seconds\n" % time)
    else:
        f.write(function_name + " : %0.2f minutes\n" % (time / 60.0))
    f.close()


def print_run_time(self):
    '''Read in run times from file and and print to screen with percentages

    Parameters
    ---------
        self : object
            DFN Class

    Returns
    --------
        None

    Notes
    --------
    This will dump out all values in the run file, not just those from the most recent run
    '''
    run_time_file = self.jobname + os.sep + self.local_jobname + "_run_time.txt"
    f = open(run_time_file).readlines()
    unit = f[-1].split()[-1]
    total = float(f[-1].split()[-2])
    if unit == 'minutes':
        total *= 60.0

    self.print_log('Runs times for ', f[0])
    percent = []
    name = []
    for i in range(1, len(f)):
        unit = f[i].split()[-1]
        time = float(f[i].split()[-2])

        if unit == 'minutes':
            time *= 60.0
        percent.append(100.0 * (time / total))
        name.append(f[i].split(':')[1])
        self.print_log(f[i], '\t--> Percent if total %0.2f \n' % percent[i - 1])

    #print("Primary Function Percentages")
    #for i in range(1,len(f) - 1):
    #    if name[i-1] == ' dfnGen ' or name[i-1] == ' dfnFlow ' or name[i-1] == ' dfnTrans ':
    #        tmp = int(percent[i-1])/10
    #        print(name[i-1]+"\t"+"*"tmp)
    self.print_log("\n")

def to_pickle(self, filename=None):
    """ Saves the DFN object into a pickle format

    Parameters
    --------------
        self : object
            DFN Class

        filename : string
            name of pickle DFN object, default is None

    Returns
    ------------
        None

    Notes
    ------------
        None
    """
    import pickle
    if filename:
        pickle_filename = f'{filename}.pkl'
    else:
        pickle_filename = f'{self.local_jobname}.pkl'
    self.print_log(f'--> Pickling DFN object to {pickle_filename}')
    if os.path.isfile(pickle_filename):
        response = input(
            f"--> Warning {pickle_filename} exists. Are you sure you want to overwrite it?\nResponse [y/n]: "
        )
        if response == 'yes' or response == 'y':
            self.print_log('--> Overwritting file')
            pickle.dump(self, open(pickle_filename, "wb"))
            self.print_log(f'--> Pickling DFN object to {pickle_filename} : Complete')
        elif response == 'no' or 'n':
            self.print_log("--> Not writting file.")
        else:
            self.print_log("Unknown Response. {response}.\nNot writting file.")
    else:
        pickle.dump(self, open(pickle_filename, "wb"))
        self.print_log(f'--> Pickling DFN object to {pickle_filename} : Complete')


def from_pickle(self):
    """ Loads the DFN object from a pickle format

    Parameters
    --------------
        self : DFN Object
        
        filename : string
            name of pickle DFN object

    Returns
    ------------
        DFN object

    Notes
    ------------
        Best if used with DFNWORKS(pickle_file = <filename>)
    """
    import pickle
    self.print_log(f"--> Loading DFN from {self.pickle_filename}")
    if os.path.isfile(self.pickle_filename):
        tmp = pickle.load(open(self.pickle_filename, "rb"))
        self.__dict__ = tmp.__dict__.copy()
    else:
        error = f"Error. Cannot find pickle file {self.pickle_filename}.\nExiting program.\n"
        self.print_log(error, 'critical')
        