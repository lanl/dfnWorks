# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 09:17:14 2022

@author: 369984
"""

import sys
import os


def add_user_fract(self,
                   shape,
                   from_file=False,
                   file_name=None,
                   by_coord=False,
                   radii=None,
                   aspect_ratio=None,
                   beta=None,
                   translation=None,
                   orientation_option=None,
                   angle_option=None,
                   normal_vector=None,
                   trend_plunge=None,
                   dip_strike=None,
                   number_of_vertices=None,
                   permeability=None,
                   transmissivity=None,
                   aperture=None):
    """Specifies user defined fracture parameters for the DFN.
    
    Parameters
    -------------
        shape: The desired shape of the fracture options are 'rect', 'ell', and 'poly' 
        
        from_file: Flag to specfy whether the file is already defined
        
        file_name: The name of the user defined fracture file
        
        by_coords: flag to specify if user defined fracture is given with coordinates
        
        additional params are for specifying the user defined fracture. 
        
        See
        
        https://dfnworks.lanl.gov/dfngen.html#user-defined-fracture-generation-parameters
        
        for additional information
        
    Returns 
    ---------
        The populated dfn parameter dictionary
        
        if from file is false a .dat file with user defined fracture information
        
    Notes
    -------
        Please be aware, the user fracture files can only be automatically written for
        ellipses and rectangles not specified by coordinate
    """

    hy_prop_type = determine_hy_prop_type(aperture, transmissivity,
                                          permeability)

    if shape == 'rect':

        rect_param_dict = {}

        if by_coord == True:

            self.params['userRecByCoord']['value'] = 1
            self.params['RectByCoord_Input_File_Path']['value'] = file_name

        else:

            if from_file == True:

                self.params['userRectanglesOnOff']['value'] = 1
                self.params['UserRect_Input_File_Path']['value'] = file_name

            else:

                self.params['userRectanglesOnOff']['value'] = 1
                self.params['UserRect_Input_File_Path']['value'] = file_name

                rect_param_dict['file_name'] = file_name
                rect_param_dict['Radii:'] = radii
                rect_param_dict['Aspect_Ratio:'] = aspect_ratio
                rect_param_dict['Beta:'] = beta
                rect_param_dict['Translation:'] = translation
                rect_param_dict['userOrientationOption:'] = orientation_option
                rect_param_dict['AngleOption:'] = angle_option
                rect_param_dict['Normal:'] = normal_vector
                rect_param_dict['Trend_Plunge:'] = trend_plunge
                rect_param_dict['Dip_Strike:'] = dip_strike
                rect_param_dict['Number_of_Vertices:'] = number_of_vertices

        rect_param_dict['aperture'] = aperture
        rect_param_dict['transmissivity'] = transmissivity
        rect_param_dict['permeability'] = permeability
        rect_param_dict['hy_prop_type'] = hy_prop_type

        self.user_rect_params.append(rect_param_dict)

    elif shape == 'ell':

        ell_param_dict = {}

        if by_coord == True:

            self.params['userEllByCoord']['value'] = 1
            self.params['EllByCoord_Input_File_Path']['value'] = file_name

        else:

            if from_file == True:

                self.params['userEllipsesOnOff']['value'] = 1
                self.params['UserEll_Input_File_Path']['value'] = file_name

            else:

                self.params['userEllipsesOnOff']['value'] = 1
                self.params['UserEll_Input_File_Path']['value'] = file_name

                ell_param_dict['file_name'] = file_name
                ell_param_dict['Radii:'] = radii
                ell_param_dict['Aspect_Ratio:'] = aspect_ratio
                ell_param_dict['Beta:'] = beta
                ell_param_dict['Translation:'] = translation
                ell_param_dict['userOrientationOption:'] = orientation_option
                ell_param_dict['AngleOption:'] = angle_option
                ell_param_dict['Normal:'] = normal_vector
                ell_param_dict['Trend_Plunge:'] = trend_plunge
                ell_param_dict['Dip_Strike:'] = dip_strike
                ell_param_dict['Number_of_Vertices:'] = number_of_vertices

        ell_param_dict['aperture'] = aperture
        ell_param_dict['transmissivity'] = transmissivity
        ell_param_dict['permeability'] = permeability
        ell_param_dict['hy_prop_type'] = hy_prop_type

        self.user_ell_params.append(ell_param_dict)

    elif shape == 'poly':

        # user polygon
        self.params['userPolygonByCoord']['value'] = 1
        self.params['PolygonByCoord_Input_File_Path']['value'] = file_name

        poly_param_dict = {}

        poly_param_dict['aperture'] = aperture
        poly_param_dict['transmissivity'] = transmissivity
        poly_param_dict['permeability'] = permeability
        poly_param_dict['hy_prop_type'] = hy_prop_type

        self.user_poly_params.append(poly_param_dict)

    else:
        error = "user fracture shape is not specified correctly, options are 'rect', 'ell', or 'poly'\n"
        sys.stderr.write(error)
        sys.exit(1)


def write_user_fractures_to_file(self):
    """Writes the user defined fracutres to a file if file is not already specified

        Parameters
        ------------
            self : DFN object

        Returns
        ---------
            user defined fracture file

        Notes
        -------
            None
    """

    n_rects = len(self.user_rect_params)
    n_ells = len(self.user_ell_params)

    if n_ells > 0:

        with open(self.user_ell_params[0]['file_name'], 'w+') as ell_file:

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
                                sys.stderr.write(error)
                                sys.exit(1)

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
                                sys.stderr.write(error)
                                sys.exit(1)

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
                                sys.stderr.write(error)
                                sys.exit(1)

                        ell_file.write('\n')

                    else:
                        continue

                elif key == 'file_name':
                    continue

                else:

                    ell_file.write(f'{key} \n')
                    for j in range(n_ells):
                        value = self.user_ell_params[j][key]
                        ell_file.write(f'{value} \n')
                    ell_file.write('\n')

    if n_rects > 0:

        with open(self.user_rect_params[0]['file_name'], 'w+') as rect_file:

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
                                sys.stderr.write(error)
                                sys.exit(1)

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
                                sys.stderr.write(error)
                                sys.exit(1)

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
                                sys.exit(1)

                        rect_file.write('\n')

                    else:
                        continue

                elif key == 'file_name':
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

    if aperture != None:
        hy_prop_type = 'aperture'

    if transmissivity != None:
        if hy_prop_type != None:
            error = "\nPlease specify exactly one of the following for user defined fracture: aperture, transmissivity, permeability\n"
            sys.stderr.write(error)
            sys.exit(1)
        else:
            hy_prop_type = 'transmissivity'

    if permeability != None:
        if hy_prop_type != None:
            error = "\nPlease specify exactly one of the following for user defined fracture: aperture, transmissivity, permeability\n"
            sys.stderr.write(error)
            sys.exit(1)
        else:
            hy_prop_type = 'permeability'

    if hy_prop_type == None:
        error = "\nPlease specify exactly one of the following for user defined fracture: aperture, transmissivity, permeability\n"
        sys.stderr.write(error)
        sys.exit(1)

    return hy_prop_type
