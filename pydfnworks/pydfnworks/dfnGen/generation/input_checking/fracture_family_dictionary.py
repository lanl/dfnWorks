def fracture_family(family_number):
    """Creates a fracture family dictionary
    
    Parameters
    --------------
        family_number: The number id for the family
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
            'value': family_number,
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
            'value': None,
            'description': 'Assign family to a layer in the domain'
        },
        'region': {
            'type': int,
            'value': None,
            'description': 'Assign family to a region in the domain'
        },
        'p32': {
            'type': float,
            'value': None,
            'description': 'Target fracture intensity'
        },
        'aspect': {
            'type': float,
            'value': None,
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
            None,
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
        'radius_min': {
            'type': float,
            'value': None,
            'description': 'Minimum radius created by distribution'
        },
        'radius_max': {
            'type': float,
            'value': None,
            'description': 'Maximum radius created by distribution'
        },
    }
    return family
