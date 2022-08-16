import pydfnworks.dfnGen.generation.input_checking.helper_functions as hf


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
        write_value_to_params(params, 'min', fracture_family, 'radius_min',
                              fracture_type_prefix)
        write_value_to_params(params, 'max', fracture_family, 'radius_max',
                              fracture_type_prefix)

    if distribution_type == 'log_normal':
        write_value_to_params(params, 'LogMin', fracture_family, 'radius_min',
                              fracture_type_prefix)
        write_value_to_params(params, 'LogMax', fracture_family, 'radius_max',
                              fracture_type_prefix)

    if distribution_type == 'exp':
        write_value_to_params(params, 'ExpMin', fracture_family, 'radius_min',
                              fracture_type_prefix)
        write_value_to_params(params, 'ExpMax', fracture_family, 'radius_max',
                              fracture_type_prefix)

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

    ### if value is not present raise error
    if value == None:
        hf.print_error(value_dict_key + ' not specified')

    else:
        if params[fracture_type_prefix + param_key]['value'] == None:
            params[fracture_type_prefix + param_key]['value'] = [value]

        else:
            params[fracture_type_prefix + param_key]['value'].append(value)
