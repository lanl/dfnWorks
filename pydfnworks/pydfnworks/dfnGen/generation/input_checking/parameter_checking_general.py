import pydfnworks.dfnGen.generation.input_checking.helper_functions as hf
from shutil import copy


def check_stop_condition(params):
    """ Check the number of polygons if stopCondition is set to 1, else check the p32 target parameters.

    Parameters
    -------------
        params : dict
            parameter dictionary
    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """
    if not params['stopCondition']['value']:
        check_n_poly(params['nPoly']['value'])
    else:
        check_p32_targets(params)


def check_n_poly(n_poly):
    """ Verifies the number of polygons is a positive integer.
    Parameters
    -------------
        n_poly : int
            number of requested polygons
            
    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    if n_poly <= 0:
        hf.print_error(
            f"\"nPoly\" must be a positive integer be zero. {n_poly} value provided."
        )


def check_p32_targets(params):
    """ Check the number of polygons if stopCondition is set to 1, else check the p32 target parameters.

    Parameters
    -------------
        params : dict
            parameter dictionary
    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """
    # Check P32 inputs for ellipses
    if params['nFamEll']['value'] > 0:
        hf.check_none('e_p32Targets', params['e_p32Targets']['value'])
        hf.check_length('e_p32Targets', params['e_p32Targets']['value'],params['nFamEll']['value'])
        hf.check_values('e_p32Targets',params['e_p32Targets']['value'],0)

    # Check P32 inputs for rectangles
    if params['nFamRect']['value'] > 0:
        hf.check_none('r_p32Targets', params['r_p32Targets']['value'])
        hf.check_length('r_p32Targets', params['r_p32Targets']['value'],params['nFamRect']['value'])
        hf.check_values('r_p32Targets',params['r_p32Targets']['value'],0)

def check_domain(params):
    """ Check that domain properties. 
    * domainSize, 3 entires greater than 0
    * domainSizeIncrease, 3 entires, must be less than 1/2 corresponding domain size
    * ignoreBoundaryFaces, bool
    * boundaryFaces, 6 entires (0 or 1)

    Parameters
    -------------
        params : dict
            parameter dictionary
    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    if len(params['domainSize']['value']) != 3:
        hf.print_error(
            f"\"domainSize\" has defined {len(params['domainSize']['value'])} value(s) but there must be 3 non-zero values to represent x, y, and z dimensions"
        )

    for i, val in enumerate(params['domainSize']['value']):
        if val <= 0:
            hf.print_error(
                f"\"domainSize\" entry {i+1} has value {val}. Value must be positive"
            )

    if len(params['domainSizeIncrease']
           ['value']) != 3:
        hf.print_error(
            f"\"domainSizeIncrease\" has defined {len(params['domainSizeIncrease']['value'])} value(s) but there must be 3 non-zero values to represent x, y, and z dimensions"
        )

    ## Check Domain Size increase
    for i, val in enumerate(params['domainSizeIncrease']['value']):
        if val < 0:
            hf.print_error(
                f"\"domainSize\" entry {i+1} has value {val}. Value must be non-negative"
            )

        elif val >= params['domainSize']['value'][i] / 2:
            hf.print_error(
                f"\"domainSizeIncrease\" entry {i+1} is {val}, which is more than half of the domain's range in that dimension. Cannot change the domain's size by more than half of that dimension's value defined in \"domainSize\". This risks collapsing or doubling the domain."
            )

    # Check Boundary Faces
    try:
        if not params['ignoreBoundaryFaces']['value']:
            if len(params['boundaryFaces']
                   ['value']) != params['boundaryFaces']['list_length']:
                hf.print_error(
                    f"\"boundaryFaces\" must be a list of 6 flags (0 or 1), {len(params['boundaryFaces']['value'])} have(has) been defined. Each flag represents a side of the domain, {{+x, -x, +y, -y, +z, -z}}."
                )
            for i, val in enumerate(params['boundaryFaces']['value']):
                if val not in [0, 1]:
                    hf.print_error(
                        f"\"boundaryFaces\" entry {i+1} has value {val}. Must be 0 or 1."
                    )
        else:
            hf.print_warning("--> Ignoring boundary faces. Keeping all clusters.")
    except:
        print("Error while checking 'boundaryFaces' parameters.")
        print(f"Values provided: {params['boundaryFaces']['value']}\n")
        print(params['boundaryFaces']['description'])
        hf.print_error("")

def check_rejects_per_fracture(rejectsPerFracture):
    """ Check that the value of the rejectsPerFracture is a positive integer. If a value of 0 is provided, it's changed to 1. 

    Parameters
    -------------
        seed : dict
            seed entry of params dictionary
    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    if rejectsPerFracture['value'] < 0:
        hf.print_error(
            f"\"rejectsPerFracture\" has value {rejectsPerFracture['value']}. Value must be positive"
        )
    if rejectsPerFracture['value'] == 0:
        rejectsPerFracture['value'] = 1
        hf.print_warning(
            "--> Changing \"rejectsPerFracture\" from 0 to 1. Cannot ensure 0 rejections."
        )


def check_seed(seed):
    """ Check the value of the seed used for pseudorandom number generation.

    Parameters
    -------------
        seed : dict
            seed entry of params dictionary
    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    if seed['value'] < 0:
        hf.print_error(
            f"\"seed\" must be non-negative. {seed['value']} value provided.")

    elif seed['value'] == 0:
        hf.print_warning(
            "\"seed\" has been set to 0. Random generator will use current wall time so distribution's random selection will not be as repeatable. Use an integer greater than 0 for better repeatability."
        )


def check_family_count(params):
    """Makes sure at least one polygon family has been defined in nFamRect or nFamEll
    OR that there is a user input file for polygons.

    Parameters
    -------------
        params : dict
            parameter dictionary
    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    if params['userEllipsesOnOff']['value'] or params['userRectanglesOnOff'][
            'value'] or params['userRecByCoord']['value'] or params[
                'userEllByCoord']['value'] or params['userPolygonByCoord'][
                    'value']:
        user_def_exists = True
    else:
        user_def_exists = False

    if params['nFamEll']['value'] + params['nFamRect'][
            'value'] <= 0 and not user_def_exists:
        hf.print_error("Zero polygon families have been defined. Please create at least one family "\
              "of ellipses/rectangles, or provide a user-defined-polygon input file path in "\
              "\"UserEll_Input_File_Path\", \"UserRect_Input_File_Path\", \"UserEll_Input_File_Path\", or "\
              "\"RectByCoord_Input_File_Path\" and set the corresponding flag to '1'.")


def check_family_prob(params):
    """ Check the list of family probabilities (the list of  probabilities that a fracture is in each family). If the probabilities don't sum to 1, they are rescaled to do so. 

    Parameters
    -------------
        params : dict
            parameter dictionary
    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    if (params['nFamEll']['value'] + params['nFamRect']['value']) > 0:
        if len(params['famProb']['value']) != (params['nFamEll']['value'] +
                                               params['nFamRect']['value']):
            hf.print_error(
                f"\"famProb\" must have {(params['nFamEll']['value'] + params['nFamRect']['value'])} (nFamEll + nFamRect) non-zero elements, one for each family of ellipses and rectangles. {len(params['famProb']['value'])} probabiliies have been defined."
            )

        total = sum(params['famProb']['value'])
        if total != 1:
            rescaled = [
                float("{:.6}".format(x / total))
                for x in params['famProb']['value']
            ]
            hf.print_warning(
                "'famProb' probabilities did not sum to 1. They have been re-scaled accordingly"
            )
            params['famProb']['value'] = [x / total for x in rescaled]
            print(f"--> New Values: {params['famProb']['value']}")


def check_no_dep_flags(params):
    """ Check for dependency flags. Not sure this does anything."""
    no_dependancy_flags = [
        'outputAllRadii', 'outputFinalRadiiPerFamily',
        'outputAcceptedRadiiPerFamily', 'ecpmOutput', 'tripleIntersections',
        'printRejectReasons', 'visualizationMode', 'keepOnlyLargestCluster',
        'keepIsolatedFractures', 'insertUserRectanglesFirst',
        'forceLargeFractures', 'orientationOption'
    ]

    for key in no_dependancy_flags:
        if params[key]['value'] is None:
            hf.print_error(f"\"{key}\" not provided.")


# def check_fram(disableFram)
#     if disableFram['value']:
#         hf.print_warning("FRAM (feature rejection algorithm for meshing) is disabled.")


def check_aperture(params):
    """ Checks how apertures are being defined. This feature will be removed in the future and apertures will be defined by family.. 

    Parameters
    -------------
        params : dict
            parameter dictionary
    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    if params['aperture']['value'] == 1:
        hf.check_none('meanAperture', params['meanAperture']['value'])
        hf.check_values('meanAperture', params['meanAperture']['value'])
        hf.check_none('stdAperture', params['stdAperture']['value'])
        hf.check_values('stdAperture', params['stdAperture']['value'], 0)

    elif params['aperture']['value'] == 2:
        hf.check_none('apertureFromTransmissivity',
                      params['apertureFromTransmissivity']['value'])
        hf.check_length('apertureFromTransmissivity',
                        params['apertureFromTransmissivity']['value'], 2)
        if params['apertureFromTransmissivity']['value'][0] == 0:
            hf.print_error(
                "\"apertureFromTransmissivity\"'s first value cannot be 0.")
        if params['apertureFromTransmissivity']['value'][1] == 0:
            hf.print_warning(
                "\"apertureFromTransmissivity\"'s second value is 0, which will result in a constant aperture."
            )

    elif params['aperture']['value'] == 3:
        hf.check_none('constantAperture', params['constantAperture']['value'])
        hf.check_values('constantAperture',
                        params['constantAperture']['value'], 0)

    elif params['aperture']['value'] == 4:
        hf.check_none('lengthCorrelatedAperture',
                      params['lengthCorrelatedAperture']['value'])
        hf.check_length('lengthCorrelatedAperture',
                        params['lengthCorrelatedAperture']['value'], 2)
        if params['lengthCorrelatedAperture']['value'][0] == 0:
            hf.print_error(
                "\"lengthCorrelatedAperture\"'s first value cannot be 0.")
        if params['lengthCorrelatedAperture']['value'][1] == 0:
            hf.print_warning(
                "\"lengthCorrelatedAperture\"'s second value is 0, which will result in a constant aperture."
            )
    else:
        hf.print_error("\"aperture\" must only be option 1 (log-normal), 2 (from transmissivity), "\
              "3 (constant), or 4 (length correlated).")


def check_permeability(params):
    """Verify the float used for permeability, if permOption is set to 1

    Parameters
    -------------
        params : dict
            parameter dictionary
    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    if params['permOption']['value'] == 1:
        hf.check_none('constantPermeability',
                      params['constantPermeability']['value'])
        hf.check_values('constantPermeability',
                        params['constantPermeability']['value'], 0)


def check_layers_general(params):
    """ Check the number of layers provided matching the requested number. Checks boundaries of layers that they are within the domain.

    Parameters
    -------------
        params : dict
            parameter dictionary
    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """
    hf.check_none('layers', params['layers']['value'])
    hf.check_length('layers', params['layers']['value'],
                    params['numOfLayers']['value'])

    half_z_domain = params['domainSize']['value'][
        2] / 2.0  ## -index[2] becaue domainSize = [x,y,z]
    ## -center of z-domain at z = 0 so
    ##  whole Zdomain is -zDomainSize to +zDomainSize
    for i, layer in enumerate(params['layers']['value']):
        if len(layer) != 2:
            hf.print_error(
                f"\"layers\" has defined layer #{i+1} to have {len(layer)} element(s) but each layer must have 2 elements, which define its upper and lower bounds"
            )

        if params['layers']['value'].count(layer) > 1:
            hf.print_error(
                "\"layers\" has defined the same layer more than once.")
        minZ = layer[0]
        maxZ = layer[1]
        if maxZ <= minZ:
            hf.print_error(
                f"\"layers\" has defined layer #{i+1} where zmin: {minZ} is greater than zmax {maxZ}"
            )

        if minZ <= -half_z_domain and maxZ <= -half_z_domain:
            hf.print_error(
                f"\"layers\" has defined layer #{i+1} to have both upper and lower bounds completely below the domain's z-dimensional range ({-half_z_domain} to {half_z_domain}). At least one boundary must be within the domain's range. The domain's range is half of 3rd value in \"domainSize (z-dimension) in both positive and negative directions."
            )

        if minZ >= half_z_domain and maxZ >= half_z_domain:
            hf.print_error(
                f"\"layers\" has defined layer #{i+1} to have both upper and lower bounds completely above the domain's z-dimensional range ({-half_z_domain} to {half_z_domain}). At least one boundary must be within the domain's range. The domain's range is half of 3rd value in \"domainSize\" (z-dimension) in both positive and negative directions."
            )


def check_regions_general(params):
    """ Check the number of regions provided matching the requested number. Checks boundaries of regions that they are within the domain. Checks that region_min_value < region_max_value for all three spatial coordinates.

    Parameters
    -------------
        params : dict
            parameter dictionary
    Returns
    ---------
        None

    Notes
    ---------
        Exits program is inconsistencies are found.
    """

    hf.check_none('regions', params['regions']['value'])
    hf.check_length('regions', params['regions']['value'],
                    params['numOfRegions']['value'])

    half_x_domain = params['domainSize']['value'][0] / 2.0
    half_y_domain = params['domainSize']['value'][1] / 2.0
    half_z_domain = params['domainSize']['value'][2] / 2.0

    for i, region in enumerate(params['regions']['value']):
        if len(region) != 6:
            hf.print_error(
                f"\"regions\" has defined layer #{i+1} to have {len(region)} element(s) but each region must have 6 elements, which define its upper and lower bounds"
            )

        if params['regions']['value'].count(region) > 1:
            hf.print_error(
                "\"regions\" has defined the same region more than once.")

        # X direction
        if region[1] <= region[0]:
            hf.print_error(
                f"\"regions\" has defined region #{i+1} where xmin: {region[0]} is greater than xmax: {region[1]}"
            )

        if region[0] <= -half_x_domain and region[1] <= -half_x_domain:
            hf.print_error(
                f"\"regions\" has defined region #{i+1} to have both upper and lower x-bounds completely below the domain's x-dimensional range ({-half_x_domain} to {half_x_domain}). At least one boundary must be within the domain's range. The domain's range is half of 1st value in \"domainSize\" (x-dimension) in both positive and negative directions."
            )

        if region[0] >= half_x_domain and region[1] >= half_x_domain:
            hf.print_error(
                f"\"regions\" has defined region #{i+1} to have both upper and lower x-bounds completely above the domain's x-dimensional range ({-half_x_domain} to {half_x_domain}). At least one boundary must be within the domain's range. The domain's range is half of 1st value in \"domainSize\" (x-dimension) in both positive and negative directions."
            )

        # Y direction
        if region[3] <= region[2]:
            hf.print_error(
                f"\"regions\" has defined region #{i+1} where ymin: {region[2]} is greater than ymax: {region[3]}"
            )

        if region[2] <= -half_y_domain and region[3] <= -half_y_domain:
            hf.print_error(
                f"\"regions\" has defined region #{i+1} to have both upper and lower y-bounds completely below the domain's y-dimensional range ({-half_y_domain} to {half_y_domain}). At least one boundary must be within the domain's range. The domain's range is half of 2nd value in \"domainSize\" (y-dimension) in both positive and negative directions."
            )

        if region[2] >= half_y_domain and region[3] >= half_y_domain:
            hf.print_error(
                f"\"regions\" has defined region #{i+1} to have both upper and lower y-bounds completely above the domain's y-dimensional range ({-half_y_domain} to {half_y_domain}). At least one boundary must be within the domain's range. The domain's range is half of 2nd value in \"domainSize\" (y-dimension) in both positive and negative directions."
            )

        # Z direction
        if region[5] <= region[4]:
            hf.print_error(
                f"\"regions\" has defined region #{i+1} where zmin: {region[4]} is greater than zmax: {region[5]}"
            )

        if region[4] <= -half_z_domain and region[5] <= -half_z_domain:
            hf.print_error(
                f"\"regions\" has defined region #{i+1} to have both upper and lower z-bounds completely below the domain's y-dimensional range ({-half_z_domain} to {half_z_domain}). At least one boundary must be within the domain's range. The domain's range is half of 3rd value in \"domainSize\" (z-dimension) in both positive and negative directions."
            )

        if region[4] >= half_z_domain and region[5] >= half_z_domain:
            hf.print_error(
                f"\"regions\" has defined region #{i+1} to have both upper and lower y-bounds completely above the domain's y-dimensional range ({-half_y_domain} to {half_z_domain}). At least one boundary must be within the domain's range. The domain's range is half of 3rd value in \"domainSize\" (z-dimension) in both positive and negative directions."
            )


def check_user_defined(params):

    user_files = [("userEllipsesOnOff", "UserEll_Input_File_Path"),
                  ("userRectanglesOnOff", "UserRect_Input_File_Path"),
                  ("userRecByCoord", "RectByCoord_Input_File_Path"),
                  ("userEllByCoord", "EllByCoord_Input_File_Path"),
                  ("userPolygonByCoord", "PolygonByCoord_Input_File_Path")]

    for flag, path in user_files:

        # User Ellipse
        hf.check_none(flag, params[flag]['value'])
        if params[flag]['value']:
            hf.check_path(params[path]['value'])
            copy(params[path]['value'], "./")


def check_general(params):
    print(f"--> Checking General Parameters")
    check_stop_condition(params)
    check_domain(params)
    check_family_count(params)
    check_family_prob(params)
    check_no_dep_flags(params)
    check_rejects_per_fracture(params['rejectsPerFracture'])
    check_seed(params['seed'])
    check_aperture(params)
    check_permeability(params)

    if params['numOfLayers']['value'] > 0:
        check_layers_general(params)
    if params['numOfRegions']['value'] > 0:
        check_regions_general(params)
