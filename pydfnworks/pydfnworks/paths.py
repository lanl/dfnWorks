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
    os.environ['dfnworks_PATH'] = '/home/tsherman/dfnworks-main/'
    valid('dfnworks_PATH')
    if not (os.path.isdir(os.path.abspath(os.environ['dfnworks_PATH'] + 'tests/'))):
        print "INVALID VERSION OF dfnworks - does not have tests folder of official release 2.0"
        exit()

    # PETSC paths
    os.environ['PETSC_DIR']='/home/satkarra/src/petsc-git/petsc-3.7-release'
    os.environ['PETSC_ARCH']='/Ubuntu-14.04-nodebug'
    valid('PETSC_DIR')
#    valid('PETSC_ARCH')

    # PFLOTRAN path
    os.environ['PFLOTRAN_DIR']='/home/satkarra/src/pflotran-dev-pt-testing'
    valid('PFLOTRAN_DIR')

    # Python executable
    #os.environ['python_dfn'] = '/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/2.4.1/bin/python'
    os.environ['python_dfn'] = '/n/swdev/packages/Ubuntu-16.04-x86_64/anaconda-python/4.4.0/bin/python'
    valid('python_dfn')
    
    # LaGriT executable
#    os.environ['lagrit_dfn'] = '/n/swqa/LAGRIT/lagrit.lanl.gov/downloads/lagrit_ulin3.2' 
    os.environ['lagrit_dfn'] = '/n/swdev/mesh_tools/lagrit/install-Ubuntu-16.04-x86_64-gcc5.4.0/bin/lagrit'
    #os.environ['lagrit_dfn'] = '/n/swdev/mesh_tools/lagrit/install-Ubuntu-14.04-x86_64/3.2.0/dev/gcc-4.8.4/lagrit'
    valid('lagrit_dfn')

    # =================================================== 
    # THESE PATHS ARE AUTOMATICALLY SET. DO NOT CHANGE.
    # ====================================================
   
    # Directories
    os.environ['DFNGEN_PATH']=os.environ['dfnworks_PATH']+'DFNGen/'
    os.environ['DFNTRANS_PATH']= os.environ['dfnworks_PATH'] +'ParticleTracking_TDRW/'
    os.environ['PYdfnworks_PATH'] = os.environ['dfnworks_PATH'] + 'pydfnworks/'
    os.environ['connect_test'] = os.environ['dfnworks_PATH']+'DFN_Mesh_Connectivity_Test/'
    os.environ['correct_uge_PATH'] = os.environ['dfnworks_PATH']+'C_uge_correct/' 

