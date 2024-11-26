import os
import sys
from datetime import datetime
from time import time
import subprocess
import io
import logging
import select
import subprocess
import sys

from pydfnworks.general.logging import local_print_log



def call_executable(self, command):
    ''' Calls subprocess.run to call compiled executables like dfnGen, PFLOTRAN, LaGriT, etc.

    Parameters
    -----------------
        command : string
            command to execute

    Returns
    -------------
        None

    '''
    # line = command.split(" ")
    # p = subprocess.check_output(command, shell=True, stderr=subprocess.PIPE, text = True)
    # print(p)
    # # ## But do not wait till netstat finish, start displaying output immediately ##
    # # while True:
    # #     out = p.stderr.read(1)
    # #     if out == '' and p.poll() != None:
    # #         break
    # #     if out != '':
    # #         # sys.stdout.write(out)
    # #         # sys.stdout.flush()
    # #         self.print_log(p.stdout.decode())
            

    print(f"Executing {command}")
    subprocess.call(command, shell = True)


def print_parameters(self):
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

def print_out(self):

    self.print_log("-->Opening dfnGen LogFile...\n")
    with open('dfngen_logfile.txt', 'r') as f:
        self.print_log(f.read())

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
    print_log(f'--> Pickling DFN object to {pickle_filename}')
    if os.path.isfile(pickle_filename):
        response = input(
            f"--> Warning {pickle_filename} exists. Are you sure you want to overwrite it?\nResponse [y/n]: "
        )
        if response == 'yes' or response == 'y':
            print_log('--> Overwritting file')
            pickle.dump(self, open(pickle_filename, "wb"))
            print_log(f'--> Pickling DFN object to {pickle_filename} : Complete')
        elif response == 'no' or 'n':
            print_log("--> Not writting file.")
        else:
            print_log("Unknown Response. {response}.\nNot writting file.")
    else:
        pickle.dump(self, open(pickle_filename, "wb"))
        print_log(f'--> Pickling DFN object to {pickle_filename} : Complete')


def from_pickle(self, filename):
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
    print_log(f"--> Loading DFN from {filename}")
    if os.path.isfile(filename):
        tmp = pickle.load(open(filename, "rb"))
        self.__dict__ = tmp.__dict__.copy()
    else:
        error = f"Error. Cannot find pickle file {filename}.\nExiting program.\n"
        sys.stderr.write(error)
        sys.exit(1)