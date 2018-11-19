import os

def valid(name):
    if not (os.path.isfile(os.path.abspath(os.environ[name])) or os.path.isdir(os.path.abspath(os.environ[name]))):
        error_msg = "ERROR: " + name  + " has an invalid path name: " + os.environ[name]
        print error_msg
        exit()

def define_paths():

    # ================================================
    # THESE PATHS MUST BE SET BY THE USER.
    # ================================================
    
    # the dfnworks-main  repository 
    os.environ['dfnworks_PATH'] = '/home/jhyman/dfnworks/dfnworks-main/'
    valid('dfnworks_PATH')

    # PETSC paths
    os.environ['PETSC_DIR']='/home/satkarra/src/petsc-3.10.2'
    os.environ['PETSC_ARCH']='/Ubuntu-18.04-nodebug'
    valid('PETSC_DIR')

    # PFLOTRAN EXE 
    os.environ['PFLOTRAN_EXE']='/home/satkarra/src/pflotran-petsc.3.10.2/src/pflotran/pflotran'
    valid('PFLOTRAN_EXE')

    # FEHM EXE
    os.environ['FEHM_EXE']='/home/jhyman/bin/xfehm'
    valid('FEHM_EXE')

    # Python executable
    os.environ['PYTHON_EXE'] = '/n/swdev/packages/Ubuntu-16.04-x86_64/anaconda-python/4.4.0/bin/python'
    valid('PYTHON_EXE')
    
    # LaGriT executable
    os.environ['LAGRIT_EXE'] = '/n/swdev/mesh_tools/lagrit/install-Ubuntu-16.04-x86_64-gcc5.4.0/bin/lagrit'
    valid('LAGRIT_EXE')
    # =================================================== 
    # THESE PATHS ARE AUTOMATICALLY SET. DO NOT CHANGE.
    # ====================================================
    
    # Directories
    os.environ['DFNGEN_PATH']=os.environ['dfnworks_PATH']+'DFNGen/'
    os.environ['DFNTRANS_PATH']= os.environ['dfnworks_PATH'] +'ParticleTracking_TDRW/'
    os.environ['pyfnworks_PATH'] = os.environ['dfnworks_PATH'] + 'pydfnworks/'
    os.environ['connect_test'] = os.environ['dfnworks_PATH']+'DFN_Mesh_Connectivity_Test/'
    os.environ['correct_uge_PATH'] = os.environ['dfnworks_PATH']+'C_uge_correct/' 
    os.environ['correct_stor_PATH'] = os.environ['dfnworks_PATH']+'C_stor_correct/'
