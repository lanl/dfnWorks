
import numpy as np 
import os 
import pandas as pd 

def parse_params_file(self, quiet=False):
    """ Reads params.txt file from DFNGen and parses information

    Parameters
    ---------
        self :
            DFN object

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
        self.print_log("--> Parsing params.txt file")

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
        self.print_log("--> Number of Fractures: %d" % self.num_frac)
        self.print_log(f"--> h: {self.h:0.2e} m")
        if self.visual_mode > 0:
            self.visual_mode = True
            self.print_log("--> Visual mode is on")
        else:
            self.visual_mode = False
            self.print_log("--> Visual mode is off")

        self.print_log(f"--> Expected Number of dudded points: {self.dudded_points}")
        self.print_log(f"--> X Domain Size {self.domain['x']} m")
        self.print_log(f"--> Y Domain Size {self.domain['y']} m")
        self.print_log(f"--> Z Domain Size {self.domain['z']} m")
        
        self.x_min = -0.5*self.domain['x']
        self.x_max = 0.5*self.domain['x']

        self.y_min = -0.5*self.domain['y']
        self.y_max = 0.5*self.domain['y']
        
        self.z_max = 0.5*self.domain['z']
        self.z_min = -0.5*self.domain['z']

        self.print_log("--> Parsing params.txt complete\n")


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
    self.print_log("--> Parsing dfnWorks output and adding to object")
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
    
    self.compute_fracture_p21()

def read_boundaries(file_path):
    '''Reads in boundary files, and corrects format is file is empty of length 1
    Parameters
    -----------
        file_path : the path to boundary file

    Returns
    --------
        data : array of values (or empty array if file is empty
    
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

    self.print_log("--> Assign hydraulic properties: Starting ")
    ### Assign variables for fracture families
    self.print_log("--> Assign hydraulic properties to fracture families : Starting ")
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
    self.print_log("--> Assign hydraulic properties to fracture families : Complete ")

    ### Assign variables for user defined fractures and skip rejected fractures
    ##Logic here, loop through user defined fractures
    ## first check flag to insert
    file_path = 'dfnGen_output/userFractureRejections.dat'
    if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
        try:
            reject_fracs, frac_type = np.genfromtxt(file_path, delimiter = ',', skip_header = 1, unpack=True)
            reject_fracs = np.array([reject_fracs]) #needed for case with one rejected fracture, genfromtxt reads in float otherwise
            frac_type = np.array([frac_type])
        except:
            self.print_log('--> No Rejected User Fractures, Ignore Following Warning.')
            reject_fracs = np.array([])
            frac_type = np.array([])
    else: #if no fractures are rejected
        self.print_log('--> No Rejected User Fractures, Ignore Following Warning.')
        reject_fracs = np.array([])
        frac_type = np.array([])

    rect_reject = reject_fracs[(frac_type == -2)] #integer corresponds to fracture type
    ell_reject = reject_fracs[(frac_type == -1)]
    poly_reject = reject_fracs[(frac_type == -3)]

    fracture_num = 1 #keep track of overall fracture number, and numbers for different types of fractures
    frac_ell_num = 1
    frac_rect_num = 1
    frac_poly_num = 1

    if self.params['insertUserRectanglesFirst']['value'] == 0:
        self.print_log('--> Inserting User Ellipse Hydraulic Params First')
        for i in range(len(self.user_ell_params)):
            for j in range(self.user_ell_params[i]['nPolygons']):
                if frac_ell_num not in ell_reject:
                    self.print_log(f'--> Inserting User Ell Hydraulic Params {fracture_num}')
                    hy_prop_type = self.user_ell_params[i]['hy_prop_type']
                    value = self.user_ell_params[i][hy_prop_type][j]
                    self.print_log(f'{hy_prop_type} = {value}')
                    self.set_fracture_hydraulic_values(hy_prop_type, [fracture_num],
                                               [value])
                    fracture_num += 1

                frac_ell_num += 1

        for i in range(len(self.user_rect_params)):
            for j in range(self.user_rect_params[i]['nPolygons']):
                if frac_rect_num not in rect_reject:
                    self.print_log(f'--> Inserting User Rect Hydraulic Params {fracture_num}')
                    hy_prop_type = self.user_rect_params[i]['hy_prop_type']
                    value = self.user_rect_params[i][hy_prop_type][j]
                    self.print_log(f'{hy_prop_type} = {value}')
                    self.set_fracture_hydraulic_values(hy_prop_type, [fracture_num],
                                               [value])
                    fracture_num += 1

                frac_rect_num += 1

        for i in range(len(self.user_poly_params)):
            for j in range(self.user_poly_params[i]['nPolygons']):
                if frac_poly_num not in poly_reject:
                    self.print_log(f'--> Inserting User Poly Hydraulic Params {fracture_num}')
                    hy_prop_type = self.user_poly_params[i]['hy_prop_type']
                    value = self.user_poly_params[i][hy_prop_type][j]
                    self.print_log(f'{hy_prop_type} = {value}')
                    self.set_fracture_hydraulic_values(hy_prop_type, [fracture_num],
                                               [value])
                    fracture_num += 1

                frac_poly_num += 1

    else:
        self.print_log('--> Inserting User Rectangle Hydraulic Params First')
        for i in range(len(self.user_rect_params)):
            for j in range(self.user_rect_params[i]['nPolygons']):
                if frac_rect_num not in rect_reject:
                    self.print_log(f'--> Inserting User Rect Hydraulic Params {fracture_num}')
                    hy_prop_type = self.user_rect_params[i]['hy_prop_type']
                    value = self.user_rect_params[i][hy_prop_type][j]
                    self.print_log(f'{hy_prop_type} = {value}')
                    self.set_fracture_hydraulic_values(hy_prop_type, [fracture_num],
                                               [value])
                    fracture_num += 1
                
                frac_rect_num += 1

        for i in range(len(self.user_ell_params)):
            for j in range(self.user_ell_params[i]['nPolygons']): 
                if frac_ell_num not in ell_reject:
                    self.print_log(f'--> Inserting User Ell Hydraulic Params {fracture_num}')
                    hy_prop_type = self.user_ell_params[i]['hy_prop_type']
                    value = self.user_ell_params[i][hy_prop_type][j]
                    self.print_log(f'{hy_prop_type} = {value}')
        
                    self.set_fracture_hydraulic_values(hy_prop_type, [fracture_num],
                                               [value])
                    fracture_num += 1
                
                frac_ell_num += 1

        for i in range(len(self.user_poly_params)):
            for j in range(self.user_poly_params[i]['nPolygons']):
                if frac_poly_num not in poly_reject:
                    self.print_log(f'--> Inserting User Poly Hydraulic Params {fracture_num}')
                    hy_prop_type = self.user_poly_params[i]['hy_prop_type']
                    value = self.user_poly_params[i][hy_prop_type][j]
                    self.print_log(f'{hy_prop_type} = {value}')
                    self.set_fracture_hydraulic_values(hy_prop_type, [fracture_num],
                                               [value])
                    fracture_num += 1

                frac_poly_num += 1

    # self.dump_hydraulic_values()
    self.print_log("--> Assign hydraulic properties: Complete ")

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

    self.print_log("--> Loading Polygon information onto DFN object")
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
    self.print_log('--> Data from polygons.dat stored on class in self.polygons\n')


def _get_intersection_length(fracture_id: int, df: pd.DataFrame) -> float:
        """
        Compute the total intersection length for a given fracture ID.
        Only counts intersections where both f1 and f2 are > 0.
        """
        mask = (
            ((df['f1'] == fracture_id) | (df['f2'] == fracture_id))
            & (df['f1'] > 0)
            & (df['f2'] > 0)
        )
        return df.loc[mask, 'length'].sum()

def compute_fracture_p21(self):
    """
    Compute P21 per fracture:
    P21[i] = (sum of intersection lengths involving fracture i+1) / surface_area[i]
    Assumes fracture IDs are 1..self.num_frac.
    """
    print("--> Computing P21 per fracture")
    # Convert intersection list into DataFrame
    df = pd.DataFrame(self.intersection_list, columns=['f1', 'f2', 'x', 'y', 'z', 'length'])

    # Initialize array for results
    self.p21 = np.zeros(self.num_frac, dtype=float)

    for i in range(1, self.num_frac + 1):
        total_length = _get_intersection_length(i, df)
        self.p21[i - 1] = total_length / self.surface_area[i - 1]
        print(f"Fracture ID: {i:3d} | P21: {self.p21[i - 1]:.2e}")

    # Also create a DataFrame view for convenience
    self.p21_table = pd.DataFrame({
        'fracture_id': np.arange(1, self.num_frac + 1),
        'p21': self.p21
    })
