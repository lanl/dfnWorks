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
        error = "ERROR! Wrong flow solver requested\n"
        sys.stderr.write(error)
        sys.exit(1)

    self.stor_file = self.inp_file[:-4] + '.stor'
    self.mat_zone_file = self.inp_file[:-4] + '_material.zone'
    with open("convert_stor_params.txt", "w") as fp:
        fp.write(f"{self.mat_zone_file}\n")
        fp.write(f"{self.stor_file}\n")
        fp.write(f"{self.stor_file[:-5]}_vol_area.stor\n")
        fp.write(f"{self.aper_file}\n")

    self.dump_aperture(self.aper_file, format='fehm')

    t = time()
    cmd = os.environ['CORRECT_STOR_EXE'] + ' convert_stor_params.txt'
    if subprocess.call(cmd, shell=True) > 0:
        error = 'Error: Stor conversion failed\nExiting Program\n'
        sys.stderr.write(error)
        sys.exit(1)
    elapsed = time() - t
    print('--> Time elapsed for STOR file conversion: %0.3f seconds\n' %
          elapsed)


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
        error = "Error. Wrong flow solver requested to run FEFHM\n"
        sys.stderr.write(error)
        sys.exit(1)

    try:
        shutil.copy(self.dfnFlow_file, os.getcwd())
    except:
        error = f"-->Error copying FEHM run file: {self.dfnFlow_file}"
        sys.stderr.write(error)
        sys.exit(1)

    path = self.dfnFlow_file.strip(self.local_dfnFlow_file)
    fp = open(self.local_dfnFlow_file)
    line = fp.readline()
    fehm_input = line.split()[-1]
    fp.close()
    try:
        shutil.copy(path + fehm_input, os.getcwd())
    except:
        error = "-->ERROR copying FEHM input file:\n" % fehm_input
        sys.stderr.write(error)
        sys.exit(1)

    # dump perm for fehm
    self.dump_perm('perm.dat', format='fehm')
    tic = time()
    subprocess.call(os.environ["FEHM_EXE"] + " " + self.local_dfnFlow_file,
                    shell=True)
    print('=' * 80)
    print("FEHM Complete")
    print("Time Required %0.2f Seconds" % (time() - tic))
    print('=' * 80)
