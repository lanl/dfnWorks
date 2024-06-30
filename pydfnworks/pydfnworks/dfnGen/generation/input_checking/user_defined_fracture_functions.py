from pydfnworks.dfnGen.generation.input_checking.helper_functions import print_error, print_warning
from pydfnworks.general.logging import local_print_log


import sys
import os
from numpy import pi


def check_angle_option(angle_option, array):
    for val in array:
        if angle_option == "radian":
            if val > 2 * pi:
                print_warning(
                    "Value greater than 2 PI, angle option of radians has been selected"
                )
        elif angle_option == "degree":
            if val > 360:
                print_warning(
                    "Value greater than 2 PI, angle option of radians has been selected"
                )


def print_user_fracture_information(self, shape, frac_number=None):
    """ Prints information about a user defined fracture to screen

    Parameters
    ----------------
        self : DFN object

        shape: string
            The shape of the fracture options are 'rect', 'ell', and 'poly' - Required

        fracture_number : int
            Index of fracture. If none (default), then information about all user fractures of input shape are printed to screen

    Returns
    ---------------
        None

    Notes
    --------------
        None
    """
    self.print_log(f"\n--> User Fracture information")
    if shape == 'rect':
        if frac_number:
            fracture_dictionary = self.user_rect_params[frac_number]
        else:
            fracture_dictionaries = self.user_rect_params

    elif shape == 'ell':
        if frac_number:
            fracture_dictionary = self.user_ell_params[frac_number]
        else:
            fracture_dictionaries = self.user_ell_params

    elif shape == 'poly':
        fracture_dictionaries = self.user_poly_params

    if frac_number:
        self.print_log(f"* Fracture Number {frac_number} *")
        self.print_log("{:40s}{:}".format("Name", "Value"))
        self.print_log("{:40s}{:}".format("----------------------------",
                                 "---------------"))
        for key in fracture_dictionary.keys():
            self.print_log(f"{key:40s} {fracture_dictionary[key]}")
    else:
        for i, fracture_dictionary in enumerate(fracture_dictionaries):
            self.print_log(f"* Fracture Number {i+1} *")
            self.print_log("{:40s}{:}".format("Name", "Value"))
            self.print_log("{:40s}{:}".format("----------------------------",
                                     "---------------"))
            for key in fracture_dictionary.keys():
                self.print_log(f"{key:40s} {fracture_dictionary[key]}")
            self.print_log("\n")


def add_user_fract_from_file(self,
                             filename,
                             shape,
                             nPolygons,
                             by_coord=False,
                             aperture=None,
                             transmissivity=None,
                             permeability=None):
    """ Sets up paths for fractures defined in user input file. When inserting user fractures from file, hydraulic properties must be provided as a list of length nPolygons (number of fractures defined in the file)

    Parameters
    ----------------
        filename : string
            path to source file

        shape: string
            The shape of the fracture options are 'rect', 'ell', and 'poly' - Required

        by_coord : boolean
            True / False of file format for coordinate or general input

        nPolygons : int
            The number of polygons specified in the file

        permeability : list or array
            Permeabilities of the fractures 

        transmissivity : list or array
            Fracture Tramsmissivities

        aperture : list or array
            Hydraulic apertures of the fracture

    Returns
    ---------------
        None

    Notes
    --------------
        Does not write the file, only sets up paths
    ~/src/dfnworks-aidan/pydfnworks/pydfnworks/ 
    """
    fracture_dictionary = {"shape": shape, "filename": filename}

    hy_prop_type = determine_hy_prop_type(aperture, transmissivity,
                                          permeability)
    fracture_dictionary['aperture'] = aperture
    fracture_dictionary['transmissivity'] = transmissivity
    fracture_dictionary['permeability'] = permeability
    fracture_dictionary['hy_prop_type'] = hy_prop_type
    fracture_dictionary['nPolygons'] = nPolygons


    if aperture is not None:
        if len(aperture) != nPolygons:
            print_error("Error. aperture list for user fractures from file is not the same length as nPolygons, please check input for add_user_fract_from_file\n")
    if transmissivity is not None:
        if len(transmissivity) != nPolygons:
            print_error("Error. transmissivity list for user fractures from file is not the same length as nPolygons, please check input for add_user_fract_from_file\n")
    if permeability is not None:
        if len(permeability) != nPolygons:
            print_error("Error. aperture list for user fractures from file is not the same length as nPolygons, please check input for add_user_fract_from_file\n")


    if shape == 'rect':
        self.params['RectByCoord_Input_File_Path']['value'] = filename
        if by_coord:
            self.params['userRectByCoord']['value'] = True
        else:
            self.params['userRectanglesOnOff']['value'] = True
        self.user_rect_params.append(fracture_dictionary)
        frac_number = len(self.user_rect_params)
        self.print_user_fracture_information('rect', frac_number - 1)

    elif shape == 'ell':
        self.params['EllByCoord_Input_File_Path']['value'] = filename
        if by_coord:
            self.params['userEllByCoord']['value'] = True
        else:
            self.params['userEllipsesOnOff']['value'] = True
        self.user_ell_params.append(fracture_dictionary)
        frac_number = len(self.user_ell_params)
        self.print_user_fracture_information('ell', frac_number - 1)
    elif shape == 'poly':
        # user polygon
        self.params['userPolygonByCoord']['value'] = True
        self.params['PolygonByCoord_Input_File_Path']['value'] = filename
        self.user_poly_params.append(fracture_dictionary)
        self.print_user_fracture_information('poly')
    else:
        print_error(
            "Error.user fracture shape is not specified correctly, options are 'rect', 'ell', or 'poly'\n"
        )


def add_user_fract(self,
                   shape,
                   radii,
                   translation,
                   filename=None,
                   aspect_ratio=1,
                   beta=0,
                   angle_option='degree',
                   orientation_option='normal',
                   normal_vector=None,
                   trend_plunge=None,
                   dip_strike=None,
                   number_of_vertices=None,
                   permeability=None,
                   transmissivity=None,
                   aperture=None):
    """
    Specifies user defined fracture parameters for the DFN.
    
    Parameters
    -------------
        shape: string
            The desired shape of the fracture options are 'rect', 'ell', and 'poly' - Required
        
        radii : float
            1/2 size of the fracture in meters - Required

        translation : list of floats [3]
            Fracture center

        filename: string
            The name of the user defined fracture file. Default is user_defined_{shape}.dat
        
        aspect_ratio : float
            Fracture aspect ratio

        beta : float
            Rotation angle around center of the fracture

        angle_option : string
            Angle option 'degree' or 'radian'. Default is degree

        orientation_option : string
            Choice of fracture orienation  'normal', 'trend_plunge', 'dip_strike'

        normal_vector : list [3]
            normal vector of the fracture

        trend_plunge : list [2]
            trend and plunge of the fracture 

        dip_strike : list [2]
            dip and strike of the fracture

        number_of_vertices : int
            Number of vertices on the fracture boundary. 

        permeability : float
            Permeability of the fracture 

        transmissivity : float
            Fracture Tramsmissivity

        aperture : float
            Hydraulic aperture of the fracture
        
    Returns 
    ---------
        None - fracture dictionaries are attached to the DFN object
        
    Notes
    -------
        Please be aware, the user fracture files can only be automatically written for
        ellipses and rectangles not specified by coordinate.

        See
        
        https://dfnworks.lanl.gov/dfngen.html#user-defined-fracture-generation-parameters
        
        for additional information

    """

    # if specifying details in the python driver file.
    fracture_dictionary = {"shape": shape}
    fracture_dictionary['nPolygons'] = 1
    # Check input parameters
    if filename:
        fracture_dictionary['filename'] = filename
    else:
        filename = self.jobname + f"/dfnGen_output/user_defined_{shape}.dat"
        fracture_dictionary['filename'] = filename

    # Check radius is positive.
    if radii > 0:
        fracture_dictionary['Radii:'] = radii
    else:
        print_error(
            f"Error. Fracture radius must be positive. Value provided {radii}. Exiting."
        )

    # Check Aspect Ratio is positive
    if aspect_ratio > 0:
        fracture_dictionary['Aspect_Ratio:'] = aspect_ratio
    else:
        print_error(
            f"Error. Aspect Ratio must be positive. Value provided {aspect_ratio}. Exiting."
        )

    ## check beta Rotation in non-negative.
    if beta >= 0:
        fracture_dictionary['Beta:'] = beta
    else:
        print_error(
            f"Error. Beta rotation must be non-negative (>0). Value provided {beta}. Exiting."
        )

    # Check Angle options
    angle_options = ['radian', 'degree']
    if angle_option in angle_options:
        fracture_dictionary['AngleOption:'] = angle_option
    else:
        print_error(
            f"Error. Unknown angle_option value provided: {angle_option}. Acceptable values are 'radian', 'degree'.\nExiting."
        )

    if len(translation) == 3:
        fracture_dictionary['Translation:'] = translation
    else:
        print_error(
            f"Error. Fracture Translation (center) must have 3 elements, only {len(translation)} provided.\nValue provided: {translation}. Exiting"
        )

    ## Check orienations and consistency
    if orientation_option == 'normal':
        fracture_dictionary['userOrientationOption:'] = 0
        if normal_vector:
            fracture_dictionary['Normal:'] = normal_vector
        else:
            print_error(
                "Error. Requested user fracture orienation 0, but normal vector was not provided. exiting."
            )
        if len(normal_vector) != 3:
            print_error(
                f"Error. Normal vector must have 3 elements, only {len(normal_vector)} provided.\nNormal: {normal_vector}. Exiting"
            )

    elif orientation_option == 'trend_plunge':
        fracture_dictionary['userOrientationOption:'] = 1
        if trend_plunge:
            fracture_dictionary['Trend_Plunge:'] = trend_plunge
        else:
            print_error(
                "Error. Requested user fracture orienation trend_plunge, but trend_plunge was not provided. exiting."
            )

        if len(trend_plunge) != 2:
            print_error(
                f"Error. Trend/Plunge must have 2 elements, only {len(trend_plunge)} provided.\trend_plunge: {trend_plunge}. Exiting"
            )

        # Check is angles make sense given radians or degrees
        self.print_log("--> Checking trend_plunge angles")
        check_angle_option(angle_option, trend_plunge)

    elif orientation_option == 'dip_strike':
        fracture_dictionary['userOrientationOption:'] = 2
        if dip_strike:
            fracture_dictionary['Dip_Strike:'] = dip_strike
        else:
            print_error(
                "Error. Requested user fracture orienation dip_strike, but dip_strike was not provided. exiting."
            )
        if len(dip_strike) != 2:
            print_error(
                f"Error. Dip/Strike must have 2 elements, only {len(dip_strike)} provided.\trend_plunge: {dip_strike}. Exiting"
            )
    else:
        print_error(
            f"Error. Unknown orientation_option provided. Value: {orientation_option}. Options are 'normal', 'trend_plunge', and 'dip_strike'. Exiting"
        )

        # Check is angles make sense given radians or degrees
        self.print_log("--> Checking dip_strike angles")
        check_angle_option(angle_option, dip_strike)

    # hydraulic properties
    hy_prop_type = determine_hy_prop_type(aperture, transmissivity,
                                          permeability)
    fracture_dictionary['aperture'] = [aperture]
    fracture_dictionary['transmissivity'] = [transmissivity]
    fracture_dictionary['permeability'] = [permeability]
    fracture_dictionary['hy_prop_type'] = hy_prop_type

    ## Logic for i/o
    if shape == 'rect':
        self.params['userRectanglesOnOff']['value'] = True
        self.params['UserRect_Input_File_Path']['value'] = fracture_dictionary[
            'filename']
        self.user_rect_params.append(fracture_dictionary)
        frac_number = len(self.user_rect_params)
        self.print_user_fracture_information('rect', frac_number - 1)

    elif shape == 'ell':
        if number_of_vertices > 2:
            fracture_dictionary['Number_of_Vertices:'] = number_of_vertices
        else:
            print_error(
                f"Error. number_of_vertices must be greater than 2. VAlue provided: {number_of_vertices}. Exiting."
            )

        self.params['userEllipsesOnOff']['value'] = True
        self.params['UserEll_Input_File_Path']['value'] = fracture_dictionary[
            'filename']

        self.user_ell_params.append(fracture_dictionary)
        frac_number = len(self.user_ell_params)
        self.print_user_fracture_information('ell', frac_number - 1)


def write_user_fractures_to_file(self):
    """Writes the user defined fracutres to a file if file is not already specified

        Parameters
        ------------
            self : DFN object

        Returns
        ---------
            None 

        Notes
        -------
            None
    """

    n_rects = len(self.user_rect_params)
    n_ells = len(self.user_ell_params)

    if n_ells > 0:
        self.print_log(
            f"--> Writing user defined ellispes to file {self.params['UserEll_Input_File_Path']['value']}"
        )
        with open(self.params['UserEll_Input_File_Path']['value'],
                  'w+') as ell_file:
            ell_file.write(f'nUserEll: {n_ells} \n \n')
            orientation_option = self.user_ell_params[0][
                'userOrientationOption:']
            for key in self.user_ell_params[0].keys():
                if key == 'userOrientationOption:':
                    value = self.user_ell_params[0][key]
                    ell_file.write(f'{key} {value} \n \n')
                elif key == 'Normal:':
                    if orientation_option == 0:
                        ell_file.write(f'{key} \n')
                        for j in range(n_ells):
                            value = self.user_ell_params[j][key]
                            if value is not None:
                                ell_file.write(f'{value} \n')
                            else:
                                error = "user orientation option not specified correctly \n0:'normal'\n1:'trend_plunge'\n2:'dip_strike'\n"
                                self.print_log(error, 'error')

                        ell_file.write('\n')

                    else:
                        continue

                elif key == 'Trend_Plunge:':

                    if orientation_option == 1:
                        ell_file.write(f'{key} \n')
                        for j in range(n_ells):
                            value = self.user_ell_params[j][key]
                            if value is not None:
                                ell_file.write(f'{value} \n')
                            else:
                                error = "user orientation option not specified correctly \n0:'normal'\n1:'trend_plunge'\n2:'dip_strike'\n"
                                self.print_log(error, 'error')

                        ell_file.write('\n')

                    else:
                        continue

                elif key == 'Dip_Strike:':

                    if orientation_option == 2:
                        ell_file.write(f'{key} \n')
                        for j in range(n_ells):
                            value = self.user_ell_params[j][key]
                            if value is not None:
                                ell_file.write(f'{value} \n')
                            else:
                                error = "user orientation option not specified correctly \n0:'normal'\n1:'trend_plunge'\n2:'dip_strike'\n"
                                self.print_log(error, 'error')

                        ell_file.write('\n')

                    else:
                        continue

                elif key == 'filename' or key == 'shape':
                    continue
                else:

                    ell_file.write(f'{key} \n')
                    for j in range(n_ells):
                        value = self.user_ell_params[j][key]
                        ell_file.write(f'{value} \n')
                    ell_file.write('\n')

    if n_rects > 0:

        self.print_log(
            f"--> Writing user defined rectangles to file {self.params['UserRect_Input_File_Path']['value']}"
        )
        with open(self.params['UserRect_Input_File_Path']['value'],
                  'w+') as rect_file:

            rect_file.write(f'nUserRect: {n_rects} \n \n')

            orientation_option = self.user_rect_params[0][
                'userOrientationOption:']

            for key in self.user_rect_params[0].keys():

                if key == 'userOrientationOption:':

                    value = self.user_rect_params[0][key]
                    rect_file.write(f'{key} {value} \n \n')

                elif key == 'Normal:':

                    if orientation_option == 0:
                        rect_file.write(f'{key} \n')
                        for j in range(n_rects):
                            value = self.user_rect_params[j][key]
                            if value is not None:
                                rect_file.write(f'{value} \n')
                            else:
                                error = "user orientation option not specified correctly \n0:'Normal'\n1:'Trend_Plunge'\n2:Dip_Strike'"
                                self.print_log(error, 'error')

                        rect_file.write('\n')

                    else:
                        continue

                elif key == 'Trend_Plunge:':

                    if orientation_option == 1:
                        rect_file.write(f'{key} \n')
                        for j in range(n_rects):
                            value = self.user_rect_params[j][key]
                            if value is not None:
                                rect_file.write(f'{value} \n')
                            else:
                                error = "user orientation option not specified correctly \n0:'Normal'\n1:'Trend_Plunge'\n2:Dip_Strike'"
                                self.print_log(error, 'error')

                        rect_file.write('\n')

                    else:
                        continue

                elif key == 'Dip_Strike:':

                    if orientation_option == 2:
                        rect_file.write(f'{key} \n')
                        for j in range(n_rects):
                            value = self.user_rect_params[j][key]
                            if value is not None:
                                rect_file.write(f'{value} \n')
                            else:
                                error = "user orientation option not specified correctly \n0:'Normal'\n1:'Trend_Plunge'\n2:Dip_Strike'"
                                sys.stderr.write(error)

                        rect_file.write('\n')

                    else:
                        continue

                elif key == 'filename':
                    continue
                elif key == 'shape':
                    continue

                else:

                    rect_file.write(f'{key} \n')
                    for j in range(n_rects):
                        value = self.user_rect_params[j][key]
                        rect_file.write(f'{value} \n')
                    rect_file.write('\n')


def determine_hy_prop_type(aperture, transmissivity, permeability):
    """Determines the type of user defined hydraulic property based on user inupt

        Parameters
        -------------
            aperture : None or Float
            transmissivity : None or Float
            permeability : None or Float

        Returns
        ---------
            The hydraulic property type. Exactly one of the three parameters must be a float or an exception will be thrown
                                                                                           Notes
        -------"""

    #Determine Hydraulic Property type

    hy_prop_type = None

    if aperture is not None:
        hy_prop_type = 'aperture'

    if transmissivity is not None:
        if hy_prop_type != None:
            error = "Please specify exactly one of the following for user defined fracture: aperture, transmissivity, permeability\n"
            local_print_log(error, 'error')
        else:
            hy_prop_type = 'transmissivity'

    if permeability is not None:
        if hy_prop_type != None:
            error = "Please specify exactly one of the following for user defined fracture: aperture, transmissivity, permeability\n"
            local_print_log(error, 'error')
        else:
            hy_prop_type = 'permeability'

    if hy_prop_type == None:
        error = "\nPlease specify exactly one of the following for user defined fracture: aperture, transmissivity, permeability\n"
        local_print_log(error, 'error')

    return hy_prop_type
