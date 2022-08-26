import pydfnworks.dfnGen.generation.input_checking.helper_functions as hf

def write_fracture_families(self):
    """Reorder fracture families in DFN, and then write them to 
    the DFN parameter dictionary

    Parameters
    ------------
        DFN(self): the descete fracture network object
    
    Returns
    --------
    DFN object with populated fracture family fields

    Notes
    ------
    None
    """
    
    self.reorder_fracture_families()

    for i in range(len(self.fracture_families)):
        add_fracture_family_to_params(self.params, self.fracture_families[i])

    return self.params

def add_fracture_family_to_params(params, fracture_family):
    """Add values from fracture family dictionary
    to the parameter dictionary
    
    Parameters
    -------------
        params: The dfn parameter dictionary
        
        fracture_family: fracture family dictionary for a family
        
    Returns 
    ---------
        params: The populated dfn parameter dictionary
        
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

    params, distribution_type = add_distribution_params(
        fracture_family, params, fracture_type_prefix)

    if distribution_type == 'tpl':
        write_value_to_params(params, 'distr', fracture_family, 'distribution', fracture_type_prefix)
        params[fracture_type_prefix + 'distr']['value'][-1] = 2
        write_value_to_params(params, 'min', fracture_family, 'min_radius',
                              fracture_type_prefix)
        write_value_to_params(params, 'max', fracture_family, 'max_radius',
                              fracture_type_prefix)

    if distribution_type == 'log_normal':
        write_value_to_params(params, 'distr', fracture_family, 'distribution', fracture_type_prefix)
        params[fracture_type_prefix + 'distr']['value'][-1] = 1
        write_value_to_params(params, 'LogMin', fracture_family, 'min_radius',
                              fracture_type_prefix)
        write_value_to_params(params, 'LogMax', fracture_family, 'max_radius',
                              fracture_type_prefix)

    if distribution_type == 'exp':
        write_value_to_params(params, 'distr', fracture_family, 'distribution', fracture_type_prefix)
        params[fracture_type_prefix + 'distr']['value'][-1] = 3
        write_value_to_params(params, 'ExpMin', fracture_family, 'min_radius',
                              fracture_type_prefix)
        write_value_to_params(params, 'ExpMax', fracture_family, 'max_radius',
                              fracture_type_prefix)

    if distribution_type == 'constant':
        write_value_to_params(params, 'distr', fracture_family, 'distribution', fracture_type_prefix)
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

    return params


def determine_type(fracture_family):
    """Determine whether the fracture family is elliptical or rectangular
    
    Parameters
    -------------        
        fracture_family: fracture family dictionary for a family
        
    Returns 
    ---------
        fracture_type_prefix: the prefix 'r' for rectangular or 'e' for elliptical
        
    Notes
    -------
        None at the moment
    """

    if fracture_family['type']['value']['ellipse'] == True and fracture_family[
            'type']['value']['rect'] == False:
        fracture_type_prefix = 'e'

    elif fracture_family['type']['value'][
            'ellipse'] == False and fracture_family['type']['value'][
                'rect'] == True:
        fracture_type_prefix = 'r'

    else:

        hf.print_error('Fracture family type is not specified')

    return fracture_type_prefix


def add_distribution_params(fracture_family, params, fracture_type_prefix):
    """Add distribution values from fracture family dictionary
    to the parameter dictionary
    
    Parameters
    -------------
        params: The dfn parameter dictionary
        
        fracture_family: fracture family dictionary for a family
        
        fracture_type_prefix: specifies the type of fractures 'r' for rectangular or 'e' for elliptical
        
    Returns 
    ---------
        params: Populated parameter dictionary
        
    Notes
    -------
        None at the moment
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
        hf.print_error(
            'Exactly one distribution value must be True for a fracture family'
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

    fisher_params = fracture_family['fisher']['value']

    for key in fisher_params.keys():
        if key == 'theta' or key == 'phi':
            if params['orientationOption']['value'] == 0:
                write_value_to_params(params,
                                    key,
                                    fisher_params,
                                    key,
                                    fracture_type_prefix,
                                    value_flag=True)

        if key == 'trend' or key == 'plunge':
            if params['orientationOption']['value'] == 1:
                write_value_to_params(params, 
                                    key, 
                                    fisher_params, 
                                    key, 
                                    fracture_type_prefix, 
                                    value_flag=True)

        if key == 'strike' or key == 'dip':
            if params['orientationOption']['value'] == 2:
                write_value_to_params(params, 
                                    key, 
                                    fisher_params, 
                                    key, 
                                    fracture_type_prefix, 
                                    value_flag=True)

        if key == 'kappa':
            write_value_to_params(params, 
                                key, 
                                fisher_params, 
                                key, 
                                fracture_type_prefix, 
                                value_flag=True)

    return params, distribution_type


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
        params: The dfn parameter dictionary
        
        param_key: the key for the parameter value to be written
        
        fracture_family: fracture family dictionary for a family
        
        fracture_family_key: the key for the parameter that will be transferred 
        from the fracture family dictionary

        fracture_type_prefix: specifies the type of fractures 'r' for rectangular or 'e' for elliptical
        
        value_flag: defaults to False, determines whether dictionary is in order [param][value] (False) or [value][param] (True)        
    Returns 
    ---------
        params: Populated parameter dictionary
        
    Notes
    -------
        None at the moment
    """
    if value_flag == False:
        value = value_dict[value_dict_key]['value']
    else:
        value = value_dict[value_dict_key]

    ### if value is not present an exception can be raised
    if value == None:
        pass
        # hf.print_error(value_dict_key + ' not specified')

    else:
        if params[fracture_type_prefix + param_key]['value'] == None:
            params[fracture_type_prefix + param_key]['value'] = [value]

        else:
            params[fracture_type_prefix + param_key]['value'].append(value)


def reorder_fracture_families(self):
    
    """Reorder the fracture families to pass to backend code
    
    Parameters
    --------------
        DFN(self): the DFN object
    Returns
    --------
        DFN : DFN with reordered fracture attributes
            
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
        
        if current_fracture_family['type']['value']['ellipse'] == True and current_fracture_family[
                'type']['value']['rect'] == False:
            
            ellipse_list.append(current_fracture_family)
            
            ellipse_index.append(i)
    
        elif current_fracture_family['type']['value'][
                'ellipse'] == False and current_fracture_family['type']['value'][
                    'rect'] == True:

            rect_list.append(current_fracture_family)
            
            rect_index.append(i)            
            
    
        else:
            hf.print_error('Fracture family type is not specified')
    
    
    ellipse_index.extend(rect_index)
    final_order = ellipse_index

    ellipse_list.extend(rect_list)
    final_list = ellipse_list
    
    self.fracture_families = final_list
    
    if original_order == final_order:
        print("Fracture Family order was not changed")
    
    else:
        print("Fracture Families have been reordered")
        print("Original order = ", original_order)
        print("Final order = ", final_order)
