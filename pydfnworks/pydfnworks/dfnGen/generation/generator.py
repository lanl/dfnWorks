import os
import sys
import numpy as np
import shutil
from time import time
import subprocess


def dfn_gen(self, output=True):
    ''' Wrapper script the runs the dfnGen workflow:    
        1) make_working_directory: Create a directory with name of job
        2) check_input: Check input parameters and create a clean version of the input file
        3) create_network: Create network. DFNGEN v2.0 is called and creates the network
        4) output_report: Generate a PDF summary of the DFN generation
        5) mesh_network: calls module dfnGen_meshing and runs LaGriT to mesh the DFN

    Parameters
    ----------
        self :
            DFN object
        output : bool
            If True, output pdf will be created. If False, no pdf is made 
        visual_mode : None
            If the user wants to run in a different meshing mode from what is in params.txt, set visual_mode = True/False on command line to override meshing mode

    Returns
    -------
        None

    Notes
    -----
        Details of each portion of the routine are in those sections

    '''
    # Create Working directory
    self.make_working_directory()
    # Check input file
    self.check_input()
    # Create network
    self.create_network()
    if output:
        self.output_report()
    # Mesh Network
    self.mesh_network()
    print('=' * 80)
    print('dfnGen Complete')
    print('=' * 80)


def make_working_directory(self, delete=False):
    ''' Make working directory for dfnWorks Simulation

    Parameters
    ----------
        self :
            DFN object

        delete : bool
            If True, deletes the existing working directory. Default = False

    Returns
    -------
        None

    Notes
    -----
    If directory already exists, user is prompted if they want to overwrite and proceed. If not, program exits. 
    '''

    if not delete:
        try:
            os.mkdir(self.jobname)
        except OSError:
            if os.path.isdir(self.jobname):
                print('\nFolder ', self.jobname, ' exists')
                keep = input('Do you want to delete it? [yes/no] \n')
                if keep == 'yes' or keep == 'y':
                    print('Deleting', self.jobname)
                    shutil.rmtree(self.jobname)
                    print('Creating', self.jobname)
                    os.mkdir(self.jobname)
                elif keep == 'no' or 'n':
                    error = "Not deleting folder. Exiting Program\n"
                    sys.stderr.write(error)
                    sys.exit(1)
                else:
                    error = "Unknown Response. Exiting Program\n"
                    sys.stderr.write(error)
                    sys.exit(1)
            else:
                error = f"Unable to create working directory {self.jobname}\n. Please check the provided path.\nExiting\n"
                sys.stderr.write(error)
                sys.exit(1)
    else:
        if not os.path.isdir(self.jobname):
            os.mkdir(self.jobname)
        else:
            try:
                shutil.rmtree(self.jobname)
                print('--> Creating ', self.jobname)
                os.mkdir(self.jobname)
            except:
                error = "ERROR deleting and creating directory.\nExiting\n"
                sys.stderr.write(error)
                sys.exit(1)

    os.mkdir(self.jobname + '/dfnGen_output')
    os.mkdir(self.jobname + '/dfnGen_output/radii')
    os.mkdir(self.jobname + '/intersections')
    os.mkdir(self.jobname + '/polys')
    os.chdir(self.jobname)

    print(f"Current directory is now: {os.getcwd()}")
    print(f"Jobname is {self.jobname}")


def create_network(self):
    ''' Execute dfnGen

    Parameters
    ----------
        self :
            DFN object 

    Returns
    -------
        None

    Notes
    -----
    After generation is complete, this script checks whether the generation of the fracture network failed or succeeded based on the existence of the file params.txt. 
    '''
    print('--> Running DFNGEN')
    os.chdir(self.jobname)
    cmd = os.environ[
        'DFNGEN_EXE'] + ' ' + 'dfnGen_output/' + self.local_dfnGen_file[:
                                                     -4] + '_clean.dat' + ' ' + self.jobname

    print(f"Running:\n>>{cmd}")
    subprocess.call(cmd, shell=True)

    if os.path.isfile("params.txt"):
        self.gather_dfn_gen_output()
        self.assign_hydraulic_properties()
        print('-' * 80)
        print("Generation Succeeded")
        print('-' * 80)
    else:
        error = f"Error. Unable to find 'params.txt' in current directory {os.getcwd}.\n"
        sys.stderr.write(error)
        sys.exit(1)

def parse_params_file(self, quiet=False):
    """ Reads params.txt file from DFNGen and parses information

    Parameters
    ---------
        quiet : bool
            If True details are not printed to screen, if False they area 

    Returns
    -------
        None
    
    Notes
    -----
        None
    """
    if not quiet:
        print("\n--> Parsing  params.txt")

    fparams = open('params.txt', 'r')
    # Line 1 is the number of polygons
    self.num_frac = int(fparams.readline())
    #Line 2 is the h scale
    self.h = float(fparams.readline())
    # Line 3 is the visualization mode: '1' is True, '0' is False.
    self.visual_mode = int(fparams.readline())
    # line 4 dudded points
    self.dudded_points = int(fparams.readline())

    # Dict domain contains the length of the domain in x,y, and z
    self.domain = {'x': 0, 'y': 0, 'z': 0}
    #Line 5 is the x domain length
    self.domain['x'] = (float(fparams.readline()))

    #Line 5 is the x domain length
    self.domain['y'] = (float(fparams.readline()))

    #Line 5 is the x domain length
    self.domain['z'] = (float(fparams.readline()))
    self.r_fram = self.params['rFram']['value']
    
    fparams.close()

    if not quiet:
        print("--> Number of Fractures: %d" % self.num_frac)
        print(f"--> h: {self.h:0.2e} m")
        if self.visual_mode > 0:
            self.visual_mode = True
            print("--> Visual mode is on")
        else:
            self.visual_mode = False
            print("--> Visual mode is off")

        print(f"--> Expected Number of dudded points: {self.dudded_points}")
        print(f"--> X Domain Size {self.domain['x']} m")
        print(f"--> Y Domain Size {self.domain['y']} m")
        print(f"--> Z Domain Size {self.domain['z']} m")
        
        self.x_min = -0.5*self.domain['x']
        self.x_max = 0.5*self.domain['x']

        self.y_min = -0.5*self.domain['y']
        self.y_max = 0.5*self.domain['y']
        
        self.z_max = 0.5*self.domain['z']
        self.z_min = -0.5*self.domain['z']

        print("--> Parsing params.txt complete\n")


def gather_dfn_gen_output(self):
    """ Reads in information about fractures and add them to the DFN object. Information is taken from radii.dat, translations.dat, normal_vectors.dat, and surface_area_Final.dat files. Information for each fracture is stored in a dictionary created by create_fracture_dictionary() that includes the fracture id, radius, normal vector, center, family number, surface area, and if the fracture was removed due to being isolated 

    Parameters
    -----------
        None

    Returns
    --------
        fractures : list
            List of fracture dictionaries with information.
    Notes
    ------
        Both fractures in the final network and those removed due to being isolated are included in the list. 

    """
    print("--> Parsing dfnWorks output and adding to object")
    self.parse_params_file(quiet=False)

    ## load radii
    data = np.genfromtxt('dfnGen_output/radii_Final.dat', skip_header=2)
    ## populate radius array
    self.radii = np.zeros((self.num_frac, 3))
    # First Column is x, second is y, 3rd is max
    if self.num_frac == 1:
        data = np.array([data])
    
    self.radii[:, :2] = data[:, :2]
    for i in range(self.num_frac):
        self.radii[i, 2] = max(self.radii[i, 0], self.radii[i, 1])

    # gather fracture families
    self.families = data[:, 2].astype(int)

    ## load surface area
    self.surface_area = np.genfromtxt('dfnGen_output/surface_area_Final.dat', skip_header=1)
    ## load normal vectors
    self.normal_vectors = np.genfromtxt('dfnGen_output/normal_vectors.dat')
    # Get fracture centers
    centers = []
    with open('dfnGen_output/translations.dat', "r") as fp:
        fp.readline()  # header
        for i, line in enumerate(fp.readlines()):
            if "R" not in line:
                line = line.split()
                centers.append(
                    [float(line[0]),
                     float(line[1]),
                     float(line[2])])
    self.centers = np.array(centers)

    # Grab Polygon information
    self.poly_info = np.genfromtxt('poly_info.dat')

    # write polygon information to class
    if self.store_polygon_data == True:
        self.grab_polygon_data()

    ## create holder arrays for b, k, and T
    self.aperture = np.zeros(self.num_frac)
    self.perm = np.zeros(self.num_frac)
    self.transmissivity = np.zeros(self.num_frac)

    # gather indexes for fracture families
    self.family = []
    ## get number of families
    self.num_families = int(max(self.families))
    for i in range(1, self.num_families + 1):
        idx = np.where(self.families == i)
        self.family.append(idx)

    # get fracture_info
    self.fracture_info = np.genfromtxt('dfnGen_output/fracture_info.dat', skip_header = 1)
    
    # get intersection_list
    self.intersection_list = np.genfromtxt('dfnGen_output/intersection_list.dat', skip_header = 1)
    
    # get boundary_files
    self.back = read_boundaries('dfnGen_output/back.dat')
    self.front = read_boundaries('dfnGen_output/front.dat')
    self.left = read_boundaries('dfnGen_output/left.dat')
    self.right = read_boundaries('dfnGen_output/right.dat')
    self.top = read_boundaries('dfnGen_output/top.dat')
    self.bottom = read_boundaries('dfnGen/bottom.dat')

def read_boundaries(file_path):
    '''Reads in boundary files, and corrects format is file is empty of length 1
    Parameters
    -----------
        file_path : the path to boundary file

    Returns
    --------
        array of values (or empty array if file is empty
    
    Notes
    ------
    None
    '''

    if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
        data = np.genfromtxt(file_path)
    else:
        data = np.array([])

    try:
        array_length = len(data)
    except:
        data = np.array([data])

    return data


def assign_hydraulic_properties(self):
    '''Assigns hydraulic properties for each familiy and user defined fractures    
    
    Parameters
    -----------
        self : DFN object

    Returns
    --------
        None
    
    Notes
    ------
        None
    '''

    print("--> Assign hydraulic properties: Starting ")
    ### Assign variables for fracture families
    print("--> Assign hydraulic properties to fracture families : Starting ")
    for i in range(self.params['nFracFam']['value']):
        hy_variable = self.fracture_families[i]['hydraulic_properties'][
            'variable']['value']
        hy_function = self.fracture_families[i]['hydraulic_properties'][
            'function']['value']
        hy_params = self.fracture_families[i]['hydraulic_properties'][
            'params']['value']

        if hy_variable is not None:
            self.generate_hydraulic_values(hy_variable,
                                           hy_function,
                                           hy_params,
                                           family_id=i + 1)
    print("--> Assign hydraulic properties to fracture families : Complete ")

    ### Assign variables for user defined fractures
    ##Logic here, loop through user defined fractures
    ## first check flag to insert
    fracture_num = 1
    if self.params['insertUserRectanglesFirst']['value'] == 0:
        print('--> Inserting User Ellipse Hydraulic Params First')
        for i in range(len(self.user_ell_params)):
            for j in range(self.user_ell_params[i]['nPolygons']):
                print(f'--> Inserting User Ell Hydraulic Params {fracture_num}')
                hy_prop_type = self.user_ell_params[i]['hy_prop_type']
                value = self.user_ell_params[i][hy_prop_type][j]
                print(f'{hy_prop_type} = {value}')
                self.set_fracture_hydraulic_values(hy_prop_type, [fracture_num],
                                               [value])
                fracture_num += 1

        for i in range(len(self.user_rect_params)):
            for j in range(self.user_rect_params[i]['nPolygons']):
                print(f'--> Inserting User Rect Hydraulic Params {fracture_num}')
                hy_prop_type = self.user_rect_params[i]['hy_prop_type']
                value = self.user_rect_params[i][hy_prop_type][j]
                print(f'{hy_prop_type} = {value}')
                self.set_fracture_hydraulic_values(hy_prop_type, [fracture_num],
                                               [value])
                fracture_num += 1

        for i in range(len(self.user_poly_params)):
            for j in range(self.user_poly_params[i]['nPolygons']):
                print(f'--> Inserting User Poly Hydraulic Params {fracture_num}')
                hy_prop_type = self.user_poly_params[i]['hy_prop_type']
                value = self.user_poly_params[i][hy_prop_type][j]
                print(f'{hy_prop_type} = {value}')
                self.set_fracture_hydraulic_values(hy_prop_type, [fracture_num],
                                               [value])
                fracture_num += 1

    else:
        print('--> Inserting User Rectangles Hydraulic Params First')
        for i in range(len(self.user_rect_params)):
            for j in range(self.user_rect_params[i]['nPolygons']):
                print(f'--> Inserting User Rect Hydraulic Params {fracture_num}')
                hy_prop_type = self.user_rect_params[i]['hy_prop_type']
                value = self.user_rect_params[i][hy_prop_type][j]
                print(f'{hy_prop_type} = {value}')
                self.set_fracture_hydraulic_values(hy_prop_type, [fracture_num],
                                               [value])
                fracture_num += 1

        for i in range(len(self.user_ell_params)):
            for j in range(self.user_ell_params[i]['nPolygons']):
                print(f'--> Inserting User Ell Hydraulic Params {fracture_num}')
                hy_prop_type = self.user_ell_params[i]['hy_prop_type']
                value = self.user_ell_params[i][hy_prop_type][j]
                print(f'{hy_prop_type} = {value}')
                self.set_fracture_hydraulic_values(hy_prop_type, [fracture_num],
                                               [value])
                fracture_num += 1

        for i in range(len(self.user_poly_params)):
            for j in range(self.user_poly_params[i]['nPolygons']):
                print(f'--> Inserting User Poly Hydraulic Params {fracture_num}')
                hy_prop_type = self.user_poly_params[i]['hy_prop_type']
                value = self.user_poly_params[i][hy_prop_type][j]
                print(f'{hy_prop_type} = {value}')
                self.set_fracture_hydraulic_values(hy_prop_type, [fracture_num],
                                               [value])
                fracture_num += 1

    # self.dump_hydraulic_values()
    print("--> Assign hydraulic properties: Complete ")

def grab_polygon_data(self):
    '''If flag self.store_polygon_data is set to True, the information stored in polygon.dat is written to a dictionary self.polygons. 
    To access the points that define an individual polygon, call self.polygons[f'poly{i}'] where i is a number between 1 and the number of defined polygons. This returns an array of coordinates in the format np.array([x1,y1,z1],[x2,y2,z2],...[xn,yn,zn])

    Parameters
    -----------
        self : DFN object

    Returns
    --------
        None

    Notes
    ------
        None
        '''

    print("--> Loading Polygon information onto DFN object")
    self.polygons = {}

    polygon_data = np.genfromtxt('dfnGen_output/polygons.dat', dtype = str, delimiter = 'dummy', skip_header = 1) #weird format, so read data in as strings
    
    if self.num_frac == 1:
        polygon_data = np.array([polygon_data])


    for i in range(len(polygon_data)):
        poly_dat = polygon_data[i] #read in data for one polygon
        poly_dat = poly_dat.replace('}', '') #get rid of weird characters
        poly_dat = poly_dat.replace('{', '')
        poly_dat = poly_dat.replace(',', '')
        poly_dat = poly_dat.split() #convert string to list, and then array
        poly_dat = np.array(poly_dat)
        poly_dat = poly_dat.astype(float)
        poly = []
        for j in range(int(poly_dat[0])): #loop through and reformat individual coordinates
            poly.append(poly_dat[3*j+1:3*j+4])
        poly = np.array(poly)
        self.polygons[f'fracture-{i+1}'] = poly #store in dictionary
    print('--> Data from polygons.dat stored on class in self.polygons\n')

