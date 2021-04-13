def load_parameters():
    ## BIG TODO s -----
    ## ==== Problems ==== ##
    ## 11. Multiple keys on one line
    ## 15. check # values (famprob: {.5,.5} {.3, .3., .4})
    ## organize by general and fracture type.
    params = {
        # general
        'stopCondition': {
            'type': bool,
            'list': False,
            'value': None
        },
        'nPoly': {
            'type': int,
            'list': False,
            'value': None
        },
        'domainSize': {
            'type': float,
            'list': True,
            'list_length': 3,
            'value': None
        },
        'domainSizeIncrease': {
            'type': float,
            'list': True,
            'list_length': 3,
            'value': None
        },
        'boundaryFaces': {
            'type': int,
            'list': True,
            'list_length': 6,
            'value': None
        },
        'insertUserRectanglesFirst': {
            'type': bool,
            'list': False,
            'value': None
        },
        'keepOnlyLargestCluster': {
            'type': bool,
            'list': False,
            'value': None
        },
        'keepIsolatedFractures': {
            'type': bool,
            'list': False,
            'value': None
        },
        'ignoreBoundaryFaces': {
            'type': bool,
            'list': False,
            'value': None
        },
        'numOfLayers': {
            'type': int,
            'list': False,
            'value': None
        },
        'layers': {
            'type': float,
            'list': True,
            'value': None
        },
        'numOfRegions': {
            'type': int,
            'list': False,
            'value': None
        },
        'regions': {
            'type': float,
            'list': True,
            'value': None
        },
        'h': {
            'type': float,
            'list': False,
            'value': None
        },
        'seed': {
            'type': int,
            'list': False,
            'value': None
        },
        'tripleIntersections': {
            'type': bool,
            'list': False,
            'value': None
        },
        'forceLargeFractures': {
            'type': bool,
            'list': False,
            'value': None
        },
        'orientationOption': {
            'type': int,
            'list': False,
            'value': None
        },
        'disableFram': {
            'type': bool,
            'list': False,
            'value': None
        },
        'radiiListIncrease': {
            'type': float,
            'list': False,
            'value': None
        },
        'removeFracturesLessThan': {
            'type': float,
            'list': False,
            'value': None
        },
        'rejectsPerFracture': {
            'type': int,
            'list': False,
            'value': None
        },

        # output
        'printRejectReasons': {
            'type': bool,
            'list': False,
            'value': None
        },
        'outputAllRadii': {
            'type': bool,
            'list': False,
            'value': None
        },
        'outputFinalRadiiPerFamily': {
            'type': bool,
            'list': False,
            'value': None
        },
        'visualizationMode': {
            'type': bool,
            'list': False,
            'value': None
        },
        'outputAcceptedRadiiPerFamily': {
            'type': bool,
            'list': False,
            'value': None
        },

        # Fracture Families
        'famProb': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        # ellipses
        'nFamEll': {
            'type': int,
            'list': False,
            'value': None
        },
        'eAngleOption': {
            'type': int,
            'list': False,
            'value': None
        },
        'eLayer': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None
        },
        'eRegion': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None
        },
        'edistr': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None
        },
        'ebetaDistribution': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None
        },
        'ebeta': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'e_p32Targets': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'easpect': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'enumPoints': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None
        },
        'etheta': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'ephi': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'etrend': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'eplunge': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'edip': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'estrike': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'ekappa': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'eLogMean': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'esd': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'eLogMin': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'eLogMax': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'ealpha': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'emin': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'emax': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'eExpMean': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'eExpMin': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'eExpMax': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'econst': {
            'type': float,
            'list': True,
            'value': None
        },

        # REctangles
        'nFamRect': {
            'type': int,
            'list': False,
            'value': None
        },
        'rAngleOption': {
            'type': int,
            'list': False,
            'value': None
        },
        'rLayer': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rRegion': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rdistr': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rbetaDistribution': {
            'type': int,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rbeta': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'r_p32Targets': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'raspect': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rtheta': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rphi': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rtrend': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rplunge': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rdip': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rstrike': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rkappa': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rLogMean': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rsd': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rLogMin': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rLogMax': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'ralpha': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rmin': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rmax': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rExpMean': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rExpMin': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rExpMax': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },
        'rconst': {
            'type': float,
            'list': True,
            'list_length': None,
            'value': None
        },

        # user defined rects
        'userRectanglesOnOff': {
            'type': bool,
            'list': False,
            'value': None
        },
        'UserRect_Input_File_Path': {
            'type': str,
            'list': False,
            'value': None
        },
        'userRecByCoord': {
            'type': bool,
            'list': False,
            'value': None
        },
        'RectByCoord_Input_File_Path': {
            'type': str,
            'list': False,
            'value': None
        },
        # user defined ells
        'userEllByCoord': {
            'type': bool,
            'list': False,
            'value': None
        },
        'EllByCoord_Input_File_Path': {
            'type': str,
            'list': False,
            'value': None
        },
        'userEllipsesOnOff': {
            'type': bool,
            'list': False,
            'value': None
        },
        'UserEll_Input_File_Path': {
            'type': str,
            'list': False,
            'value': None
        },
        # user polygon
        'userPolygonByCoord': {
            'type': bool,
            'list': False,
            'value': None
        },
        'PolygonByCoord_Input_File_Path': {
            'type': str,
            'list': False,
            'value': None
        },
        # aperture
        'aperture': {
            'type': int,
            'list': False,
            'value': None
        },
        'lengthCorrelatedAperture': {
            'type': float,
            'list': True,
            'list_length': 2,
            'value': None
        },
        'meanAperture': {
            'type': float,
            'list': False,
            'value': None
        },
        'stdAperture': {
            'type': float,
            'list': False,
            'value': None
        },
        'constantAperture': {
            'type': float,
            'list': False,
            'value': None
        },
        'apertureFromTransmissivity': {
            'type': float,
            'list': True,
            'list_length': 2,
            'value': None
        },
        # perm
        'permOption': {
            'type': int,
            'list': False,
            'value': None
        },
        'constantPermeability': {
            'type': float,
            'list': False,
            'value': None
        },
        'minimum_fracture_size': {
            'type': float,
            'list': False,
            'value': None
        },
    }

    mandatory = {
        'stopCondition', 'domainSize', 'numOfLayers', 'numOfRegions',
        'outputAllRadii', 'outputFinalRadiiPerFamily',
        'outputAcceptedRadiiPerFamily', 'tripleIntersections',
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
