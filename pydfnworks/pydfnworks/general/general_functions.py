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


class MagicPopen(subprocess.Popen):
    """A subprocess.Popen with superpowers

    This is a wrapper for subprocess.Popen,
    which is guaranteed to have a .stdout and .stderr property,
    which will always be StringIO objects (not bytes).

    It's the return value for magicrun(),
    and shouldn't be used elsewhere.
    """

    stdout: io.StringIO
    stderr: io.StringIO


def magicrun(
    cmd, print_output=True, log_output=False, check=True,
) -> MagicPopen:
    """Run a command, with superpowers

    Params:

    * `cmd`: The command to run. If a string, it will be passed to a shell.
    * `print_output`: Print the command's stdout/stderr in to the controlling terminal's stdout/stderr in real time.
        stdout/stderr is always captured and returned, whether this is True or False (superpowers).
        The .stdout and .stderr properties are always strings, not bytes
        (which is required because we must use universal_newlines=True).
        * <https://gist.github.com/nawatts/e2cdca610463200c12eac2a14efc0bfb>
        * <https://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running>
    * `log_output`: Log the command's stdout/stderr in a single log message (each) after the command completes.
    * `check`: Raise an exception if the command returns a non-zero exit code.
        Unlike subprocess.run, this is True by default.
    * `*args, **kwargs`: Passed to subprocess.Popen
        Do not pass the following arguments, as they are used internally:
        * shell: Determined automatically based on the type of cmd
        * stdout: Always subprocess.PIPE
        * stderr: Always subprocess.PIPE
        * universal_newlines: Always True
        * bufsize: Always 1

    A `MagicPopen` object is always returned.
    """
    shell = isinstance(cmd, str)

    logging.debug(f"Running command: {cmd}")

    # ignore mypy errors because *args and **kwargs confuses it
    process = subprocess.Popen(  # type: ignore
        cmd,
        shell=True,
        bufsize=1,  # Output is line buffered, required to print output in real time
        universal_newlines=True,  # Required for line buffering
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdoutbuf = io.StringIO()
    stderrbuf = io.StringIO()

    # Ignore mypy errors related to stdout/stderrbuf not being file objects.
    # We know they're file objects because we set them to subprocess.PIPE.

    stdout_fileno = process.stdout.fileno()  # type: ignore
    stderr_fileno = process.stderr.fileno()  # type: ignore

    # This returns None until the process terminates
    while process.poll() is None:

        # select() waits until there is data to read (or an "exceptional case") on any of the streams
        readready, writeready, exceptionready = select.select(
            [process.stdout, process.stderr],
            [],
            [process.stdout, process.stderr],
            0.5,
        )

        # Check if what is ready is a stream, and if so, which stream.
        # Copy the stream to the buffer so we can use it,
        # and print it to stdout/stderr in real time if print_output is True.
        for stream in readready:
            if stream.fileno() == stdout_fileno:
                line = process.stdout.readline()  # type: ignore
                stdoutbuf.write(line)
                if print_output:
                    # sys.stdout.write(line)
                    local_print_log(line.rstrip("\n"))
            elif stream.fileno() == stderr_fileno:
                line = process.stderr.readline()  # type: ignore
                stderrbuf.write(line)
                if print_output:
                    local_print_log(line.rstrip("\n"))
                    # sys.stderr.write(line)
            else:
                raise Exception(
                    f"Unknown file descriptor in select result. Fileno: {stream.fileno()}"
                )

        # If what is ready is an exceptional situation, blow up I guess;
        # I haven't encountered this and this should probably do something more sophisticated.
        for stream in exceptionready:
            if stream.fileno() == stdout_fileno:
                raise Exception("Exception on stdout")
            elif stream.fileno() == stderr_fileno:
                raise Exception("Exception on stderr")
            else:
                raise Exception(
                    f"Unknown exception in select result. Fileno: {stream.fileno()}"
                )

    # Check for any remaining output after the process has exited.
    # Without this, the last line of output may not be printed,
    # if output is buffered (very normal)
    # and the process doesn't explictly flush upon exit
    # (also very normal, and will definitely happen if the process crashes or gets KILLed).
    for stream in [process.stdout, process.stderr]:
        for line in stream.readlines():
            if stream.fileno() == stdout_fileno:
                stdoutbuf.write(line)
                if print_output:
                    # sys.stdout.write(line)
                    local_print_log(line.rstrip("\n"))

            elif stream.fileno() == stderr_fileno:
                stderrbuf.write(line)
                if print_output:
                    # sys.stderr.write(line)
                    local_print_log(line.rstrip("\n"))

    # We'd like to just seek(0) on the stdout/stderr buffers, but "underlying stream is not seekable",
    # So we create new buffers above, write to them line by line, and replace the old ones with these.
    process.stdout.close()  # type: ignore
    stdoutbuf.seek(0)
    process.stdout = stdoutbuf
    process.stderr.close()  # type: ignore
    stderrbuf.seek(0)
    process.stderr = stderrbuf

    if check and process.returncode != 0:
        msg = f"Command failed with exit code {process.returncode}: {cmd}"
        logging.error(msg)
        logging.info(f"stdout: {process.stdout.getvalue()}")
        logging.info(f"stderr: {process.stderr.getvalue()}")
        raise Exception(msg)

    logging.info(f"Command completed with return code {process.returncode}: {cmd}")

    # The user may have already seen the output in std out/err,
    # but logging it here also logs it to syslog (if configured).
    if log_output:
        # Note that .getvalue() is not (always?) available on normal Popen stdout/stderr,
        # but it is available on our StringIO objects.
        # .getvalue() doesn't change the seek position.
        logging.info(f"stdout: {process.stdout.getvalue()}")
        logging.info(f"stderr: {process.stderr.getvalue()}")

    # Now that we've set stdout/err to StringIO objects,
    # we can return the Popen object as a MagicPopen object.
    magic_process: MagicPopen = process
    return magic_process

    

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
            

    # # print(f"Executing {command}")

    # # cmd = subprocess.run(line, capture_output=True)
    # self.print_log(p.stdout.decode())
    # self.print_log(p.stderr.decode())
    print_out(self)

    magicrun(command, log_output=False)

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