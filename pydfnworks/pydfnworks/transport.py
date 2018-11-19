import os
import sys
import shutil
import helper
from time import time
import subprocess

def dfn_trans(self):
    """Setup and run dfnTrans 

    Paramters
    ---------
    None
   
    Returns
    --------
    None
    """
    print('='*80)
    print("\ndfnTrans Starting\n")
    print('='*80)
    self.copy_dfn_trans_files()
    self.check_dfn_trans_run_files()
    tic=time()
    self.run_dfn_trans()
    delta_time = time() - tic
    helper.dump_time(self.jobname, 'Process: dfnTrans', delta_time)   
    print('='*80)
    print("\ndfnTrans Complete\n")
    print("Time Required for dfnTrans: %0.2f Seconds\n"%delta_time)
    print('='*80)

def copy_dfn_trans_files(self):
    """Creates symlink to dfnTrans Execuateble and copies input files for dfnTrans into working directory

    Paramters
    ---------
    None
   
    Returns
    --------
    None
    """
    #Create Path to DFNTrans   
    try:
        os.symlink(os.environ['DFNTRANS_PATH']+'DFNTrans_TDRW', './DFNTrans_TDRW')
    except OSError:
        os.remove('DFNTrans_TDRW')   
        os.symlink(os.environ['DFNTRANS_PATH']+'DFNTrans_TDRW', './DFNTrans_TDRW')
    except:
        sys.exit("Cannot create link to DFNTrans. Exiting Program")
    
    # Copy DFNTrans input file
    print(os.getcwd())

    print("Attempting to Copy %s\n"%self.dfnTrans_file) 
    try:
        shutil.copy(self.dfnTrans_file, os.path.abspath(os.getcwd())) 
    except OSError:
        print("--> Problem copying %s file"%self.local_dfnTrans_file)
        print("--> Trying to delete and recopy") 
        os.remove(self.local_dfnTrans_file)
        shutil.copy(self.dfnTrans_file, os.path.abspath(os.getcwd())) 
    except:
        print("--> ERROR: Problem copying %s file"%self.dfnTrans_file)
        sys.exit("Unable to replace. Exiting Program")

def run_dfn_trans(self):
    """ Execute dfnTrans

    Paramters
    ---------
    None
   
    Returns
    --------
    None
    """
    failure = subprocess.call('./DFNTrans_TDRW '+self.local_dfnTrans_file, shell = True)
    if failure != 0:
        sys.exit("--> ERROR: dfnTrans did not complete\n")

def create_dfn_trans_links(self, path = '../'):
    """ Create symlinks to files required to run dfnTrans that are in another directory. 

    Paramters
    ---------
    path: Absolute path to primary directory. 
   
    Returns
    --------
    None

    Notes
    -------
    Typically, the path is DFN.path, which is set by the command line argument -path

    """
    files = ['params.txt', 'allboundaries.zone', 'full_mesh.stor',
        'poly_info.dat', 'full_mesh.inp', 'aperture.dat']
    if self.flow_solver == 'PFLOTRAN':
        files.append('cellinfo.dat')
        files.append('darcyvel.dat')
        files.append('full_mesh_vol_area.uge')
    if self.flow_solver == 'FEHM':
        files.append('tri_frac.fin')
 
    for f in files:
        try:
            os.symlink(path+f, f)
        except:
            print("--> Error Creating link for %s"%f)

def check_dfn_trans_run_files(self):
    """ Ensures that all files required for dfnTrans run are in the current directory
 
    Paramters
    ---------
    None 
   
    Returns
    --------
    None

    Notes
    -------
    None
    """
    cwd = os.getcwd()
    print("\nChecking that all files required for dfnTrans are in the current directory")
    print("--> Current Working Directory: %s"%cwd)
    print("--> dfnTrans is running from: %s"%self.local_dfnTrans_file)

    files = {"param:": None ,"poly:":None, "inp:": None, "stor:": None, "boundary:": None, "aperture_file:": None}
    if self.flow_solver == "PFLOTRAN":
        files["PFLOTRAN_vel:"]=None
        files["PFLOTRAN_cell:"]=None
        files["PFLOTRAN_uge:"]=None
    if self.flow_solver == "FEHM":
        files["FEHM_fin:"]=None

    keys = files.keys()
    with open(self.local_dfnTrans_file) as fp:
        for line in fp.readlines():
               for key in keys:
                    if key in line:
                        if files[key] == None:
                            files[key] = line.split()[-1]

    for key in keys:
        if not os.path.isfile(files[key]) or os.stat(files[key]).st_size == 0:
            sys.exit("ERROR!!!!!\nRequired file %s is either empty of not in the current directory.\nPlease check required files\nExiting Program"%files[key])
    print("--> All files required for dfnTrans have been found in current directory\n\n")

