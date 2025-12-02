import os 
from shutil import copy, move
from pydfnworks.dfnGen.meshing.mesh_dfn import mesh_dfn_helper as mh

def load_connectivity_file(path):
    """ Load file
 
    Parameters
    ---------
        path : path to file

    Returns
    -------
        connectivity : list

    Notes
    -----

   """
    connectivity = []
    with open(path + "/dfnGen_output/connectivity.dat", "r") as fp:
        for line in fp.readlines():
            tmp = []
            line = line.split()
            for frac in line:
                tmp.append(int(frac))
            connectivity.append(tmp)
    return connectivity

def edit_intersection_files(self):
    """ If pruning a DFN, this function walks through the intersection files
    and removes references to files that are not included in the 
    fractures that will remain in the network.
 
    Parameters
    ---------
        self.num_frac : int 
            Number of Fractures in the original DFN
        
        fracture_list :list of int
            List of fractures to keep in the DFN

    Returns
    -------
        None

    Notes
    -----
    1. Currently running in serial, but it could be parallelized
    2. Assumes the pruning directory is not the original directory

   """
    # Make list of connectivity.dat
    fractures_to_remove = list(
        set(range(1, self.num_frac + 1)) - set(self.fracture_list))

    # remove symbolic link and setup local intersection directory
    if os.path.isdir(self.jobname + '/intersections'):
        os.unlink(self.jobname + '/intersections')
        os.mkdir(self.jobname + '/intersections')
    else:
        os.mkdir(self.jobname + '/intersections')
    os.chdir(self.jobname + '/intersections')

    ## DEBUGGING ##
    # clean up directory
    #fl_list = glob.glob("*prune.inp")
    #for fl in fl_list:
    #   os.remove(fl)
    ## DEBUGGING ##

    self.print_log("--> Editing Intersection Files")
    connectivity = load_connectivity_file(self.path)


    ## Note this could be easily changed to run in parallel if needed. Just use cf
    for ifrac in self.fracture_list:
        filename = f'intersections_{ifrac}.inp'
        self.print_log(f'--> Working on: {filename}')
        intersecting_fractures = connectivity[ifrac - 1]
        pull_list = list(
            set(intersecting_fractures).intersection(set(fractures_to_remove)))
        if len(pull_list) > 0:
            # Create Symlink to original intersection file
            os.symlink(self.path + 'intersections/' + filename, filename)
            # Create LaGriT script to remove intersections with fractures not in prune_file
            lagrit_script = f"""
read / {filename} / mo1 
pset / pset2remove / attribute / b_a / 1,0,0 / eq / {pull_list[0]}
"""
            for jfrac in pull_list[1:]:
                lagrit_script += f'''
pset / prune / attribute / b_a / 1,0,0 / eq / {jfrac}
pset / pset2remove / union / pset2remove, prune
rmpoint / pset, get, prune
pset / prune / delete
     '''
            lagrit_script += f'''
rmpoint / pset, get, pset2remove 
rmpoint / compress
    
cmo / modatt / mo1 / imt / ioflag / l
cmo / modatt / mo1 / itp / ioflag / l
cmo / modatt / mo1 / isn / ioflag / l
cmo / modatt / mo1 / icr / ioflag / l
    
cmo / status / brief
dump / intersections_{ifrac}_prune.inp / mo1
finish
'''

            lagrit_filename = 'prune_intersection.lgi'
            with open(lagrit_filename, 'w') as f:
                f.write(lagrit_script)
                f.flush()

            mh.run_lagrit_script("prune_intersection.lgi",
                                 f"pruning_{ifrac}.txt",
                                 quiet=True)
            
            os.remove(filename)
            if os.path.isfile(f"intersections_{ifrac}_prune.inp"):
                move(f"intersections_{ifrac}_prune.inp",
                     f"intersections_{ifrac}.inp")
            else:
                error = f"Error. intersections_{ifrac}_prune.inp file not found.\nExitting Program"
                self.print_log(error, 'error')
        else:
            try:
                copy(self.path + 'intersections/' + filename, filename)
            except Exception as e:
                error = f"Error creating path for {filename}\n {e}.\nExitting Program" 
                self.print_log(error, 'error')
                pass

    os.chdir(self.jobname)
    self.num_frac = len(self.fracture_list)
    self.print_log("--> Done editting intersection files")

