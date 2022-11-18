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
        self : DFN object

        family_number : the id of the fracture family information to be returned
        
        Returns
        --------
        prints fracture family parameters

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
    """Generates a fracture family

        Parameters
        --------------
        self : DFN object
        
        shape : 'rect' or 'ell' deines the fracture family shape 
        
        distribution : 'tpl', 'log_normal', 'exp', or 'constant' defines the sample distribution for the fracture radius
        
        kappa : concentration param of the von Mises-Fisher distribution
        
        family_number : fracutre family id. default = None
        
        probability : probabily of a fracture belonging to this family. default = None. use if stopCondition = 0 
        
        p32 : fracture intensity for the family. default = None. use if stopCondition = 1
        layer : assigns fracture family to a layer in the domain. default = 0
        
        region : assigns fracture family to a region in the domain. default = 0
        
        number_of_points : specifies the number of vertices defining th eboundary of each fracture. default = 8
        
        aspect : the aspect ratio of the fractures. default = 1
        
        beta_distribution : 0 (uniform distribtuion [0,2pi) or 1 (constant rotation specfied by ebeta) rotation of each fractures normal vector. default 0
        
        beta : angle fo constant rotation. use if beta_distribution = 1. default = 0
        
        theta : use if orientationOption = 0 (default). default = None
        
        phi : use if orientationOption = 0 (default). default = None
        
        strike : use if orientationOption = 1. default = None
        
        dip : use if orientationOption = 1. default = None
        
        trend : use if orientationOption = 2. default = None
        
        plunge : use if orientationOption = 2. default = None
        
        alpha : parameter for 'tpl'. default = None
        
        log_mean : parameter for 'log_normal'. default = None
        
        log_std : parameter for 'log_normal'. default = None
        
        exp_mean : parameter for 'exp'. default = None
        
        constant : parameter for 'constant'. default = None
        
        min_radius : minimum fracture radius for 'tpl' 'log_normal' or 'exp'. default = None
        
        max_radius : maximum fracture radius for 'tpl' 'log_normal' or 'exp'. default = None
        
        hy_variable : hydraulic variable to assign values to. options are 'aperture', 'permeability', 'transmissivity', 
        
        hy_function : relationship between hydraulic variable and fracture radius. options are 'correlated', 'semi-correlated', 'constant', 'log-normal'
        
        hy_params : parameters for the hydraulic function. see next lines for syntax and options
            if 'correlated' --> {"alpha":value, "beta:value}
            if 'semi-correlated' --> {"alpha":value, "beta":value, "sigma":value}
            if 'constant' --> {"mu":value}
            if 'log-normal' --> {"mu":value, "sigma":value}
        
        Returns
        --------
        populated fracture family dictionary for specified family

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

    ## Radius Distribution
    if distribution == "tpl":
        family['distribution']['value']['tpl'] = True
        if alpha != None:
            family['tpl']['value']['alpha'] = alpha
        else:
            # Aidan. Copy this for the other distributions so the parameters are required.
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
