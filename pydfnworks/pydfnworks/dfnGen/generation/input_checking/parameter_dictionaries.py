def load_parameters():
    """ load dictionary of DFNGen parameters

    Parameters
    --------------
        None
    Returns
    --------
        params : dictionary
            input parameter dictionary

    Notes
    ---------
        None
    """

    params = {
        # general
        'stopCondition': {
            'type': bool,
            'list': False,
            'value': None,
            'description': "Type <boolean>\nPossible Values\n0: Stop once nPoly fractures are accepted \n1: Stop once all family's p32 values are equal or greater than the families target p32 values"
        },
        'nPoly': {
            'type': int,
            'list': False,
            'value': None,
            'description': "Type <int>\n Used when stopCondition is set to 0. This value is the total number of fractures you would like to have in the domain you defined. DFNGen will complete once you have nPoly number of fractures"
        },
        'domainSize': {
            'type': float,
            'list': True,
            'list_length': 3,
            'value': None,
            'description': "Type <list of 3 floats>, e.g., {x,y,z}\nSpatial dimensions of the domain centered at the origin in meters."
        },
        'domainSizeIncrease': {
            'type': float,
            'list': True,
            'list_length': 3,
            'value': None,
            'description': "Type <list of 3 floats>, e.g., {x,y,z}\nCreates a temporary size increase of the domain during sampling.\nExample: {1,1,1} will increase the domain size by adding 0.5 to the +x, and subtracting 0.5 to the -x.\nMust be less than 1/2 the domain size value in that direction."
        },
        'boundaryFaces': {
            'type': int,
            'list': True,
            'list_length': 6,
            'value': None,
            'description': """Type <list of 6 booleans>\nDFN will only keep clusters with connections to domain boundaries which are set to 1:
            boundaryFaces[0] = +X domain boundary
            boundaryFaces[1] = -X domain boundary
            boundaryFaces[2] = +Y domain boundary
            boundaryFaces[3] = -Y domain boundary
            boundaryFaces[4] = +Z domain boundary
            boundaryFaces[5] = -Z domain boundary    
            Only called if ignoreBoundaryFaces is equal to 0"""
        },
        'insertUserRectanglesFirst': {
            'type': bool,
            'list': False,
            'value': None,
            'description': "Type <boolean>\nPossible Values\n0: User defined ellipses will be inserted first\n1: User defined rectangles will be inserted first"
        },
        'keepOnlyLargestCluster': {
            'type': bool,
            'list': False,
            'value': None,
            'description': "Type <boolean>\nPossible Values:\n 0: Keep any clusters which connects the specified boundary faces in boundaryFaces option below\n1: Keep only the largest cluster which connects the specified boundary faces in boundaryFaces option below"
        },
        'keepIsolatedFractures': {
            'type': bool,
            'list': False,
            'value': None,
            'description': "Type <boolean>\nPossible Values:\n0: Remove all isolated fracture. i.e., those with 0 intersections.\n 1: Keep all fractures in the domain, even those with 0 intersections."
        },
        'ignoreBoundaryFaces': {
            'type': bool,
            'list': False,
            'value': None,
            'description': "Type <boolean>\nPossible Values:\n0: Use the boundaryFaces option.\n1: Keep all clusters in the domain."
        },
        'numOfLayers': {
            'type': int,
            'list': False,
            'value': None,
            'description': "Type <int>\nNumber of layers in the domain. If set equal to 0, there are no layers. Fracture families are assigned to layers using either the eLayer or rLayer options.\n"
        },
        'layers': {
            'type': float,
            'list': True,
            'value': None,
            'description': "Type: Set of numOfLayers arrays with two elements. {zMin, zMax}\nDefines the lower and upper limits for each layer. The first layer listed is layer 1, the second is layer 2, etc. Every stochastic families *must* be assigned to a layer. If the family is assigned to layer 0, then the family in generated through the entire domain.\n"
        },
        'numOfRegions': {
            'type': int,
            'list': False,
            'value':None,
            'description': "Type < int>\nDefines the number of cuboid regions in the domain. If numOfRegions is 0, then there are no regions. Fracture families are assigned to regions using either the eRegion or rRegion options.\n" 
        },
        'regions': {
            'type': float,
            'list': True,
            'value': None,
            'description':"Type: Set of numOfRegions arrays with six elements. {minX, maxX, minY, maxY, minZ, maxZ}. Defines the bounding box of each region. The first region listed is region 1, the region is region 2, etc. Stochastic families *must* be assigned to theses regions. If the family is assigned to region 0, then the family in generated through the entire domain."
        },
        'h': {
            'type': float,
            'list': False,
            'value': "Type: Positive <double>\nMinimum feature size accepted into the network.\n"
        },
        'seed': {
            'type': int,
            'list': False,
            'value': "Type: Non-negative <int> Seed for random generator. Setting the seed equal to 0 will seed off the clock and a unique network will be produced. Setting the seed equal to a value > 0 will create the same network every time, which is useful for reproducibility."
        },
        'tripleIntersections': {
            'type': bool,
            'list': False,
            'value': None,
            'description':"Type <boolean>\nSelection of whether triple intersection are accepted into the network.\n0: Reject all triple intersections\n1: Accept triple intersections that meet FRAM criteria.\n"
        },
        'forceLargeFractures': {
            'type': bool,
            'list': False,
            'value': None,
            'description':"Type <boolean>\nInsert the largest fracture from each family into the domain prior to sampling sequential from family based on their respective probabilities.\n0: Do not force the largest fractures\n1: Force the largest fractures\n"
        },
        'orientationOption': {
            'type': int,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'disableFram': {
            'type': bool,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'radiiListIncrease': {
            'type': float,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'removeFracturesLessThan': {
            'type': float,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rejectsPerFracture': {
            'type': int,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },

        # output
        'printRejectReasons': {
            'type': bool,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'outputAllRadii': {
            'type': bool,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'outputFinalRadiiPerFamily': {
            'type': bool,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'visualizationMode': {
            'type': bool,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'outputAcceptedRadiiPerFamily': {
            'type': bool,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'ecpmOutput': {
            'type': bool,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        # Fracture Families
        'famProb': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        # ellipses
        'nFamEll': {
            'type': int,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'eAngleOption': {
            'type': int,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'eLayer': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'eRegion': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'edistr': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'ebetaDistribution': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'ebeta': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'e_p32Targets': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'easpect': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'enumPoints': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'etheta': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'ephi': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'etrend': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'eplunge': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'edip': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'estrike': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'ekappa': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'eLogMean': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'esd': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'eLogMin': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'eLogMax': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'ealpha': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'emin': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'emax': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'eExpMean': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'eExpMin': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'eExpMax': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'econst': {
            'type': float,
            'list': True,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },

        # Rectangles
        'nFamRect': {
            'type': int,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rAngleOption': {
            'type': int,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rLayer': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rRegion': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rdistr': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rbetaDistribution': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rbeta': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'r_p32Targets': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'raspect': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rtheta': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rphi': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rtrend': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rplunge': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rdip': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rstrike': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rkappa': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rLogMean': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rsd': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rLogMin': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rLogMax': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'ralpha': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rmin': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rmax': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rExpMean': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rExpMin': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rExpMax': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'rconst': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },

        # user defined rects
        'userRectanglesOnOff': {
            'type': bool,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'UserRect_Input_File_Path': {
            'type': str,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'userRecByCoord': {
            'type': bool,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'RectByCoord_Input_File_Path': {
            'type': str,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        # user defined ells
        'userEllByCoord': {
            'type': bool,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'EllByCoord_Input_File_Path': {
            'type': str,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'userEllipsesOnOff': {
            'type': bool,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'UserEll_Input_File_Path': {
            'type': str,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        # user polygon
        'userPolygonByCoord': {
            'type': bool,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'PolygonByCoord_Input_File_Path': {
            'type': str,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        # aperture
        'aperture': {
            'type': int,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'lengthCorrelatedAperture': {
            'type': float,
            'list': True,
            'list_length': 2,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'meanAperture': {
            'type': float,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'stdAperture': {
            'type': float,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'constantAperture': {
            'type': float,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'apertureFromTransmissivity': {
            'type': float,
            'list': True,
            'list_length': 2,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        # perm
        'permOption': {
            'type': int,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'constantPermeability': {
            'type': float,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
        'minimum_fracture_size': {
            'type': float,
            'list': False,
            'value': None,
            'description': 'See dfnGen documenation https://dfnworks.lanl.gov/dfngen.html for more details'
        },
    }

    mandatory = {
        'stopCondition', 'domainSize', 'numOfLayers', 'numOfRegions',
        'outputAllRadii', 'outputFinalRadiiPerFamily',
        'outputAcceptedRadiiPerFamily', 'ecpmOutput', 'tripleIntersections',
        'printRejectReasons', 'disableFram', 'visualizationMode', 'seed',
        'domainSizeIncrease', 'keepOnlyLargestCluster',
        'keepIsolatedFractures', 'ignoreBoundaryFaces', 'rejectsPerFracture',
        'famProb', 'insertUserRectanglesFirst', 'nFamEll', 'nFamRect',
        'userEllipsesOnOff', 'userRectanglesOnOff', 'userEllByCoord',
        'userRecByCoord', 'userPolygonByCoord', 'aperture', 'permOption',
        'forceLargeFractures', 'orientationOption', 'radiiListIncrease',
        'removeFracturesLessThan'
    }

    return params, mandatory
