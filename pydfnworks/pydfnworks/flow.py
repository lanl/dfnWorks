import os 
import subprocess
import sys
import helper
import glob
import shutil
from time import time 
import numpy as np
import h5py


def set_flow_solver(self, flow_solver):
    ''' set_flow_solver: sets DFN.flow_solver
        
    Kwargs:
        * flow_solver: name of flow solver. Currently supported flow sovlers are FEHM and PFLOTRAN
    '''
    if flow_solver == "FEHM" or flow_solver == "PFLOTRAN":
        print("Using flow solver %s"%flow_solver)
        self.flow_solver = flow_solver
    else:
        sys.exit("ERROR: Unknown flow solver requested %s\nCurrently supported flow solvers are FEHM and PFLOTRAN\nExiting dfnWorks\n"%flow_solver)


def dfn_flow(self):
    ''' dfnFlow
    Run the dfnFlow portion of the workflow.
    ''' 

    print('='*80)
    print("\ndfnFlow Starting\n")
    print('='*80)

    tic_flow = time()
    
    if self.flow_solver == "PFLOTRAN":
        print("Using flow solver: %s"%self.flow_solver)
        tic = time()
        self.lagrit2pflotran()
        helper.dump_time(self.jobname, 'Function: lagrit2pflotran', time() - tic)   
        
        tic = time()    
        self.pflotran()
        helper.dump_time(self.jobname, 'Function: pflotran', time() - tic)  

        tic = time()    
        self.parse_pflotran_vtk_python()
        helper.dump_time(self.jobname, 'Function: parse_pflotran_vtk', time() - tic)    

        tic = time()    
        self.pflotran_cleanup()
        helper.dump_time(self.jobname, 'Function: parse_cleanup', time() - tic) 
    elif self.flow_solver == "FEHM":
        print("Using flow solver: %s"%self.flow_solver)
        self.correct_stor_file()
        self.fehm()

    helper.dump_time(self.jobname,'Process: dfnFlow',time() - tic_flow)    

    print('='*80)
    print("\ndfnFlow Complete\n")
    print('='*80)
       
def lagrit2pflotran(self, inp_file='', mesh_type='', hex2tet=False):
    """  Takes output from LaGriT and processes it for use in PFLOTRAN.
    
    Kwargs:
        * inp_file (str): name of the inp (AVS) file produced by LaGriT 
        * mesh_type (str): the type of mesh
        * hex2tet (boolean): True if hex mesh elements should be converted to tet elements, False otherwise.
    """
    if self.flow_solver != "PFLOTRAN":
        sys.exit("ERROR! Wrong flow solver requested")
    print ('='*80)
    print("Starting conversion of files for PFLOTRAN ")
    print ('='*80)
    if inp_file:
        self.inp_file = inp_file
    else:
        inp_file = self.inp_file

    if inp_file == '':
        sys.exit('ERROR: Please provide inp filename!')

    if mesh_type:
        if mesh_type in mesh_types_allowed:
            self.mesh_type = mesh_type
        else:
            sys.exit('ERROR: Unknown mesh type. Select one of dfn, volume or mixed!')
    else:
        mesh_type = self.mesh_type

    if mesh_type == '':
        sys.exit('ERROR: Please provide mesh type!')

    self.uge_file = inp_file[:-4] + '.uge'
    # Check if UGE file was created by LaGriT, if it does not exists, exit
    failure = os.path.isfile(self.uge_file)
    if failure == False:
        sys.exit('Failed to run LaGrit to get initial .uge file')

    if mesh_type == 'dfn':
        self.write_perms_and_correct_volumes_areas() # Make sure perm and aper files are specified

    # Convert zone files to ex format
    #self.zone2ex(zone_file='boundary_back_s.zone',face='south')
    #self.zone2ex(zone_file='boundary_front_n.zone',face='north')
    #self.zone2ex(zone_file='boundary_left_w.zone',face='west')
    #self.zone2ex(zone_file='boundary_right_e.zone',face='east')
    #self.zone2ex(zone_file='boundary_top.zone',face='top')
    #self.zone2ex(zone_file='boundary_bottom.zone',face='bottom')
    self.zone2ex(zone_file='all')
    print ('='*80)
    print("Conversion of files for PFLOTRAN complete")
    print ('='*80)
    print("\n\n")

def zone2ex(self, uge_file='', zone_file='', face='', boundary_cell_area = 1.e-1):
    '''zone2ex    
    Convert zone files from LaGriT into ex format for LaGriT
    inputs:
    uge_file: name of uge file
    zone_file: name of zone file
    face: face of the plane corresponding to the zone file

    zone_file='all' processes all directions, top, bottom, left, right, front, back
    '''

    print('--> Converting zone files to ex')    
    if self.uge_file:
        uge_file = self.uge_file
    else:
        self.uge_file = uge_file

    uge_file = self.uge_file
    if uge_file == '':
        sys.exit('ERROR: Please provide uge filename!')
    # Opening uge file
    print('\n--> Opening uge file')
    fuge = open(uge_file, 'r')

    # Reading cell ids, cells centers and cell volumes
    line = fuge.readline()
    line = line.split()
    NumCells = int(line[1])

    Cell_id = np.zeros(NumCells, 'int')
    Cell_coord = np.zeros((NumCells, 3), 'float')
    Cell_vol = np.zeros(NumCells, 'float')

    for cells in range(NumCells):
        line = fuge.readline()
        line = line.split()
        Cell_id[cells] = int(line.pop(0))
        line = [float(id) for id in line]
        Cell_vol[cells] = line.pop(3)
        Cell_coord[cells] = line
    fuge.close()

    print('--> Finished with uge file\n')

    # loop through zone files
    if zone_file is 'all':
            zone_files = ['pboundary_front_n.zone', 'pboundary_back_s.zone', 'pboundary_left_w.zone', \
                            'pboundary_right_e.zone', 'pboundary_top.zone', 'pboundary_bottom.zone']
            face_names = ['north', 'south', 'west', 'east', 'top', 'bottom']
    else: 
            if zone_file == '':
                sys.exit('ERROR: Please provide boundary zone filename!')
            if face == '':
                sys.exit('ERROR: Please provide face name among: top, bottom, north, south, east, west !')
            zone_files = [zone_file]
            face_names = [face]
            
    for iface,zone_file in enumerate(zone_files):
            face = face_names[iface]
            # Ex filename
            ex_file = zone_file.strip('zone') + 'ex'

            # Opening the input file
            print '--> Opening zone file: ', zone_file
            fzone = open(zone_file, 'r')
            fzone.readline()
            fzone.readline()
            fzone.readline()

            # Read number of boundary nodes
            print('--> Calculating number of nodes')
            NumNodes = int(fzone.readline())
            Node_array = np.zeros(NumNodes, 'int')
            # Read the boundary node ids
            print('--> Reading boundary node ids')

            if (NumNodes < 10):
                g = fzone.readline()
                node_array = g.split()
                # Convert string to integer array
                node_array = [int(id) for id in node_array]
                Node_array = np.asarray(node_array)
            else:
                for i in range(NumNodes / 10 + 1):
                    g = fzone.readline()
                    node_array = g.split()
                    # Convert string to integer array
                    node_array = [int(id) for id in node_array]
                    if (NumNodes - 10 * i < 10):
                        for j in range(NumNodes % 10):
                            Node_array[i * 10 + j] = node_array[j]
                    else:
                        for j in range(10):
                            Node_array[i * 10 + j] = node_array[j]
            fzone.close()
            print('--> Finished with zone file')

            Boundary_cell_area = np.zeros(NumNodes, 'float')
            for i in range(NumNodes):
                Boundary_cell_area[i] = boundary_cell_area  # Fix the area to a large number

            print('--> Finished calculating boundary connections')

            boundary_cell_coord = [Cell_coord[Cell_id[i - 1] - 1] for i in Node_array]
            epsilon = 1e-0  # Make distance really small
            if (face == 'top'):
                boundary_cell_coord = [[cell[0], cell[1], cell[2] + epsilon] for cell in boundary_cell_coord]
            elif (face == 'bottom'):
                boundary_cell_coord = [[cell[0], cell[1], cell[2] - epsilon] for cell in boundary_cell_coord]
            elif (face == 'north'):
                boundary_cell_coord = [[cell[0], cell[1] + epsilon, cell[2]] for cell in boundary_cell_coord]
            elif (face == 'south'):
                boundary_cell_coord = [[cell[0], cell[1] - epsilon, cell[2]] for cell in boundary_cell_coord]
            elif (face == 'east'):
                boundary_cell_coord = [[cell[0] + epsilon, cell[1], cell[2]] for cell in boundary_cell_coord]
            elif (face == 'west'):
                boundary_cell_coord = [[cell[0] - epsilon, cell[1], cell[2]] for cell in boundary_cell_coord]
            elif (face == 'none'):
                boundary_cell_coord = [[cell[0], cell[1], cell[2]] for cell in boundary_cell_coord]
            else:
                sys.exit('ERROR: unknown face. Select one of: top, bottom, east, west, north, south.')

            with open(ex_file, 'w') as f:
                f.write('CONNECTIONS\t%i\n' % Node_array.size)
                for idx, cell in enumerate(boundary_cell_coord):
                    f.write('%i\t%.6e\t%.6e\t%.6e\t%.6e\n' % (
                        Node_array[idx], cell[0], cell[1], cell[2], Boundary_cell_area[idx]))
            print('--> Finished writing ex file "' + ex_file + '" corresponding to the zone file: ' + zone_file+'\n')

    print('--> Converting zone files to ex complete')    

def inp2gmv(self, inp_file=''):
    """ Convert inp file to gmv file, for general mesh viewer .
    
    Kwargs:
        inp_file (str): name of inp file
    """

    if inp_file:
        self.inp_file = inp_file
    else:
        inp_file = self.inp_file

    if inp_file == '':
        sys.exit('ERROR: inp file must be specified in inp2gmv!')

    gmv_file = inp_file[:-4] + '.gmv'

    with open('inp2gmv.lgi', 'w') as fid:
        fid.write('read / avs / ' + inp_file + ' / mo\n')
        fid.write('dump / gmv / ' + gmv_file + ' / mo\n')
        fid.write('finish \n\n')

    cmd = lagrit_path + ' <inp2gmv.lgi ' + '> lagrit_inp2gmv.txt'
    failure = subprocess.call(cmd, shell = True)
    if failure:
        sys.exit('ERROR: Failed to run LaGrit to get gmv from inp file!')
    print("--> Finished writing gmv format from avs format")


def write_perms_and_correct_volumes_areas(self, inp_file='', uge_file='', perm_file='', aper_file=''):
    """ Write permeability values to perm_file, write aperture values to aper_file, and correct volume areas in uge_file 
    """
    print("--> Writing Perms and Correct Volume Areas")
    if inp_file:
        self.inp_file = inp_file
    else:
        inp_file = self.inp_file
    
    if inp_file == '':
        sys.exit('ERROR: inp file must be specified!')

    if uge_file:
        self.uge_file = uge_file
    else:
        uge_file = self.uge_file

    if uge_file == '':
        sys.exit('ERROR: uge file must be specified!')

    if perm_file:
        self.perm_file = perm_file
    else:
        perm_file = self.perm_file

    if perm_file == '' and self.perm_cell_file == '':
        sys.exit('ERROR: perm file must be specified!')

    if aper_file:
        self.aper_file = aper_file
    else:
        aper_file = self.aper_file

    if aper_file == '' and self.aper_cell_file == '':
        sys.exit('ERROR: aperture file must be specified!')

    mat_file = 'materialid.dat'
    t = time()
    # Make input file for C UGE converter
    f = open("convert_uge_params.txt", "w")
    f.write("%s\n"%inp_file)
    f.write("%s\n"%mat_file)
    f.write("%s\n"%uge_file)
    f.write("%s"%(uge_file[:-4]+'_vol_area.uge\n'))
    if self.aper_cell_file:
            f.write("%s\n"%self.aper_cell_file)
            f.write("1\n")
    else:
            f.write("%s\n"%self.aper_file)
            f.write("-1\n")
    f.close()

    cmd = os.environ['correct_uge_PATH']+ 'correct_uge' + ' convert_uge_params.txt' 
    failure = subprocess.call(cmd, shell = True)
    if failure > 0:
            sys.exit('ERROR: UGE conversion failed\nExiting Program')
    elapsed = time() - t
    print '--> Time elapsed for UGE file conversion: %0.3f seconds\n'%elapsed

    # need number of nodes and mat ID file
    print('--> Writing HDF5 File')
    materialid = np.genfromtxt(mat_file, skip_header = 3).astype(int)
    materialid = -1 * materialid - 6
    NumIntNodes = len(materialid)

    if perm_file:
        filename = 'dfn_properties.h5'
        h5file = h5py.File(filename, mode='w')
        print('--> Beginning writing to HDF5 file')
        print('--> Allocating cell index array')
        iarray = np.zeros(NumIntNodes, '=i4')
        print('--> Writing cell indices')
        # add cell ids to file
        for i in range(NumIntNodes):
            iarray[i] = i + 1
        dataset_name = 'Cell Ids'
        h5dset = h5file.create_dataset(dataset_name, data=iarray)

        print ('--> Allocating permeability array')
        perm = np.zeros(NumIntNodes, '=f8')

        print('--> reading permeability data')
        print('--> Note: this script assumes isotropic permeability')
        perm_list = np.genfromtxt(perm_file,skip_header = 1)
        perm_list = np.delete(perm_list, np.s_[1:5], 1)

        matid_index = -1*materialid - 7
        for i in range(NumIntNodes):
            j = matid_index[i]
            if int(perm_list[j,0]) == materialid[i]:
                    perm[i] = perm_list[j, 1]
            else:
                    sys.exit('Indexing Error in Perm File')

        dataset_name = 'Permeability'
        h5dset = h5file.create_dataset(dataset_name, data=perm)

        h5file.close()
        print("--> Done writing permeability to h5 file")
        del perm_list

    if self.perm_cell_file:
        filename = 'dfn_properties.h5'
        h5file = h5py.File(filename, mode='w')

        print('--> Beginning writing to HDF5 file')
        print('--> Allocating cell index array')
        iarray = np.zeros(NumIntNodes, '=i4')
        print('--> Writing cell indices')
        # add cell ids to file
        for i in range(NumIntNodes):
            iarray[i] = i + 1
        dataset_name = 'Cell Ids'
        h5dset = h5file.create_dataset(dataset_name, data=iarray)
        print ('--> Allocating permeability array')
        perm = np.zeros(NumIntNodes, '=f8')
        print('--> reading permeability data')
        print('--> Note: this script assumes isotropic permeability')
        f = open(self.perm_cell_file, 'r')
        f.readline()
        perm_list = []
        while True:
            h = f.readline()
            h = h.split()
            if h == []:
                break
            h.pop(0)
            perm_list.append(h)

        perm_list = [float(perm[0]) for perm in perm_list]
        
        dataset_name = 'Permeability'
        h5dset = h5file.create_dataset(dataset_name, data=perm_list)
        f.close()

        h5file.close()
        print('--> Done writing permeability to h5 file')


def pflotran(self):
    ''' Run pflotran
    Copy PFLOTRAN run file into working directory and run with ncpus
    '''
    if self.flow_solver != "PFLOTRAN":
        sys.exit("ERROR! Wrong flow solver requested")
    try: 
            shutil.copy(os.path.abspath(self.dfnFlow_file), os.path.abspath(os.getcwd()))
    except:
            print("-->ERROR copying PFLOTRAN input file")
            exit()
    print("="*80)
    print("--> Running PFLOTRAN") 
    cmd = os.environ['PETSC_DIR']+'/'+os.environ['PETSC_ARCH']+'/bin/mpirun -np ' + str(self.ncpu) + \
          ' ' + os.environ['PFLOTRAN_DIR']+'/src/pflotran/pflotran -pflotranin ' + self.local_dfnFlow_file 
    print("Running: %s"%cmd)
    subprocess.call(cmd, shell = True)
    print('='*80)
    print("--> Running PFLOTRAN Complete")
    print('='*80)
    print("\n")

def pflotran_cleanup(self, index = 1):
    '''pflotran_cleanup
    Concatenate PFLOTRAN output files and then delete them 
    input: index, if PFLOTRAN has multiple dumps use this to pick which
           dump is put into cellinfo.day and darcyvel.dat
    '''
    if self.flow_solver != "PFLOTRAN":
        sys.exit("ERROR! Wrong flow solver requested")
    print '--> Processing PFLOTRAN output' 
    
    cmd = 'cat '+self.local_dfnFlow_file[:-3]+'-cellinfo-%03d-rank*.dat > cellinfo.dat'%index
    print("Running >> %s"%cmd)
    subprocess.call(cmd, shell = True)

    cmd = 'cat '+self.local_dfnFlow_file[:-3]+'-darcyvel-%03d-rank*.dat > darcyvel.dat'%index
    print("Running >> %s"%cmd)
    subprocess.call(cmd, shell = True)

    for fl in glob.glob(self.local_dfnFlow_file[:-3]+'-cellinfo-000-rank*.dat'):
            os.remove(fl)    
    for fl in glob.glob(self.local_dfnFlow_file[:-3]+'-darcyvel-000-rank*.dat'):
            os.remove(fl)    

    for fl in glob.glob(self.local_dfnFlow_file[:-3]+'-cellinfo-%03d-rank*.dat'%index):
            os.remove(fl)    
    for fl in glob.glob(self.local_dfnFlow_file[:-3]+'-darcyvel-%03d-rank*.dat'%index):
            os.remove(fl)    

def create_dfn_flow_links(self, path = '../'):
    files = ['full_mesh.uge', 'full_mesh.inp', 'full_mesh_vol_area.uge',
        'materialid.dat','pboundary_bottom.zone', 'pboundary_top.zone', 
        'pboundary_back_s.zone', 'pboundary_front_n.zone', 
        'pboundary_left_w.zone', 'pboundary_right_e.zone']
    for f in files:
        try:
            os.symlink(path+f, f)
        except:
            print("--> Error Creating link for %s"%f)
 
def uncorrelated(self, sigma, path = '../'):
    print '--> Creating Uncorrelated Transmissivity Fields'
    print 'Variance: ', sigma
    print 'Running un-correlated'
    x = np.genfromtxt(path + 'aperture.dat', skip_header = 1)[:,-1]
    k = np.genfromtxt(path + '/perm.dat', skip_header = 1)[0,-1]
    n = len(x)

    print np.mean(x)

    perm = np.log(k)*np.ones(n) 
    perturbation = np.random.normal(0.0, 1.0, n)
    perm = np.exp(perm + np.sqrt(sigma)*perturbation) 

    aper = np.sqrt((12.0*perm))
    #aper -= np.mean(aper)
    #aper += np.mean(x)

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

    output_filename = 'aperture_' + str(sigma) + '.dat'
    f = open(output_filename,'w+')
    f.write('aperture\n')
    for i in range(n):
    	f.write('-%d 0 0 %0.5e\n'%(i + 7, aper[i]))
    f.close()
    os.symlink(output_filename, 'aperture.dat')

    output_filename = 'perm_' + str(sigma) + '.dat'
    f = open(output_filename,'w+')
    f.write('permeability\n')
    for i in range(n):
    	f.write('-%d 0 0 %0.5e %0.5e %0.5e\n'%(i+7, perm[i], perm[i], perm[i]))
    f.close()

    os.symlink(output_filename, 'perm.dat')
        

def parse_pflotran_vtk(self, grid_vtk_file=''): 
    """ Using C++ VTK library, convert inp file to VTK file, then change name of CELL_DATA to POINT_DATA.
    """
    if self.flow_solver != "PFLOTRAN":
        sys.exit("ERROR! Wrong flow solver requested")
    print '--> Parsing PFLOTRAN output using C++'
    files = glob.glob('*-[0-9][0-9][0-9].vtk')
    out_dir = 'parsed_vtk'
    vtk_filename_list = []
    replacements = {'CELL_DATA':'POINT_DATA'} 
    header = ['# vtk DataFile Version 2.0\n',
              'PFLOTRAN output\n',
              'ASCII\n']
   
    inp_file = self.inp_file
    inp_file_copy = self.inp_file[:-4] + '_copy.inp'
    subprocess.call('cp ' + inp_file + ' ' + inp_file_copy, shell=True)
    jobname = self.jobname + '/'

    for fle in files:

        if os.stat(fle).st_size == 0:
            print 'ERROR: opening an empty pflotran output file'
            exit()
        
        temp_file = fle[:-4] + '_temp.vtk'
        with open(fle, 'r') as infile, open(temp_file, 'w') as outfile:
            ct = 0 
            for line in infile:
                if 'CELL_DATA' in line:
                    num_cells = line.strip(' ').split()[1]
                    outfile.write('POINT_DATA\t ' + num_cells + '\n')
                else: 
                    outfile.write(line)
        infile.close()
        outfile.close()
        vtk_filename = out_dir + '/' + fle.split('/')[-1]
        if not os.path.exists(os.path.dirname(vtk_filename)):
            os.makedirs(os.path.dirname(vtk_filename))
        arg_string = os.environ['VTK_PATH'] + ' '  +  jobname + inp_file + ' ' + jobname + vtk_filename  
        subprocess.call(arg_string, shell=True)
        arg_string = 'tail -n +6 ' + jobname + temp_file + ' > ' + jobname + temp_file + '.tmp && mv ' + jobname + temp_file +  '.tmp ' + jobname + temp_file  
        subprocess.call(arg_string, shell=True)
        arg_string = 'cat ' +  jobname + temp_file + ' >> ' + jobname + vtk_filename
        subprocess.call(arg_string, shell=True) 

    print '--> Parsing PFLOTRAN output complete'

def inp2vtk_python(self, inp_file=''):
    import pyvtk as pv
    """ Using Python VTK library, convert inp file to VTK file.  then change name of CELL_DATA to POINT_DATA.
    """
    if self.flow_solver != "PFLOTRAN":
        sys.exit("ERROR! Wrong flow solver requested")
    print("--> Using Python to convert inp files to VTK files")
    if self.inp_file:
        inp_file = self.inp_file
    else:
        self.inp_file = inp_file

    if inp_file == '':
        sys.exit('ERROR: Please provide inp filename!')

    if self.vtk_file:
        vtk_file = self.vtk_file
    else:
        vtk_file = inp_file[:-4]
        self.vtk_file = vtk_file + '.vtk'

    print("--> Reading inp data")

    with open(inp_file, 'r') as f:
        line = f.readline()
        num_nodes = int(line.strip(' ').split()[0])
        num_elems = int(line.strip(' ').split()[1])

        coord = np.zeros((num_nodes, 3), 'float')
        elem_list_tri = []
        elem_list_tetra = []

        for i in range(num_nodes):
            line = f.readline()
            coord[i, 0] = float(line.strip(' ').split()[1])
            coord[i, 1] = float(line.strip(' ').split()[2])
            coord[i, 2] = float(line.strip(' ').split()[3])

        for i in range(num_elems):
            line = f.readline().strip(' ').split()
            line.pop(0)
            line.pop(0)
            elem_type = line.pop(0)
            if elem_type == 'tri':
                elem_list_tri.append([int(i) - 1 for i in line])
            if elem_type == 'tet':
                elem_list_tetra.append([int(i) - 1 for i in line])

    print('--> Writing inp data to vtk format')

    vtk = pv.VtkData(pv.UnstructuredGrid(coord, tetra=elem_list_tetra, triangle=elem_list_tri),
                     'Unstructured pflotran grid')
    vtk.tofile(vtk_file)


def parse_pflotran_vtk_python(self, grid_vtk_file=''):
    """ Replace CELL_DATA with POINT_DATA in the VTK output."""
    print '--> Parsing PFLOTRAN output with Python'
    if self.flow_solver != "PFLOTRAN":
        sys.exit("ERROR! Wrong flow solver requested")
    if grid_vtk_file:
        self.vtk_file = grid_vtk_file
    else:
        self.inp2vtk_python()

    grid_file = self.vtk_file
    
    files = glob.glob('*-[0-9][0-9][0-9].vtk')
    with open(grid_file, 'r') as f:
        grid = f.readlines()[3:]

    out_dir = 'parsed_vtk'
    for line in grid:
        if 'POINTS' in line:
            num_cells = line.strip(' ').split()[1]

    for file in files:
        with open(file, 'r') as f:
            pflotran_out = f.readlines()[4:]
        pflotran_out = [w.replace('CELL_DATA', 'POINT_DATA ') for w in pflotran_out]
        header = ['# vtk DataFile Version 2.0\n',
                  'PFLOTRAN output\n',
                  'ASCII\n']
        filename = out_dir + '/' + file
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'w') as f:
            for line in header:
                f.write(line)
            for line in grid:
                f.write(line)
            f.write('\n')
            f.write('\n')
            if 'vel' in file:
                f.write('POINT_DATA\t ' + num_cells + '\n')
            for line in pflotran_out:
                f.write(line)
    print '--> Parsing PFLOTRAN output complete'

def correct_stor_file(self):
    """corrects volumes in stor file to account for apertures"""
     # Make input file for C Stor converter
    if self.flow_solver != "FEHM":
        sys.exit("ERROR! Wrong flow solver requested")

    self.stor_file = self.inp_file[:-4] + '.stor'
    self.mat_file= self.inp_file[:-4] + '_material.zone'
    f = open("convert_stor_params.txt", "w")
    f.write("%s\n"%self.mat_file)
    f.write("%s\n"%self.stor_file)
    f.write("%s"%(self.stor_file[:-5]+'_vol_area.stor\n'))
    f.write("%s\n"%self.aper_file)
    f.close()

    t = time()
    cmd = os.environ['correct_stor_PATH']+ 'correct_stor' + ' convert_stor_params.txt' 
    failure = subprocess.call(cmd, shell = True)
    if failure > 0:
            sys.exit('ERROR: stor conversion failed\nExiting Program')
    elapsed = time() - t
    print('--> Time elapsed for STOR file conversion: %0.3f seconds\n'%elapsed)

def fehm(self):
    """ runs fehm """
    if self.flow_solver != "FEHM":
        sys.exit("ERROR! Wrong flow solver requested")
    print("Here is where I'll run FEHM") 
    subprocess.call(os.environ["FEHM_DIR"]+os.sep+"xfehm", shell = True)

