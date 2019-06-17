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
    # Make input file for C Stor converter
    if self.flow_solver != "FEHM":
        error = "ERROR! Wrong flow solver requested"
        sys.stderr.write(error)
        sys.exit(1)

    self.stor_file = self.inp_file[:-4] + '.stor'
    self.mat_file = self.inp_file[:-4] + '_material.zone'
    f = open("convert_stor_params.txt", "w")
    f.write("%s\n" % self.mat_file)
    f.write("%s\n" % self.stor_file)
    f.write("%s" % (self.stor_file[:-5] + '_vol_area.stor\n'))
    f.write("%s\n" % self.aper_file)
    f.close()

    t = time()
    cmd = os.environ['CORRECT_STOR_EXE'] + ' convert_stor_params.txt'
    failure = subprocess.call(cmd, shell=True)
    if failure > 0:
        error = 'ERROR: stor conversion failed\nExiting Program'
        sys.stderr.write(error)
        sys.exit(1)
    elapsed = time() - t
    print('--> Time elapsed for STOR file conversion: %0.3f seconds\n' %
          elapsed)


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
    fp = open("perm.dat")
    lines = fp.readlines()
    fp.close()
    # Check if the last line of file is just a new line
    # If it is not, then add a new line at the end of the file
    if len(lines[-1].split()) != 0:
        print("--> Adding line to perm.dat")
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
    print("--> Running FEHM")
    if self.flow_solver != "FEHM":
        error = "ERROR! Wrong flow solver requested"
        sys.stderr.write(error)
        sys.exit(1)

    try:
        shutil.copy(self.dfnFlow_file, os.getcwd())
    except:
        error = "-->ERROR copying FEHM run file: %s" % self.dfnFlow_file
        std.stderr.write(error)
        sys.exit(1)

    path = self.dfnFlow_file.strip(self.local_dfnFlow_file)
    fp = open(self.local_dfnFlow_file)
    line = fp.readline()
    fehm_input = line.split()[-1]
    fp.close()
    try:
        shutil.copy(path + fehm_input, os.getcwd())
    except:
        error = "-->ERROR copying FEHM input file:" % fehm_input
        sys.stderr.write(error)
        sys.exit(1)

    correct_perm_for_fehm()
    tic = time()
    subprocess.call(os.environ["FEHM_EXE"] + " " + self.local_dfnFlow_file,
                    shell=True)
    print('=' * 80)
    print("FEHM Complete")
    print("Time Required %0.2f Seconds" % (time() - tic))
    print('=' * 80)
