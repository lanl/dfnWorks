import re
import sys
import os
from pydfnworks.general.logging import local_print_log

def print_error(error_string):
    """ print an error
    
    Args:
        errString (str): a string describing the error
    """
    error = f"\nError while parsing input\n\n{error_string}\n\nProgram terminated.\n"
    local_print_log(error,'error')


def print_warning(warning_string):
    """ print warning
    
    Args:
        warnStinrg (str): a string with the warning
    """
    warning_string = f"--> Warning while parsing input\n\n{warning_string}\nBe Careful out there\n"
    local_print_log(warning_string,'warning')

def curly_to_list(curly_list):
    """ Converts a list with curly brackets used in input files into a python list.  '{1,2,3}' --> [1,2,3]

    Parameters
    -------------
    	curly_list : string

    Returns
    ----------
    	list

	Notes 
	---------
		None
    """
    return re.sub("{|}", "", curly_list).strip().split(",")


def has_curlys(line, key):
    """ Checks to see that every { has a matching }.

    Parameters
    -------------
    	line : string
    		string read from input file
    	key : string
    		name of key on line

    Returns
    ----------
    	bool : True if okay. 

	Notes 
	---------
		None

    """
    if '{' in line and '}' in line:
        return True
    elif '{' in line or '}' in line:
        print_error(f"Line defining \"{key}\" contains a single curly brace.")
    return False


def check_none(key, value):
    if value == None:
        print_error(
            f"\"{key}\" was not defined. Please define one {key} for each family."
        )


def check_length(key, value, desired_length):

    if len(value) != desired_length:
        print_error(
            f"\"{key}\" has defined {len(value)} value(s) but there is(are) {desired_length} families. Please define one {key} for each family."
        )


def check_values(key, value, min_val=None, max_val=None):

    if type(value) is list:
        for i, val in enumerate(value):
            if min_val is not None:
                if val < min_val:
                    print_error(
                        f"\"{key}\" entry has value {val}, which is less than minimum value of {min_val} "
                    )
            if max_val is not None:
                if val > max_val:
                    print_error(
                        f"\"{key}\" entry has value {val}, which above the maximum value {max_val}."
                    )
    else:
        if min_val is not None:
            if value < min_val:
                print_error(
                    f"\"{key}\" entry has value {value}, which is less than minimum value of {min_val} "
                )
            if max_val is not None:
                if value > max_val:
                    print_error(
                        f"\"{key}\" entry has value {value}, which above the maximum value {max_val}."
                    )


def get_groups(line, key):
    """ extract values between { and } 
    """
    curlyGroup = re.compile('({.*?})')
    groups = re.findall(curlyGroup, line)
    for group in groups:
        line = line.replace(group, '', 1)  ## only delete first occurrence
        value_list = curly_to_list(group)
    return value_list
    if line.strip() != "":
        print_error(f"Unexpected character found while parsing \"{key}\".")


def check_min_max(min_val, max_val, i, dist):
    """ Checks that the minimum parameter for a family is not greater or equal to the maximum parameter.
    """
    if min_val == max_val:
        hf.print_error(
            f"Minimum {min_val} and maximum {max_val} value are equal in {dist} entry number {i+1}"
        )
    if min_val > max_val:
        hf.print_error(
            f"Minimum {min_val} is larger than maximum {max_val} value are equal in {dist} entry number {i+1}"
        )


def check_mean(mean_param, min_param, max_param):
    """ Warns the user if the minimum value of a parameter is greater than the family's mean value, or if the
    maximum value of the parameter is less than the family's mean value.
    """
    for minV, meanV in zip(self.value_of(minParam), self.value_of(meanParam)):
        if minV > meanV:
            self.warning("\"{}\" contains a min value greater than its family's mean value in "\
                   "\"{}\". This could drastically increase computation time due to increased "\
                   "rejection rate of the most common fracture sizes.".format(minParam, meanParam), warningFile)
    for maxV, meanV in zip(self.value_of(maxParam), self.value_of(meanParam)):
        if maxV < meanV:
            self.warning("\"{}\" contains a max value less than its family's mean value in "\
                   "\"{}\". This could drastically increase computation time due to increased "\
                   "rejection rate of the most common fracture sizes.".format(maxParam, meanParam), warningFile)


def check_min_frac_size(params, value):
    """ Corrects the minimum fracture size if necessary, by looking at the values in valList.
    """

    if params['minimum_fracture_size']['value'] == None:
        params['minimum_fracture_size']['value'] = value
    elif value < params['minimum_fracture_size']['value']:
        params['minimum_fracture_size']['value'] = value


def check_path(filename, filepath):
    if filepath:
        if not os.path.isfile(filepath):
            print_error(
                f"{filepath} path is for {filename} not valid. Please check input file"
            )
    else:
        print_error(f"{filename} was not provided.")
