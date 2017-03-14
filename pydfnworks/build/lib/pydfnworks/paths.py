from tempfile import mkstemp
from shutil import move
import os

def define_paths():

    # ================================================
    # THESE PATHS MUST BE SET BY THE USER.
    # ================================================
    
    # the dfnWorks-Version2.0  repository 
    os.environ['DFNWORKS_PATH'] = 'LOUIS_THE_CHILD/dfnWorks-Version2.0/'
    
    # PETSC paths
    os.environ['PETSC_DIR']='/home/satkarra/src/petsc-git/petsc-3.7-release'
    os.environ['PETSC_ARCH']='/Ubuntu-14.04-nodebug'
    
    # PFLOTRAN path
    os.environ['PFLOTRAN_DIR']='/home/satkarra/src/pflotran-dev-pt-testing'

    # Python executable
    os.environ['python_dfn'] = '/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/2.4.1/bin/python'

    # LaGriT executable
    os.environ['lagrit_dfn'] = '/n/swdev/mesh_tools/lagrit/install-Ubuntu-14.04-x86_64/3.2.0/release/gcc-4.8.4/bin/lagrit'
    
    # =================================================== 
    # THESE PATHS ARE AUTOMATICALLY SET. DO NOT CHANGE.
    # ====================================================
   
    # Directories
    os.environ['DFNGEN_PATH']=os.environ['DFNWORKS_PATH']+'DFNGen/'
    os.environ['DFNTRANS_PATH']= os.environ['DFNWORKS_PATH'] +'ParticleTracking/'
    os.environ['PYDFNWORKS_PATH'] = os.environ['DFNWORKS_PATH'] + 'pydfnworks/'
    os.environ['connect_test'] = os.environ['DFNWORKS_PATH']+'DFN_Mesh_Connectivity_Test/'
    os.environ['correct_uge_PATH'] = os.environ['DFNWORKS_PATH']+'C_uge_correct/' 
    os.environ['VTK_PATH'] = os.environ['DFNWORKS_PATH'] + 'inp_2_vtk/'

    #===============================================
    # correct all the paths in the tests directory

    test_directory = os.environ['DFNWORKS_PATH'] + 'tests'
    prefix = os.environ['DFNWORKS_PATH'].split('dfnWorks-Version2.0')[0]
    for test_input_fle in os.listdir(test_directory):
        fh, abs_path = mkstemp()
        with open(abs_path, 'w') as new_file:
            test_input_fle = test_directory + '/' + test_input_fle
            with open(test_input_fle, 'r') as old_file:
                if '.txt' in test_input_fle:
                    for line in old_file:
                        temp_line = line
                        path_to_edit = temp_line.split()[1] 
                        print 'path to edit is ', path_to_edit
                        old_prefix = path_to_edit.split('dfnWorks-Version2.0')[0]
                        print 'old prefix is ', old_prefix
                        new_file.write(line.replace(old_prefix, prefix))
        os.close(fh)
        os.remove(test_input_fle)
        move(abs_path, test_input_fle)
