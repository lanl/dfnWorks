"""
.. file:: dfnWorks.py
   :synopsis: Contains classes and functions used to wrap the dfnWorks workflow
   :version: 2.0
   :maintainer: Jeffrey Hyman, Satish Karra, Nathaniel Knapp
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

from shutil import copy, rmtree
import numpy as np
import scipy
from scipy.stats import norm, lognorm, powerlaw
from scipy.integrate import odeint 
from dfntools import *
import h5py
import argparse

import matplotlib.pylab as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.mlab as mlab
import dfnGen_meshing as mesh
from pylagrit import PyLaGriT


class dfnworks(Frozen):
    """Class for DFN Generation and meshing
    """
    def __init__(self, jobname='', local_jobname='',dfnGen_file='',output_file='',local_dfnGen_file='',ncpu='', dfnFlow_file = '', local_dfnFlow_file = '', dfnTrans_file = '', inp_file='full_mesh.inp', uge_file='', vtk_file='', mesh_type='dfn', perm_file='', aper_file='',perm_cell_file='',aper_cell_file='', dfnTrans_version ='', num_frac = ''):
        """Class constructor for DFN Generation and meshing. 

            Kwargs:
              jobname (str): Name of the job. 
               local_jobname (str): Same as jobname. (JH)
               dfnGen_file (str): Input file for dfnGen
               output_file (str): Name of output file. (? Name will be suffixed with _output_report JH)
               local_dfnGen_file (str): JH
               ncpu (int): Number of CPUs that dfnWorks will use.
               dfnFlow_file (str): Input file for dfnFlow.
               local_dfnFlow_file (str): JH
               dfnTrans_file (str): INput file for dfnTrans. 
               inp_file (str): Name of LaGriT input file. (? JH)
               uge_file (str): Name of (? JH)
               vtk_file (str): Name of vtk file used for Paraview visualization of (? JH)
               mesh_type (str): JH
               aper_file (str): Name of aperture input file.
               perm_cell_file (str): Name of permeability input file. JH
               aper_cell_file (str): JH
               dfnTrans_version (str): Version of dfnTrans to run.
            num_frac (int): Number of fractures.
        """

        self._jobname = jobname
        self._ncpu = ncpu
        self._local_jobname = self._jobname.split('/')[-1]

        self._dfnGen_file = dfnGen_file
        self._local_dfnGen_file = self._dfnGen_file.split('/')[-1]
        
        self._output_file = self._dfnGen_file.split('/')[-1]
        
        self._dfnFlow_file = dfnFlow_file 
        self._local_dfnFlow_file = self._dfnFlow_file.split('/')[-1]

        self._dfnTrans_file = dfnTrans_file 
        self._local_dfnTrans_file = self._dfnTrans_file.split('/')[-1]

        self._vtk_file = vtk_file
        self._inp_file = inp_file
        self._uge_file = uge_file
        self._mesh_type = mesh_type
        self._perm_file = perm_file
        self._aper_file = aper_file
        self._perm_cell_file = perm_cell_file
        self._aper_cell_file = aper_cell_file
        #self._flow_solver = 'pflotran'
        self._dfnTrans_version= 2.0
        self._freeze

    def dfnGen(self):
        """
        Run the dfnGen workflow. 
        1) make_working_directory: Create a directory with name of job
        2) check_input: Check input parameters and create a clean version of the input file
        3) create_network: Create network. DFNGEN v2.0 is called and creates the network
        4) output_report: Generate a PDF summary of the DFN generation
        5) mesh_network: calls module dfnGen_meshing and runs LaGriT to mesh the DFN
        """
        tic_gen = time()
        # Create Working directory
        tic = time()
        self.make_working_directory()
        self.dump_time('Function: make_working_directory', time()- tic)    

        # Check input file    
        tic = time()
        self.check_input()
        self.dump_time('Function: check_input', time() - tic)    
    
        # Create network    
        tic = time()
        self.create_network()
        self.dump_time('Function: create_network', time() - tic)    
        
        tic = time()
        self.output_report()
        self.dump_time('output_report', time() - tic)    
        # Mesh Network

        tic = time()
        self.mesh_network()
        self.dump_time('Function: mesh_network', time() - tic)    
        print ('='*80)
        print 'dfnGen Complete'
        print ('='*80)
        print ''
        self.dump_time('Process: dfnGen',time() - tic_gen)    

    def dfnFlow(self):
        """ dfnFlow
        Run the dfnFlow portion of the workflow.
        1) lagrit2pflotran: takes output from LaGriT and processes it for use in PFLOTRAN
        """    
    
        print('='*80)
        print("\ndfnFlow Starting\n")
        print('='*80)

        tic_flow = time()

        tic = time()
        self.lagrit2pflotran()
        self.dump_time('Function: lagrit2pflotran', time() - tic)    
        
        tic = time()    
        self.pflotran()
        self.dump_time('Function: pflotran', time() - tic)    

        tic = time()    
        self.parse_pflotran_vtk()        
        self.dump_time('Function: parse_pflotran_vtk', time() - tic)    
        
        tic = time()    
        self.pflotran_cleanup()
        self.dump_time('Function: parse_cleanup', time() - tic)    
        self.dump_time('Process: dfnFlow',time() - tic_flow)    
    
        print('='*80)
        print("\ndfnFlow Complete\n")
        print('='*80)

    def dfnTrans(self):
        """dfnTrans
        Copy input files for dfnTrans into working directory and run DFNTrans
        """
        print('='*80)
        print("\ndfnTrans Starting\n")
        print('='*80)
    
        try:
            os.symlink(os.environ['DFNTRANS_PATH']+'DFNTrans', './DFNTrans')
        except:
            print("--> ERROR: Problem creating link to DFNTrans")
        try:    
            copy(self._dfnTrans_file, self._local_dfnTrans_file) 
        except:
            print("--> ERROR: Problem copying PTDFN_control.dat file")
        tic = time()    
        failure = os.system('./DFNTrans '+self._local_dfnTrans_file)
        self.dump_time('Process: dfnTrans', time() - tic)    
        if failure == 0:
            print('='*80)
            print("\ndfnTrans Complete\n")
            print('='*80)
        else:
            sys.exit("--> ERROR: dfnTrans did not complete\n")
    def dump_time(self, section_name, time):
        if (os.path.isfile(self._local_jobname+"_run_time.txt")==False):    
            f = open(self._local_jobname+"_run_time.txt", "w")
            f.write("Runs times for " + self._jobname + "\n")
        else:
            f = open(self._local_jobname+"_run_time.txt", "a")
        if time < 60.0:
            line = section_name + " :  %f seconds\n"%time
        else:
            line = section_name + " :  %f minutes\n"%(time/60.0)
        f.write(line)
        f.close()

    def print_run_time(self):
        """print_run_time
        Read in run times from file and and print to screen with percentages
        """
        f=open(self._local_jobname+"_run_time.txt").readlines()
        unit = f[-1].split()[-1]
        total = float(f[-1].split()[-2])
        if unit=='minutes':
            total *= 60.0

        print 'Runs times for ', f[0]
        percent = []
        name = []
        for i in range(1,len(f)):
            unit = f[i].split()[-1]
            time = float(f[i].split()[-2])
    
            if unit=='minutes':
                time *= 60.0
            percent.append(100.0*(time/total))
            name.append(f[i].split(':')[1])
            print f[i], '\t--> Percent if total %0.2f \n'%percent[i-1]
        print("Primary Function Percentages")

        for i in range(1,len(f) - 1):
            if name[i-1] == ' dfnGen ' or name[i-1] == ' dfnFlow ' or name[i-1] == ' dfnTrans ':
                print(name[i-1]+"\t"+"*"*int(percent[i-1]))
        print("\n")

    #################### dfnGen Functions ##########################
    def make_working_directory(self,jobname=''):
        """ Make working directories for fracture generation.
            Kwargs:
             jobname (str): Name of the job. 
        """

        if self._jobname:
            jobname = self._jobname
        else:
            self._jobname = jobname
        try:
            os.mkdir(jobname)
            os.mkdir(jobname + '/radii')
            os.mkdir(jobname + '/intersections')
            os.mkdir(jobname + '/polys')
            os.chdir(self._jobname)
            cwd = os.getcwd()
            print("Current directory is now: %s\n"%cwd)
        except OSError:
            print '\nFolder ', jobname, ' exists'
        #    keep = raw_input('Do you want to delete it? [yes/no] \n')
        #    if keep == 'yes' or keep == 'y':
            print 'Deleting', jobname 
            rmtree(jobname)
            print 'Creating', jobname 
            os.mkdir(jobname)    
            os.mkdir(jobname + '/radii')
            os.mkdir(jobname + '/intersections')
            os.mkdir(jobname + '/polys')
            os.chdir(self._jobname)
            cwd = os.getcwd()
            print("Current directory is now: %s\n"%cwd)

        #    elif keep == 'no' or 'n':
        #        sys.exit("Not deleting folder. Exiting Program") 
        #    else:
        #        sys.exit("Unknown Response. Exiting Program") 


    def check_input(self,input_file='',output_file=''):
        """
                        ## Input Format Requirements ##

            1. Each parameter must be defined on its own line (seperate by newline '\n')
            2. A parameter (key) MUST be separated from its value by a colon ':' (ie. --> key: value)
            - Values may also be placed on lines after the 'key:' (ie. --> key: \n value)
            3. Comment Format:  On a line containg // or /*, nothing after */ or // will be processed
                    but text before a comment will be processed 
                       // Single line comment
                       /* Multline
                      comment */ This will NOT be processed
                    This WILL be processed
         
        """
        ## BIG TODO s -----
            ## ==== Problems ==== ##
        ## 11. Multiple keys on one line
        ## 15. check # values (famprob: {.5,.5} {.3, .3., .4})
        params = { 'esd':[],'insertUserRectanglesFirst':[],'keepOnlyLargestCluster':[],'rmin':[],
        'rAngleOption':[],'boundaryFaces':[],'userRectanglesOnOff':[],'printRejectReasons':[],'numOfLayers':[],
        'RectByCoord_Input_File_Path':[],'eLogMean':[],'rExpMin':[],'lengthCorrelatedAperture':[],'ebetaDistribution':[],
        'tripleIntersections':[],'layers':[],'stdAperture':[],'ealpha':[],'constantPermeability':[],'rLogMax':[],
        'rLogMean':[],'nFamRect':[],'etheta':[],'eLogMax':[],'rphi':[],'outputAllRadii':[],
        'r_p32Targets':[],'permOption':[],'userEllByCoord':[],'userRecByCoord':[],'userEllipsesOnOff':[],'UserEll_Input_File_Path':[],
        'rExpMean':[],'rbetaDistribution':[],'aperture':[],'emax':[],'eExpMean':[],'e_p32Targets':[],'eLayer':[],
        'domainSizeIncrease':[],'h':[],'outputFinalRadiiPerFamily':[],'rbeta':[],'rLogMin':[],'edistr':[],'domainSize':[],
        'eExpMin':[],'ekappa':[],'rLayer':[],'seed':[],'constantAperture':[],'stopCondition':[],'enumPoints':[],
        'meanAperture':[],'eLogMin':[],'easpect':[],'rtheta':[],'rdistr':[],
        'UserRect_Input_File_Path':[],'EllByCoord_Input_File_Path':[], 'rconst':[],'rExpMax':[],'ignoreBoundaryFaces':[],
        'visualizationMode':[],'outputAcceptedRadiiPerFamily':[],'apertureFromTransmissivity':[],'rsd':[],'ebeta':[],
        'nFamEll':[],'econst':[],'raspect':[],'eAngleOption':[],'emin':[],'ephi':[],'rmax':[],'famProb':[],'disableFram':[],
        'ralpha':[],'nPoly':[],'rejectsPerFracture':[],'rkappa':[],'eExpMax':[], 'forceLargeFractures':[], 'radiiListIncrease':[], 
        'removeFracturesLessThan':[]} 

        unfoundKeys={'stopCondition','nPoly','outputAllRadii','outputAllRadii','outputFinalRadiiPerFamily',
        'outputAcceptedRadiiPerFamily','domainSize', 'numOfLayers', 'layers', 'h', 
        'tripleIntersections', 'printRejectReasons', 'disableFram', 'visualizationMode', 'seed', 'domainSizeIncrease', 'rsd',
        'keepOnlyLargestCluster', 'ignoreBoundaryFaces', 'boundaryFaces', 'rejectsPerFracture', 'famProb', 'insertUserRectanglesFirst',
        'nFamEll', 'eLayer', 'edistr', 'ebetaDistribution', 'e_p32Targets', 'easpect', 'enumPoints', 'eAngleOption', 'etheta', 'ephi',
        'ebeta', 'ekappa', 'eLogMean', 'esd', 'eLogMin', 'eLogMax', 'eExpMean', 'eExpMin', 'eExpMax', 'econst', 'emin', 'emax',
        'ealpha', 'nFamRect', 'rLayer', 'rdistr', 'rbetaDistribution', 'r_p32Targets', 'raspect', 'rAngleOption', 'rtheta', 'rphi',
        'rbeta', 'rkappa', 'rLogMean', 'ssd', 'rLogMin', 'rLogMax', 'rmin', 'rmax', 'ralpha', 'rExpMean', 'rExpMin', 'rExpMax',
        'rconst', 'userEllipsesOnOff', 'UserEll_Input_File_Path', 'userRectanglesOnOff', 'UserRect_Input_File_Path','EllByCoord_Input_File_Path', 'userEllByCoord', 'userRecByCoord',
        'RectByCoord_Input_File_Path', 'aperture', 'meanAperture', 'stdAperture', 'apertureFromTransmissivity', 'constantAperture',
        'lengthCorrelatedAperture', 'permOption', 'constantPermeability', 'forceLargeFractures', 'radiiListIncrease', 'removeFracturesLessThan'}

        mandatory = {'stopCondition','domainSize','numOfLayers','outputAllRadii', 'outputFinalRadiiPerFamily',
        'outputAcceptedRadiiPerFamily','tripleIntersections','printRejectReasons',
        'disableFram','visualizationMode','seed','domainSizeIncrease','keepOnlyLargestCluster','ignoreBoundaryFaces',
        'rejectsPerFracture','famProb','insertUserRectanglesFirst','nFamEll','nFamRect','userEllipsesOnOff','userRectanglesOnOff',
        'userEllByCoord','userRecByCoord','aperture','permOption', 'forceLargeFractures', 'radiiListIncrease', 'removeFracturesLessThan'}

        noDependancyFlags = ['outputAllRadii','outputFinalRadiiPerFamily',
        'outputAcceptedRadiiPerFamily','tripleIntersections','printRejectReasons',
        'visualizationMode', 'keepOnlyLargestCluster','insertUserRectanglesFirst', 'forceLargeFractures']

        examples = {"Flag":"(0 or 1)", "Float":"(0.5, 1.6, 4.0, etc.)" , "Int":"(0,1,2,3,etc.)"}

        global ellipseFams
        ellipseFams = 0
        global rectFams
        rectFams = 0
        global numLayers
        numLayers = 0
        global minFracSize
        minFracSize = 99999999.9
            ## WARNING: Index[0] for the following lists should never be used. See edistr() and rdistr() for clarity.
        global numEdistribs 
        numEdistribs = [-1,0,0,0,0] ## [0 = no-op, 1 = # log-normal's, 2 = # Truncated Power Law's, 3 = # Exp's, # constant's]  
        global numRdistribs
        numRdistribs = [-1,0,0,0,0] ## [0 = no-op, 1 = # log-normal's, 2 = # Truncated Power Law's, 3 = # Exp's, # constant's]
        global warningFile
        warningFile = open("warningFileDFNGen.txt", 'w')        


        ## ====================================================================== ##
        ##                              Parsing Functions                         ##
        ## ====================================================================== ##
        def extractParameters(line):
            """ Extract paramters from lines of the input file.
                Args:
                 line (str): A line of the input file.
            """

            if "/*" in line:
                comment = line
                line = line[:line.index("/*")] ## only process text before '/*' comment
                while "*/" not in comment:
                    comment = next(inputIterator) ## just moves iterator past comment

            elif "//" in line:
                line = line[:line.index("//")] ## only process text before '//' comment
                
            return line.strip()


        def findVal(line, key):
            """ Get the value contained in a line, associated with a parameter key.
                Args:
                 line (str): A line of the input file.
                 key (str): A Python dictionary key associated with a parameter (ie 'domainSize').
            """
            valList = []
            line = line[line.index(":") + 1:].strip()
            if line != "" : valHelper(line, valList, key)

            line = extractParameters(next(inputIterator))
            while ':' not in line:
                line = line.strip()
                if line != "" :
                    valHelper(line, valList, key)
                try:
                    line = extractParameters(next(inputIterator))
                except StopIteration:
                    break
            
            if valList == [] and key in mandatory:
                error("\"{}\" is a mandatory parameter and must be defined.".format(key))
            if key is not None:
                params[key] = valList if valList != [] else [""] ## allows nothing to be entered for unused params 
            if line != "": processLine(line)
                
        def findKey(line):
            """ Input: line containing a parameter (key) preceding a ":"
                Returns: key -- if it has not been defined yet and is valid
                 None -- if key does not exist
                exits -- if the key has already been defined to prevent duplicate confusion
            """    
            key = line[:line.index(":")].strip()
            if key in unfoundKeys:
                unfoundKeys.remove(key)
                return key
            try:
                params[key]
                print "params[key] already exists for key ", key, "parameter value ", params[key], "\n"
                error("\"{}\" has been defined more than once.".format(key))
            except KeyError:
                warning("\"" + key + "\" is not one of the valid parameter names.")

        def processLine(line):
            """Processes a line."""
            if line.strip != "":
                key = findKey(line)
                if key != None: findVal(line, key)   


        ## ====================================================================== ##
        ##                              Verification                              ##
        ## ====================================================================== ##
        ## Note: Always provide EITHER a key (ie "stopCondition") 
        ##         OR inList = True/False (boolean indicating val being checked is inside a list) 

        def verifyFlag(value, key = "", inList = False):
            """    Input: value - value being checked
                key - parameter the value belongs to
                inList - (Optional)
            """
            if value == '0' or value == '1':
                return int(value)
            elif inList:
                return None
            else:
                error("\"{}\" must be either '0' or '1'".format(key))

        def verifyFloat(value, key = "", inList = False, noNeg = False):
            """    Input: value - value being checked
                key - parameter the value belongs to
                inList - (Optional)
                noNeg - Boolean parameter that indicates whether value can be negative. 
            """
            if type(value)==list:
                error("\"{}\" contains curly braces {{}} but should not be a list value.".format(key))
            try:
                if noNeg and float(value) < 0:
                    error("\"{}\" cannot be a negative number.".format(key))
                return float(value)
            except ValueError:
                if inList: return None
                else:
                    error("\"{}\" contains an unexpected character. Must be a single "\
                          "floating point value (0.5, 1.6, 4.0, etc.)".format(key))
                    
                    
        def verifyInt(value, key = "", inList = False, noNeg = False):
            """    Input: value - value being checked
                key - parameter the value belongs to
                inList - (Optional)
                noNeg - Boolean parameter that indicates whether value can be negative. 
            """
            if type(value)==list:
                error("\"{}\" contains curly braces {{}} but should not be a list value.".format(key))
            try:
                if noNeg and int(re.sub(r'\.0*$', '', value)) < 0:
                    error("\"{}\" cannot be a negative number.".format(key))
                return int(re.sub(r'\.0*$', '', value)) ## regex for removing .0* (ie 4.00 -> 4)
            except ValueError:
                if inList: return None
                else:
                    error("\"{}\" contains an unexpected character. Must be a single "\
                          "integer value (0,1,2,3,etc.)".format(key))
                    
        def verifyList(valList, key, verificationFn, desiredLength, noZeros=False, noNegs=False):
            """ Verifies input list that come in format {0, 1, 2, 3}

            Input:  valList - List of values (flags, floats, or ints) corresponding to a parameter
                key - the name of the parameter whose list is being verified
                verificationFn - (either verifyFlag, verifyFloat or verifyInt) checks each list element
                desiredLength - how many elements are supposed to be in the list
                noZeros - (Optional) True for lists than cannot contain 0's, False if 0's are ok
                noNegs - (Optional) True for lists than cannot contain negative numbers, False otherwise
            Output: returns negative value of list length to indicate incorrect length and provide meaningful error message
                Prints error and exits if a value of the wrong type is found in the list
                returns None if successful
            """
            if valList == ['']: return 0
            if type(valList) is not list:
                error("\"{}\"'s value must be a list enclosed in curly brackets {{}}.".format(key))
            if desiredLength != 0 and len(valList) != desiredLength:
                return -len(valList)
            for i, value in enumerate(valList):
                value = value.strip()
                verifiedVal = verificationFn(value, inList = True)
                print "verified val==", verifiedVal
                if verifiedVal == None:
                    listType = re.sub('Integer', 'Int', re.sub(r'verify', '', verificationFn.__name__)) ## 'verifyInt' --> 'Integer'
                    error("\"{}\" must be a list of {}s {}. Non-{} found in "\
                          "list".format(key, listType, examples[listType], listType))
                if noZeros and verifiedVal == 0:
                    error("\"{}\" list cannot contain any zeroes.".format(key))
                if noNegs and isNegative(float(verifiedVal)):
                    error("\"{}\" list cannot contain any negative values.".format(key)) 
                valList[i] = verifiedVal 
               

        ## def verifyNumValsIs(length, key):f
               ##  if len(params[key]) != length:
                ##     error("ERROR: ", "\"" + param + "\"", "should have", length, "value(s) but", len(params[key]), "are defined.")
                 ##    sys.exit()                
            

        ## ====================================================================== ##
        ##                              Helper Functions                          ##
        ## ====================================================================== ##

        ## '{1,2,3}' --> [1,2,3]
        def curlyToList(curlyList):
            """converts curly braced list to a normal python list"""
            return re.sub("{|}", "", curlyList).strip().split(",")

        ## [1,2,3] --> '{1,2,3}'   for writing output
        def listToCurly(strList):
            """converts Python list to a list with curly braces."""
             curl = re.sub(r'\[','{', strList)
             curl = re.sub(r'\]','}', curl)
             curl = re.sub(r"\'", '', curl)
             return curl 

        def hasCurlys(line, key):
            """tests if a line has curly brackets"""
            if '{' in line and '}' in line: return True 
            elif '{' in line or '}' in line: 
                error("Line defining \"{}\" contains a single curly brace.".format(key))
            return False

        ## Use to get key's value in params. writing always false  
        def valueOf(key, writing = False):
            """gets the value of a key in the parameter dictionary"""
            if (not writing) and (len(params[key]) > 1):
                error("\"{}\" can only correspond to 1 list. {} lists have been defined.".format(key, len(params[key])))
            try:    
                val = params[key][0]
                if val == '' or val == []:
                    error("\"{}\" does not have a value.".format(key))
                return val
            except IndexError:
                error("\"{}\" has not been defined.".format(key)) ## Include assumptions (ie no Angleoption -> degrees?)

        def getGroups(line, valList, key):
            curlyGroup = re.compile('({.*?})')
            groups = re.findall(curlyGroup, line)
            for group in groups:
                line = line.replace(group, '', 1) ## only delete first occurence
                valList.append(curlyToList(group))
                
            if line.strip() != "":
                error("Unexpected character found while parsing \"{}\".".format(key))

        def valHelper(line, valList, key):
            if hasCurlys(line, key):
                getGroups(line, valList, key)
            else:
                valList.append(line)
            
        def error(errString):
            print("\nERROR --- " + errString)
            print("\n----Program terminated while parsing input----\n")
            sys.exit(1)

        def warning(warnString):
            global warningFile
            print("WARNING --- " + warnString)
            warningFile.write("WARNING --- " + warnString + "\n")

        def isNegative(num): 
            return True if num < 0 else False

        ## Makes sure at least one polygon family has been defined in nFamRect or nFamEll
        ##      OR that there is a user input file for polygons. 
        def checkFamCount():
            userDefExists = (valueOf('userEllipsesOnOff') == '1') |\
                       (valueOf('userRectanglesOnOff') == '1') |\
                       (valueOf('userRecByCoord') == '1') |\
                       (valueOf('userEllByCoord') == '1')

            if ellipseFams + rectFams <= 0 and not userDefExists:
                error("Zero polygon families have been defined. Please create at least one family "\
                      "of ellipses/rectagnles, or provide a user-defined-polygon input file path in "\
                      "\"UserEll_Input_File_Path\", \"UserRect_Input_File_Path\", \"UserEll_Input_File_Path\", or "\
                      "\"RectByCoord_Input_File_Path\" and set the corresponding flag to '1'.")

        ## scales list of probabilities (famProb) that doesn't add up to 1
        ## ie [.2, .2, .4] --> [0.25, 0.25, 0.5]        
        def scale(probList):
            total = sum(probList)
            scaled = [float("{:.6}".format(x/total)) for x in probList]
            warning("'famProb' probabilities did not add to 1 and have been scaled accordingly "\
                "for their current sum, {:.6}. Scaled {} to {}".format(total, probList, scaled))
            return [x/total for x in probList]                

        def zeroInStdDevs(valList):
            for val in valList:
                if float(val) == 0: return True
            
        def checkMinMax(minParam, maxParam, shape):
            for minV, maxV in zip(valueOf(minParam), valueOf(maxParam)):
                if minV == maxV:
                    error("\"{}\" and \"{}\" contain equal values for the same {} family. "\
                          "If {} and {} were intended to be the same, use the constant distribution "\
                          "(4) instead.".format(minParam, maxParam, shape, minParam, maxParam, ))
                if minV > maxV:
                    error("\"{}\" is greater than \"{}\" in a(n) {} family.".format(minParam, maxParam, shape))
                    sys.exit()

        def checkMean(minParam, maxParam, meanParam):
            for minV, meanV in zip(valueOf(minParam), valueOf(meanParam)):
                if minV > meanV: 
                    warning("\"{}\" contains a min value greater than its family's mean value in "\
                          "\"{}\". This could drastically increase computation time due to increased "\
                          "rejection rate of the most common fracture sizes.".format(minParam, meanParam))
            for maxV, meanV in zip(valueOf(maxParam), valueOf(meanParam)):
                if maxV < meanV: 
                    warning("\"{}\" contains a max value less than its family's mean value in "\
                          "\"{}\". This could drastically increase computation time due to increased "\
                          "rejection rate of the most common fracture sizes.".format(maxParam, meanParam))

        def checkMinFracSize(valList):
            global minFracSize
            for val in valList:
                if val < minFracSize: minFracSize = val
            
                

        ## ===================================================================== ##
        ##                      Mandatory Parameters                             ##
        ## ===================================================================== ##

        ## Each of these should be called in the order they are defined in to accomadate for dependecies 
        def nFamEll():
            global ellipseFams 
            ## verifyNumValsIs(1, 'nFamEll')
            ellipseFams = verifyInt(valueOf('nFamEll'), 'nFamEll', noNeg = True)
            if ellipseFams == 0:
                warning("You have set the number of ellipse families to 0, no ellipses will be generated.")

        def nFamRect():
            global rectFams
            ## verifyNumValsIs(1, 'nFamRect')
            rectFams = verifyInt(valueOf('nFamRect'), 'nFamRect', noNeg = True)
            if rectFams == 0:
                warning("You have set the number of rectangle families to 0, no rectangles will be generated.")

        def stopCondition():
            ## verifyNumValsIs(1, 'stopCondition')
            if verifyFlag(valueOf('stopCondition'), 'stopCondition') == 0: 
                nPoly()
            else:
                p32Targets()


        def checkNoDepFlags():
            for flagName in noDependancyFlags:
                verifyFlag(valueOf(flagName), flagName)
            

        ## domainSize MUST have 3 non-zero values to define the 
        ## size of each dimension (x,y,z) of the domain 
        def domainSize():
            errResult = verifyList(valueOf('domainSize'), 'domainSize', verifyFloat, desiredLength = 3,
                           noZeros = True, noNegs=True)
            if errResult != None:
                error("\"domainSize\" has defined {} value(s) but there must be 3 non-zero "\
                      "values to represent x, y, and z dimensions".format(-errResult))

        def domainSizeIncrease():
            errResult = verifyList(valueOf('domainSizeIncrease'), domainSizeIncrease, verifyFloat, desiredLength = 3)
            if errResult != None:
                error("\"domainSizeIncrease\" has defined {} value(s) but there must be 3 non-zero "\
                      "values to represent extensions in the x, y, and z dimensions".format(-errResult))

            for i,val in enumerate(valueOf('domainSizeIncrease')):
                if val >= valueOf('domainSize')[i]/2:
                    error("\"domainSizeIncrease\" contains {} which is more than half of the domain's "
                          "range in that dimension. Cannot change the domain's size by more than half of "
                          "that dimension's value defined in \"domainSize\". This risks collapsing or "
                          "doubling the domain.".format(val))

        def numOfLayers():
            global numLayers
            numLayers = verifyInt(valueOf('numOfLayers'), 'numOfLayers', noNeg = True)
            if numLayers > 0:
                if numLayers != len(params['layers']):
                    error("\"layers\" has defined {} layers but \"numLayers\" was defined to "\
                          "be {}.".format(len(params['layers']), numLayers))
                else: layers()

        def layers():
            halfZdomain = params['domainSize'][0][2]/2.0  ## -index[2] becaue domainSize = [x,y,z]
                                      ## -center of z-domain at z = 0 so 
                                      ##  whole Zdomain==-zDomainSize to +zDomainSize
            for i, layer in enumerate(params['layers']):
                errResult = verifyList(layer, "layer #{}".format(i+1), verifyFloat, desiredLength = 2)
                if errResult != None:
                    error("\"layers\" has defined layer #{} to have {} element(s) but each layer must "\
                          "have 2 elements, which define its upper and lower bounds".format(i+1, -errResult))
                if params['layers'].count(layer) > 1:
                    error("\"layers\" has defined the same layer more than once.")
                minZ = layer[0]
                maxZ = layer[1]
                if minZ <= -halfZdomain and maxZ <= -halfZdomain:
                    error("\"layers\" has defined layer #{} to have both upper and lower bounds completely "\
                          "below the domain's z-dimensional range ({} to {}). At least one boundary must be within "\
                          "the domain's range. The domain's range is half of 3rd value in \"domainSize\" "\
                          "(z-dimension) in both positive and negative directions.".format(i+1, -halfZdomain, halfZdomain))
                if minZ >= halfZdomain and maxZ >= halfZdomain:
                    error("\"layers\" has defined layer #{} to have both upper and lower bounds completely "\
                          "above the domain's z-dimensional range ({} to {}). At least one boundary must be within "\
                          "the domain's range. The domain's range is half of 3rd value in \"domainSize\" "\
                          "(z-dimension) in both positive and negative directions.".format(i+1, -halfZdomain, halfZdomain))

             
        def disableFram():
            if verifyFlag(valueOf('disableFram'), 'disableFram') == 0:
                h()

        def seed():
            val = verifyInt(valueOf('seed'), 'seed', noNeg = True)
            if val == 0:
                warning("\"seed\" has been set to 0. Random generator will use current wall "\
                    "time so distribution's random selection will not be as repeatable. "\
                    "Use an integer greater than 0 for better repeatability.")
            params['seed'][0] = val
            

        def ignoreBoundaryFaces():
            if verifyFlag(valueOf('ignoreBoundaryFaces'), 'ignoreBoundaryFaces') == 0:
                boundaryFaces()

        def rejectsPerFracture():
            val = verifyInt(valueOf('rejectsPerFracture'), 'rejectsPerFracture', noNeg = True)
            if val == 0:
                val = 1
                warning("changing \"rejectsPerFracture\" from 0 to 1. Can't ensure 0 rejections.")

            params['rejectsPerFracture'][0] = val 
            
        def famProb():
            errResult = verifyList(valueOf('famProb'), 'famProb', verifyFloat,
                           desiredLength = ellipseFams + rectFams, noZeros = True, noNegs = True)
            if errResult != None:
                error("\"famProb\" must have {} (nFamEll + nFamRect) non-zero elements,"\
                      "one for each family of ellipses and rectangles. {} probabiliies have "\
                      "been defined.".format(ellipseFams + rectFams, -errResult))

            probList = [float(x) for x in valueOf('famProb')]
            if sum(probList) != 1:
                scale(probList)

        def userDefined():
            userEs = "userEllipsesOnOff"
            userRs = "userRectanglesOnOff"
            recByCoord = "userRecByCoord"
            ellByCoord = "userEllByCoord"
            ePath = "UserEll_Input_File_Path"
            rPath = "UserRect_Input_File_Path"
            coordPath = "RectByCoord_Input_File_Path"
            ecoordPath = "EllByCoord_Input_File_Path"
            invalid = "\"{}\" is not a valid path."

            if verifyFlag(valueOf(ellByCoord), ellByCoord) == 1:
                if not os.path.isfile(valueOf(ecoordPath)):
                    error(invalid.format(ecoordPath))
                else:
                    copy(valueOf(ecoordPath), self._jobname)

            if verifyFlag(valueOf(userEs), userEs) == 1:
                if not os.path.isfile(valueOf(ePath)):
                    error(invalid.format(ePath))
                else:
                    copy(valueOf(ePath), self._jobname)
                
            if verifyFlag(valueOf(userRs), userRs) == 1:
                if not os.path.isfile(valueOf(rPath)):
                    error(invalid.format(rPath))
                else:
                    copy(valueOf(rPath), self._jobname)
                
            if verifyFlag(valueOf(recByCoord), recByCoord) == 1:
                if not os.path.isfile(valueOf(coordPath)):
                    error(invalid.format(coordPath))    
                else:
                    copy(valueOf(coordPath), self._jobname)

        def aperture():
            apOption = verifyInt(valueOf('aperture'), 'aperture')

            if apOption == 1:
                if verifyFloat(valueOf('meanAperture'), 'meanAperture', noNeg=True) == 0:
                    error("\"meanAperture\" cannot be 0.")
                if verifyFloat(valueOf('stdAperture'), 'stdAperture', noNeg=True) == 0:
                    error("\"stdAperture\" cannot be 0. If you wish to have a standard deviation "\
                          "of 0, use a constant aperture instead.") 

            elif apOption == 2:
                verifyList(valueOf('apertureFromTransmissivity'), 'apertureFromTransmissivity', 
                       verifyFloat, desiredLength = 2, noNegs=True)
                if valueOf('apertureFromTransmissivity')[0] == 0:
                    error("\"apertureFromTransmissivity\"'s first value cannot be 0.")
                if valueOf('apertureFromTransmissivity')[1] == 0:
                    warning("\"apertureFromTransmissivity\"'s second value is 0, which will result in a constant aperature.")

            elif apOption == 3:
                if verifyFloat(valueOf('constantAperture'), 'constantAperture', noNeg=True) == 0:
                    params['constantAperture'][0] = 1e-25
                    warning("\"constantAperture\" was set to 0 and has been changed "\
                          "to 1e-25 so fractures have non-zero thickness.")

            elif apOption == 4:
                verifyList(valueOf('lengthCorrelatedAperture'), 'lengthCorrelatedAperture', 
                       verifyFloat, desiredLength = 2, noNegs=True)
                if valueOf('lengthCorrelatedAperture')[0] == 0:
                    error("\"lengthCorrelatedAperture\"'s first value cannot be 0.")
                if valueOf('lengthCorrelatedAperture')[1] == 0:
                    warning("\"lengthCorrelatedAperture\"'s second value is 0, which will result in a constant aperature.") 
                    
            else:
                error("\"aperture\" must only be option 1 (log-normal), 2 (from transmissivity), "\
                      "3 (constant), or 4 (length correlated).")

        def permeability():
            if verifyFlag(valueOf('permOption'), 'permOption') == 1:
                if verifyFloat(valueOf('constantPermeability'), 'constantPermeability') == 0:
                    params['constantPermeability'][0] = 1e-25
                    warning("\"constantPermeability\" was set to 0 and has been changed "\
                          "to 1e-25 so fractures have non-zero permeability.")
                    

        ## ========================================================================= ##
        ##                      Non-Mandatory Parameters                             ##
        ## ========================================================================= ##

        def nPoly():
            val = verifyInt(valueOf('nPoly'), 'nPoly', noNeg = True)
            if val == 0: error("\"nPoly\" cannot be zero.")
            params['nPoly'][0] = val

        def p32Targets():
            global ellipseFams, rectFams
            errResult = None if (ellipseFams == 0) else verifyList(valueOf('e_p32Targets'), 'e_p32Targets', \
                                      verifyFloat, desiredLength =  ellipseFams, noNegs=True, noZeros=True)
            if errResult != None:
                error("\"e_p32Targets\" has defined {} p32 values but there is(are) {} ellipse family(ies). "\
                      "Need one p32 value per ellipse family.".format(-errResult, ellipseFams))

            errResult = None if (rectFams == 0) else verifyList(valueOf('r_p32Targets'), "r_p32Targets", \
                                    verifyFloat, desiredLength =  rectFams, noNegs=True, noZeros=True)
            if errResult != None:
                error("\"r_p32Targets\" has defined {} p32 value(s) but there is(are) {} rectangle "\
                      "family(ies). Need one p32 value per rectangle family)".format(-errResult, rectFams))

        def f(theta, t, a, b):
            return 1.0/np.sqrt( (a*np.sin(theta))**2 + (b*np.cos(theta)**2))

        def h_shapeCheck(aspect, minRadius, num_points=4):
            # Major and Minor Axis of Ellipse
            ## aspect = 1.0 ## param
            r = minRadius

            ## TODO check > 3h 
            a = aspect
            b = 1.0

            # approximation of total arclength
            c = np.pi*(a + b)*(1.0 + (3.0*  ((a - b)/(a + b))**2)/(10. + np.sqrt(4. - 3.* ((a - b)/(a + b))**2)))

            #number of points
            n = num_points
            # expected arclength
            ds = c/n

            # array of steps
            steps = np.linspace(0,c,n+1)
            # Numerically integrate arclength ODE
            theta = odeint(f, 0, steps, args=(a, b), rtol = 10**-10)

            # Convert theta to x and y
            x = a*r*np.cos(theta)
            y = b*r*np.sin(theta)

            # Check Euclidean Distance between consectutive points
            h_min = 99999999999
            for i in range(1,n):
                for j in range(i,n):
                    if (i != j):
                        h_current =np.sqrt((x[i] - x[j])**2 + (y[i] - y[j])**2) 
                        if (h_current < h_min):
                            h_min = h_current

            return h_min

        def comparePtsVSh(prefix, hval):
            shape = "ellipse" if prefix=='e' else "rectangle"
            aspectList = params[prefix+"aspect"][0]
            numPointsList = None

            if shape == "ellipse":
                numPointsList = params['enumPoints'][0]
                
            ## indicies for each list as we check for ellipse generating features less than h
            numLog = 0
            numTPL = 0
            numEXP = 0
            numConst = 0
            numAspect = 0

            for distrib in params[prefix+'distr'][0]:
                if distrib in [1,2,3,4]:
                    if distrib == 1:
                        minRad = params[prefix+'LogMin'][0][numLog]
                        numLog += 1
                    elif distrib == 2:
                        minRad = params[prefix+'min'][0][numTPL]
                        numTPL += 1
                    elif distrib == 3:
                        minRad = params[prefix+'ExpMin'][0][numEXP]
                        numEXP += 1
                    elif distrib == 4:
                        minRad = params[prefix+'const'][0][numConst]
                        numConst += 1  
                    if shape == "ellipse":
                        hmin = h_shapeCheck(float(aspectList[numAspect]), float(minRad), int(numPointsList[numAspect]))
                    else:
                        hmin = h_shapeCheck(float(aspectList[numAspect]), float(minRad)) ## dont need numPoints for rectangle, default 4

                    if hmin < (3 * hval):
                        error(shape + " family #{} has defined a shape with features too small for meshing. Increase the aspect "\
                                 "ratio or minimum radius so that no 2 points of the polygon create a line of length less "\
                                 "than 3h".format(numAspect+1))
                         
                    numAspect += 1 ## this counts the family number 

        def h():
            val = verifyFloat(valueOf('h'), 'h', noNeg=True)
            if val == 0: error("\"h\" cannot be 0.")
            if val < minFracSize/1000.0 and ellipseFams + rectFams > 0: ####### NOTE ----- future developers TODO, delete the 
                                            ## "and ellipseFams + rectFams > 0" once you are also
                                            ## checking the userInput Files for minimums that could be 
                                            ## "minFracSize".  "minFracSize"==initialized to 99999999 so if no 
                                            ## ellipse/rect fams are defined and the only polygons come from user 
                                            ## Input, the warning message says the min Frac size is 99999999 
                                            ## since it never gets reset by one of the distribution minima.  
                warning("\"h\" (length scale) is smaller than one 1000th of the minimum "\
                      "fracture size ({}). The generated mesh will be extremely fine and will likely be "\
                      "computationally exhausting to create. Computation may take longer than usual.".format(minFracSize))
            if val > minFracSize/10.0:
                warning("\"h\" (length scale) is greater than one 10th of the minimum "\
                      "fracture size ({}). The generated mesh will be very coarse and there will likely "\
                      "be a high rate of fracture rejection.".format(minFracSize))

            comparePtsVSh('e',val)
            comparePtsVSh('r',val)
            
            params['h'][0] = val


        ## Must be a list of flags of length 6, one for each side of the domain
        ## ie {1, 1, 1, 0, 0, 1} represents --> {+x, -x, +y, -y, +z, -z}
        ## DFN only keeps clusters with connections to domain boundaries set to 1
        def boundaryFaces():
            errResult = verifyList(valueOf('boundaryFaces'), 'boundaryFaces', verifyFlag, 6)
            if errResult != None:
                error("\"boundaryFaces\" must be a list of 6 flags (0 or 1), {} have(has) been defined. Each flag "\
                      "represents a side of the domain, {{+x, -x, +y, -y, +z, -z}}.".format(-errResult))

        def enumPoints():
            errResult = verifyList(valueOf('enumPoints'), 'enumPoints', verifyInt, 
                           desiredLength=ellipseFams, noZeros=True, noNegs=True)
            if errResult != None:
                error("\"enumPoints\" has defined {} value(s) but there is(are) {} families of ellipses. Please "\
                      "define one enumPoints value greater than 4 for each ellipse family.".format(-errResult, ellipseFams))
            for val in valueOf("enumPoints"):
                if val <= 4:
                    error("\"enumPoints\" contains a value less than or equal to 4. If 4 points were intended, "\
                          "define this family as a rectangle family. No polygons with less than 4 verticies are acceptable.")


        ## ========================================================================= ##
        ##                      Generalized Mandatory Params                         ##
        ## ========================================================================= ##
                ###                                                ### 
                ###        Prefix MUST be either 'e' or 'r'        ### 
                ###                                                ###  
                ### ============================================== ###        


        def aspect(prefix):
            shape = "ellipse" if prefix=='e' else "rectangle"
            numFamilies = ellipseFams if prefix=='e' else rectFams
            paramName = prefix + "aspect"

            errResult = verifyList(valueOf(paramName), paramName, verifyFloat, 
                    desiredLength = numFamilies, noZeros = True, noNegs = True)
            if errResult != None:
                error("\"{}\" has defined {} value(s) but there is(are) {} {} families. Please define one "\
                      "aspect ratio for each family.".format(paramName, -errResult, numFamilies, shape))

        def angleOption(prefix):
            paramName = prefix + "AngleOption"
            verifyFlag(valueOf(paramName), paramName)

        def layer(prefix):
            shape = "ellipse" if prefix=='e' else "rectangle"
            numFamilies = ellipseFams if prefix=='e' else rectFams
            paramName = prefix + "Layer"

            errResult = verifyList(valueOf(paramName), paramName, verifyInt, desiredLength = numFamilies)
            if errResult != None:
                error("\"{}\" has defined {} layer(s) but there is(are) {} {} families. "\
                      "Need one layer per {} family. Layers are numbered by the order they "\
                      "are defined in 'layers' parameter. Layer 0 is the whole domain."\
                      .format(paramName, -errResult, numFamilies, shape, shape))

            for layer in valueOf(paramName):
                if isNegative(int(layer)):
                    error("\"{}\" contains a negative layer number. Only values from 0 to "\
                          "{} (numOfLayers) are accepted. Layer 0 corresponds to the entire"\
                          "domain.".format(paramName, numLayers))
                if int(layer) > numLayers:
                    error("\"{}\" contains value '{}' but only {} layer(s) is(are) defined. Make sure the "\
                          "layer numbers referenced here are found in that same postion in \"layers\" "\
                          "parameter.".format(paramName, layer, numLayers))

        def thetaPhiKappa(prefix):
            shape = "ellipse" if prefix=='e' else "rectangle"
            numFamilies = ellipseFams if prefix=='e' else rectFams
            paramNames = [prefix + name for name in ["theta", "phi", "kappa"]]
            errString = "\"{}\" has defined {} angle(s) but there is(are) {} {} family(ies)."\
                    "Please defined one angle for each {} family."
            
            for param in paramNames:
                errResult = verifyList(valueOf(param), param, verifyFloat, desiredLength = numFamilies)
                if errResult != None:
                    error(errString.format(param, -errResult, numFamilies, shape, shape))


        ## ========================================================================= ##
        ##                        Generalized Distributions                          ##
        ## ========================================================================= ##
                ###                                                ### 
                ###        Prefix MUST be either 'e' or 'r'        ### 
                ###                                                ### 
                ### ============================================== ###        

        ## Verifies both the "ebetaDistribution" and "rBetaDistribution". If either contain any flags
        ## indicating contant angle (1) then the corresponding "ebeta" and/or "rbeta" parameters are 
        ## also verified. 
        def betaDistribution(prefix):
            shape = "ellipse" if prefix=='e' else "rectangle"
            numFamilies = ellipseFams if prefix=='e' else rectFams
            paramName = prefix + "betaDistribution"

            errResult = verifyList(valueOf(paramName), paramName, verifyFlag, desiredLength = numFamilies)
            if errResult != None:
                error("\"{}\" has defined {} value(s) but there is(are) {} {} family(ies). Need one "\
                      "flag (0 or 1) per {} family.".format(paramName, -errResult, numFamilies, shape, shape))

            numBetas = valueOf(paramName).count(1) ## number of 1's in list
            if numBetas == 0: return

            betaParam = prefix + "beta"
            errResult = verifyList(valueOf(betaParam), betaParam, verifyFloat, desiredLength = numBetas)
            if errResult != None:
                error("\"{}\" defined {} constant angle(s) but {} flag(s) was(were) set to 1 "\
                      "in {}. Please define one constant angle (beta value) for each flag set "\
                      "to 1 in \"{}\"".format(betaParam, -errResult, numBetas, paramName, paramName))


        ## Verifies "edistr" and "rdistr" making sure one disrtibution is defined per family and
        ## each distribution is either 1 (log-normal), 2 (Truncated Power Law), 3 (Exponential), or 4 (constant).
        ## 
        ## Stores how many of each distrib are in use in numEdistribs or numRdistribs lists  
        def distr(prefix):
            shape = "ellipse" if prefix=='e' else "rectangle"
            distribList = numEdistribs if prefix=='e' else numRdistribs
            numFamilies = ellipseFams if prefix=='e' else rectFams
            paramName = prefix + "distr"

            errResult = verifyList(valueOf(paramName), paramName, verifyInt, desiredLength = numFamilies)
            if errResult != None:
                error("\"{}\" has defined {} distributions but there are {} {} families. " \
                    "Need one distribution per family (1 = lognormal, 2 = Truncated Power Law, "
                    "3 = Exponential, or 4 = constant).".format(paramName, -errResult, numFamilies, shape)) 
            try:
                for dist in valueOf(paramName):
                    if int(dist) <= 0: raise IndexError()
                    distribList[int(dist)] += 1  
            except IndexError:
                error("\"{}\" contains '{}' which is not a valid distribution option. " \
                       "Only values 1 through 4 can define a family's distribution (1 = lognormal, " \
                       "2 = Truncated Power Law, 3 = Exponential, or 4 = constant).".format(paramName, dist))


        # prefix- "e" or "r"
        ## Verifies all logNormal Paramters for ellipses and Rectangles        
        def lognormalDist(prefix):
            shape = "ellipse" if prefix=='e' else "rectangle"
            distribList = numEdistribs if prefix=='e' else numRdistribs
            paramNames = [prefix + name for name in ["LogMean", "sd", "LogMin", "LogMax"]]
            errString = "\"{}\" has defined {} value(s) but {} lognormal distrbution(s) was(were) " \
                    "defined in \"{}\". Please define one value for each lognormal (distrib. #1) family."

            for param in paramNames:
                zTmp = True if "sd" not in param else False  ## Turns off noZeros check only for 'sd' for better error msg
                errResult = verifyList(valueOf(param), param, verifyFloat, desiredLength = distribList[1],
                            noZeros = zTmp, noNegs = True)         
                if errResult != None:
                    error(errString.format(param, -errResult, distribList[1], prefix+'distr'))

            sdParam = prefix + "sd"
            if zeroInStdDevs(valueOf(sdParam)): 
                error("\"{}\" list contains a standard deviation of 0. If this was intended, " \
                    "use the constant distribution (4) instead. Otherwise, _make sure \"{}\" " \
                    "only contains values greater than 0.".format(sdParam, sdParam))

            checkMinMax(prefix+"LogMin", prefix+"LogMax", shape)
            checkMean(prefix+"LogMin", prefix+"LogMax", prefix+"LogMean")
            checkMinFracSize(valueOf(prefix+"LogMin"))
            
            #HERE, check that the parameters given will not produce fractures larger than twice the domain size
            for i in range(0, len(valueOf('rLogMean'))):
                lgn_mean = valueOf('rLogMean')[i] 
                lgn_standard_deviation = valueOf('rsd')[i]
                domain_size = max(params['domainSize'][0]) 
                print 'domain size is ', domain_size
                print 'lgn_standard_deviation is ', lgn_standard_deviation
                print 'lgn_mean is ', lgn_mean
                if (lgn_mean + 3.5*lgn_standard_deviation > np.log(2 * domain_size)):        
                    error("The user inputs for the lognormal distribution (mean = %02d, standard deviation = %02d)," \
                         "  allow the generator to create fractures with lengths  greater than two times the" \
                         "    domain size (%02d m)."% (lgn_mean, lgn_standard_deviation, domain_size))        

        #r Truncated Power Law Distribution
        def tplDist(prefix):
            shape = "ellipse" if prefix=='e' else "rectangle"
            distribList = numEdistribs if prefix=='e' else numRdistribs
            paramNames = [prefix + name for name in ["min", "max", "alpha"]]
            errString = "\"{}\" has defined {} value(s) but {} truncated power-law distrbution(s) was(were) " \
                    "defined in \"{}\". Please define one value for each truncated power-law (distrib. #2) family."

            for param in paramNames:
                errResult = verifyList(valueOf(param), param, verifyFloat, desiredLength = distribList[2], 
                            noZeros = True, noNegs = True)
                if errResult != None:
                    error(errString.format(param, -errResult, distribList[2], prefix+'distr'))
                    
            checkMinMax(prefix+"min", prefix+"max", shape)
            checkMinFracSize(valueOf(prefix+"min"))
            

        def exponentialDist(prefix):
            shape = "ellipse" if prefix=='e' else "rectangle"
            distribList = numEdistribs if prefix=='e' else numRdistribs
            paramNames = [prefix + name for name in ["ExpMean", "ExpMin", "ExpMax"]]
            errString = "\"{}\" has defined {} value(s) but {} exponential distrbution(s) was(were) " \
                    "defined in \"{}\". Please define one value for each exponential (distrib. #3) family."

            for param in paramNames:
                errResult = verifyList(valueOf(param), param, verifyFloat, desiredLength = distribList[3], 
                            noZeros = True, noNegs = True)
                if errResult != None:
                    error(errString.format(param, -errResult, distribList[3], prefix+'distr'))
                    
            checkMinMax(prefix+"ExpMin", prefix+"ExpMax", shape)
            checkMean(prefix+"ExpMin", prefix+"ExpMax", prefix+"ExpMean")
            checkMinFracSize(valueOf(prefix+"ExpMin"))

        def constantDist(prefix):
            paramName = prefix + "const"
            numFamilies = ellipseFams if prefix=='e' else rectFams
            distribList = numEdistribs if prefix=='e' else numRdistribs

            errResult = verifyList(valueOf(paramName), paramName, verifyFloat, desiredLength = distribList[4],
                         noZeros = True, noNegs = True)
            if errResult != None:
                error("\"{}\" has defined {} value(s) but {} constant distrbution(s) was(were) " \
                      "defined in \"{}\". Please define one value for each family with a constant (distrib. "\
                      "#4) distribution.".format(paramName, -errResult, distribList[4], prefix + 'distr'))
             
            checkMinFracSize(valueOf(paramName))
            

        ## ========================================================================= ##
        ##                      Main for I/O Checkin and Writing                     ##
        ## ========================================================================= ##
###
#        def checkIOargs(ioPaths):
#            try:
#                ioPaths["input"] = sys.argv[1]
#            except IndexError:
#                error("Please provide an input file path as the first command line argument.\n"\
#                      "    $ python3 inputParser.py [inputPath] [outputPath (Optional)]")
#
#            try:
#                ioPaths["output"] = sys.argv[2]
#            except IndexError:
#                ioPaths["output"] = "polishedOutput.txt"
#                warning("No output path has been provided so output will be written to "\
#                    "\"polishedOutput.txt\" in your current working directory.")
#
        def parseInput():
            for line in inputIterator:
                line = extractParameters(line) ## this strips comments
                if (line != "" and ":" in line):
                    processLine(line)
            needed = [unfound for unfound in unfoundKeys if unfound in mandatory]
            if needed != []:
                errString = ""
                for key in needed: errString += "\t\"" + key + "\"\n"
                error("Missing the following mandatory parameters: \n{}".format(errString))    
         
            
        def verifyParams():
            firstPriority = [nFamEll, nFamRect, stopCondition, domainSize, numOfLayers, 
                     seed, domainSizeIncrease, ignoreBoundaryFaces, rejectsPerFracture, 
                     userDefined, checkFamCount, checkNoDepFlags, famProb]
            generalized = [layer, aspect, angleOption, thetaPhiKappa, betaDistribution, distr]
            distribs = [lognormalDist, tplDist, exponentialDist, constantDist]
            checkLast = [disableFram, aperture, permeability]
            
            for paramFunc in firstPriority: paramFunc()

            if rectFams > 0:
                for paramFunc in generalized: paramFunc('r')  
            if ellipseFams > 0:
                enumPoints()
                for paramFunc in generalized: paramFunc('e')              

            for i, paramFunc in enumerate(distribs):
                if numEdistribs[i+1] > 0: paramFunc('e') ## only call if there have been 1+ of a distrib defined
                if numRdistribs[i+1] > 0: paramFunc('r') ## +1 for reason stated in list instantiation above
                
            for paramFunc in checkLast: paramFunc()

        def writeBack():
            for param in params:
                if param == 'layers':
                    writer.write(param + ': ')
                    for layer in params['layers']:
                        writer.write(listToCurly(str(layer)) + " ")
                    writer.write('\n')    
                elif type(valueOf(param, writing=True))==list:
                    curl = listToCurly(str(valueOf(param, writing = True)))
                    writer.write(param + ': ' + curl + '\n')
                else:
                    writer.write(param + ': ' + str(valueOf(param, writing=True)) + '\n')              
            
        print '--> Checking input files'    
        try:
            copy(self._dfnGen_file, './')
        except:
            sys.exit("Unable to copy dfnGen input file\n%s\nExiting"%self._dfnGen_file)

        ioPaths = {"input":"", "output":""}
        try:
            ioPaths["input"] = self._local_dfnGen_file
        except IndexError:
            error("Please provide an input file path as the first command line argument.\n"\
                  "    $ python3 inputParser.py [inputPath] [outputPath (Optional)]")
        try:
            ioPaths["output"] = self._local_dfnGen_file[:-4]+'_clean.dat'
        except IndexError:
            ioPaths["output"] = "polishedOutput.txt"
            warning("No output path has been provided so output will be written to "\
                "\"polishedOutput.txt\" in your current working directory.")
        try:
            reader = open(ioPaths["input"], 'r')
            writer = open(ioPaths["output"], 'w')
            inputIterator = iter(reader)
        except:
            error("Check that the path of your input file is valid.")
          
        print '--> Checking input data'
        print '--> Input Data: ', ioPaths["input"] 
        print '--> Output File: ',ioPaths["output"] 
 
        parseInput()
        verifyParams()
        writeBack()

        print '--> Checking Input Data Complete'

    def create_network(self):
        print '--> Running DFNGEN'    
        # copy input file into job folder    
        os.system(os.environ['DFNGENC_PATH']+'/./DFNGen ' + self._local_dfnGen_file[:-4] + '_clean.dat' + ' ' + self._jobname )
        os.chdir(self._jobname)
        if os.path.isfile("params.txt")==False:
            print '--> Generation Failed'
            print '--> Exiting Program'
            exit()
        else:
            print('-'*80)
            print("Generation Succeeded")
            print('-'*80)

    def mesh_network(self, ncpu = ''):
        """
        Mesh Fracture Network using ncpus and lagrit
        meshing file is seperate file: dfnGen_meshing.py
        """
        print('='*80)
        print("Meshing Network Using LaGriT : Starting")
        print('='*80)
        production_mode = 1
        refine_factor = 1    
        
        nPoly, h, visualMode, dudded_points  = mesh.parse_params_file()
        self._num_frac = nPoly
        tic2 = time()
        mesh.create_parameter_mlgi_file(nPoly, h)
        mesh.create_lagrit_scripts(production_mode, self._ncpu, refine_factor, visualMode)
        failure = mesh.mesh_fractures_header(nPoly, self._ncpu, visualMode)
        self.dump_time('Process: Meshing Fractures', time() - tic2)
        if failure > 0:
            mesh.cleanup_dir()
            print 'Exiting Program due to mesh failure'
            sys.exit(1)
        
        tic2 = time()
        n_jobs = mesh.create_merge_poly_files(self._ncpu, nPoly, visualMode)

        mesh.merge_the_meshes(nPoly, self._ncpu, n_jobs, visualMode)
        self.dump_time('Process: Merging the Mesh', time() - tic2)    

        if(visualMode == 0):    
            if (mesh.check_dudded_points(dudded_points) == False):
                print 'Exiting Program due to mesh dudded points failure'
                cleanup_dir()
                sys.exit(1)
    
        if production_mode > 0:
            mesh.cleanup_dir()
        if(visualMode == 0): 
            mesh.redefine_zones(h)

        mesh.output_meshing_report(visualMode)
        print ('='*80)
        print("Meshing Network Using LaGriT : Complete")
        print ('='*80)

    def output_report(self, radiiFile = 'radii.dat', famFile ='families.dat', transFile='translations.dat', rejectFile = 'rejections.dat', output_name = ''):
        """
        Create PDF report of generator 
        Notes
        1. Set the number of histogram buckets (bins) by changing numBuckets variable in his graphing functions
        2. Also change number of x-values used to plot lines by changing numXpoints variable in appropriate funcs
        3. Set show = True to show plots immediately and still make pdf
        4. NOTE future developers of this code should ass functionality for radiiList of size 0. 

        
        """
        #TODO: Throw specific error if X forwarding is not on
        if ('DISPLAY' not in os.environ):
            print 'ERROR: To output the PDF report of DFNGen, you must have X forwarding turned on'
            exit()

        print '--> Creating Report of DFN generation'
        families = {'all':[], 'notRemoved':[]} ## families['all'] contains all radii.   
                               ## families['notRemoved'] contains all non-isolated fractures. 
                               ##   Isolated fracs get radiiList, distrib, infoStr, parameters):
        output_name = self._local_jobname + '_output_report.pdf'
        print 'Writing output into: ', output_name
        outputPDF = PdfPages(output_name) ## TODO to make this cmd line option --> outputPDF = PdfPages(sys.argv[5])
        show = False ## Set to true for showing plots immediately instead of having to open pdf. Still makes pdf
    
        class polyFam:
            def __init__(self, globFamNum, radiiList, distrib, infoStr, parameters):
                self.globFamNum = globFamNum
                self.radiiList = radiiList
                self.distrib = distrib
                self.infoStr = infoStr
                self.parameters = parameters

            def printPolyFam(self):
                print("famNum:\n", self.globFamNum)
                print("\nradiiList:\n",self.radiiList)
                print("\ndistrib:\n", self.distrib)
                print("\ninfoStr:\n", self.infoStr)
                print("\nparameters:\n", self.parameters)
                print("\n\n")
                   

        ## Rejection File line format:   "118424 Short Intersections" --> {"Short Intersections": 118424}
        def graphRejections():
            rejects = {}
            plt.subplots()

            for line in open(rejectFile):
                num = int(line[:line.index(" ", 0)]) ## number comes before first space in line
                name = line[line.index(" ", 0) + 1:].strip() ## name comes after first space
                midSpaceIndex = 1
                while midSpaceIndex < len(name) / 2 and " " in name[midSpaceIndex+1:]: ## cut long names in half
                    midSpaceIndex = name.index(" ", midSpaceIndex + 1)
                name = name[:midSpaceIndex] + "\n" + name[midSpaceIndex+1:]
                rejects[name] = num
            
            totalRejects = float(sum(rejects.values())) 
            figWidth = max(rejects.values()) * 1.25 ## make width 25% bigger than biggest val
            labelOffset = figWidth * 0.02 if figWidth != 0 else 0.05   
            offset = 2
            h = 0.35   # height of horiz bar (vertical thickness)

            horizBar = plt.barh(np.arange(len(rejects)) + offset, rejects.values(), height=h, align='center')
            plt.yticks(np.arange(len(rejects)) + offset, rejects.keys(), fontsize=6)
            plt.title("Rejection Reasons", fontsize=18)
            plt.xlim(xmin=0, xmax=figWidth if figWidth != 0 else 1)        

            for bar in horizBar:
                width = bar.get_width()
                if width != 0:
                    label = '{0:d}\n{1:.2f}%'.format(int(width), width / totalRejects * 100)
                else: label = 0
                plt.text(bar.get_width()+labelOffset, bar.get_y()+h/2.0, label, va='center', fontsize=10)

            plt.gcf().subplots_adjust(right=0.98)
            plt.savefig(outputPDF, format='pdf')
            if show: plt.show()


        ## Histogram making helper function for graphTranslations()
        def transHist(prefix, allList, unRemovedList):
            plt.subplots()
            numBuckets = 20
            minSize = min(allList)
            maxSize = max(allList)
            plt.hist(allList, bins=numBuckets, color='b', range=(minSize, maxSize), alpha=0.7, 
                 label='All Fractures\n(Connected and Unconnected')
            plt.hist(unRemovedList, bins=numBuckets, color='r', range=(minSize, maxSize), alpha=0.7, 
                 label='Non-isolated fractures (connected)')
            plt.title(prefix + "-Position Distribution")
            plt.xlabel("Fracture Position (Spatial Coordinate)")
            plt.ylabel("Number of Fractures")
            plt.legend(loc="upper center")
            plt.savefig(outputPDF, format='pdf')
            if show: plt.show()

        ## Graphs position of fractures as histogram for x, y and z dimensions
        ## Input file format:    Xpos Ypos Zpos (R) [R is optional, indicates it was removed due to isolation]
        def graphTranslations():
            xAll = []
            xUnremoved = []
            yAll = []
            yUnremoved = []
            zAll = []
            zUnremoved = []
            
            for line in open(transFile):
                line = line.split(" ")
                try:
                    xAll.append(float(line[0]))
                    yAll.append(float(line[1]))
                    zAll.append(float(line[2].strip()))
                    if len(line) < 4:           ## no 'R' at end of line 
                        xUnremoved.append(float(line[0]))
                        yUnremoved.append(float(line[1]))
                        zUnremoved.append(float(line[2].strip()))                 
                except ValueError:
                    continue

            transHist('X', xAll, xUnremoved)
            transHist('Y', yAll, yUnremoved)
            transHist('Z', zAll, zUnremoved)
            

        def collectFamilyInfo():
            famObj = polyFam(0, [], 0, "", {})
            possibleParams = ["Mean", "Standard Deviation", "Alpha", "Lambda"]
            bounds = ["Minimum Radius", "Maximum Radius"]

            for line in open(famFile):
                if line.strip() == "":
                    if famObj.distrib == "Constant":
                        famObj.infoStr += "\nConstant distribution, only contains one radius size.\n"\
                                   "No distribution graphs will be made for this family."

                    famObj = polyFam(0, [], 0, "", {}) ## create new famObj for next family
                
                else:   ## append all info to info sting 
                    famObj.infoStr += line

                if "Global Family" in line:
                    ## input format:     Global Family 1
                    famNum = line[line.index("y") + 1:].strip()
                    famObj.globFamNum = famNum
                    families[famNum] = famObj
                elif "Distribution:" in line:
                    ## input format:     Distribution: "distribution name"
                    famObj.distrib = line[line.index(":") + 1:].strip()
                elif ":" in line and line[:line.index(":")].strip() in possibleParams:
                    ## if one of the distribution param names is in the line, 
                    ##   match the name to the value and store in parameters attribute
                    ## Mean: 0.5 ----> famObj.parameters["Mean"] = 0.5
                    paramList = line.split(":")
                    famObj.parameters[paramList[0].strip()] = float(paramList[1].strip())
                elif ":" in line and line[:line.index(":")].strip() in bounds:
                    ## get min/max radius & convert 10m -> 10
                    paramList = line.split(":")            
                    famObj.parameters[paramList[0]] = float(re.sub("m", "", paramList[1]).strip())

                ## ======== Jeffrey, this==where you can add the family building parser code ====== #
                ## elif ":" in line:
                ##          paramList = line.split(":")
                ##          family parameter name = paramList[0]
                ##          parameter value = paramList[1]
                ## 
                ## Just add all necessary attributes to the polyFam class and you should be good to go

            ## Also add each object to global and not Removed if not empty
            ## input file's line format:   xRadius yRadius Family# Removed (Optional)

            
        
            for line in open(radiiFile):
                try:
                    elems = line.split(' ')
                    radius = float(elems[0])
                    famNum = elems[2].strip()
                    families['all'].append(radius)
                    if len(elems) < 4:              ## len = 4 when 'R' is on line
                        families['notRemoved'].append(radius)                
                    if famNum not in families and famNum >= 0:
                        families[famNum].radiiList = [radius]
                    elif famNum not in families and famNum == -1:
                        families['userDefined'].radiiList = [radius]
                    elif famNum == -1:
                        families['userDefined'].radiiList.append(radius)
                    else:
                        families[famNum].radiiList.append(radius)
                except ValueError:
                    continue
            
            for fam in families:
                if fam != 'all' and fam != 'notRemoved':
                    pass # families[fam].printPolyFam()


        ############# Histogram & PDF ##############
        ## histogram of sizes (from data) and PDF (from input parameters
        ## returns histHeights (height of all hist bars) for plotting cdf
        ##         & list of x values of binCenters (also for cdf)
        def histAndPDF(radiiSizes, pdfArray, xmin, xmax, xVals):
            numBuckets = 100
            fig, histo = plt.subplots()
            ### fig = plt.figure(figsize=(8., 6.), dpi=500)  ## comment out if you dont want pdf
            ## histo = plt.ax_stack()

            ## plot hist, set xtick labels
            histHeights, binEdges, patches = histo.hist(radiiSizes, numBuckets, normed=1, color='r',
                                        alpha=0.75, label='Empirical data')
            binCenters = [((binEdges[x] + binEdges[x+1]) / 2.0) for x in range(len(binEdges)-1)] ## need for cdf
                     ## ^ -1 to prevent Index Error when calculating last bin Center
        #    histo.set_xsticks(binEdges)
            histo.set_xticks(binEdges[0:len(binEdges)/10:-1])
            histo.locator_params(tight = True, axis = 'x', nbins = numBuckets/8.0) ## num of axis value labels
            histo.xaxis.set_major_formatter(FormatStrFormatter('%0.1f'))
            
            ## now plot pdf over histogram
            plt.plot(xVals, pdfArray, 'k', linewidth=4, label='Analytical PDF from input parameters')
            plt.xlabel("Fracture Radius")
            plt.ylabel("Probability Density")
            plt.legend()
            plt.grid()
            plt.tight_layout()
            plt.subplots_adjust(top=0.87)

            return histHeights, binCenters

        ############# CDF ##############
        ## 2 cdfs, analytical (from pdf from given mu and sigma) and empirical (from histogram)
        def cdfs(histHeights, binCenters, pdf, xmin, xmax, xVals):
            plt.subplots()
            analyticCDF = 1. * np.cumsum(pdf) / sum(pdf)      
            empiricalCDF = 1. * np.cumsum(histHeights) / sum(histHeights) ## need these to correspond to xVals
            plt.plot(xVals, analyticCDF, 'b', label='Analytic CDF (from input)')
            plt.plot(binCenters, empiricalCDF, 'r', label='Empirical CDF (from data)')
            plt.title("CDF of Empirical Data & Analytical PDF from Input Parameters")
            plt.legend(loc="lower right")
            plt.xlabel("Fracture Size")
            plt.ylabel("Probability Density")
            plt.grid()
            plt.tight_layout()
            plt.subplots_adjust(top=0.9)

        ############# Q & Q  ##############
        ## histogram values (x) vs. analytical PDF values (y) & a line showing ideal 1 to 1 ratio
        def qq(trueVals, histHeights):
            fig, ax = plt.subplots()
            qq = plt.scatter(histHeights, trueVals, c='r', marker='o', 
                     label="x=Empirical value\ny=Analytical PDF value")
            minMax = [np.min([min(trueVals), min(histHeights)]),  # min of both axes
                  np.max([max(trueVals), max(histHeights)])]  # max of both axes
            plt.plot(minMax, minMax, 'k-', alpha=0.75, zorder=0, label="y/x = 1") ## 1 to 1 ratio for reference
            plt.legend(loc="lower right")
            plt.title("Q-Q Plot of Data vs.Analytical Distrbution At Same Point (Bin Center)")
            plt.xlabel("Probability Density of Data")
            plt.ylabel("Probability Density on Analytical PDF")
            plt.grid()
            plt.tight_layout()
            plt.subplots_adjust(top=0.9)

        def lognormCDF(x, mu, sigma):
            return 0.5 + (0.5 * scipy.special.erf( (np.log(x) - mu) / (np.sqrt(2) * sigma) ) )
        
        def getLogNormPDF(xVals, sigma, mu):
            pdfVals = []
            pi = 3.141592653589793
            for x in xVals:
                first_term = 1 / (sigma*x*np.sqrt(2*pi))
                exp_num = -math.pow(np.log(x) - mu, 2.0)
                exp_denom = 2*math.pow(sigma, 2.0) 
                currentVal = first_term * np.exp(exp_num/exp_denom)
                pdfVals.append(currentVal)
            return pdfVals

        def graphLognormal(famObj):
            if (len(famObj.radiiList) == 0):
                print 'WARNING: Lognormal distribution with num  ', famObj.globFamNum, ' has no fractures:not graphing'
                return
            numXpoints = 1000
            mu, sigma = famObj.parameters["Mean"], famObj.parameters["Standard Deviation"]
            #xmin = max(min(famObj.radiiList), mu - 2.5*sigma ) ##parameters["Minimum Radius"] Use list max because distrib doesnt always get
            #xmax = min(max(famObj.radiiList), mu + 2.5*sigma ) ##parameters["Maximum Radius"]   the desired max value.
            xmin = min(famObj.radiiList)
            xmax = max(famObj.radiiList)    
            
            xVals = np.linspace(xmin, xmax, numXpoints)
            normConstant = 1.0
            try:       
                normConstant = 1.0 / (lognormCDF(xmax, mu, sigma) - lognormCDF(xmin, mu, sigma))
            except ZeroDivisionError: ## happens when there is only one fracture in family so ^ has 0 in denominator
                pass  
            #lognormPDFVals = [x * normConstant for x in lognorm.pdf(xVals, sigma, loc=mu)]
            lognormPDFVals = [x * normConstant for x in getLogNormPDF(xVals, sigma, mu)]

            histHeights, binCenters = histAndPDF(famObj.radiiList, lognormPDFVals, xmin, xmax, xVals) 
            plt.title("Histogram of Obtained Radii Sizes & Lognormal Distribution PDF."\
                  "\nFamily #" + famObj.globFamNum)
            plt.savefig(outputPDF, format='pdf')
            if show: plt.show()

            cdfs(histHeights, binCenters, lognormPDFVals, xmin, xmax, xVals)
            plt.savefig(outputPDF, format='pdf')
            if show: plt.show()
            
            trueVals = getLogNormPDF(binCenters, sigma, mu) 
            #trueVals = [lognorm.pdf(binCenters[i], sigma, loc=mu) for i in range(len(binCenters))]
            qq(trueVals, histHeights)
            plt.savefig(outputPDF, format='pdf')
            if show: plt.show()
          
              
        def powLawPDF(normConst, xmin, x, a):
            return normConst * ( (a*(xmin**a)) / float(x**(a+1)) ) 

        def powLawCDF(x, xmin, a):
            return 1 - ( (xmin / float(x))**a ) 

        def graphTruncPowerLaw(famObj):
            if (len(famObj.radiiList) == 0):
                print 'WARNING: truncPowerLaw family with num ', famObj.globFamNum, ' has no fractures; not graphing'
                return
            numBuckets = 100
            numXpoints = 1000
            alpha = famObj.parameters["Alpha"]
            radiiSizes = famObj.radiiList
            xmin = min(famObj.radiiList) ##parameters["Minimum Radius"] Use list max because distrib doesnt always get
            xmax = max(famObj.radiiList) ##parameters["Maximum Radius"]   the desired max value.
            xVals = np.linspace(xmin, xmax, numXpoints)
            normConst = 1.0
            try:
                normConst = 1.0 / (powLawCDF(xmax, xmin, alpha) - powLawCDF(xmin, xmin, alpha))
            except ZeroDivisionError: ## happens when there is only one fracture in family so ^ has 0 in denominator
                pass        
            powLawPDFVals = [powLawPDF(normConst, xmin, x, alpha) for x in xVals]

            histHeights, binCenters = histAndPDF(radiiSizes, powLawPDFVals, xmin, xmax, xVals)
            plt.title("Histogram of Obtained Radii Sizes & Truncated Power Law Distribution PDF."\
                  "\n Family #" + famObj.globFamNum)
            plt.savefig(outputPDF, format='pdf')
            if show: plt.show()

            cdfs(histHeights, binCenters, powLawPDFVals, xmin, xmax, xVals)
            plt.savefig(outputPDF, format='pdf')
            if show: plt.show()

            trueVals = [powLawPDF(normConst, xmin, binCenters[i], alpha) for i in range(len(binCenters))]

            qq(trueVals, histHeights)
            plt.savefig(outputPDF, format='pdf')
            if show: plt.show()



        def expPDF(normConst, eLambda, x):
            return normConst * eLambda * np.e**(-eLambda*x)

        def expCDF(eLambda, x):
            return 1 - (np.e**(-eLambda*x))
            
        def graphExponential(famObj):
            if (len(famObj.radiiList) == 0):
                print 'WARNING: expoential family with num ', famObj.globFamNum, ' has no fractures; not graphing'
                return
            numXpoints = 1000
            numBuckets = 100
            radiiSizes = famObj.radiiList
            eLambda = famObj.parameters["Lambda"]
            xmin = min(famObj.radiiList) ##parameters["Minimum Radius"] Use list max because distrib doesnt always get
            xmax = max(famObj.radiiList) ##parameters["Maximum Radius"]   the desired max value.
            xVals = np.linspace(xmin, xmax, numXpoints)
            normConst = 1.0
            try:
                normConst = 1.0 / ( expCDF(eLambda, xmax) - expCDF(eLambda, xmin) )
            except ZeroDivisionError: ## happens when there is only one fracture in family so ^ has 0 in denominator
                pass          
            expPDFVals = [expPDF(normConst, eLambda, x) for x in xVals]

            histHeights, binCenters = histAndPDF(radiiSizes, expPDFVals, xmin, xmax, xVals)
            plt.title("Histogram of Obtained Radii Sizes & Exponential Distribution PDF."\
                  "\nFamily #" + famObj.globFamNum) 
            plt.savefig(outputPDF, format='pdf')
            if show: plt.show()

            cdfs(histHeights, binCenters, expPDFVals, xmin, xmax, xVals)
            plt.savefig(outputPDF, format='pdf')
            if show: plt.show()

            trueVals = [expPDF(normConst, eLambda, binCenters[i]) for i in range(len(binCenters))]
            qq(trueVals, histHeights)
            plt.savefig(outputPDF, format='pdf')
            if show: plt.show()


        def graphConstant(famObj):
            #print("  Family #" + famObj.globFamNum + " is a constant distribution and only contains one radius size.")
            pass

        def graphAllAndNotRemoved():
            numBuckets = 50
            allList = families['all'] 
            unRemovedList = families['notRemoved']
            minSize = min(allList)
            maxSize = max(allList)
            # If constant fracture size, increase max so histogram is not a delta function
            if minSize == maxSize:
                maxSize += 1.0
            twentiethOfWidth = (maxSize - minSize) * 0.05
            fig, ax = plt.subplots()
            histCount, bins, patches = plt.hist(allList, bins=numBuckets, color='b', range=(minSize, maxSize), 
                      alpha=0.7, label='All Fractures\n(Connected and Unconnected')

            binWidth = bins[1]-bins[0]
            figHeight = max(histCount) * 1.2 ## need room to show vals above bars
            ax.set_xticks(bins)
            ax.locator_params(tight = True, axis = 'x', nbins = numBuckets/5.0) ## num of axis value labels
            ax.xaxis.set_major_formatter(FormatStrFormatter('%0.1f'))

            ## if no fractures removed, there's no point in using the same 2 histograms, 
            if len(allList) != len(unRemovedList):
                plt.hist(unRemovedList, bins=numBuckets, color='r', range=(minSize, maxSize), alpha=0.7,
                      label='Non-isolated fractures (connected)')

            ## Add y values above all non-zero histogram bars        
            for count, x in zip(histCount, bins):
                if count != 0:
                    ax.annotate(str(count), xy=(x, count + (figHeight*0.03)), 
                            rotation='vertical', va='bottom')
                   
            plt.ylim(ymin=0, ymax=figHeight)
            plt.xlim(xmin=minSize-twentiethOfWidth, xmax=maxSize+twentiethOfWidth)
            plt.gcf().subplots_adjust(right=0.98)
            plt.title("Fractures Sizes From All Families")
            plt.xlabel("Fracture Radius")
            plt.ylabel("Number of Fractures")
            plt.legend()
            plt.savefig(outputPDF, format='pdf')
            if show: plt.show()
                
            
        def graphDistribs():
            famNum = 1
            updateStr = "Graphing Family #{} which contains {} fractures."
            graphDistFuncs = {"Lognormal" : graphLognormal,              ## dict of graph functions
                      "Truncated Power-Law" : graphTruncPowerLaw,
                      "Exponential" : graphExponential,
                      "Constant" : graphConstant }
            
            try: 
                while famNum > 0:
                    famObj = families[str(famNum)]
                    print(updateStr.format(famObj.globFamNum, len(famObj.radiiList)))

                    ## give info string from families file its own figure
                    fig = plt.figure()
                    fig.text(.1,.2,famObj.infoStr, fontsize=10, bbox=dict(facecolor='red', alpha=0.5))
                    plt.savefig(outputPDF, format='pdf')

                    ## then graph info 
                    graphDistFuncs[famObj.distrib](famObj) ## families' keys are strings
                    plt.close("all")
                    famNum += 1
            except KeyError: ## throws key error when we've finished the last family number
                pass


        
        
        collectFamilyInfo()
        graphTranslations()
        graphDistribs()
        graphAllAndNotRemoved()
        graphRejections()

        outputPDF.close()
    #################### End dfnGen Functions ##########################


    #################### Start dfnFlow Functions ##########################
    def lagrit2pflotran(self, inp_file='', mesh_type='', hex2tet=False):
        print ('='*80)
        print("Starting conversion of files for PFLOTRAN ")
        print ('='*80)
        if inp_file:
            self._inp_file = inp_file
        else:
            inp_file = self._inp_file

        if inp_file == '':
            sys.exit('ERROR: Please provide inp filename!')

        if mesh_type:
            if mesh_type in mesh_types_allowed:
            self._mesh_type = mesh_type
            else:
            sys.exit('ERROR: Unknown mesh type. Select one of dfn, volume or mixed!')
        else:
            mesh_type = self._mesh_type

        if mesh_type == '':
            sys.exit('ERROR: Please provide mesh type!')

        self._uge_file = inp_file[:-4] + '.uge'
        # Check if UGE file was created by LaGriT, if it does not exists, exit
        failure = os.path.isfile(self._uge_file)
        if failure == False:
            sys.exit('Failed to run LaGrit to get initial .uge file')

        if mesh_type == 'dfn':
            self.write_perms_and_correct_volumes_areas() # Make sure perm and aper files are specified

        # Convert zone files to ex format
        #self.zone2ex(zone_file='pboundary_back_n.zone',face='north')
        #self.zone2ex(zone_file='pboundary_front_s.zone',face='south')
        #self.zone2ex(zone_file='pboundary_left_w.zone',face='west')
        #self.zone2ex(zone_file='pboundary_right_e.zone',face='east')
        #self.zone2ex(zone_file='pboundary_top.zone',face='top')
        #self.zone2ex(zone_file='pboundary_bottom.zone',face='bottom')
        self.zone2ex(zone_file='all')
        print ('='*80)
        print("Conversion of files for PFLOTRAN complete")
        print ('='*80)
        print("\n\n")

    def zone2ex(self, uge_file='', zone_file='', face=''):
        """zone2ex    
        Convert zone files from LaGriT into ex format for LaGriT
        inputs:
        uge_file: name of uge file
        zone_file: name of zone file
        face: face of the plane corresponding to the zone file

        zone_file='all' processes all directions, top, bottom, left, right, front, back
        """
    
        print('--> Converting zone files to ex')    
        if self._uge_file:
            uge_file = self._uge_file
        else:
            self._uge_file = uge_file

        uge_file = self._uge_file
        if uge_file == '':
            sys.exit('ERROR: Please provide uge filename!')
        # Opening uge file
        print('\n--> Opening uge file')
        fuge = open(uge_file, 'r')

        # Reading cell ids, cells centers and cell volumes
        line = fuge.readline()
        line = line.split()
        NumCells = int(line[1])

        Cell_id = np.zeros(NumCells, 'int')
        Cell_coord = np.zeros((NumCells, 3), 'float')
        Cell_vol = np.zeros(NumCells, 'float')

        for cells in range(NumCells):
            line = fuge.readline()
            line = line.split()
            Cell_id[cells] = int(line.pop(0))
            line = [float(id) for id in line]
            Cell_vol[cells] = line.pop(3)
            Cell_coord[cells] = line
        fuge.close()

        print('--> Finished with uge file\n')

        # loop through zone files
        if zone_file=='all':
            zone_files = ['pboundary_front_s.zone', 'pboundary_back_n.zone', 'pboundary_left_w.zone', \
                    'pboundary_right_e.zone', 'pboundary_top.zone', 'pboundary_bottom.zone']
            face_names = ['south', 'north', 'west', 'east', 'top', 'bottom']
        else: 
            if zone_file == '':
                sys.exit('ERROR: Please provide boundary zone filename!')
            if face == '':
                sys.exit('ERROR: Please provide face name among: top, bottom, north, south, east, west !')
            zone_files = [zone_file]
            face_names = [face]
            
        for iface,zone_file in enumerate(zone_files):
            face = face_names[iface]
            # Ex filename
            ex_file = zone_file.strip('zone') + 'ex'

            # Opening the input file
            print '--> Opening zone file: ', zone_file
            fzone = open(zone_file, 'r')
            fzone.readline()
            fzone.readline()
            fzone.readline()

            # Read number of boundary nodes
            print('--> Calculating number of nodes')
            NumNodes = int(fzone.readline())
            Node_array = np.zeros(NumNodes, 'int')
            # Read the boundary node ids
            print('--> Reading boundary node ids')

            if (NumNodes < 10):
                g = fzone.readline()
                node_array = g.split()
                # Convert string to integer array
                node_array = [int(id) for id in node_array]
                Node_array = np.asarray(node_array)
            else:
                for i in range(NumNodes / 10 + 1):
                g = fzone.readline()
                node_array = g.split()
                # Convert string to integer array
                node_array = [int(id) for id in node_array]
                if (NumNodes - 10 * i < 10):
                    for j in range(NumNodes % 10):
                    Node_array[i * 10 + j] = node_array[j]
                else:
                    for j in range(10):
                    Node_array[i * 10 + j] = node_array[j]
            fzone.close()
            print('--> Finished with zone file')

            Boundary_cell_area = np.zeros(NumNodes, 'float')
            for i in range(NumNodes):
                Boundary_cell_area[i] = 1.e20  # Fix the area to a large number

            print('--> Finished calculating boundary connections')

            boundary_cell_coord = [Cell_coord[Cell_id[i - 1] - 1] for i in Node_array]
            epsilon = 1e-0  # Make distance really small
            if face == 'top'):
                boundary_cell_coord = [[cell[0], cell[1], cell[2] + epsilon] for cell in boundary_cell_coord]
            elif (face == 'bottom'):
                boundary_cell_coord = [[cell[0], cell[1], cell[2] - epsilon] for cell in boundary_cell_coord]
            elif (face == 'north'):
                boundary_cell_coord = [[cell[0], cell[1] + epsilon, cell[2]] for cell in boundary_cell_coord]
            elif (face == 'south'):
                boundary_cell_coord = [[cell[0], cell[1] - epsilon, cell[2]] for cell in boundary_cell_coord]
            elif (face == 'east'):
                boundary_cell_coord = [[cell[0] + epsilon, cell[1], cell[2]] for cell in boundary_cell_coord]
            elif (face == 'west'):
                boundary_cell_coord = [[cell[0] - epsilon, cell[1], cell[2]] for cell in boundary_cell_coord]
            elif (face == 'none'):
                boundary_cell_coord = [[cell[0], cell[1], cell[2]] for cell in boundary_cell_coord]
            else:
                sys.exit('ERROR: unknown face. Select one of: top, bottom, east, west, north, south.')

            with open(ex_file, 'w') as f:
                f.write('CONNECTIONS\t%i\n' % Node_array.size)
                for idx, cell in enumerate(boundary_cell_coord):
                f.write('%i\t%.6e\t%.6e\t%.6e\t%.6e\n' % (
                    Node_array[idx], cell[0], cell[1], cell[2], Boundary_cell_area[idx]))
            print('--> Finished writing ex file "' + ex_file + '" corresponding to the zone file: ' + zone_file+'\n')

        print('--> Converting zone files to ex complete')    

    def inp2vtk(self, inp_file=''):
        import pyvtk as pv
        """
        :rtype : object
        """
        if self._inp_file:
            inp_file = self._inp_file
        else:
            self._inp_file = inp_file

        if inp_file == '':
            sys.exit('ERROR: Please provide inp filename!')

        if self._vtk_file:
            vtk_file = self._vtk_file
        else:
            vtk_file = inp_file[:-4]
            self._vtk_file = vtk_file + '.vtk'

        print("--> Reading inp data")

        with open(inp_file, 'r') as f:
            line = f.readline()
            num_nodes = int(line.strip(' ').split()[0])
            num_elems = int(line.strip(' ').split()[1])

            coord = np.zeros((num_nodes, 3), 'float')
            elem_list_tri = []
            elem_list_tetra = []

            for i in range(num_nodes):
            line = f.readline()
            coord[i, 0] = float(line.strip(' ').split()[1])
            coord[i, 1] = float(line.strip(' ').split()[2])
            coord[i, 2] = float(line.strip(' ').split()[3])

            for i in range(num_elems):
            line = f.readline().strip(' ').split()
            line.pop(0)
            line.pop(0)
            elem_type = line.pop(0)
            if elem_type == 'tri':
                elem_list_tri.append([int(i) - 1 for i in line])
            if elem_type == 'tet':
                elem_list_tetra.append([int(i) - 1 for i in line])

        print('--> Writing inp data to vtk format')

        vtk = pv.VtkData(pv.UnstructuredGrid(coord, tetra=elem_list_tetra, triangle=elem_list_tri),
                 'Unstructured pflotran grid')
        vtk.tofile(vtk_file)

    def extract_common_nodes(self, volume_mesh_uge_file='', dfn_mesh_uge_file='', common_table_file='',
                 combined_uge_file='combined.uge'):

        print('--> Extracting nodes common to the volume and dfn meshes')

        table_file = common_table_file
        dat = np.genfromtxt(table_file, skip_header=7)
        common_dat = [[arr[0], arr[5]] for arr in dat if arr[1] == 21]

        file = dfn_mesh_uge_file
        f = open(file, 'r')
        num_cells = int(f.readline().strip('').split()[1])
        cell_count = num_cells

        cell_list = []
        for i in range(num_cells):
            line = f.readline().strip('').split()
            cell_list.append(line)

        conn_list = []
        num_conns = int(f.readline().strip('').split()[1])
        for i in range(num_conns):
            line = f.readline().strip('').split()
            conn_list.append(line)

        f.close()

        file = volume_mesh_uge_file
        f = open(file, 'r')
        num_cells = int(f.readline().strip('').split()[1])

        for i in range(num_cells):
            line = f.readline().strip('').split()
            line[0] = str(int(line[0]) + cell_count)
            cell_list.append(line)

        num_conns = int(f.readline().strip('').split()[1])
        for i in range(num_conns):
            line = f.readline().strip('').split()
            line[0] = str(int(line[0]) + cell_count)
            line[1] = str(int(line[1]) + cell_count)
            conn_list.append(line)

        f.close()

        epsilon = 1.e-3
        area = 1.e9

        for dat in common_dat:
            conn_list.append([cell_list[int(dat[0]) - 1][0], cell_list[int(dat[1]) - 1][0],
                      str(float(cell_list[int(dat[0]) - 1][1]) + epsilon),
                      str(float(cell_list[int(dat[0]) - 1][2]) + epsilon),
                      str(float(cell_list[int(dat[0]) - 1][3]) + epsilon), str(area)])

        for dat in common_dat:
            cell_list[int(dat[1]) - 1][1] = str(float(cell_list[int(dat[1]) - 1][1]) + epsilon)
            cell_list[int(dat[1]) - 1][2] = str(float(cell_list[int(dat[1]) - 1][2]) + epsilon)
            cell_list[int(dat[1]) - 1][3] = str(float(cell_list[int(dat[1]) - 1][3]) + epsilon)

        with open(combined_uge_file, 'w') as f:
            f.write('CELLS\t%i\n' % len(cell_list))
            for cell in cell_list:
            f.write('%i\t%.6e\t%.6e\t%.6e\t%.6e\n' % (
                int(cell[0]), float(cell[1]), float(cell[2]), float(cell[3]), float(cell[4])))
            f.write('CONNECTIONS\t%i\n' % len(conn_list))
            for conn in conn_list:
            f.write('%i\t%i\t%.6e\t%.6e\t%.6e\t%.6e\n' % (
                int(conn[0]), int(conn[1]), float(conn[2]), float(conn[3]), float(conn[4]), float(conn[5])))

    def parse_pflotran_vtk(self, grid_vtk_file=''):
        print '--> Parsing PFLOTRAN output'
        if grid_vtk_file:
            self._vtk_file = grid_vtk_file
        else:
            self.inp2vtk()

        grid_file = self._vtk_file
        
        files = glob.glob('*-[0-9][0-9][0-9].vtk')
        with open(grid_file, 'r') as f:
            grid = f.readlines()[3:]

        out_dir = 'parsed_vtk'
        for line in grid:
            if 'POINTS' in line:
            num_cells = line.strip(' ').split()[1]

        for file in files:
            with open(file, 'r') as f:
            pflotran_out = f.readlines()[4:]
            pflotran_out = [w.replace('CELL_DATA', 'POINT_DATA ') for w in pflotran_out]
            header = ['# vtk DataFile Version 2.0\n',
                  'PFLOTRAN output\n',
                  'ASCII\n']
            filename = out_dir + '/' + file
            if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
            with open(filename, 'w') as f:
            for line in header:
                f.write(line)
            for line in grid:
                f.write(line)
            f.write('\n')
            f.write('\n')
            if 'vel' in file:
                f.write('POINT_DATA\t ' + num_cells + '\n')
            for line in pflotran_out:
                f.write(line)
        print '--> Parsing PFLOTRAN output complete'
    
    def inp2gmv(self, inp_file=''):

        if inp_file:
            self._inp_file = inp_file
        else:
            inp_file = self._inp_file

        if inp_file == '':
            sys.exit('ERROR: inp file must be specified in inp2gmv!')

        gmv_file = inp_file[:-4] + '.gmv'

        with open('inp2gmv.lgi', 'w') as fid:
            fid.write('read / avs / ' + inp_file + ' / mo\n')
            fid.write('dump / gmv / ' + gmv_file + ' / mo\n')
            fid.write('finish \n\n')

        cmd = lagrit_path + ' <inp2gmv.lgi ' + '>lagrit_inp2gmv.txt'
        failure = os.system(cmd)
        if failure:
            sys.exit('ERROR: Failed to run LaGrit to get gmv from inp file!')
        print("--> Finished writing gmv format from avs format")


    def write_perms_and_correct_volumes_areas(self, inp_file='', uge_file='', perm_file='', aper_file=''):
    
        print("--> Writing Perms and Correct Volume Areas")
        if inp_file:
            self._inp_file = inp_file
        else:
            inp_file = self._inp_file
        
        if inp_file == '':
            sys.exit('ERROR: inp file must be specified!')

        if uge_file:
            self._uge_file = uge_file
        else:
            uge_file = self._uge_file

        if uge_file == '':
            sys.exit('ERROR: uge file must be specified!')

        if perm_file:
            self._perm_file = perm_file
        else:
            perm_file = self._perm_file

        if perm_file == '' and self._perm_cell_file == '':
            sys.exit('ERROR: perm file must be specified!')

        if aper_file:
            self._aper_file = aper_file
        else:
            aper_file = self._aper_file

        if aper_file == '' and self._aper_cell_file == '':
            sys.exit('ERROR: aperture file must be specified!')

        mat_file = 'materialid.dat'
        t = time()
        # Make input file for C UGE converter
        f = open("convert_uge_params.txt", "w")
        f.write("%s\n"%inp_file)
        f.write("%s\n"%mat_file)
        f.write("%s\n"%uge_file)
        f.write("%s"%(uge_file[:-4]+'_vol_area.uge\n'))
        if self._aper_cell_file:
            f.write("%s\n"%self._aper_cell_file)
            f.write("1\n")
        else:
            f.write("%s\n"%self._aper_file)
            f.write("-1\n")
        f.close()
    
        cmd = os.environ['correct_uge_PATH']+ ' convert_uge_params.txt' 
        failure = os.system(cmd)
        if failure > 0:
            sys.exit('ERROR: UGE conversion failed\nExiting Program')
        elapsed = time() - t
        print '--> Time elapsed for UGE file conversion: %0.3f seconds\n'%elapsed

        # need number of nodes and mat ID file
        print('--> Writing HDF5 File')
        materialid = np.genfromtxt(mat_file, skip_header = 3).astype(int)
        materialid = -1 * materialid - 6
        NumIntNodes = len(materialid)

        if perm_file:
            filename = 'dfn_properties.h5'
            h5file = h5py.File(filename, mode='w')
            print('--> Beginning writing to HDF5 file')
            print('--> Allocating cell index array')
            iarray = np.zeros(NumIntNodes, '=i4')
            print('--> Writing cell indices')
            # add cell ids to file
            for i in range(NumIntNodes):
            iarray[i] = i + 1
            dataset_name = 'Cell Ids'
            h5dset = h5file.create_dataset(dataset_name, data=iarray)

            print ('--> Allocating permeability array')
            perm = np.zeros(NumIntNodes, '=f8')

            print('--> reading permeability data')
            print('--> Note: this script assumes isotropic permeability')
            perm_list = np.genfromtxt(perm_file,skip_header = 1)
            perm_list = np.delete(perm_list, np.s_[1:5], 1)

            matid_index = -1*materialid - 7
            for i in range(NumIntNodes):
            j = matid_index[i]
            if int(perm_list[j,0]) == materialid[i]:
                perm[i] = perm_list[j, 1]
            else:
                sys.exit('Indexing Error in Perm File')

            dataset_name = 'Permeability'
            h5dset = h5file.create_dataset(dataset_name, data=perm)

            h5file.close()
            print("--> Done writing permeability to h5 file")
            del perm_list

        if self._perm_cell_file:
            filename = 'dfn_properties.h5'
            h5file = h5py.File(filename, mode='w')

            print('--> Beginning writing to HDF5 file')
            print('--> Allocating cell index array')
            iarray = np.zeros(NumIntNodes, '=i4')
            print('--> Writing cell indices')
            # add cell ids to file
            for i in range(NumIntNodes):
            iarray[i] = i + 1
            dataset_name = 'Cell Ids'
            h5dset = h5file.create_dataset(dataset_name, data=iarray)
            print ('--> Allocating permeability array')
            perm = np.zeros(NumIntNodes, '=f8')
            print('--> reading permeability data')
            print('--> Note: this script assumes isotropic permeability')
            f = open(self._perm_cell_file, 'r')
            f.readline()
            perm_list = []
            while True:
            h = f.readline()
            h = h.split()
            if h == []:
                break
            h.pop(0)
            perm_list.append(h)

            perm_list = [float(perm[0]) for perm in perm_list]
            
            dataset_name = 'Permeability'
            h5dset = h5file.create_dataset(dataset_name, data=perm_list)
            f.close()

            h5file.close()
            print('--> Done writing permeability to h5 file')

    
    def pflotran(self):
        """ Run pflotran
        Copy PFLOTRAN run file into working directory and run with ncpus
        """
        try: 
            copy(self._dfnFlow_file, './')
        except:
            print("-->ERROR copying PFLOTRAN input file")
        print("="*80)
        print("--> Running PFLOTRAN") 
        cmd = '${PETSC_DIR}/${PETSC_ARCH}/bin/mpirun -np ' + str(self._ncpu) + ' $PFLOTRAN_DIR/src/pflotran/pflotran -pflotranin ' + self._local_dfnFlow_file
        os.system(cmd)    
        print('='*80)
        print("--> Running PFLOTRAN Complete")
        print('='*80)
        print("\n")

    def pflotran_cleanup(self):
        """pflotran_cleanup
        Concatenate PFLOTRAN output files and then delete them 
        """
        print '--> Processing PFLOTRAN output' 
        
        cmd = 'cat '+self._local_dfnFlow_file[:-3]+'-cellinfo-001-rank*.dat > cellinfo.dat'
        os.system(cmd)

        cmd = 'cat '+self._local_dfnFlow_file[:-3]+'-darcyvel-001-rank*.dat > darcyvel.dat'
        os.system(cmd)

        for fl in glob.glob(self._local_dfnFlow_file[:-3]+'-cellinfo*.dat'):
            os.remove(fl)    
        for fl in glob.glob(self._local_dfnFlow_file[:-3]+'-darcyvel*.dat'):
            os.remove(fl)    

    #################### End dfnFlow Functions ##########################
    def uncorrelated(self, sigma):
        print '--> Creating Uncorrelated Transmissivity Fields'
        print 'Variance: ', sigma
        print 'Running un-correlated'
        x = np.genfromtxt('../aperture.dat', skip_header = 1)[:,-1]
        k = np.genfromtxt('../perm.dat', skip_header = 1)[0,-1]
        n = len(x)

        print np.mean(x)

        perm = np.log(k)*np.ones(n) 
        perturbation = np.random.normal(0.0, 1.0, n)
        perm = np.np.exp(perm + np.sqrt(sigma)*perturbation) 

        aper = np.sqrt((12.0*perm))
        aper -= np.mean(aper)
        aper += np.mean(x)

        print '\nPerm Stats'
        print '\tMean:', np.mean(perm)
        print '\tMean:', np.mean(np.log(perm))
        print '\tVariance:',np.var(np.log(perm))
        print '\tMinimum:',min(perm)
        print '\tMaximum:',max(perm)
        print '\tMinimum:',min(np.log(perm))
        print '\tMaximum:',max(np.log(perm))

        print '\nAperture Stats'
        print '\tMean:', np.mean(aper)
        print '\tVariance:',np.var(aper)
        print '\tMinimum:',min(aper)
        print '\tMaximum:',max(aper)


        output_filename = 'aperture_' + str(sigma) + '.dat'
        f = open(output_filename,'w+')
        f.write('aperture\n')
        for i in range(n):
            f.write('-%d 0 0 %0.5e\n'%(i + 7, aper[i]))
        f.close()

        cmd = 'ln -s ' + output_filename + ' aperture.dat '
        os.system(cmd)

        output_filename = 'perm_' + str(sigma) + '.dat'
        f = open(output_filename,'w+')
        f.write('permeability\n')
        for i in range(n):
            f.write('-%d 0 0 %0.5e %0.5e %0.5e\n'%(i+7, perm[i], perm[i], perm[i]))
        f.close()

        cmd = 'ln -s ' + output_filename + ' perm.dat '
        os.system(cmd)

    def create_dfnFlow_links(self):
        os.symlink('../full_mesh.uge', 'full_mesh.uge')
        os.symlink('../full_mesh_vol_area.uge', 'full_mesh_vol_area.uge')
        os.symlink('../full_mesh.inp', 'full_mesh.inp')
        os.symlink('../pboundary_back_n.ex', 'pboundary_back_n.ex')
        os.symlink('../pboundary_front_s.ex', 'pboundary_front_s.ex')
        os.symlink('../pboundary_left_w.ex', 'pboundary_left_w.ex')
        os.symlink('../pboundary_right_e.ex', 'pboundary_right_e.ex')
        os.symlink('../pboundary_top.ex', 'pboundary_top.ex')
        os.symlink('../pboundary_bottom.ex', 'pboundary_bottom.ex')
        os.symlink('../materialid.dat', 'materialid.dat')
        #os.symlink(self._jobname+'/*ex', './')
    
    def create_dfnTrans_links(self):
        os.symlink('../params.txt', 'params.txt')
        os.symlink('../allboundaries.zone', 'allboundaries.zone')
        os.symlink('../tri_fracture.stor', 'tri_fracture.stor')
        os.symlink('../poly_info.dat','poly_info.dat')
        #os.symlink(self._jobname+'/*ex', './')

    def get_num_frac(self):
        try: 
            f = open('params.txt')
            self._num_frac = int(f.readline())
            f.close()
        except:
            print '-->ERROR getting number of fractures, no params.txt file'

def commandline_options():
    """Read command lines for use in dfnWorks.
    Options:
    -name : Jobname (Mandatory)
    -ncpu : Number of CPUS (Optional, default=4)

    -gen : Generator Input File (Mandatory, can be included within this file)
    -flow : PFLORAN Input File (Mandatory, can be included within this file)
    -trans: Transport Input File (Mandatory, can be included within this file)

    -cell: True/False Set True for use with cell 
        based aperture and permeabuility (Optional, default=False)
    """
    parser = argparse.ArgumentParser(description="Command Line Arguments for dfnWorks")
    parser.add_argument("-ncpu", "--ncpu", default=4, type=int, 
              help="Number of CPUs")
    parser.add_argument("-name", "--jobname", default="", type=str,
              help="jobname") 
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
    
    if options.jobname=="":
        sys.exit("Error: Jobname is required. Exiting.")
    return options

def create_dfn(dfnGen_file="", dfnFlow_file="", dfnTrans_file=""):
    """create_dfn
    Parse command line inputs and input files to create and populate dfnworks class
    """

    options = commandline_options()
    print("Command Line Inputs:")
    print options
    print("\n-->Creating DFN class")
    dfn = dfnworks(jobname=options.jobname, ncpu=options.ncpu)

    if options.input_file != "":
        with open(options.input_file) as f:
            for line in f:
                line=line.rstrip('\n')
                line=line.split()

                if line[0].find("dfnGen") == 0:
                    dfn._dfnGen_file = line[1]
                    dfn._local_dfnGen_file = line[1].split('/')[-1]

                elif line[0].find("dfnFlow") == 0:
                    dfn._dfnFlow_file = line[1]
                    dfn._local_dfnFlow_file = line[1].split('/')[-1]

                elif line[0].find("dfnTrans") == 0:
                    dfn._dfnTrans_file = line[1]
                    dfn._local_dfnTrans_file = line[1].split('/')[-1]
    else:    
        if options.dfnGen != "":
            dfn._dfnGen_file = options.dfnGen
        elif dfnGen_file != "":
            dfn._dfnGen_file = dfnGen_file  
        else:
            sys.exit("ERROR: Input File for dfnGen not provided. Exiting")
        
        if options.dfnFlow != "":
            dfn._dfnFlow_file = options.dfnFlow
        elif dfnFlow_file != "":
            dfn._dfnFlow_file = dfnFlow_file  
        else:
            sys.exit("ERROR: Input File for dfnFlow not provided. Exiting")
        
        if options.dfnTrans != "":
            dfn._dfnTrans_file = options.dfnTrans
        elif dfnTrans_file != "":
            dfn._dfnTrans_file = dfnTrans_file  
        else:
            sys.exit("ERROR: Input File for dfnTrans not provided. Exiting")

    if options.cell==True:
        dfn._aper_cell_file = 'aper_node.dat'
        dfn._perm_cell_file = 'perm_node.dat'
    else:
        dfn._aper_file = 'aperture.dat'
        dfn._perm_file = 'perm.dat'

    print("\n-->Creating DFN class: Complete")
    print 'Jobname: ', dfn._jobname
    print 'Number of cpus requested: ', dfn._ncpu 
    print '--> dfnGen input file: ',dfn._dfnGen_file
    print '--> dfnFlow input file: ',dfn._dfnFlow_file
    print '--> dfnTrans input file: ',dfn._dfnTrans_file
    if options.cell==True:
        print '--> Expecting Cell Based Aperture and Permeability'
    print("="*80+"\n")    

    return dfn



