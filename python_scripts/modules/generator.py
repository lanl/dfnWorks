import os
import sys
import meshdfn as mesh
import shutil

def make_working_directory(self):
    '''
    make working directories for fracture generation
    '''    

    try:
        os.mkdir(self._jobname)
    except OSError:
        print '\nFolder ', self._jobname, ' exists'
        keep = raw_input('Do you want to delete it? [yes/no] \n')
        if keep == 'yes' or keep == 'y':
            print 'Deleting', self._jobname 
            shutil.rmtree(self._jobname)
            print 'Creating', self._jobname 
            os.mkdir(self._jobname)    
        elif keep == 'no' or 'n':
            sys.exit("Not deleting folder. Exiting Program") 
        else:
            sys.exit("Unknown Response. Exiting Program") 
    os.mkdir(self._jobname + '/radii')
    os.mkdir(self._jobname + '/intersections')
    os.mkdir(self._jobname + '/polys')
    os.chdir(self._jobname)
    cwd = os.getcwd()
    print("Current directory is now: %s\n"%cwd)
    print "Jobname is ", self._jobname   

def create_network(self):
    print '--> Running DFNGEN'    
    # copy input file into job folder    
    os.system(os.environ['DFNGEN_PATH']+'/./DFNGen ' + self._local_dfnGen_file[:-4] + '_clean.dat' + ' ' + self._jobname )

    if os.path.isfile("params.txt") is False:
        print '--> Generation Failed'
        print '--> Exiting Program'
        exit()
    else:
        print('-'*80)
        print("Generation Succeeded")
        print('-'*80)
