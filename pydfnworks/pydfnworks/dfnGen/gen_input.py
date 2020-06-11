import os
import sys
import shutil
import numpy as np
import scipy.integrate
import re

#pydfnworks modules
from pydfnworks.dfnGen import distributions as distr_module


class input_helper():
    """ Functions to help parse the input file and check input parameters.
        
        Attributes:
            * params (list): list of parameters specified in the input file.
            * minFracSize (float): the minimum fracture size.
    """

    def __init__(self, params, minFracSize):
        self.params = params
        self.minFracSize = minFracSize

    ## ====================================================================== ##
    ##                              Helper Functions                          ##
    ## ====================================================================== ##

    def curly_to_list(self, curlyList):
        """ '{1,2,3}' --> [1,2,3]
        """
        return re.sub("{|}", "", curlyList).strip().split(",")

    def list_to_curly(self, strList):
        """ [1,2,3] --> '{1,2,3}'   for writing output
        """
        curl = re.sub(r'\[', '{', strList)
        curl = re.sub(r'\]', '}', curl)
        curl = re.sub(r"\'", '', curl)
        return curl

    def has_curlys(self, line, key):
        """ Checks to see that every { has a matching }.
        """
        if '{' in line and '}' in line: return True
        elif '{' in line or '}' in line:
            self.error(
                "Line defining \"{}\" contains a single curly brace.".format(
                    key))
        return False

    def value_of(self, key, writing=False):
        """ Use to get key's value in params. writing always false  
        """
        if (not writing) and (len(self.params[key]) > 1):
            self.error(
                "\"{}\" can only correspond to 1 list. {} lists have been defined."
                .format(key, len(self.params[key])))
        #try:
        val = self.params[key][0]
        if val == '' or val == []:
            self.error("\"{}\" does not have a value.".format(key))
        return val
        #except IndexError:
        #    self.error("\"{}\" has not been defined.".format(key)) ## Include assumptions (ie no Angleoption -> degrees?)

    def get_groups(self, line, valList, key):
        """ extract values between { and } 
        """
        curlyGroup = re.compile('({.*?})')
        groups = re.findall(curlyGroup, line)
        for group in groups:
            line = line.replace(group, '', 1)  ## only delete first occurence
            valList.append(self.curly_to_list(group))

        if line.strip() != "":
            self.error(
                "Unexpected character found while parsing \"{}\".".format(key))

    def val_helper(self, line, valList, key):
        """ pulls values from culry brackets 
        """
        if self.has_curlys(line, key):
            self.get_groups(line, valList, key)
        else:
            valList.append(line)

    def error(self, errString):
        """ print an error
        
        Args:
            errString (str): a string describing the error
        """
        error = "\nERROR --- " + errString + "\n----Program terminated while parsing input----\n"
        sys.stderr.write(error)
        sys.exit(1)

    def warning(self, warnString):
        """ print warning
        
        Args:
            warnStinrg (str): a string with the warning
        """
        print("WARNING --- " + warnString)

    def warning(self, warnString, warningFile=''):
        """ print a warning to a file (currently does not work)"""
        #global warningFile
        print("WARNING --- " + warnString)
        #warningFile.write("WARNING --- " + warnString + "\n")

    def is_negative(self, num):
        """"returns True if num is negative, false otherwise
        """
        return True if num < 0 else False

    def check_fam_count(self):
        """Makes sure at least one polygon family has been defined in nFamRect or nFamEll
        OR that there is a user input file for polygons.
        """
        userDefExists = (self.value_of('userEllipsesOnOff') == '1') |\
                   (self.value_of('userRectanglesOnOff') == '1') |\
                   (self.value_of('userRecByCoord') == '1') |\
                   (self.value_of('userEllByCoord') == '1')

        ellipseFams = len(self.value_of('nFamRect'))
        rectFams = len(self.value_of('nFamEll'))

        if ellipseFams + rectFams <= 0 and not userDefExists:
            self.error("Zero polygon families have been defined. Please create at least one family "\
                  "of ellipses/rectagnles, or provide a user-defined-polygon input file path in "\
                  "\"UserEll_Input_File_Path\", \"UserRect_Input_File_Path\", \"UserEll_Input_File_Path\", or "\
                  "\"RectByCoord_Input_File_Path\" and set the corresponding flag to '1'.")

    def scale(self, probList, warningFile):
        """ scales list of probabilities (famProb) that doesn't add up to 1
        ie [.2, .2, .4] --> [0.25, 0.25, 0.5] 
        """
        total = sum(probList)
        scaled = [float("{:.6}".format(x / total)) for x in probList]
        self.warning("'famProb' probabilities did not add to 1 and have been scaled accordingly "\
            "for their current sum, {:.6}. Scaled {} to {}".format(total, probList, scaled), warningFile)
        return [x / total for x in probList]

    def zero_in_std_devs(self, valList):
        """ returns True is there is a zero in valList of standard deviations
        """
        for val in valList:
            if float(val) == 0: return True

    def check_min_max(self, minParam, maxParam, shape):
        """ Checks that the minimum parameter for a family is not greater or equal to the maximum parameter.
        """
        for minV, maxV in zip(self.value_of(minParam),
                              self.value_of(maxParam)):
            if minV == maxV:
                self.error("\"{}\" and \"{}\" contain equal values for the same {} family. "\
                      "If {} and {} were intended to be the same, use the constant distribution "\
                      "(4) instead.".format(minParam, maxParam, shape, minParam, maxParam))
            if minV > maxV:
                self.error(
                    "\"{}\" is greater than \"{}\" in a(n) {} family.".format(
                        minParam, maxParam, shape))
                sys.exit(1)

    def check_mean(self, minParam, maxParam, meanParam, warningFile=''):
        """ Warns the user if the minimum value of a parameter is greater than the family's mean value, or if the
        maximum value of the parameter is less than the family's mean value.
        """
        for minV, meanV in zip(self.value_of(minParam),
                               self.value_of(meanParam)):
            if minV > meanV:
                self.warning("\"{}\" contains a min value greater than its family's mean value in "\
                       "\"{}\". This could drastically increase computation time due to increased "\
                       "rejection rate of the most common fracture sizes.".format(minParam, meanParam), warningFile)
        for maxV, meanV in zip(self.value_of(maxParam),
                               self.value_of(meanParam)):
            if maxV < meanV:
                self.warning("\"{}\" contains a max value less than its family's mean value in "\
                       "\"{}\". This could drastically increase computation time due to increased "\
                       "rejection rate of the most common fracture sizes.".format(maxParam, meanParam), warningFile)

    def check_min_frac_size(self, valList):
        """ Corrects the minimum fracture size if necessary, by looking at the values in valList.
        """
        global minFracSize
        for val in valList:
            if minFracSize == None:
                minFracSize = val
            elif val < minFracSize: 
                minFracSize = val

    ## ====================================================================== ##
    ##                              Parsing Functions                         ##
    ## ====================================================================== ##
    def extract_parameters(self, line, inputIterator):
        """Returns line without comments or white space.
        """
        if "/*" in line:
            comment = line
            line = line[:line.index(
                "/*")]  ## only process text before '/*' comment
            while "*/" not in comment:
                comment = next(
                    inputIterator)  ## just moves iterator past comment

        elif "//" in line:
            line = line[:line.index(
                "//")]  ## only process text before '//' comment

        return line.strip()

    def find_val(self, line, key, inputIterator, unfoundKeys, warningFile):
        """ Extract the value for key from line. 
        """
        valList = []
        line = line[line.index(":") + 1:].strip()
        if line != "": self.val_helper(line, valList, key)

        line = self.extract_parameters(next(inputIterator), inputIterator)
        while ':' not in line:
            line = line.strip()
            if line != "":
                self.val_helper(line, valList, key)
            try:
                line = self.extract_parameters(next(inputIterator),
                                               inputIterator)
            except StopIteration:
                break

        if valList == [] and key in mandatory:
            self.error(
                "\"{}\" is a mandatory parameter and must be defined.".format(
                    key))
        if key is not None:
            self.params[key] = valList if valList != [] else [
                ""
            ]  ## allows nothing to be entered for unused params
        if line != "":
            self.process_line(line, unfoundKeys, inputIterator, warningFile)

    def find_key(self, line, unfoundKeys, warningFile):
        """ Input: line containing a paramter (key) preceding a ":" 
           
        Returns: 
            * key -- if it has not been defined yet and is valid
            * None -- if key does not exist
            * exits -- if the key has already been defined to prevent duplicate confusion        
        """
        key = line[:line.index(":")].strip()
        if key in unfoundKeys:
            unfoundKeys.remove(key)
            return key
        try:
            self.params[key]
            self.error("\"{}\" has been defined more than once.".format(key))
        except KeyError:
            self.warning(
                "\"" + key + "\" is not one of the valid parameter names.",
                warningFile)

    def process_line(self, line, unfoundKeys, inputIterator, warningFile):
        """ Find the key in a line, and the value for that key.
        """
        if line.strip != "":
            key = self.find_key(line, unfoundKeys, warningFile)
            if key != None:
                self.find_val(line, key, inputIterator, unfoundKeys,
                              warningFile)

    ## ====================================================================== ##
    ##                              Verification                              ##
    ## ====================================================================== ##
    ## Note: Always provide EITHER a key (ie "stopCondition")
    ##         OR inList = True/False (boolean indicating val being checked is inside a list)

    ## Input: value - value being checked
    ##        key - parameter the value belongs to
    ##        inList - (Optional)
    def verify_flag(self, value, key="", inList=False):
        """ Verify that value is either a 0 or a 1.
        """
        if value is '0' or value is '1':
            return int(value)
        elif inList:
            return None
        else:
            self.error("\"{}\" must be either '0' or '1'".format(key))

    def verify_float(self, value, key="", inList=False, noNeg=False):
        """ Verify that value is a positive float.
        """
        if type(value) is list:
            self.error(
                "\"{}\" contains curly braces {{}} but should not be a list value."
                .format(key))
        try:
            if noNeg and float(value) < 0:
                self.error("\"{}\" cannot be a negative number.".format(key))
            return float(value)
        except ValueError:
            if inList: return None
            else:
                self.error("\"{}\" contains an unexpected character. Must be a single "\
                      "floating point value (0.5, 1.6, 4.0, etc.)".format(key))

    def verify_int(self, value, key="", inList=False, noNeg=False):
        """ Verify that value is a positive integer.
        """
        if type(value) is list:
            self.error(
                "\"{}\" contains curly braces {{}} but should not be a list value."
                .format(key))
        try:
            if noNeg and int(re.sub(r'\.0*$', '', value)) < 0:
                self.error("\"{}\" cannot be a negative number.".format(key))
            return int(re.sub(r'\.0*$', '',
                              value))  ## regex for removing .0* (ie 4.00 -> 4)
        except ValueError:
            if inList: return None
            else:
                self.error("\"{}\" contains an unexpected character. Must be a single "\
                      "integer value (0,1,2,3,etc.)".format(key))

    def verify_list(self,
                    valList,
                    key,
                    verificationFn,
                    desiredLength,
                    noZeros=False,
                    noNegs=False):
        """verifies input list that come in format {0, 1, 2, 3}
       
        Input: 
            * valList - list of values (flags, floats, or ints) corresponding to a parameter
            * key - the name of the parameter whose list is being verified
            * verificationFn - (either verifyflag, verifyfloat or verifyint) checks each list element 
            * desiredLength - how many elements are supposed to be in the list
            * noZeros - (optional) True for lists than cannot contain 0's, false if 0's are ok  
            * noNegs - (optional) True for lists than cannot contain negative numbers, false otherwise
        Output:
            * returns negative value of list length to indicate incorrect length and provide meaningful error message
            * prints error and exits if a value of the wrong type is found in the list
            * returns None if successful"""

        if valList == ['']: return 0
        if type(valList) is not list:
            self.error(
                "\"{}\"'s value must be a list encolsed in curly brackets {{}}."
                .format(key))
        if desiredLength != 0 and int(len(valList)) != int(desiredLength):
            print('list desired length is ', desiredLength, 'but valList is ',
                  valList, 'with length ', len(valList))
            return -len(valList)
        for i, value in enumerate(valList):
            value = value.strip()
            verifiedVal = verificationFn(value, inList=True)
            if verifiedVal == None:
                listType = re.sub(
                    'integer', 'int',
                    re.sub(
                        r'verify', '',
                        verificationFn.__name__))  ## 'verifyint' --> 'integer'
                self.error("\"{}\" must be a list of {}s {}. non-{} found in "\
                      "list".format(key, listType, examples[listType], listType))
            if noZeros and verifiedVal == 0:
                self.error(
                    "\"{}\" list cannot contain any zeroes.".format(key))
            if noNegs and self.is_negative(float(verifiedVal)):
                self.error(
                    "\"{}\" list cannot contain any negative values.".format(
                        key))
            valList[i] = verifiedVal

    ## def verifynumvalsis(length, key):f
    ##  if len(self.params[key]) != length:
    ##     self.error("error: ", "\"" + param + "\"", "should have", length, "value(s) but", len(self.params[key]), "are defined.")
    ##    sys.exit()


def check_input(self, input_file='', output_file=''):
    """Check input file for DFNGen to make sure all necessary parameters are defined

     Input Format Requirements:  
        * Each parameter must be defined on its own line (separate by newline)
        * A parameter (key) MUST be separated from its value by a colon ':' (ie. --> key: value)
        * Values may also be placed on lines after the 'key'
        * Comment Format:  On a line containing  // or / ``*``, nothing after ``*`` / or // will be processed  but text before a comment will be processed 
    
    Parameters
    ----------
        input_file : string
            name of dfnGen input file
        output_file : string 
            Name of stripped down input file for DFNGen (input_file_clean.dat) 

    Returns
    -------
        None

    Notes
    -----
    There are warnings and errors raised in this function. Warning will let you continue while errors will stop the run. Continue past warnings are your own risk.     
    """
    global params
    ## BIG TODO s -----
    ## ==== Problems ==== ##
    ## 11. Multiple keys on one line
    ## 15. check # values (famprob: {.5,.5} {.3, .3., .4})
    params = {
        'esd': [],
        'insertUserRectanglesFirst': [],
        'keepOnlyLargestCluster': [],
        'rmin': [],
        'rAngleOption': [],
        'boundaryFaces': [],
        'userRectanglesOnOff': [],
        'printRejectReasons': [],
        'numOfLayers': [],
        'RectByCoord_Input_File_Path': [],
        'eLogMean': [],
        'rExpMin': [],
        'lengthCorrelatedAperture': [],
        'ebetaDistribution': [],
        'tripleIntersections': [],
        'layers': [],
        'stdAperture': [],
        'ealpha': [],
        'constantPermeability': [],
        'rLogMax': [],
        'rLogMean': [],
        'nFamRect': [],
        'etheta': [],
        'eLogMax': [],
        'rphi': [],
        'outputAllRadii': [],
        'r_p32Targets': [],
        'permOption': [],
        'userEllByCoord': [],
        'userRecByCoord': [],
        'userEllipsesOnOff': [],
        'UserEll_Input_File_Path': [],
        'rExpMean': [],
        'rbetaDistribution': [],
        'aperture': [],
        'emax': [],
        'eExpMean': [],
        'e_p32Targets': [],
        'eLayer': [],
        'domainSizeIncrease': [],
        'h': [],
        'outputFinalRadiiPerFamily': [],
        'rbeta': [],
        'rLogMin': [],
        'edistr': [],
        'domainSize': [],
        'eExpMin': [],
        'ekappa': [],
        'rLayer': [],
        'seed': [],
        'constantAperture': [],
        'stopCondition': [],
        'enumPoints': [],
        'meanAperture': [],
        'eLogMin': [],
        'easpect': [],
        'rtheta': [],
        'rdistr': [],
        'UserRect_Input_File_Path': [],
        'EllByCoord_Input_File_Path': [],
        'rconst': [],
        'rExpMax': [],
        'ignoreBoundaryFaces': [],
        'visualizationMode': [],
        'outputAcceptedRadiiPerFamily': [],
        'apertureFromTransmissivity': [],
        'rsd': [],
        'ebeta': [],
        'nFamEll': [],
        'econst': [],
        'raspect': [],
        'eAngleOption': [],
        'emin': [],
        'ephi': [],
        'rmax': [],
        'famProb': [],
        'disableFram': [],
        'ralpha': [],
        'nPoly': [],
        'rejectsPerFracture': [],
        'rkappa': [],
        'eExpMax': [],
        'forceLargeFractures': [],
        'radiiListIncrease': [],
        'removeFracturesLessThan': []
    }
    global unfoundKeys

    unfoundKeys = {
        'stopCondition', 'nPoly', 'outputAllRadii', 'outputAllRadii',
        'outputFinalRadiiPerFamily', 'outputAcceptedRadiiPerFamily',
        'domainSize', 'numOfLayers', 'layers', 'h', 'tripleIntersections',
        'printRejectReasons', 'disableFram', 'visualizationMode', 'seed',
        'domainSizeIncrease', 'keepOnlyLargestCluster', 'ignoreBoundaryFaces',
        'boundaryFaces', 'rejectsPerFracture', 'famProb',
        'insertUserRectanglesFirst', 'nFamEll', 'eLayer', 'edistr',
        'ebetaDistribution', 'e_p32Targets', 'easpect', 'enumPoints',
        'eAngleOption', 'etheta', 'ephi', 'ebeta', 'ekappa', 'eLogMean', 'esd',
        'eLogMin', 'eLogMax', 'eExpMean', 'eExpMin', 'eExpMax', 'econst',
        'emin', 'emax', 'ealpha', 'nFamRect', 'rLayer', 'rdistr',
        'rbetaDistribution', 'r_p32Targets', 'raspect', 'rAngleOption',
        'rtheta', 'rphi', 'rbeta', 'rkappa', 'rLogMean', 'rsd', 'rLogMin',
        'rLogMax', 'rmin', 'rmax', 'ralpha', 'rExpMean', 'rExpMin', 'rExpMax',
        'rconst', 'userEllipsesOnOff', 'UserEll_Input_File_Path',
        'userRectanglesOnOff', 'UserRect_Input_File_Path',
        'EllByCoord_Input_File_Path', 'userEllByCoord', 'userRecByCoord',
        'RectByCoord_Input_File_Path', 'aperture', 'meanAperture',
        'stdAperture', 'apertureFromTransmissivity', 'constantAperture',
        'lengthCorrelatedAperture', 'permOption', 'constantPermeability',
        'forceLargeFractures', 'radiiListIncrease', 'removeFracturesLessThan'
    }

    global mandatory
    mandatory = {
        'stopCondition', 'domainSize', 'numOfLayers', 'outputAllRadii',
        'outputFinalRadiiPerFamily', 'outputAcceptedRadiiPerFamily',
        'tripleIntersections', 'printRejectReasons', 'disableFram',
        'visualizationMode', 'seed', 'domainSizeIncrease',
        'keepOnlyLargestCluster', 'ignoreBoundaryFaces', 'rejectsPerFracture',
        'famProb', 'insertUserRectanglesFirst', 'nFamEll', 'nFamRect',
        'userEllipsesOnOff', 'userRectanglesOnOff', 'userEllByCoord',
        'userRecByCoord', 'aperture', 'permOption', 'forceLargeFractures',
        'radiiListIncrease', 'removeFracturesLessThan'
    }

    global noDependancyFlags
    noDependancyFlags = [
        'outputAllRadii', 'outputFinalRadiiPerFamily',
        'outputAcceptedRadiiPerFamily', 'tripleIntersections',
        'printRejectReasons', 'visualizationMode', 'keepOnlyLargestCluster',
        'insertUserRectanglesFirst', 'forceLargeFractures'
    ]

    examples = {
        "Flag": "(0 or 1)",
        "Float": "(0.5, 1.6, 4.0, etc.)",
        "Int": "(0,1,2,3,etc.)"
    }

    global ellipseFams
    ellipseFams = 0
    global rectFams
    rectFams = 0
    global numLayers
    numLayers = 0
    global minFracSize
    minFracSize = None

    ## WARNING: Index[0] for the following lists should never be used. See edistr() and rdistr() for clarity.
    global numEdistribs
    numEdistribs = [
        -1, 0, 0, 0, 0
    ]  ## [0 = no-op, 1 = # log-normal's, 2 = # Truncated Power Law's, 3 = # Exp's, # constant's]
    global numRdistribs
    numRdistribs = [
        -1, 0, 0, 0, 0
    ]  ## [0 = no-op, 1 = # log-normal's, 2 = # Truncated Power Law's, 3 = # Exp's, # constant's]
    global warningFile
    warningFile = open("warningFileDFNGen.txt", 'w')
    global jobname
    jobname = self.jobname

    input_helper_methods = input_helper(params, minFracSize)

    ## ===================================================================== ##
    ##                      Mandatory Parameters                             ##
    ## ===================================================================== ##

    ## Each of these should be called in the order they are defined in to accomadate for dependecies
    def n_fam_ell():
        """ Check the number of families of ellipses."""
        global ellipseFams
        ## input_helper_methods.verifyNumValsIs(1, 'nFamEll')
        ellipseFams = input_helper_methods.verify_int(
            input_helper_methods.value_of('nFamEll', params),
            'nFamEll',
            noNeg=True)
        if ellipseFams == 0:
            input_helper_methods.warning(
                "You have set the number of ellipse families to 0, outside user-defined ellipses, no ellipses will be generated.",
                params)

    def n_fam_rect():
        """ Check the number of families of rectangles."""
        global rectFams
        ## input_helper_methods.verifyNumValsIs(1, 'nFamRect')
        rectFams = input_helper_methods.verify_int(
            input_helper_methods.value_of('nFamRect', params),
            'nFamRect',
            noNeg=True)
        if rectFams == 0:
            input_helper_methods.warning(
                "You have set the number of rectangle families to 0, outside user-defined rectangles, no rectangles will be generated.",
                params)

    def stop_condition():
        """ Check the number of polygons if stopCondition is set to 1, else check the p32 target parameters."""
        ## input_helper_methods.verifyNumValsIs(1, 'stopCondition')
        if input_helper_methods.verify_flag(
                input_helper_methods.value_of('stopCondition', params),
                'stopCondition') == 0:
            n_poly()
        else:
            p32_targets()

    def check_no_dep_flags():
        """ Check for dependency flags."""
        for flagName in noDependancyFlags:
            input_helper_methods.verify_flag(
                input_helper_methods.value_of(flagName, params), flagName)

    def domain_size():
        """ Check that domainSize has 3 non-zero values to define the 
        size of each dimension (x,y,z) of the domain.
        """
        errResult = input_helper_methods.verify_list(
            input_helper_methods.value_of('domainSize', params),
            'domainSize',
            input_helper_methods.verify_float,
            desiredLength=3,
            noZeros=True,
            noNegs=True)
        if errResult != None:
            input_helper_methods.error("\"domainSize\" has defined {} value(s) but there must be 3 non-zero "\
                  "values to represent x, y, and z dimensions".format(-errResult))

    def domain_size_increase():
        """ Check the domain size increase parameters.
        """
        errResult = input_helper_methods.verify_list(
            input_helper_methods.value_of('domainSizeIncrease', params),
            domain_size_increase,
            input_helper_methods.verify_float,
            desiredLength=3)
        if errResult != None:
            input_helper_methods.error("\"domainSizeIncrease\" has defined {} value(s) but there must be 3 non-zero "\
                  "values to represent extensions in the x, y, and z dimensions".format(-errResult))

        for i, val in enumerate(
                input_helper_methods.value_of('domainSizeIncrease', params)):
            if val >= input_helper_methods.value_of('domainSize',
                                                    params)[i] / 2:
                input_helper_methods.error(
                    "\"domainSizeIncrease\" contains {} which is more than half of the domain's "
                    "range in that dimension. Cannot change the domain's size by more than half of "
                    "that dimension's value defined in \"domainSize\". This risks collapsing or "
                    "doubling the domain.".format(val))

    def num_of_layers():
        """ Check the number of layers parameter."""
        global numLayers
        numLayers = input_helper_methods.verify_int(
            input_helper_methods.value_of('numOfLayers', params),
            'numOfLayers',
            noNeg=True)
        if numLayers > 0:
            if numLayers != len(params['layers']):
                input_helper_methods.error("\"layers\" has defined {} layers but \"numLayers\" was defined to "\
                      "be {}.".format(len(params['layers']), numLayers))
            else:
                layers()

    def layers():
        """ Check the layer parameters provided. """
        halfZdomain = params['domainSize'][0][
            2] / 2.0  ## -index[2] becaue domainSize = [x,y,z]
        ## -center of z-domain at z = 0 so
        ##  whole Zdomain is -zDomainSize to +zDomainSize
        for i, layer in enumerate(params['layers']):
            errResult = input_helper_methods.verify_list(
                layer,
                "layer #{}".format(i + 1),
                input_helper_methods.verify_float,
                desiredLength=2)
            if errResult != None:
                input_helper_methods.error("\"layers\" has defined layer #{} to have {} element(s) but each layer must "\
                      "have 2 elements, which define its upper and lower bounds".format(i+1, -errResult))
            if params['layers'].count(layer) > 1:
                input_helper_methods.error(
                    "\"layers\" has defined the same layer more than once.")
            minZ = layer[0]
            maxZ = layer[1]
            if minZ <= -halfZdomain and maxZ <= -halfZdomain:
                input_helper_methods.error("\"layers\" has defined layer #{} to have both upper and lower bounds completely "\
                      "below the domain's z-dimensional range ({} to {}). At least one boundary must be within "\
                      "the domain's range. The domain's range is half of 3rd value in \"domainSize\" "\
                      "(z-dimension) in both positive and negative directions.".format(i+1, -halfZdomain, halfZdomain))
            if minZ >= halfZdomain and maxZ >= halfZdomain:
                input_helper_methods.error("\"layers\" has defined layer #{} to have both upper and lower bounds completely "\
                      "above the domain's z-dimensional range ({} to {}). At least one boundary must be within "\
                      "the domain's range. The domain's range is half of 3rd value in \"domainSize\" "\
                      "(z-dimension) in both positive and negative directions.".format(i+1, -halfZdomain, halfZdomain))

    def disable_fram():
        """ Verify the flag that indicates whether if FRAM is disabled.
            If FRAM is enabled, verify the value of h is valid.  
        """
        if input_helper_methods.verify_flag(
                input_helper_methods.value_of('disableFram', params),
                'disableFram') == 0:
            h()
        else:
            input_helper_methods.warning("FRAM (feature rejection algorithm for meshing) is disabled. This means that"\
                                         "dfnWorks will only run through fracture network generation (the code will stop before meshing)."\
                                         "To run the full code change the disableFram option to 1")

    def seed():
        """ Check the value of the seed used for pseudorandom number generation.
        """
        val = input_helper_methods.verify_int(input_helper_methods.value_of(
            'seed', params),
                                              'seed',
                                              noNeg=True)
        if val == 0:
            input_helper_methods.warning("\"seed\" has been set to 0. Random generator will use current wall "\
                "time so distribution's random selection will not be as repeatable. "\
                "Use an integer greater than 0 for better repeatability.", params)
        params['seed'][0] = val

    def ignore_boundary_faces():
        """ Check the value fo the ignoreBoundaryFaces flag.
        """
        if input_helper_methods.verify_flag(
                input_helper_methods.value_of('ignoreBoundaryFaces', params),
                'ignoreBoundaryFaces') == 0:
            boundary_faces()

    def rejects_per_fracture():
        """ Check the value of the rejectsPerFracture int. 
        """
        val = input_helper_methods.verify_int(input_helper_methods.value_of(
            'rejectsPerFracture', params),
                                              'rejectsPerFracture',
                                              noNeg=True)
        if val == 0:
            val = 1
            input_helper_methods.warning(
                "changing \"rejectsPerFracture\" from 0 to 1. Can't ensure 0 rejections.",
                params)

        params['rejectsPerFracture'][0] = val

    def fam_prob():
        """ Check the list of family probabilites (the list of  probabilities that a fracture is in each family).
        """

        errResult = input_helper_methods.verify_list(
            input_helper_methods.value_of('famProb', params),
            'famProb',
            input_helper_methods.verify_float,
            desiredLength=ellipseFams + rectFams,
            noZeros=True,
            noNegs=True)

        if errResult != None:
            print(errResult)
            input_helper_methods.error("\"famProb\" must have {} (nFamEll + nFamRect) non-zero elements,"\
                  "one for each family of ellipses and rectangles. {} probabiliies have "\
                  "been defined.".format(ellipseFams + rectFams, -errResult))

        probList = [
            float(x) for x in input_helper_methods.value_of('famProb', params)
        ]
        if sum(probList) != 1:
            input_helper_methods.scale(probList, warningFile)

    def user_defined():
        """ Check the parameters for user-defined rectangles and ellipses.
        """
        userEs = "userEllipsesOnOff"
        userRs = "userRectanglesOnOff"
        recByCoord = "userRecByCoord"
        ellByCoord = "userEllByCoord"
        ePath = "UserEll_Input_File_Path"
        rPath = "UserRect_Input_File_Path"
        coordPath = "RectByCoord_Input_File_Path"
        ecoordPath = "EllByCoord_Input_File_Path"
        invalid = "\"{}\" is not a valid path."

        if input_helper_methods.verify_flag(
                input_helper_methods.value_of(ellByCoord, params),
                ellByCoord) == 1:
            if not os.path.isfile(
                    input_helper_methods.value_of(ecoordPath, params)):
                print('THIS PATH IS NOT A VALID FILE PATH: ',
                      input_helper_methods.value_of(ecoordPath, params))
                input_helper_methods.error(invalid.format(ecoordPath))
            else:
                shutil.copy(input_helper_methods.value_of(ecoordPath, params),
                            self.jobname)

        if input_helper_methods.verify_flag(
                input_helper_methods.value_of(userEs, params), userEs) == 1:
            if not os.path.isfile(input_helper_methods.value_of(ePath,
                                                                params)):
                print('THIS PATH IS NOT A VALID FILE PATH: ',
                      input_helper_methods.value_of(ePath, params))
                input_helper_methods.error(invalid.format(ePath))
            else:
                shutil.copy(input_helper_methods.value_of(ePath, params),
                            self.jobname)

        if input_helper_methods.verify_flag(
                input_helper_methods.value_of(userRs, params), userRs) == 1:
            if not os.path.isfile(input_helper_methods.value_of(rPath,
                                                                params)):
                print('THIS PATH IS NOT A VALID FILE PATH: ',
                      input_helper_methods.value_of(rPath, params))
                input_helper_methods.error(invalid.format(rPath))
            else:
                shutil.copy(input_helper_methods.value_of(rPath, params),
                            self.jobname)

        if input_helper_methods.verify_flag(
                input_helper_methods.value_of(recByCoord, params),
                recByCoord) == 1:
            if not os.path.isfile(
                    input_helper_methods.value_of(coordPath, params)):
                print('THIS PATH IS NOT A VALID FILE PATH: ',
                      input_helper_methods.value_of(coordPath, params))
                input_helper_methods.error(invalid.format(coordPath))
            else:
                shutil.copy(input_helper_methods.value_of(coordPath, params),
                            self.jobname)

    def aperture():
        """ Verify the int value used for aperture.
        """
        apOption = input_helper_methods.verify_int(
            input_helper_methods.value_of('aperture', params), 'aperture')

        if apOption == 1:
            if input_helper_methods.verify_float(input_helper_methods.value_of(
                    'meanAperture', params),
                                                 'meanAperture',
                                                 noNeg=True) == 0:
                input_helper_methods.error("\"meanAperture\" cannot be 0.")
            if input_helper_methods.verify_float(input_helper_methods.value_of(
                    'stdAperture', params),
                                                 'stdAperture',
                                                 noNeg=True) == 0:
                input_helper_methods.error("\"stdAperture\" cannot be 0. If you wish to have a standard deviation "\
                      "of 0, use a constant aperture instead.")

        elif apOption == 2:
            input_helper_methods.verify_list(input_helper_methods.value_of(
                'apertureFromTransmissivity', params),
                                             'apertureFromTransmissivity',
                                             input_helper_methods.verify_float,
                                             desiredLength=2,
                                             noNegs=True)
            if input_helper_methods.value_of('apertureFromTransmissivity',
                                             params)[0] == 0:
                input_helper_methods.error(
                    "\"apertureFromTransmissivity\"'s first value cannot be 0."
                )
            if input_helper_methods.value_of('apertureFromTransmissivity',
                                             params)[1] == 0:
                input_helper_methods.warning(
                    "\"apertureFromTransmissivity\"'s second value is 0, which will result in a constant aperature.",
                    params)

        elif apOption == 3:
            if input_helper_methods.verify_float(input_helper_methods.value_of(
                    'constantAperture', params),
                                                 'constantAperture',
                                                 noNeg=True) == 0:

                params['constantAperture'][0] = 1e-25
                input_helper_methods.warning("\"constantAperture\" was set to 0 and has been changed "\
                      "to 1e-25 so fractures have non-zero thickness.", params)

        elif apOption == 4:
            input_helper_methods.verify_list(input_helper_methods.value_of(
                'lengthCorrelatedAperture', params),
                                             'lengthCorrelatedAperture',
                                             input_helper_methods.verify_float,
                                             desiredLength=2,
                                             noNegs=True)
            if input_helper_methods.value_of('lengthCorrelatedAperture',
                                             params)[0] == 0:
                input_helper_methods.error(
                    "\"lengthCorrelatedAperture\"'s first value cannot be 0.")
            if input_helper_methods.value_of('lengthCorrelatedAperture',
                                             params)[1] == 0:
                input_helper_methods.warning(
                    "\"lengthCorrelatedAperture\"'s second value is 0, which will result in a constant aperature.",
                    params)

        else:
            input_helper_methods.error("\"aperture\" must only be option 1 (log-normal), 2 (from transmissivity), "\
                  "3 (constant), or 4 (length correlated).")

    def permeability():
        """Verify the float used for permeability, if permOption is set to 1"""
        if input_helper_methods.verify_flag(
                input_helper_methods.value_of('permOption'),
                'permOption') == 1:
            if input_helper_methods.verify_float(
                    input_helper_methods.value_of('constantPermeability',
                                                  params),
                    'constantPermeability') == 0:
                params['constantPermeability'][0] = 1e-25
                input_helper_methods.warning("\"constantPermeability\" was set to 0 and has been changed "\
                      "to 1e-25 so fractures have non-zero permeability.", params)

    ## ========================================================================= ##
    ##                      Non-Mandatory Parameters                             ##
    ## ========================================================================= ##

    def n_poly():
        """Verify the number of polygons integer."""
        val = input_helper_methods.verify_int(input_helper_methods.value_of(
            'nPoly', params),
                                              'nPoly',
                                              noNeg=True)
        if val == 0: input_helper_methods.error("\"nPoly\" cannot be zero.")
        params['nPoly'][0] = val

    def p32_targets():
        """Verify the p32 target parameters for ellipses and parameters."""
        global ellipseFams, rectFams
        errResult = None if (ellipseFams == 0) else input_helper_methods.verify_list(input_helper_methods.value_of('e_p32Targets', params), 'e_p32Targets', \
                                  input_helper_methods.verify_float, desiredLength =  ellipseFams, noNegs=True, noZeros=True)
        if errResult != None:
            input_helper_methods.error("\"e_p32Targets\" has defined {} p32 values but there is(are) {} ellipse family(ies). "\
                  "Need one p32 value per ellipse family.".format(-errResult, ellipseFams))

        errResult = None if (rectFams == 0) else input_helper_methods.verify_list(input_helper_methods.value_of('r_p32Targets', params), "r_p32Targets", \
                                input_helper_methods.verify_float, desiredLength =  rectFams, noNegs=True, noZeros=True)
        if errResult != None:
            input_helper_methods.error("\"r_p32Targets\" has defined {} p32 value(s) but there is(are) {} rectangle "\
                  "family(ies). Need one p32 value per rectangle family)".format(-errResult, rectFams))

    def f(theta, t, a, b):
        """Differential Equation Angle Theta as a function of arc length, see Hyman et al. 2014, SIAM J. Sci. Compu
            Equation 3.3"""
        return 1.0 / np.sqrt((a * np.sin(theta))**2 + (b * np.cos(theta)**2))

    def h_shape_check(aspect, minRadius, num_points=4):
        """ Check that the arc length discretized ellipse is greater than 3*h """
        # Major and Minor Axis of Ellipse
        ## aspect = 1.0 ## param
        r = minRadius

        ## TODO check > 3h
        a = aspect
        b = 1.0

        # approximation of total arclength
        c = np.pi * (a + b) * (1.0 + (3.0 * ((a - b) / (a + b))**2) /
                               (10. + np.sqrt(4. - 3. * ((a - b) /
                                                         (a + b))**2)))

        #number of points
        n = num_points
        # expected arclength
        ds = c / n

        # array of steps
        steps = np.linspace(0, c, n + 1)
        # Numerically integrate arclength ODE
        theta = scipy.integrate.odeint(f, 0, steps, args=(a, b), rtol=10**-10)

        # Convert theta to x and y
        x = a * r * np.cos(theta)
        y = b * r * np.sin(theta)

        # Check Euclidean Distance between consecutive points
        h_min = 99999999999
        for i in range(1, n):
            for j in range(i, n):
                if (i != j):
                    h_current = np.sqrt((x[i] - x[j])**2 + (y[i] - y[j])**2)
                    if (h_current < h_min):
                        h_min = h_current

        return h_min

    def compare_pts_v_sh(prefix, hval):
        """ Check that the rectangles and ellipses generated will not involve features with length less than 3*h value used in FRAM. 
        """
        shape = "ellipse" if prefix == 'e' else "rectangle"
        aspectList = params[prefix + "aspect"][0]
        numPointsList = None

        if shape == "ellipse":
            numPointsList = params['enumPoints'][0]

        ## indicies for each list as we check for ellipse generating features less than h
        numLog = 0
        numTPL = 0
        numEXP = 0
        numConst = 0
        numAspect = 0

        for distrib in params[prefix + 'distr'][0]:
            if distrib in [1, 2, 3, 4]:
                if distrib == 1:
                    minRad = params[prefix + 'LogMin'][0][numLog]
                    numLog += 1
                elif distrib == 2:
                    minRad = params[prefix + 'min'][0][numTPL]
                    numTPL += 1
                elif distrib == 3:
                    minRad = params[prefix + 'ExpMin'][0][numEXP]
                    numEXP += 1
                elif distrib == 4:
                    minRad = params[prefix + 'const'][0][numConst]
                    numConst += 1
                if shape == "ellipse":
                    hmin = h_shape_check(float(aspectList[numAspect]),
                                         float(minRad),
                                         int(numPointsList[numAspect]))
                else:
                    hmin = h_shape_check(
                        float(aspectList[numAspect]), float(minRad)
                    )  ## dont need numPoints for rectangle, default 4

                if hmin < (3 * hval):
                    input_helper_methods.error(shape + " family #{} has defined a shape with features too small for meshing. Increase the aspect "\
                             "ratio or minimum radius so that no 2 points of the polygon create a line of length less "\
                             "than 3h".format(numAspect+1))

                numAspect += 1  ## this counts the family number

    def h():
        """ Check the float value provided for h to be used in FRAM (the feautre rejection algorithm for meshing.
        """
        global minFracSize

        val = input_helper_methods.verify_float(input_helper_methods.value_of(
            'h', params),'h',noNeg=True)

        if val == 0: input_helper_methods.error("\"h\" cannot be 0.")
        if minFracSize is None:
            minFracSize = 1
        if val < minFracSize / 1000.0 and ellipseFams + rectFams > 0:  ####### NOTE ----- future developers TODO, delete the
            ## "and ellipseFams + rectFams > 0" once you are also
            ## checking the userInput Files for minimums that could be
            ## "minFracSize".  "minFracSize" is initialized to 99999999 so if no
            ## ellipse/rect fams are defined and the only polygons come from user
            ## Input, the warning message says the min Frac size is 99999999
            ## since it never gets reset by one of the distribution minima.
            input_helper_methods.warning("\"h\" (length scale) is smaller than one 1000th of the minimum "\
                  "fracture size ({}). The generated mesh will be extremely fine and will likely be "\
                  "computationally exhausting to create. Computation may take longer than usual.".format(minFracSize))
        if val > minFracSize / 10.0:
            input_helper_methods.warning("\"h\" (length scale) is greater than one 10th of the minimum "\
                  "fracture size ({}). The generated mesh will be very coarse and there will likely "\
                  "be a high rate of fracture rejection.".format(minFracSize))

        if val > minFracSize:
            input_helper_methods.error("\"h\" (length scale) is greater than the minimum fracture size ({}). "\
                                             "Choose a smaller value for h or a greater minimum fracure size."\
                                             " ".format(minFracSize))
        compare_pts_v_sh('e', val)
        compare_pts_v_sh('r', val)

        params['h'][0] = val

    def boundary_faces():
        """Check that the boundaryFaceis list is a list of flags of length 6, one for each side of the domain
        ie {1, 1, 1, 0, 0, 1} represents --> {+x, -x, +y, -y, +z, -z}
        DFN only keeps clusters with connections to domain boundaries set to 1.
        """
        errResult = input_helper_methods.verify_list(
            input_helper_methods.value_of('boundaryFaces', params),
            'boundaryFaces', input_helper_methods.verify_flag, 6)
        if errResult != None:
            input_helper_methods.error("\"boundaryFaces\" must be a list of 6 flags (0 or 1), {} have(has) been defined. Each flag "\
                  "represents a side of the domain, {{+x, -x, +y, -y, +z, -z}}.".format(-errResult))

    def enum_points():
        """ Check the integer value of enumPoints for each ellipse family."""
        errResult = input_helper_methods.verify_list(
            input_helper_methods.value_of('enumPoints', params),
            'enumPoints',
            input_helper_methods.verify_int,
            desiredLength=ellipseFams,
            noZeros=True,
            noNegs=True)
        if errResult != None:
            input_helper_methods.error("\"enumPoints\" has defined {} value(s) but there is(are) {} families of ellipses. Please "\
                  "define one enumPoints value greater than 4 for each ellipse family.".format(-errResult, ellipseFams))
        for val in input_helper_methods.value_of("enumPoints"):
            if val <= 4:
                input_helper_methods.error("\"enumPoints\" contains a value less than or equal to 4. If 4 points were intended, "\
                      "define this family as a rectangle family. No polygons with less than 4 verticies are acceptable.")

    ## ========================================================================= ##
    ##                      Generalized Mandatory Params                         ##
    ## ========================================================================= ##
    ###                                                ###
    ###        Prefix MUST be either 'e' or 'r'        ###
    ###                                                ###
    ### ============================================== ###

    def aspect(prefix):
        """ Check the aspect of the the rectangle or ellipse families. """
        shape = "ellipse" if prefix == 'e' else "rectangle"
        numFamilies = ellipseFams if prefix == 'e' else rectFams
        paramName = prefix + "aspect"

        errResult = input_helper_methods.verify_list(
            input_helper_methods.value_of(paramName),
            paramName,
            input_helper_methods.verify_float,
            desiredLength=numFamilies,
            noZeros=True,
            noNegs=True)
        if errResult != None:
            input_helper_methods.error("\"{}\" has defined {} value(s) but there is(are) {} {} families. Please define one "\
                  "aspect ratio for each family.".format(paramName, -errResult, numFamilies, shape))

    def angle_option(prefix):
        """ Check the angle option flag. """
        paramName = prefix + "AngleOption"
        input_helper_methods.verify_flag(
            input_helper_methods.value_of(paramName), paramName)

    def layer(prefix):
        """ Check the number of layers. """
        shape = "ellipse" if prefix == 'e' else "rectangle"
        numFamilies = ellipseFams if prefix == 'e' else rectFams
        paramName = prefix + "Layer"

        errResult = input_helper_methods.verify_list(
            input_helper_methods.value_of(paramName),
            paramName,
            input_helper_methods.verify_int,
            desiredLength=numFamilies)
        if errResult != None:
            input_helper_methods.error("\"{}\" has defined {} layer(s) but there is(are) {} {} families. "\
                  "Need one layer per {} family. Layers are numbered by the order they "\
                  "are defined in 'layers' parameter. Layer 0 is the whole domain."\
                  .format(paramName, -errResult, numFamilies, shape, shape))

        for layer in input_helper_methods.value_of(paramName):
            if input_helper_methods.is_negative(int(layer)):
                input_helper_methods.error("\"{}\" contains a negative layer number. Only values from 0 to "\
                      "{} (numOfLayers) are accepted. Layer 0 corresponds to the entire"\
                      "domain.".format(paramName, numLayers))
            if int(layer) > numLayers:
                input_helper_methods.error("\"{}\" contains value '{}' but only {} layer(s) is(are) defined. Make sure the "\
                      "layer numbers referenced here are found in that same postion in \"layers\" "\
                      "parameter.".format(paramName, layer, numLayers))

    def theta_phi_kappa(prefix):
        """ Check the angle parameters used for Fisher distributions 
        """
        shape = "ellipse" if prefix == 'e' else "rectangle"
        numFamilies = ellipseFams if prefix == 'e' else rectFams
        paramNames = [prefix + name for name in ["theta", "phi", "kappa"]]
        errString = "\"{}\" has defined {} angle(s) but there is(are) {} {} family(ies)."\
                "Please defined one angle for each {} family."

        for param in paramNames:
            errResult = input_helper_methods.verify_list(
                input_helper_methods.value_of(param),
                param,
                input_helper_methods.verify_float,
                desiredLength=numFamilies)
            if errResult != None:
                input_helper_methods.error(
                    errString.format(param, -errResult, numFamilies, shape,
                                     shape))

    #
    ## ========================================================================= ##
    ##                      Main for I/O Checkin and Writing                     ##
    ## ========================================================================= ##


###
#        def check_i_oargs(ioPaths):
#            try:
#                ioPaths["input"] = sys.argv[1]
#            except IndexError:
#                input_helper_methods.error("Please provide an input file path as the first command line argument.\n"\
#                      "    $ python3 inputParser.py [inputPath] [outputPath (Optional)]")
#
#            try:
#                ioPaths["output"] = sys.argv[2]
#            except IndexError:
#                ioPaths["output"] = "polishedOutput.txt"
#                input_helper_methods.warning("No output path has been provided so output will be written to "\
#                    "\"polishedOutput.txt\" in your current working directory.", params)
#

    def parse_input():
        """ Parse each line of the input file. 
        """
        for line in inputIterator:
            line = input_helper_methods.extract_parameters(
                line, inputIterator)  ## this strips comments
            if (line != "" and ":" in line):
                input_helper_methods.process_line(line, unfoundKeys,
                                                  inputIterator, warningFile)
        needed = [unfound for unfound in unfoundKeys if unfound in mandatory]
        if needed != []:
            errString = ""
            for key in needed:
                errString += "\t\"" + key + "\"\n"
            input_helper_methods.error(
                "Missing the following mandatory parameters: \n{}".format(
                    errString))

    def verify_params():
        """ Verify all of the parameters in the input file.
        """
        distributions = distr_module.distr(params, numEdistribs, numRdistribs,
                                           minFracSize)
        firstPriority = [
            n_fam_ell, n_fam_rect, stop_condition, domain_size, num_of_layers,
            seed, domain_size_increase, ignore_boundary_faces,
            rejects_per_fracture, user_defined,
            input_helper_methods.check_fam_count, check_no_dep_flags, fam_prob
        ]

        generalized = [
            layer, aspect, angle_option, theta_phi_kappa,
            distributions.beta_distribution, distributions.distr
        ]

        distribs = [
            distributions.lognormal_dist, distributions.tpl_dist,
            distributions.exponential_dist, distributions.constant_dist
        ]

        checkLast = [disable_fram, aperture, permeability]

        for paramFunc in firstPriority:
            paramFunc()

        if rectFams > 0:
            for paramFunc in generalized:
                paramFunc('r')

        if ellipseFams > 0:
            enum_points()
            for paramFunc in generalized:
                paramFunc('e')

        for i, paramFunc in enumerate(distribs):
            if numEdistribs[i + 1] > 0:
                paramFunc(
                    'e'
                )  ## only call if there have been 1+ of a distrib defined
            if numRdistribs[i + 1] > 0:
                paramFunc(
                    'r')  ## +1 for reason stated in list instantiation above

        for paramFunc in checkLast:
            paramFunc()

    def write_back():
        """ Write the parameters from the verbose input file back to a simplified input file.
        """
        for param in params:
            if param == 'layers':
                writer.write(param + ': ')
                for layer in params['layers']:
                    writer.write(
                        input_helper_methods.list_to_curly(str(layer)) + " ")
                writer.write('\n')
            elif type(input_helper_methods.value_of(param,
                                                    writing=True)) is list:
                curl = input_helper_methods.list_to_curly(
                    str(input_helper_methods.value_of(param, writing=True)))
                writer.write(param + ': ' + curl + '\n')
            else:
                writer.write(
                    param + ': ' +
                    str(input_helper_methods.value_of(param, writing=True)) +
                    '\n')

    #print "--> Checking input files"
    try:
        if not os.path.exists(os.getcwd()):
            print("ERROR: cwd: ", os.getcwd(), " does not exist")
        if not os.path.exists(os.path.abspath(self.dfnGen_file)):
            print("ERROR: dfnGen input file path: ",
                  os.path.abspath(self.dfnGen_file), " does not exist")
        print(os.path.abspath(self.dfnGen_file))
        shutil.copy(os.path.abspath(self.dfnGen_file), os.getcwd())
    except:
        sys.exit("Unable to copy dfnGen input file\n%s\nExiting" %
                 self.dfnGen_file)

    ioPaths = {"input": "", "output": ""}
    try:
        ioPaths["input"] = self.dfnGen_file
    except IndexError:
        input_helper_methods.error("Please provide an input file path as the first command line argument.\n"\
              "    $ python3 inputParser.py [inputPath] [outputPath (Optional)]")
    try:
        ioPaths["output"] = self.jobname + '/' + self.dfnGen_file.split(
            '/')[-1][:-4] + '_clean.dat'
        ioPaths["output"] = os.path.abspath(ioPaths["output"])
        print(ioPaths["output"])
    except IndexError:
        ioPaths["output"] = "polishedOutput.txt"
        input_helper_methods.warning("No output path has been provided so output will be written to "\
            "\"polishedOutput.txt\" in your current working directory.", params)
    try:
        reader = open(ioPaths["input"], 'r')
    except:
        input_helper_methods.error(
            "Check that the path of your input file is valid")
    try:
        writer = open(ioPaths["output"], 'w')
    except:
        input_helper_methods.error(
            "Check that the path of your output file is valid.")

    inputIterator = iter(reader)
    print('--> Checking input data')
    print('--> Input Data: ', ioPaths["input"])
    print('--> Output File: ', ioPaths["output"])

    parse_input()
    verify_params()
    write_back()
    print('--> Checking Input Data Complete')
