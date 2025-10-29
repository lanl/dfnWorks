"""
.. module:: fracture_family_utils
   :synopsis: Utilities to reorder fracture families and populate the DFN parameter dictionary.
"""
import pydfnworks.dfnGen.generation.input_checking.helper_functions as hf
from pydfnworks.general.logging import initialize_log_file, print_log



def write_fracture_families(self):
    """Reorder fracture families in DFN, and then write them to 
    the DFN parameter dictionary

    Parameters
    ------------
        DFN(self): the descete fracture network object
    
    Returns
    --------
        dict
            DFN parameter dictionary with populated fracture family fields

    Notes
    ------
        None
    """

    self.reorder_fracture_families()
    self.params['nFracFam']['value'] = len(self.fracture_families)

    if self.params['nFracFam']['value'] == 0:
        self.params['orientationOption'][
            'value'] = 0  #set to 0 if there are only user defined fractures to avoid error

    for i in range(self.params['nFracFam']['value']):
        add_fracture_family_to_params(self.params, self.fracture_families[i])

    return self.params


def add_fracture_family_to_params(params, fracture_family):
    """Add values from fracture family dictionary
    to the parameter dictionary
    
    Parameters
    -------------
        params : dict
            The DFN parameter dictionary.
        
        fracture_family: fracture family dictionary for a family
        
    Returns 
    ---------
        params: dict
            The populated DFN parameter dictionary.
        
    Notes
    -------
        None at the moment
    """


    fracture_type_prefix = determine_type(fracture_family)

    if fracture_type_prefix == 'e':
        if params['nFamEll']['value'] == None:
            params['nFamEll']['value'] = 1
        else:
            params['nFamEll']['value'] += 1

    if fracture_type_prefix == 'r':
        if params['nFamRect']['value'] == None:
            params['nFamRect']['value'] = 1
        else:
            params['nFamRect']['value'] += 1

    params, distribution_type, orientation_dist = add_distribution_params(fracture_family, params, fracture_type_prefix)

    if distribution_type == 'tpl':
        write_value_to_params(params, 'distr', fracture_family, 'distribution',
                              fracture_type_prefix)
        params[fracture_type_prefix + 'distr']['value'][-1] = 2
        write_value_to_params(params, 'min', fracture_family, 'min_radius',
                              fracture_type_prefix)
        write_value_to_params(params, 'max', fracture_family, 'max_radius',
                              fracture_type_prefix)

    if distribution_type == 'log_normal':
        write_value_to_params(params, 'distr', fracture_family, 'distribution',
                              fracture_type_prefix)
        params[fracture_type_prefix + 'distr']['value'][-1] = 1
        write_value_to_params(params, 'LogMin', fracture_family, 'min_radius',
                              fracture_type_prefix)
        write_value_to_params(params, 'LogMax', fracture_family, 'max_radius',
                              fracture_type_prefix)

    if distribution_type == 'exp':
        write_value_to_params(params, 'distr', fracture_family, 'distribution',
                              fracture_type_prefix)
        params[fracture_type_prefix + 'distr']['value'][-1] = 3
        write_value_to_params(params, 'ExpMin', fracture_family, 'min_radius',
                              fracture_type_prefix)
        write_value_to_params(params, 'ExpMax', fracture_family, 'max_radius',
                              fracture_type_prefix)

    if distribution_type == 'constant':
        write_value_to_params(params, 'distr', fracture_family, 'distribution',
                              fracture_type_prefix)
        params[fracture_type_prefix + 'distr']['value'][-1] = 4

    write_value_to_params(params, 'Layer', fracture_family, 'layer',
                          fracture_type_prefix)

    write_value_to_params(params, 'Region', fracture_family, 'region',
                          fracture_type_prefix)

    write_value_to_params(params, '_p32Targets', fracture_family, 'p32',
                          fracture_type_prefix)

    write_value_to_params(params, 'aspect', fracture_family, 'aspect',
                          fracture_type_prefix)

    if fracture_type_prefix == 'e':
        write_value_to_params(params, 'numPoints', fracture_family,
                              'number_of_points', fracture_type_prefix)

    write_value_to_params(params, 'betaDistribution', fracture_family,
                          'beta_distribution', fracture_type_prefix)

    write_value_to_params(params, 'beta', fracture_family, 'beta',
                          fracture_type_prefix)

    write_value_to_params(params, 'famProb', fracture_family, 'probability',
                          '')

    if orientation_dist == 'bingham':
        write_value_to_params(params, 'orientation_distribution', fracture_family, 'orientation_distribution', fracture_type_prefix)
        params[fracture_type_prefix + 'orientation_distribution']['value'][-1] = 1
    if orientation_dist == 'fisher':
        write_value_to_params(params, 'orientation_distribution', fracture_family, 'orientation_distribution', fracture_type_prefix)
        params[fracture_type_prefix + 'orientation_distribution']['value'][-1] = 0
    
    return params


def determine_type(fracture_family):
    """Determine whether the fracture family is elliptical or rectangular
    
    Parameters
    -------------        
        fracture_family : dict
            Fracture family dictionary for a family.
        
    Returns 
    ---------
        fracture_type_prefix: str
            The prefix 'r' for rectangular or 'e' for elliptical
        
    Notes
    -------
        Raises an error if neither or both types are specified.
    """

    if fracture_family['type']['value']['ellipse'] == True and fracture_family[
            'type']['value']['rect'] == False:
        fracture_type_prefix = 'e'

    elif fracture_family['type']['value'][
            'ellipse'] == False and fracture_family['type']['value'][
                'rect'] == True:
        fracture_type_prefix = 'r'

    # else:

    #     self.print_log('Fracture family type is not specified', 'error')

    return fracture_type_prefix


def add_distribution_params(fracture_family, params, fracture_type_prefix):
    """Add distribution values from fracture family dictionary
    to the parameter dictionary
    
    Parameters
    -------------
        fracture_family : dict
            Fracture family dictionary for a family.
        
        fracture_family: dict
            The DFN parameter dictionary.
        
        fracture_type_prefix : str
            'r' for rectangular or 'e' for elliptical.
        
    Returns 
    ---------
        params: Populated parameter dictionary
        
    Notes
    -------
        Raises an error if distribution selection is ambiguous or missing.
    """

    #Figure out what distribution represents the fracture family
    #Check to make sure that distribution is uniquely prescribed
    distributions = fracture_family['distribution']['value']

    distribution_type = None

    for key in distributions.keys():
        if distributions[key] == True and distribution_type == None:
            distribution_type = key
        elif distributions[key] == False:
            pass
        else:
            hf.print_error(
                'Exactly one distribution value must be True for a fracture family'
            )
    if distribution_type == None:
        print_log(
            'Exactly one distribution value must be True for a fracture family', 'error'
        )

    #Populate the parameter dictionary with values from the fracture family dictionary
    distribution_params = fracture_family[distribution_type]['value']

    if distribution_type == 'constant':
        write_value_to_params(params, 'const', fracture_family, 'constant',
                              fracture_type_prefix)

    if distribution_type == 'tpl':
        write_value_to_params(params,
                              'alpha',
                              distribution_params,
                              'alpha',
                              fracture_type_prefix,
                              value_flag=True)

    if distribution_type == 'log_normal':
        write_value_to_params(params,
                              'LogMean',
                              distribution_params,
                              'mean',
                              fracture_type_prefix,
                              value_flag=True)
        write_value_to_params(params,
                              'sd',
                              distribution_params,
                              'std',
                              fracture_type_prefix,
                              value_flag=True)

    if distribution_type == 'exp':
        write_value_to_params(params,
                              'ExpMean',
                              distribution_params,
                              'mean',
                              fracture_type_prefix,
                              value_flag=True)
    
    orientation_dist = fracture_family['orientation_distribution']['value']
    orient_opt = params['orientationOption']['value']  # 0: theta/phi, 1: trend/plunge, 2: strike/dip

    if orientation_dist == 'fisher':
        fisher_params = fracture_family['fisher']['value']
        for key in fisher_params:
            if key in {'theta', 'phi'} and orient_opt == 0:
                write_value_to_params(params, key, fisher_params, key, fracture_type_prefix, value_flag=True)
            elif key in {'trend', 'plunge'} and orient_opt == 1:
                write_value_to_params(params, key, fisher_params, key, fracture_type_prefix, value_flag=True)
            elif key in {'strike', 'dip'} and orient_opt == 2:
                write_value_to_params(params, key, fisher_params, key, fracture_type_prefix, value_flag=True)
            elif key == 'kappa':  # Fisher concentration
                write_value_to_params(params, key, fisher_params, key, fracture_type_prefix, value_flag=True)

    elif orientation_dist == 'bingham':
        bingham_params = fracture_family['bingham']['value']
        for key in bingham_params:
            if key in {'theta', 'phi'} and orient_opt == 0:
                write_value_to_params(params, key, bingham_params, key, fracture_type_prefix, value_flag=True)
            elif key in {'trend', 'plunge'} and orient_opt == 1:
                write_value_to_params(params, key, bingham_params, key, fracture_type_prefix, value_flag=True)
            elif key in {'strike', 'dip'} and orient_opt == 2:
                write_value_to_params(params, key, bingham_params, key, fracture_type_prefix, value_flag=True)
            elif key in {'kappa1', 'kappa2'}:  # Bingham concentrations
                write_value_to_params(params, key, bingham_params, key, fracture_type_prefix, value_flag=True)
    # --- Ensure per-family list alignment with placeholders ---
    if fracture_type_prefix == 'e':  # same idea applies to 'r' if you add rectangles
        if orientation_dist == 'fisher':
            # pad ekappa1/ekappa2 so lists stay in sync
            write_value_to_params(params, 'kappa1', {'kappa1': 0.0}, 'kappa1', fracture_type_prefix, value_flag=True)
            write_value_to_params(params, 'kappa2', {'kappa2': 0.0}, 'kappa2', fracture_type_prefix, value_flag=True)
        elif orientation_dist == 'bingham':
            # pad ekappa so lists stay in sync
            write_value_to_params(params, 'kappa',  {'kappa':  0.0}, 'kappa',  fracture_type_prefix, value_flag=True)
    else:
        hf.print_error(f"Unknown orientation_distribution: {orientation_dist}")

    return params, distribution_type, orientation_dist


def write_value_to_params(params,
                          param_key,
                          value_dict,
                          value_dict_key,
                          fracture_type_prefix,
                          value_flag=False):
    """Write values from fracture family dictionary to param dictionary. Creates a list
    if type is None
    
    Parameters
    -------------
        params : dict
            The DFN parameter dictionary.
        
        param_key : str
            The key for the parameter value to be written.
        
        value_dict : dict
            Fracture family dictionary or sub-dictionary.
        
        value_dict_key : str
            The key for the parameter in value_dict.
        
        fracture_type_prefix : str
            'r' for rectangular or 'e' for elliptical.
        
        value_flag : bool, optional
            If False, value is taken from value_dict[value_dict_key]['value'],
            if True, from value_dict[value_dict_key].       
    Returns 
    ---------
        None
        
    Notes
    -------
        None 
    """
    
    if value_flag is False:
        value = value_dict[value_dict_key]['value']
    else:
        value = value_dict[value_dict_key]

    if value is None:
        return  # nothing to write

    param_name = f"{fracture_type_prefix}{param_key}"

    if param_name not in params or not isinstance(params[param_name], dict) or 'value' not in params[param_name]:
        params[param_name] = {'value': None}
    # ----------------------------------------------------------------

    if params[param_name]['value'] is None:
        params[param_name]['value'] = [value]
    else:
        params[param_name]['value'].append(value)


def reorder_fracture_families(self):
    """Reorder the fracture families to pass to backend code
    
    Parameters
    --------------
        DFN(self): the DFN object

    Returns
    --------
        None
            
    Notes
    ---------
        Prints the original and final order from user input to what is passed 
        to the backend. 
    """

    number_of_families = len(self.fracture_families)

    original_order = []

    ellipse_list = []

    ellipse_index = []

    rect_list = []

    rect_index = []

    for i in range(number_of_families):

        original_order.append(i)

        current_fracture_family = self.fracture_families[i]

        if current_fracture_family['type']['value'][
                'ellipse'] == True and current_fracture_family['type'][
                    'value']['rect'] == False:

            ellipse_list.append(current_fracture_family)

            ellipse_index.append(i)

        elif current_fracture_family['type']['value'][
                'ellipse'] == False and current_fracture_family['type'][
                    'value']['rect'] == True:

            rect_list.append(current_fracture_family)

            rect_index.append(i)

        else:
            self.print_log('Fracture family type is not specified', 'error')

    ellipse_index.extend(rect_index)
    final_order = ellipse_index

    ellipse_list.extend(rect_list)
    final_list = ellipse_list

    self.fracture_families = final_list

    if original_order == final_order:
        self.print_log("Fracture Family order was not changed")

    else:
        self.print_log("Fracture Families have been reordered")
        self.print_log("Original order = ", original_order)
        self.print_log("Final order = ", final_order)
