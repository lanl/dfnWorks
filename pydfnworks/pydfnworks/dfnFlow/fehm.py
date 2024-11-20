import os
import subprocess
import sys
import glob
import shutil
from time import time
import numpy as np
"""
Functions for using FEHM in dfnWorks
"""


def correct_stor_file(self):
    """Corrects volumes in stor file to account for apertures

    Parameters
    ----------
        self : object
            DFN Class

    Returns
    --------
        None

    Notes
    --------
    Currently does not work with cell based aperture
    """
    self.print_log('--> Correcing STOR file')
    # Make input file for C Stor converter
    if self.flow_solver != "FEHM":
        error = "Error. Incorrect flow solver requested\n"
        self.print_log(error, 'error')
        sys.exit(1)

    self.dump_hydraulic_values(format = "FEHM")

    self.stor_file = self.inp_file[:-4] + '.stor'
    self.mat_file = self.inp_file[:-4] + '_material.zone'
    with open("convert_stor_params.txt", "w") as f:
        f.write("%s\n" % self.mat_file)
        f.write("%s\n" % self.stor_file)
        f.write("%s" % (self.stor_file[:-5] + '_vol_area.stor\n'))
        f.write("%s\n" % self.aper_file)

    t = time()
    cmd = os.environ['CORRECT_STOR_EXE'] + ' convert_stor_params.txt'
    failure = subprocess.call(cmd, shell=True)
    if failure > 0:
        error = 'Erro: stor conversion failed\nExiting Program\n'
        self.print_log(error, 'error')
        sys.exit(1)
    elapsed = time() - t
    self.print_log(f'--> Time elapsed for STOR file conversion: {elapsed:0.3f} seconds')


def correct_perm_for_fehm():
    """ FEHM wants an empty line at the end of the perm file
    This functions adds that line return
    
    Parameters
    ----------
        None

    Returns
    ---------
        None

    Notes
    ------------
        Only adds a new line if the last line is not empty
    """
    # self.print_log("Modifing perm.dat for FEHM")
    fp = open("perm.dat")
    lines = fp.readlines()
    fp.close()
    # Check if the last line of file is just a new line
    # If it is not, then add a new line at the end of the file
    if len(lines[-1].split()) != 0:
        self.print_log("--> Adding line to perm.dat")
        fp = open("perm.dat", "a")
        fp.write("\n")
        fp.close()


def fehm(self):
    """Run FEHM 

    Parameters
    ----------
        self : object 
            DFN Class
   
    Returns
    -------
        None

    Notes
    -----
    See https://fehm.lanl.gov/ for details about FEHM

    """
    self.print_log("--> Running FEHM")
    if self.flow_solver != "FEHM":
        error = "Error. Incorrect flow solver requested\n"
        self.print_log(error, 'error')
        sys.exit(1)

    try:
        shutil.copy(self.dfnFlow_file, self.jobname)
    except:
        error = f"--> Error copying FEHM run file: {self.dfnFlow_file}"
        self.print_log(error, 'error')
        sys.exit(1)

    path = self.dfnFlow_file.strip(self.local_dfnFlow_file)
    with open(self.local_dfnFlow_file) as fp:
        line = fp.readline()
    fehm_input = line.split()[-1]
    try:
        shutil.copy(path + fehm_input, os.getcwd())
    except:
        error = f"--> Error copying FEHM input file: {fehm_input}"
        self.print_log(error, 'error')
        sys.exit(1)

    correct_perm_for_fehm()
    tic = time()
    cmd = os.environ["FEHM_EXE"] + " " + self.local_dfnFlow_file
    self.call_executable(cmd)
    self.print_log('=' * 80)
    self.print_log("FEHM Complete")
    elapsed = time() - tic
    self.print_log(f"Time Required {elapsed} Seconds")
    self.print_log('=' * 80)
