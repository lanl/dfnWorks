import sys


def fracture_family_dictionary():
    """Creates a fracture family dictionary
    
    Parameters
    --------------
        None

    Returns
    --------
        family : dictionary
            fracture family dictionary for specified family
            
    Notes
    ---------
        See https://dfnworks.lanl.gov/dfngen.html#domain-parameters for more 
        information about parameters in this dictionary
    """

    family = {
        'number': {
            'type': int,
            'value': None,
            'description': 'ID number for the fracture family'
        },
        'probability': {
            'type':
            float,
            'value':
            None,
            'description':
            'Probabiliy of occurence for the family of of stochastically generated fractures'
        },
        'type': {
            'type':
            bool,
            'value': {
                'rect': False,
                'ellipse': False
            },
            'description':
            'Specifies whether the fracture family consists of rectangular or elliptical fractures'
        },
        'layer': {
            'type': int,
            'value': 0,
            'description': 'Assign family to a layer in the domain'
        },
        'region': {
            'type': int,
            'value': 0,
            'description': 'Assign family to a region in the domain'
        },
        'p32': {
            'type': float,
            'value': None,
            'description': 'Target fracture intensity'
        },
        'aspect': {
            'type': float,
            'value': 1,
            'description': 'Aspect ratio of the fractures'
        },
        'number_of_points': {
            'type':
            int,
            'value':
            None,
            'description':
            'Number of vertices defining the boundary of each elliptical fracture'
        },
        'beta_distribution': {
            'type':
            bool,
            'value':
            False,
            'description':
            'Prescribe a rotation around each fractures normal vector, with the fracture centered on the x-y plane at the origin\nFalse:Uniform distribution on [0,2pi)\nTrue:Constant rotation specified by beta'
        },
        'beta': {
            'type':
            float,
            'value':
            None,
            'description':
            'Value for constant angle of rotation around the normal vector'
        },
        #fisher distribution
        'fisher': {
            'type':
            float,
            'value': {
                'theta': None,
                'phi': None,
                'strike': None,
                'dip': None,
                'trend': None,
                'plunge': None,
                'kappa': None
            },
            'description':
            '3 parameters theta, phi, and kappa for fisher distribution'
        },
        'distribution': {
            'type': bool,
            'value': {
                'tpl': False,
                'log_normal': False,
                'exp': False,
                'constant': False
            },
            'description':
            'Type of distibution fracture radii are sampled from'
        },
        'tpl': {
            'type': float,
            'value': {
                'alpha': None
            },
            'description': 'Parameter for truncated power-law distibution'
        },
        'log_normal': {
            'type': float,
            'value': {
                'mean': None,
                'std': None
            },
            'description': 'Parameters for log normal distribution'
        },
        'exp': {
            'type': float,
            'value': {
                'mean': None
            },
            'description': 'Parameter for exponential distribution'
        },
        'constant': {
            'type': float,
            'value': None,
            'description': 'Constant sized fracture family radius'
        },
        'min_radius': {
            'type': float,
            'value': None,
            'description': 'Minimum radius created by distribution'
        },
        'max_radius': {
            'type': float,
            'value': None,
            'description': 'Maximum radius created by distribution'
        },
        'hydraulic_properties': {
            'variable': {
                'type':
                str,
                'value':
                None,
                'description':
                ' Acceptable values are aperture, permeability, and transmissivity'
            },
            'function': {
                'type':
                str,
                'value':
                None,
                'description':
                'Acceptable values or correlated, semi-correlated, constant, and log-normal'
            },
            'params': {
                'type':
                dict,
                'value':
                None,
                'description':
                'if correlated {"alpha":float, "beta":float},\nif semi-correlated {"alpha":float, "beta":float, "sigma":float},\nif constant {"mu":float},\nif log-normal {"mu":float,"sigma":float}'
            }
        }
    }
    return family


def print_family_information(self, family_number):
    """Creates a fracture family dictionary

        Parameters
        --------------
        self : 
            DFN object

        family_number : int 
            The id of the fracture family information to be returned.
        
        Returns
        --------
        Prints fracture family parameters.

        Notes
        ---------
        None
        """

    if len(self.fracture_families) > 0:
        family = self.fracture_families[family_number - 1]
        print(f"--> Family information for family # {family_number}")
        for key in family.keys():
            if key == 'hydraulic_properties':
                for sub_key in family[key].keys():
                    print(
                        f"Name: {key} : {sub_key} : {family[key][sub_key]['value']}"
                    )
            else:
                print(f"Name: {key:40s}Value: {family[key]['value']}")
        print()
    else:
        print("No Defined Fracture Families")
        print()


def add_fracture_family(self,
                        shape,
                        distribution,
                        kappa,
                        family_number=None,
                        probability=None,
                        p32=None,
                        layer=0,
                        region=0,
                        number_of_points=8,
                        aspect=1,
                        beta_distribution=0,
                        beta=0,
                        theta=None,
                        phi=None,
                        strike=None,
                        dip=None,
                        trend=None,
                        plunge=None,
                        alpha=None,
                        log_mean=None,
                        log_std=None,
                        exp_mean=None,
                        constant=None,
                        min_radius=None,
                        max_radius=None,
                        hy_variable=None,
                        hy_function=None,
                        hy_params=None):
    """Generates a fracture family with specified attributes

        Parameters
        --------------
        self : 
            DFN object
        
        shape : string 
            The options are 'rect' or 'ell' Defines the fracture family shape. 
        
        distribution : string
            The options are 'tpl', 'log_normal', 'exp', or 'constant' Defines the sample distribution for the fracture radius.
        
        kappa : float
            Concentration parameter of the von Mises-Fisher distribution
        
        family_number : int 
            Fracutre family id. default = None
        
        probability : float
            Probability of a fracture belonging to this family. default = None. Use if stopCondition = 0 
        
        p32 : float
            Fracture intensity for the family. default = None. use if stopCondition = 1
        layer : int 
            Assigns fracture family to a layer in the domain. default = 0
        
        region : int
            Assigns fracture family to a region in the domain. default = 0
        
        number_of_points : int 
            Specifies the number of vertices defining the boundary of each fracture. default = 8
        
        aspect : float
            The aspect ratio of the fractures. default = 1
        
        beta_distribution : int
            0 (uniform distribtuion [0,2pi)) or 1 (constant rotation specfied by beta) Defines the rotation of each fractures normal vector. default = 0
        
        beta : float 
            Angle of constant rotation. Used if beta_distribution = 1. default = 0
        
        theta : float 
            If used automatically sets orientationOption = 0 (default). With phi defines the mean orientation of a fracture family. default = None
        
        phi : float
            If used automatically sets orientationOption = 0 (default). default = None
        
        trend : float 
            If used automatically sets orientationOption = 1. With plunge defines the mean orientation of a fracture family. default = None
        
        plunge : float
            If used automatically sets orientationOption = 1. default = None
        
        dip : float 
            If used automatically sets orientationOption = 2. With strike defines the mean orientation of a fracture family. default = None
        
        strike : float 
            If used automatically sets orientationOption = 2. default = None
        
        alpha : float 
            Parameter for 'tpl' distribution. default = None
        
        log_mean : float
            Parameter for 'log_normal' distribution. default = None
        
        log_std : float 
            Parameter for 'log_normal' distribution. default = None
        
        exp_mean : float 
            Parameter for 'exp' distribution. default = None
        
        constant : float 
            Parameter for 'constant' distribution. default = None
        
        min_radius : float 
            Minimum fracture radius for 'tpl' 'log_normal' or 'exp' distributions. default = None
        
        max_radius : float 
            Maximum fracture radius for 'tpl' 'log_normal' or 'exp' distributions. default = None
        
        hy_variable : string 
            Options are 'aperture', 'permeability', or 'transmissivity'. Sets thehydraulic variable to assign values to.  
        
        hy_function : string
            Options are 'correlated', 'semi-correlated', or 'constant', 'log-normal'. Sets the relationship between the hydraulic variable and the fracture radius.
        
        hy_params : dict 
            Sets the parameters for the hydraulic function. The options are as follows:
            if 'correlated' --> {"alpha":value, "beta:value}
            if 'semi-correlated' --> {"alpha":value, "beta":value, "sigma":value}
            if 'constant' --> {"mu":value}
            if 'log-normal' --> {"mu":value, "sigma":value}
        
        Returns
        --------
        Populated fracture family dictionary for specified fracture family 

        Notes
        ---------
        See https://dfnworks.lanl.gov/dfngen.html#domain-parameters for more
        information about parameters
    """

    print("--> Adding new facture family")

    family = fracture_family_dictionary()
    if shape == "rect":
        family['type']['value']['rect'] = True
        family['number_of_points']['value'] = 4
    elif shape == "ell":
        family['type']['value']['ellipse'] = True
        family['number_of_points']['value'] = number_of_points
    else:
        error = f"Unknown Fracture Type {shape}. Acceptable values are rect & ell. Exiting.\n"
        sys.stderr.write(error)
        sys.exit(1)

    family['layer']['value'] = layer
    family['region']['value'] = region

    if p32:
        family['p32']['value'] = p32
        family['probability']['value'] = p32
    elif probability:
        family['probability']['value'] = probability
    else:
        error = f"A value for p32 or probability must be provided. Exiting.\n"
        sys.stderr.write(error)
        sys.exit(1)

    family['aspect']['value'] = aspect

    ## Orienation
    family['beta_distribution']['value'] = beta_distribution
    family['beta']['value'] = beta
    family['fisher']['value']['theta'] = theta
    family['fisher']['value']['phi'] = phi
    family['fisher']['value']['strike'] = strike
    family['fisher']['value']['dip'] = dip
    family['fisher']['value']['trend'] = trend
    family['fisher']['value']['plunge'] = plunge
    family['fisher']['value']['kappa'] = kappa

    ## Set and check orientation option
    # note orientationOption = 0 --> theta/phi
    # orientationOption = 1 --> trend/plunge
    # orientationOption = 2 --> stirke/dip
    if theta != None and phi != None:
        if self.params['orientationOption']['value'] == None:
            print('Setting orientationOption = 0 (theta/phi)')
            self.params['orientationOption']['value'] = 0
        if self.params['orientationOption']['value'] != 0:
            error = f"0Each family must have only one of the pairs of parameters strike/dip, theta/phi or trend/plunge defined. Each family must have the same pair of parameters defined. \n"
            sys.stderr.write(error)
            sys.exit(1)
    
    if trend != None and plunge != None: 
        if self.params['orientationOption']['value'] == None:
            print('Setting orientationOption = 1 (trend/plunge)')
            self.params['orientationOption']['value'] = 1
        if self.params['orientationOption']['value'] != 1:
            error = f"1Each family must have only one of the pairs of parameters strike/dip, theta/phi or trend/plunge defined. Each family must have the same pair of parameters defined. \n"
            sys.stderr.write(error)
            sys.exit(1)

    if strike != None and dip != None:
        if self.params['orientationOption']['value'] == None:
            print('Setting orientationOption = 2 (strike/dip)')
            self.params['orientationOption']['value'] = 2
        if self.params['orientationOption']['value'] != 2:
            error = f"2Each family must have only one of the pairs of parameters strike/dip, theta/phi or trend/plunge defined. Each family must have the same pair of parameters defined. \n"
            sys.stderr.write(error)
            sys.exit(1)

    ## Radius Distribution
    if distribution == "tpl":
        family['distribution']['value']['tpl'] = True
        if alpha != None:
            family['tpl']['value']['alpha'] = alpha
        else:
            error = f"Error. A value for alpha must be provided if family is tpl distribution. Exiting.\n"
            sys.stderr.write(error)
            sys.exit(1)
    elif distribution == "log_normal":
        family['distribution']['value']['log_normal'] = True
        if log_mean != None:
            family['log_normal']['value']['mean'] = log_mean
        else:
            error = f"Error. A value for log_mean must be provided if family is log_normal distribution. Exiting. \n"
            sys.stderr.write(error)
            sys.exit(1)
        if log_std != None:
            family['log_normal']['value']['std'] = log_std
        else:
            error = f"Error. A value for log_std must be provided if family is log_normal distribution. Exiting. \n"
            sys.stderr.write(error)
            sys.exit(1)

    elif distribution == "exp":
        family['distribution']['value']['exp'] = True
        if exp_mean != None:
            family['exp']['value']['mean'] = exp_mean
        else:
            error = f"Error. A value for exp_mean must be provided if family is exp distribution. Exiting. \n"
            sys.stderr.write(error)
            sys.exit(1)
    elif distribution == "constant":
        family['distribution']['value']['constant'] = True
        if constant != None:
            family['constant']['value'] = constant
        else:
            error = f"Error. A value for constant must be provided if family is constant distribution. Exiting. \n"
            sys.stderr.write(error)
            sys.exit(1)
    else:
        error = f"Error. Unknown Fracture Distribution {distribution}. Acceptable values are 'tpl', 'exp', 'log_normal',  & 'constant'. Exiting.\n"
        sys.stderr.write(error)
        sys.exit(1)

    if distribution != "constant":
        if not min_radius or not max_radius:
            error = f"Error. Minimum and Maximum radius must be provided unless using constant distribution. Exiting.\n"
            sys.stderr.write(error)
            sys.exit(1)

    family['min_radius']['value'] = min_radius
    family['max_radius']['value'] = max_radius

    if family_number:
        family['number']['value'] = family_number
    else:
        family_number = len(self.fracture_families) + 1

    family['hydraulic_properties']['variable']['value'] = hy_variable
    family['hydraulic_properties']['function']['value'] = hy_function
    family['hydraulic_properties']['params']['value'] = hy_params
    ##Do we need exceptions? it will be checked in dfnflow

    self.fracture_families.append(family)
    self.print_family_information(family_number)
