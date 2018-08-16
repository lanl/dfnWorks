import os
import sys
import shutil
import helper
from time import time
import subprocess

def dfn_trans(self):
    '''dfnTrans
    Copy input files for dfnTrans into working directory and run DFNTrans
    '''
    print('='*80)
    print("\ndfnTrans Starting\n")
    print('='*80)

    self.copy_dfn_trans_files()
    tic=time()
    self.run_dfn_trans()
    #self.cleanup_files_at_end()
    helper.dump_time(self.jobname, 'Process: dfnTrans', time() - tic)   

def copy_dfn_trans_files(self):
    '''create link to DFNTRANS and copy input file into local directory
    '''
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
    '''run dfnTrans simulation'''
    failure = subprocess.call('./DFNTrans_TDRW '+self.local_dfnTrans_file, shell = True)
    if failure == 0:
        print('='*80)
        print("\ndfnTrans Complete\n")
        print('='*80)
    else:
        sys.exit("--> ERROR: dfnTrans did not complete\n")

def create_dfn_trans_links(self, path = '../'):
    files = ['params.txt', 'allboundaries.zone', 'tri_fracture.stor',
        'poly_info.dat', 'full_mesh.inp', 'cellinfo.dat', 'darcyvel.dat',
        'aperture.dat']
    for f in files:
        try:
            os.symlink(path+f, f)
        except:
            print("--> Error Creating link for %s"%f)
 
