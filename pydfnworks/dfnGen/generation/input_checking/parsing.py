## ====================================================================== ##
##                              Parsing Functions                         ##
## ====================================================================== ##
import pydfnworks.dfnGen.generation.input_checking.helper_functions as hf
from pydfnworks.dfnGen.generation.input_checking.parameter_dictionaries import load_parameters
from pydfnworks.general.logging import local_print_log

def check_for_mandatory_keys(params, found_keys, mandatory):
    """ Checks if all required keywords have been found. Exits program if not.

    Parameters
    --------------
        params : dictionary
            input parameter dictionary

        found_keys : list
            list of keys found in the input file

        mandatory : list
            list of mandatory keys
    Returns
    --------
        None

    Notes
    ---------
        None

    """

    local_print_log("--> Checking for mandatory keywords")
    missing = []
    for key in mandatory:
        if key not in found_keys:
            missing.append(key)

    if missing != []:
        local_print_log("Missing the following mandatory parameters:")
        for key in missing:
            local_print_log(f"{key}\n")
            local_print_log(f"{params[key]['description']}")
        hf.print_error("There are missing parameters.")
    else:
        local_print_log("--> All Mandatory keywords have been found")


def check_for_mandatory_values(params, mandatory):
    """ Checks if all required keywords have a provided value. Exits program if not.

    Parameters
    --------------
        params : dictionary
            input parameter dictionary
        mandatory : list
            list of mandatory keys
    Returns
    --------
        None

    Notes
    ---------
        None
    """

    local_print_log("--> Checking for mandatory values")
    missing = []
    for key in mandatory:
        if params[key]['value'] == None:
            missing.append(key)

    if missing != []:
        local_print_log("Missing values for the following mandatory parameters:")
        for key in missing:
            local_print_log(f"{key}\n")
            local_print_log(f"{params[key]['description']}")
        hf.print_error("")

    local_print_log("--> All mandatory values have been found")


def strip_comments(line, input_iterator):
    """ Returns line without comments or white space.

    Parameters
    --------------
        line : string
            line of text from input file
        input_iterator : iter
            iterator of input file
    Returns
    --------
        line : string
            original line with comments striped

    Notes
    ---------
        None

    """
    if "/*" in line:
        comment = line
        line = line[:line.index(
            "/*")]  ## only process text before '/*' comment
        while "*/" not in comment:
            ## just moves iterator past comment
            comment = next(input_iterator)
    ## only process text before '//' comment
    elif "//" in line:
        line = line[:line.index("//")]

    return line.strip()


def process_line(line, found_keys, params):
    """ Find the key and associated value in a line of the input file. Place values into params dictionary and add keyword into the found_keys list. 

    Parameters
    ------------
        line : string
            line of text from input file. 
        found_keys : list
            list of keys that have been found in the input file so far
        params : dictionary 
            input parameter dictionary
    Returns 
    --------
        None

    Notes
    ---------
        None
    """

    if line.strip != "":
        ## Get key
        key = find_key(line)
        ## Check if key has already been found
        if key in found_keys:
            hf.print_error(f"keyword: {key} has been defined multiple times")
        else:
            found_keys.append(key)

        #Check if key is defined
        if key in params.keys():
            params[key]['value'] = find_val(line, key)
        else:
            hf.print_error(f"keyword: {key} is unknown")


def find_key(line):
    """ Find keyword in line from input file. 

    Parameters
    -------------
        line : string
            line of text from input file. 
    
    Returns
    ---------
        key : string 
            keyword from input file. will be type None if no key is found.   
    """
    return line[:line.index(":")].strip()


def find_val(line, key):
    """ Extract the value for key from line.

    Parameters
    -------------
        line : string
            line of text from input file
        key : string
            current key word
    
    Returns
    -----------
        value : int/float/string/list
            value from file. 
    Notes
    -------
        type None is returned if line is empty.
    """
    line = line[line.index(":") + 1:].strip()
    if line != "":
        if hf.has_curlys(line, key):
            value = hf.get_groups(line, key)
        else:
            value = line

        if value == '' or value == ['']:
            value = None
        return value


def convert_params(params):
    """ Converts all parameters into their assigned type. Exits program is provided type does not match the assigned values. 

    Parameters
    ------------
        params : dictionary 
            dictionary of input parameters from file

    Returns
    ------------
        params : dictionary 
            dictionary of input parameters from file

    Notes
    -------
        None

    """

    for key in params.keys():
        try:
            # work in individual values
            if not params[key]['list']:
                # This checks if a key in not entered, it's just skipped, which is okay for some keys
                if not params[key]['value'] is None:
                    if params[key]['type'] is bool:
                        if params[key]['value'] == '0' or params[key][
                                'value'] == 0:
                            params[key]['value'] = False
                        elif params[key]['value'] == '1' or params[key][
                                'value'] == 1:
                            params[key]['value'] = True
                        else:
                            hf.print_error(
                                f"Error converting {key} value into assigned type bool (0,1). Value found in file was '{params[key]['value']}'"
                            )
                    else:
                        params[key]['value'] = params[key]['type'](
                            params[key]['value'])
            else:
                if params[key]['value'] == '' or params[key]['value'] == None:
                    params[key]['value'] = None
                else:
                    params[key]['value'] = [
                        params[key]['type'](i) for i in params[key]['value']
                    ]
        except:
            hf.print_error(
                f"Error converting {key} value into assigned type {params[key]['type']}. Value found in file was '{params[key]['value']}'"
            )

    return params


def get_layers(params, input_file):
    """ If there are layers, walk back through the file to pick them up.

    Parameters
    ------------
        input_file : string
            input file name

        params : dictionary 
            dictionary of input parameters from file
    Returns
    ------------
        None
        

    Notes
    -------
        None

    """
    flag = False
    j = 0
    key = 'layers'
    values = []
    with open(input_file, "r") as fp:
        for i, line in enumerate(fp.readlines()):
            if "layers:" in line:
                flag = True
                j = 0
            elif flag:
                if hf.has_curlys(line, key):
                    value = hf.get_groups(line, key)
                    values.append([float(value[0]), float(value[1])])
                j += 1
            if j > params["numOfLayers"]["value"]:
                break
    params["layers"]["value"] = values


def get_regions(params, input_file):
    """ If there are regions, walk back through the file to pick them up.

    Parameters
    ------------
        input_file : string
            input file name

        params : dictionary 
            dictionary of input parameters from file
    Returns
    ------------
        None


    Notes
    -------
        None

    """

    flag = False
    j = 0
    key = 'regions'
    values = []
    with open(input_file, "r") as fp:
        for i, line in enumerate(fp.readlines()):
            if "regions:" in line:
                flag = True
                j = 0
            elif flag:
                if hf.has_curlys(line, key):
                    value = hf.get_groups(line, key)
                    values.append([
                        float(value[0]),
                        float(value[1]),
                        float(value[2]),
                        float(value[3]),
                        float(value[4]),
                        float(value[5])
                    ])
                j += 1
            if j > params["numOfRegions"]["value"]:
                break
    params["regions"]["value"] = values


def parse_input(input_file):
    """ Parse each line of the input file and checks if all mandatory parameters have been found.

    Parameters
    ------------
        input_file : input file name

    Returns
    ------------
        params : dictionary 
            dictionary of input parameters from file

    Notes
    -------
        None

    """
    try:
        reader = open(input_file, 'r')
    except:
        hf.print_error(f"Input file path ({input_file} is not valid")

    input_iterator = iter(reader)

    params, mandatory = load_parameters()

    found_keys = []
    for i, line in enumerate(input_iterator):
        line = strip_comments(line, input_iterator)
        if (line != "" and ":" in line):
            process_line(line, found_keys, params)

    check_for_mandatory_keys(params, found_keys, mandatory)
    check_for_mandatory_values(params, mandatory)

    params = convert_params(params)

    # one more pass through to gather layers and regions, could be cleaned up
    if params["numOfLayers"]["value"] > 0:
        get_layers(params, input_file)

    if params["numOfRegions"]["value"] > 0:
        get_regions(params, input_file)

    return params
