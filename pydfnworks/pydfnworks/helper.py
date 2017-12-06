import os
import sys
import re
import argparse
import subprocess

def move_files(file_list, dir_name):
    os.mkdir(dir_name) 
    for fle in os.listdir(os.getcwd()):
        for name in file_list:
            if name in fle:
                subprocess.call('mv ' + fle + ' ' + dir_name, shell=True)

def cleanup_files_at_end(self):
    
    main_list = ['allboundaries.zone', 'aperture.dat', 'cellinfo.dat',
                 'darcyvel.dat', 'dfnTrans_ouput_dir', 'params.txt',
                 'PTDFN_control.dat', 'pboundary', 'zone', 'poly_info.dat',
                 '.inp', 'id_tri_node', 'intersections', 'full_mesh.inp', 'tri_fracture.stor',
                   'cellinfo.dat', 'aperture.dat']
    gen_list = ['DFN_output.txt', 'connectivity.dat', 'families.dat', 'input_generator.dat',
                'input_generator_clean.dat', 'normal_vectors.dat', 'radii', 'rejections.dat',
                'rejectsPerAttempt.dat', 'translations.dat', 'triple_points.dat', 'user_rects.dat',
                'warningFileDFNGen.txt']
    lagrit_list = ['.lgi', 'boundary_output.txt', 'finalmesh.txt', 
                    'full_mesh.gmv', 'full_mesh.lg', 'intersections',
                   'lagrit_logs', '3dgen', 'parameters', 'polys']
    pflotran_list = [  'dfn_explicit', 'dfn_properties.h5','full_mesh.uge',
                      'full_mesh_viz.inp', 'full_mesh_vol_area', 'materialid.dat', 'parsed_vtk', 'perm.dat', 
                      'pboundary_', 'convert_uge_params.txt']
    move_files(gen_list, 'DFN_generator')
    move_files(lagrit_list, 'LaGriT')
    move_files(pflotran_list, 'PFLOTRAN')

def commandline_options():
    """Read command lines for use in dfnWorks.
    
    Options:
        * -name : Jobname (Mandatory)
        * -ncpu : Number of CPUS (Optional, default=4)
        * -input : input file with paths to run files (Mandatory if the next three options are not specified)
        * -gen : Generator Input File (Mandatory, can be included within this file)
        * -flow : PFLORAN Input File (Mandatory, can be included within this file)
        * -trans: Transport Input File (Mandatory, can be included within this file)
        * -cell: True/False Set True for use with cell based aperture and permeabuility (Optional, default=False)
    
    """
    parser = argparse.ArgumentParser(description="Command Line Arguments for dfnWorks")
    parser.add_argument("-name", "--jobname", default="", type=str,
              help="jobname") 
    parser.add_argument("-ncpu", "--ncpu", default=4, type=int, 
              help="Number of CPUs")
    parser.add_argument("-input", "--input_file", default="", type=str,
              help="input file with paths to run files") 
    parser.add_argument("-gen", "--dfnGen", default="", type=str,
              help="Path to dfnGen run file") 
    parser.add_argument("-flow", "--dfnFlow", default="", type=str,
              help="Path to dfnFlow run file") 
    parser.add_argument("-trans", "--dfnTrans", default="", type=str,
              help="Path to dfnTrans run file") 
    parser.add_argument("-cell", "--cell", default=False, action="store_true",
              help="Binary For Cell Based Apereture / Perm")
    options = parser.parse_args()
#    if options.jobname is "":
#        sys.exit("Error: Jobname is required. Exiting.")
    return options


def dump_time(local_jobname, section_name, time):
    '''dump_time
    keeps log of cpu run time, current formulation is not robust
    '''
    if (os.path.isfile(local_jobname+"_run_time.txt") is False):    
        f = open(local_jobname+"_run_time.txt", "w")
        f.write("Runs times for " + local_jobname + "\n")
    else:
        f = open(local_jobname+"_run_time.txt", "a")
    if time < 60.0:
        line = section_name + " :  %f seconds\n"%time
    else:
        line = section_name + " :  %f minutes\n"%(time/60.0)
    f.write(line)
    f.close()

def print_run_time(local_jobname):
    '''print_run_time
    Read in run times from file and and print to screen with percentages
    '''
    f=open(local_jobname+"_run_time.txt").readlines()
    unit = f[-1].split()[-1]
    total = float(f[-1].split()[-2])
    if unit is 'minutes':
        total *= 60.0

    print 'Runs times for ', f[0]
    percent = []
    name = []
    for i in range(1,len(f)):
        unit = f[i].split()[-1]
        time = float(f[i].split()[-2])

        if unit is 'minutes':
            time *= 60.0
        percent.append(100.0*(time/total))
        name.append(f[i].split(':')[1])
        print f[i], '\t--> Percent if total %0.2f \n'%percent[i-1]
    print("Primary Function Percentages")

    for i in range(1,len(f) - 1):
        if name[i-1] == ' dfnGen ' or name[i-1] == ' dfnFlow ' or name[i-1] == ' dfnTrans ':
            print(name[i-1]+"\t"+"*"*int(percent[i-1]))
    print("\n")

def get_num_frac():
    """ Get the number of fractures from the params.txt file.
    """
    try: 
        f = open('params.txt')
        _num_frac = int(f.readline())
        f.close()
    except:
        print '-->ERROR getting number of fractures, no params.txt file'

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
        curl = re.sub(r'\[','{', strList)
        curl = re.sub(r'\]','}', curl)
        curl = re.sub(r"\'", '', curl)
        return curl 

    def has_curlys(self, line, key):
        """ Checks to see that every { has a matching }.
        """
        if '{' in line and '}' in line: return True 
        elif '{' in line or '}' in line: 
            self.error("Line defining \"{}\" contains a single curly brace.".format(key))
        return False

    def value_of(self, key, writing = False):
        """ Use to get key's value in params. writing always false  
        """
        if (not writing) and (len(self.params[key]) > 1):
            self.error("\"{}\" can only correspond to 1 list. {} lists have been defined.".format(key, len(self.params[key])))
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
            line = line.replace(group, '', 1) ## only delete first occurence
            valList.append(self.curly_to_list(group))
            
        if line.strip() != "":
            self.error("Unexpected character found while parsing \"{}\".".format(key))

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
        print("\nERROR --- " + errString)
        print("\n----Program terminated while parsing input----\n")
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
        scaled = [float("{:.6}".format(x/total)) for x in probList]
        self.warning("'famProb' probabilities did not add to 1 and have been scaled accordingly "\
            "for their current sum, {:.6}. Scaled {} to {}".format(total, probList, scaled), warningFile)
        return [x/total for x in probList]                

    def zero_in_std_devs(self, valList):
        """ returns True is there is a zero in valList of standard deviations
        """
        for val in valList:
            if float(val) == 0: return True
        
    def check_min_max(self, minParam, maxParam, shape):
        """ Checks that the minimum parameter for a family is not greater or equal to the maximum parameter.
        """
        for minV, maxV in zip(self.value_of(minParam), self.value_of(maxParam)):
            if minV == maxV:
                self.error("\"{}\" and \"{}\" contain equal values for the same {} family. "\
                      "If {} and {} were intended to be the same, use the constant distribution "\
                      "(4) instead.".format(minParam, maxParam, shape, minParam, maxParam))
            if minV > maxV:
                self.error("\"{}\" is greater than \"{}\" in a(n) {} family.".format(minParam, maxParam, shape))
                sys.exit()

    def check_mean(self, minParam, maxParam, meanParam, warningFile=''):
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

    def check_min_frac_size(self, valList):
        """ Corrects the minimum fracture size if necessary, by looking at the values in valList.
        """
        for val in valList:
            if val < self.minFracSize: self.minFracSize = val



    ## ====================================================================== ##
    ##                              Parsing Functions                         ##
    ## ====================================================================== ##
    def extract_parameters(self, line, inputIterator):
        """Returns line without comments or white space.
        """
        if "/*" in line:
            comment = line
            line = line[:line.index("/*")] ## only process text before '/*' comment
            while "*/" not in comment:
                comment = next(inputIterator) ## just moves iterator past comment

        elif "//" in line:
            line = line[:line.index("//")] ## only process text before '//' comment
            
        return line.strip()


    def find_val(self, line, key, inputIterator, unfoundKeys, warningFile):
        """ Extract the value for key from line. 
        """
        valList = []
        line = line[line.index(":") + 1:].strip()
        if line != "" : self.val_helper(line, valList, key)

        line = self.extract_parameters(next(inputIterator), inputIterator)
        while ':' not in line:
            line = line.strip()
            if line != "" :
                self.val_helper(line, valList, key)
            try:
                line = self.extract_parameters(next(inputIterator), inputIterator)
            except StopIteration:
                break
        
        if valList == [] and key in mandatory:
            self.error("\"{}\" is a mandatory parameter and must be defined.".format(key))
        if key is not None:
            self.params[key] = valList if valList != [] else [""] ## allows nothing to be entered for unused params 
        if line != "": self.process_line(line, unfoundKeys, inputIterator, warningFile)
            
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
           self.warning("\"" + key + "\" is not one of the valid parameter names.", warningFile)

    def process_line(self, line, unfoundKeys, inputIterator, warningFile):
        """ Find the key in a line, and the value for that key.
        """
        if line.strip != "":
            key = self.find_key(line, unfoundKeys, warningFile)
            if key != None: self.find_val(line, key, inputIterator, unfoundKeys, warningFile)   


    ## ====================================================================== ##
    ##                              Verification                              ##
    ## ====================================================================== ##
    ## Note: Always provide EITHER a key (ie "stopCondition") 
    ##         OR inList = True/False (boolean indicating val being checked is inside a list) 

    ## Input: value - value being checked
    ##        key - parameter the value belongs to
    ##        inList - (Optional)
    def verify_flag(self, value, key = "", inList = False):
        """ Verify that value is either a 0 or a 1.
        """
        if value is '0' or value is '1':
            return int(value)
        elif inList:
            return None
        else:
            self.error("\"{}\" must be either '0' or '1'".format(key))

    def verify_float(self, value, key = "", inList = False, noNeg = False):
        """ Verify that value is a positive float.
        """
        if type(value) is list:
            self.error("\"{}\" contains curly braces {{}} but should not be a list value.".format(key))
        try:
            if noNeg and float(value) < 0:
                self.error("\"{}\" cannot be a negative number.".format(key))
            return float(value)
        except ValueError:
            if inList: return None
            else:
                self.error("\"{}\" contains an unexpected character. Must be a single "\
                      "floating point value (0.5, 1.6, 4.0, etc.)".format(key))
                
                
    def verify_int(self, value, key = "", inList = False, noNeg = False):
        """ Verify that value is a positive integer.
        """
        if type(value) is list:
            self.error("\"{}\" contains curly braces {{}} but should not be a list value.".format(key))
        try:
            if noNeg and int(re.sub(r'\.0*$', '', value)) < 0:
                self.error("\"{}\" cannot be a negative number.".format(key))
            return int(re.sub(r'\.0*$', '', value)) ## regex for removing .0* (ie 4.00 -> 4)
        except ValueError:
            if inList: return None
            else:
                self.error("\"{}\" contains an unexpected character. Must be a single "\
                      "integer value (0,1,2,3,etc.)".format(key))
                
    
    def verify_list(self, valList, key, verificationFn, desiredLength, noZeros=False, noNegs=False):
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
            self.error("\"{}\"'s value must be a list encolsed in curly brackets {{}}.".format(key))
        if desiredLength != 0 and int(len(valList)) != int(desiredLength):
            print 'list desired length is ', desiredLength, 'but valList is ', valList, 'with length ', len(valList)
            return -len(valList)
        for i, value in enumerate(valList):
            value = value.strip()
            verifiedVal = verificationFn(value, inList = True)
            if verifiedVal == None:
                listType = re.sub('integer', 'int', re.sub(r'verify', '', verificationFn.__name__)) ## 'verifyint' --> 'integer'
                self.error("\"{}\" must be a list of {}s {}. non-{} found in "\
                      "list".format(key, listType, examples[listType], listType))
            if noZeros and verifiedVal == 0:
                self.error("\"{}\" list cannot contain any zeroes.".format(key))
            if noNegs and self.is_negative(float(verifiedVal)):
                self.error("\"{}\" list cannot contain any negative values.".format(key)) 
            valList[i] = verifiedVal 
           

    ## def verifynumvalsis(length, key):f
           ##  if len(self.params[key]) != length:
            ##     self.error("error: ", "\"" + param + "\"", "should have", length, "value(s) but", len(self.params[key]), "are defined.")
             ##    sys.exit()                

