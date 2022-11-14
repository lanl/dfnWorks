import os
import sys
from datetime import datetime
from time import time
import logging

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

    #self.print_log("Primary Function Percentages")
    #for i in range(1,len(f) - 1):
    #    if name[i-1] == ' dfnGen ' or name[i-1] == ' dfnFlow ' or name[i-1] == ' dfnTrans ':
    #        tmp = int(percent[i-1])/10
    #        self.print_log(name[i-1]+"\t"+"*"tmp)
    self.print_log("\n")

def print_log(self, statement):
    
    '''print and log statments to a file 

    Parameters
    ---------
    statement : the print/log statement

    Returns
    --------
    None

    Notes
    -------
    print statments in pydfnworks should generally be replaced with this print_log function. Use self.print_log if function is on DFN object
    '''
    logging.basicConfig(filename = os.getcwd() + os.sep + "dfnWorks.log", level = logging.DEBUG)
    print(statement)
    logging.info(statement)

def local_print_log(statement):

    '''print and log statments to a file

    Parameters
    ---------
    statement : the print/log statement

    Returns
    --------
    None

    Notes
    -------
    print statments in pydfnworks should generally be replaced with this print_log function. Use local_print_log if function is not in refernce to DFN object
    '''
    logging.basicConfig(filename = os.getcwd() + os.sep + "dfnWorks.log", level = logging.DEBUG)
    print(statement)
    logging.info(statement)
