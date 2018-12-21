import os 
import subprocess
import sys
import glob
import shutil
from time import time 
import numpy as np

def set_flow_solver(self, flow_solver):
    """Sets flow solver to be used 
       
    Parameters
    ----------
        self : object
            DFN Class
        flow_solver: string  
            Name of flow solver. Currently supported flow sovlers are FEHM and PFLOTRAN

    Returns
    ---------

    Notes
    --------
    Default is PFLOTRAN 

"""
    if flow_solver == "FEHM" or flow_solver == "PFLOTRAN":
        print("Using flow solver %s"%flow_solver)
        self.flow_solver = flow_solver
    else:
        sys.exit("ERROR: Unknown flow solver requested %s\nCurrently supported flow solvers are FEHM and PFLOTRAN\nExiting dfnWorks\n"%flow_solver)

def dfn_flow(self,dump_vtk=True):
    """ Run the dfnFlow portion of the workflow
       
    Parameters
    ----------
        self : object
            DFN Class
        dump_vtk : bool
            True - Write out vtk files for flow solutions 
            False  - Does not write out vtk files for flow solutions 
 
    Returns
    ---------

    Notes
    --------
    Information on individual functions is found therein 
    """

    print('='*80)
    print("\ndfnFlow Starting\n")
    print('='*80)

    tic_flow = time()
    
    if self.flow_solver == "PFLOTRAN":
        print("Using flow solver: %s"%self.flow_solver)
        tic = time()
        self.lagrit2pflotran()
        self.dump_time('Function: lagrit2pflotran', time() - tic)   
        
        tic = time()    
        self.pflotran()
        self.dump_time('Function: pflotran', time() - tic)  

        if dump_vtk:
            tic = time()    
            self.parse_pflotran_vtk_python()
            self.dump_time('Function: parse_pflotran_vtk', time() - tic)    

        tic = time()    
        self.pflotran_cleanup()
        self.dump_time('Function: parse_cleanup', time() - tic) 

        tic = time()    
        self.effective_perm()
        self.dump_time('Function: effective_perm', time() - tic) 

    elif self.flow_solver == "FEHM":
        print("Using flow solver: %s"%self.flow_solver)
        tic = time()
        self.correct_stor_file()
        self.fehm()
        self.dump_time('Function: FEHM', time() - tic) 

    delta_time = time() - tic_flow 
    self.dump_time('Process: dfnFlow',delta_time)    

    print('='*80)
    print("\ndfnFlow Complete")
    print("Time Required for dfnFlow %0.2f seconds\n"%delta_time)
    print('='*80)

def create_dfn_flow_links(self, path = '../'):
    """ Create symlinks to files required to run dfnFlow that are in another directory. 

    Paramters
    ---------
        self : object
            DFN Class
        path : string 
            Absolute path to primary directory. 
   
    Returns
    --------
        None

    Notes
    -------
        1. Typically, the path is DFN.path, which is set by the command line argument -path
        2. Currently only supported for PFLOTRAN
    """
    files = ['full_mesh.uge', 'full_mesh.inp', 'full_mesh_vol_area.uge',
        'materialid.dat','full_mesh.stor','full_mesh_material.zone',
        'full_mesh.fehmn', 'allboundaries.zone', 
        'pboundary_bottom.zone', 'pboundary_top.zone',
        'pboundary_back_s.zone', 'pboundary_front_n.zone', 
        'pboundary_left_w.zone', 'pboundary_right_e.zone',
        'perm.dat','aperture.dat']
    for f in files:
        try:
            os.symlink(path+f, f)
        except:
            print("--> Error Creating link for %s"%f)
 
def uncorrelated(self, mu, sigma, path = '../'):
    """ Creates Fracture Based Log-Normal Permeability field with mean mu and variance sigma. Aperture is dervived using the cubic law
    
    Parameters
    -----------
        mu : double 
            Mean of LogNormal Permeability field
        sigma : double
             Variance of permeability field
        path : string 
            path to original network. Can be current directory

    Returns
    ----------
        None

    Notes
    ----------
    mu is the mean of perm not log(perm)

    """
    print '--> Creating Uncorrelated Transmissivity Fields'
    print 'Mean: ', mu  
    print 'Variance: ', sigma
    print 'Running un-correlated'
    n = len(x)

    perm = np.log(mu)*np.ones(n) 
    perturbation = np.random.normal(0.0, 1.0, n)
    perm = np.exp(perm + np.sqrt(sigma)*perturbation) 
    aper = np.sqrt((12.0*perm))

    print '\nPerm Stats'
    print '\tMean:', np.mean(perm)
    print '\tMean:', np.mean(np.log(perm))
    print '\tVariance:',np.var(np.log(perm))
    print '\tMinimum:',min(perm)
    print '\tMaximum:',max(perm)
    print '\tMinimum:',min(np.log(perm))
    print '\tMaximum:',max(np.log(perm))

    print '\nAperture Stats'
    print '\tMean:', np.mean(aper)
    print '\tVariance:',np.var(aper)
    print '\tMinimum:',min(aper)
    print '\tMaximum:',max(aper)

    # Write out new aperture.dat and perm.dat files
    output_filename = 'aperture_' + str(sigma) + '.dat'
    f = open(output_filename,'w+')
    f.write('aperture\n')
    for i in range(n):
    	f.write('-%d 0 0 %0.5e\n'%(i + 7, aper[i]))
    f.close()
    try:
        os.symlink(output_filename, 'aperture.dat')
    except:
        print("WARNING!!!! Could not make symlink to aperture.dat file")

    output_filename = 'perm_' + str(sigma) + '.dat'
    f = open(output_filename,'w+')
    f.write('permeability\n')
    for i in range(n):
    	f.write('-%d 0 0 %0.5e %0.5e %0.5e\n'%(i+7, perm[i], perm[i], perm[i]))
    f.close()
    try:
        os.symlink(output_filename, 'perm.dat')
    except:
        print("WARNING!!!! Could not make symlink to perm.dat file")

