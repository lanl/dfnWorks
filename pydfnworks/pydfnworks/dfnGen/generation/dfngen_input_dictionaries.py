import sys


def create_domain_dictionary(self):
    ''' Create Dictionary for self.domain variables'''
    self.params = {
        # general
        'stopCondition': {
            'type':
            bool,
            'list':
            False,
            'value':
            None,
            'description':
            "Type <boolean>\nPossible Values\n0: Stop once nPoly fractures are accepted \n1: Stop once all family's p32 values are equal or greater than the families target p32 values"
        },
        'nPoly': {
            'type':
            int,
            'list':
            False,
            'value':
            None,
            'description':
            "Type <int>\n Used when stopCondition is set to 0. This value is the total number of fractures you would like to have in the domain you defined. DFNGen will complete once you have nPoly number of fractures"
        },
        'domainSize': {
            'type':
            float,
            'list':
            True,
            'list_length':
            3,
            'value':
            None,
            'description':
            "Type <list of 3 floats>, e.g., {x,y,z}\nSpatial dimensions of the domain centered at the origin in meters."
        },
        'domainSizeIncrease': {
            'type':
            float,
            'list':
            True,
            'list_length':
            3,
            'value':
            None,
            'description':
            "Type <list of 3 floats>, e.g., {x,y,z}\nCreates a temporary size increase of the domain during sampling.\nExample: {1,1,1} will increase the domain size by adding 0.5 to the +x, and subtracting 0.5 to the -x.\nMust be less than 1/2 the domain size value in that direction."
        },
        'boundaryFaces': {
            'type':
            int,
            'list':
            True,
            'list_length':
            6,
            'value':
            None,
            'description':
            """Type <list of 6 booleans>\nDFN will only keep clusters with connections to domain boundaries which are set to 1:
            boundaryFaces[0] = +X domain boundary
            boundaryFaces[1] = -X domain boundary
            boundaryFaces[2] = +Y domain boundary
            boundaryFaces[3] = -Y domain boundary
            boundaryFaces[4] = +Z domain boundary
            boundaryFaces[5] = -Z domain boundary    
            Only called if ignoreBoundaryFaces is equal to 0"""
        },
        'insertUserRectanglesFirst': {
            'type':
            bool,
            'list':
            False,
            'value':
            False,
            'description':
            "Type <boolean>\nPossible Values\n0: User defined ellipses will be inserted first\n1: User defined rectangles will be inserted first"
        },
        'keepOnlyLargestCluster': {
            'type':
            bool,
            'list':
            False,
            'value':
            False,
            'description':
            "Type <boolean>\nPossible Values:\n 0: Keep any clusters which connects the specified boundary faces in boundaryFaces option below\n1: Keep only the largest cluster which connects the specified boundary faces in boundaryFaces option below"
        },
        'keepIsolatedFractures': {
            'type':
            bool,
            'list':
            False,
            'value':
            False,
            'description':
            "Type <boolean>\nPossible Values:\n0: Remove all isolated fracture. i.e., those with 0 intersections.\n 1: Keep all fractures in the domain, even those with 0 intersections."
        },
        'ignoreBoundaryFaces': {
            'type':
            bool,
            'list':
            False,
            'value':
            False,
            'description':
            "Type <boolean>\nPossible Values:\n0: Use the boundaryFaces option.\n1: Keep all clusters in the domain."
        },
        'numOfLayers': {
            'type':
            int,
            'list':
            False,
            'value':
            0,
            'description':
            "Type <int>\nNumber of layers in the domain. If set equal to 0, there are no layers. Fracture families are assigned to layers using either the eLayer or rLayer options.\n"
        },
        'layers': {
            'type':
            float,
            'list':
            True,
            'value':
            None,
            'description':
            "Type: Set of numOfLayers arrays with two elements. {zMin, zMax}\nDefines the lower and upper limits for each layer. The first layer listed is layer 1, the second is layer 2, etc. Every stochastic families *must* be assigned to a layer. If the family is assigned to layer 0, then the family in generated through the entire domain.\n"
        },
        'numOfRegions': {
            'type':
            int,
            'list':
            False,
            'value':
            None,
            'description':
            "Type < int>\nDefines the number of cuboid regions in the domain. If numOfRegions is 0, then there are no regions. Fracture families are assigned to regions using either the eRegion or rRegion options.\n"
        },
        'regions': {
            'type':
            float,
            'list':
            True,
            'value':
            0,
            'description':
            "Type: Set of numOfRegions arrays with six elements. {minX, maxX, minY, maxY, minZ, maxZ}. Defines the bounding box of each region. The first region listed is region 1, the region is region 2, etc. Stochastic families *must* be assigned to theses regions. If the family is assigned to region 0, then the family in generated through the entire domain."
        },
        'h': {
            'type':
            float,
            'list':
            False,
            'value':
            "Type: Positive <double>\nMinimum feature size accepted into the network.\n"
        },
        'seed': {
            'type':
            int,
            'list':
            False,
            'value':
            1,
            'description':
            "Type: Non-negative <int> Seed for random generator. Setting the seed equal to 0 will seed off the clock and a unique network will be produced. Setting the seed equal to a value > 0 will create the same network every time, which is useful for reproducibility."
        },
        'tripleIntersections': {
            'type':
            bool,
            'list':
            False,
            'value':
            False,
            'description':
            "Type <boolean>\nSelection of whether triple intersection are accepted into the network.\n0: Reject all triple intersections\n1: Accept triple intersections that meet FRAM criteria.\n"
        },
        'forceLargeFractures': {
            'type':
            bool,
            'list':
            False,
            'value':
            False,
            'description':
            "Type <boolean>\nInsert the largest fracture from each family into the domain prior to sampling sequential from family based on their respective probabilities.\n0: Do not force the largest fractures\n1: Force the largest fractures\n"
        },
        'orientation_option': {
            'type':
            int,
            'list':
            False,
            'value':
            0,
            'description':
            'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'disableFram': {
            'type':
            bool,
            'list':
            False,
            'value':
            False,
            'description':
            'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'radiiListIncrease': {
            'type':
            float,
            'list':
            False,
            'value':
            0.1,
            'description':
            'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'removeFracturesLessThan': {
            'type':
            float,
            'list':
            False,
            'value':
            0,
            'description':
            'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rejectsPerFracture': {
            'type':
            int,
            'list':
            False,
            'value':
            10,
            'description':
            'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'visualizationMode': {
            'type':
            bool,
            'list':
            False,
            'value':
            False,
            'description':
            'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },

        # output
        'printRejectReasons': {
            'type':
            bool,
            'list':
            False,
            'value':
            False,
            'description':
            'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'outputAllRadii': {
            'type':
            bool,
            'list':
            False,
            'value':
            False,
            'description':
            'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'outputFinalRadiiPerFamily': {
            'type':
            bool,
            'list':
            False,
            'value':
            False,
            'description':
            'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'outputAcceptedRadiiPerFamily': {
            'type':
            bool,
            'list':
            False,
            'value':
            None,
            'description':
            'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        }
    }


def create_fracture_family(self,
                           shape,
                           distribution,
                           rmin,
                           rmax,
                           kappa,
                           aspect = None,
                           alpha=None,
                           mu=None,
                           sigma=None,
                           exp_lambda=None,
                           constant=None,
                           layer=0,
                           region=0,
                           p32=None,
                           num_points=None,
                           beta_distribution=False,
                           beta=0,
                           theta=None,
                           phi=None,
                           dip=None,
                           strike=None,
                           trend=None,
                           plunge=None):
    '''
    Creates a fracture family and attaches it to the DFN object

    Parameters
    --------------------



    Returns
    --------------------
        None


    Notes
    ---------------------
    
    
    '''
    family = {}
    family['shape'] = shape
    family['distribution'] = distribution
    if distribution == 'tpl':
        if alpha is None:
            error = 'Error. Requested TPL distribution but no value for alpha was provided'
            sys.stderr.write(error)
            sys.exit(1)
        else:
            family['alpha'] = alpha

    elif distribution == 'log_normal':
        if mu is None or sigma is None:
            error = 'Error. Requested Lognormal distribution but no value for mu/std was provided'
            sys.stderr.write(error)
            sys.exit(1)
        else:
            family['mu'] = mu
            family['sigma'] = sigma
    elif distribution == 'exp':
        if exp_lambda is None:
            error = 'Error. Requested Exponentional distribution but no value for mu/std was provided'
            sys.stderr.write(error)
            sys.exit(1)
        else:
            family['mean'] = exp_lambda
    elif distribution == 'constant':
        if constant is None:
            error = 'Error. Requested Exponentional distribution but no value for mu/std was provided'
            sys.stderr.write(error)
            sys.exit(1)
        else:
            family['constant'] = constant
    else:
        error = f'Error. Requested distribution is unknown. Accetable valuesa are tpl, log_normal, exp, const\\nParameter provided {distribution}'
        sys.stderr.write(error)
        sys.exit(1)

    family['layer'] = layer
    family['region'] = region
    family['p32'] = p32
    family['aspect'] = aspect
    if shape == 'rect' and num_points is None:
        num_points = 4
    elif shape == 'ellipse' and num_points is None:
        num_points = 8

    family['num_points'] = num_points
    family['beta_distribution'] = beta_distribution
    family['beta'] = beta

    ## Fisher Distribution parameters
    family['kappa'] = kappa
    if self.params['orientation_option'] == 0:
        if phi is None or theta is None:
            error = 'Error. Family orientation parameters not provided. Expecting values for phi/theta'
            sys.stderr.write(error)
            sys.exit(1)
        else:
            family['phi'] = phi
            family['theta'] = theta 

    elif self.params['orientation_option'] == 1:
        if trend is None or plunge is None:
            error = 'Error. Family orientation parameters not provided. Expecting values for phi/theta'
            sys.stderr.write(error)
            sys.exit(1)
        else:
            family['phi'] = trend 
            family['theta'] = plunge
             
    elif self.params['orientation_option'] == 2:
        if dip is None or strike is None:
            error = 'Error. Family orientation parameters not provided. Expecting values for phi/theta'
            sys.stderr.write(error)
            sys.exit(1)
        else:
            family['dip'] = dip
            family['strike'] = strike 
    

    # Parameters for aperture/radii correlations
    self.families.append(family)


def create_fractures(self, fracture_type, path):

    fractures = {}
    fracture_types = set(['coord_rect', 'coord_ell', 'user_rect', 'user_ell', 'polygon'])
    if fracture_type not in fracture_types:
        error = f'Error. User defined fracture type. Parameter provided {fracture_type}'
        sys.stderr.write(error)
        sys.exit(1)
    fractures['type'] = fracture_type
    fractures['path'] = path

    self.fractures.append(fractures)


def group_family(fractures, number_of_families, shape):
    '''Group generation parameters by family'''
    obj = family()
    for i in range(number_of_families):
        if fractures[i]['type'][shape]:
            obj['probability'].append(fractures[i]['probability'])
            obj['layer'].append(fractures[i]['layer'])
            obj['p32'].append(fractures[i]['p32'])
            obj['beta'].append(int(fractures[i]['beta']))
            obj['betaDistribution'].append(
                int(fractures[i]['beta_distribution']))
            obj['aspect'].append(fractures[i]['aspect'])
            obj['number_of_points'].append(fractures[i]['number_of_points'])
            obj['theta'].append(fractures[i]['fisher']['theta'])
            obj['phi'].append(fractures[i]['fisher']['phi'])
            obj['kappa'].append(fractures[i]['fisher']['kappa'])

            if fractures[i]['distribution']['log_normal']:
                obj['dist'].append(1)
                obj['log_min'].append(fractures[i]['min'])
                obj['log_max'].append(fractures[i]['max'])
                obj['sd'].append(fractures[i]['log_normal']['std'])
                obj['log_mean'].append(fractures[i]['log_normal']['mean'])

            elif fractures[i]['distribution']['tpl']:
                obj['dist'].append(2)
                obj['min'].append(fractures[i]['min'])
                obj['max'].append(fractures[i]['max'])
                obj['alpha'].append(fractures[i]['tpl']['alpha'])

            elif fractures[i]['distribution']['exp']:
                obj['dist'].append(3)
                obj['exp_min'].append(fractures[i]['min'])
                obj['exp_max'].append(fractures[i]['max'])
                obj['exp_mean'].append(fractures[i]['exp']['mean'])

            elif fractures[i]['distribution']['constant']:
                obj['dist'].append(4)
                obj['constant'].append(fractures[i]['constant']['value'])
    return obj
