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



                                ## Running Instructions ##

        // output will be written to polishedOutput.txt in your current working directory
         
"""

## BIG TODO s -----
        ## ==== Problems ==== ##
## 11. Multiple keys on one line
## 13. In parseInput() what if ":" is in value for some reason? 

 
import re, sys, os

params = { 'esd':[],'insertUserRectanglesFirst':[],'keepOnlyLargestCluster':[],'rmin':[],
'rAngleOption':[],'boundaryFaces':[],'userRectanglesOnOff':[],'printRejectReasons':[],'numOfLayers':[],
'RectByCood_Input_File_Path':[],'eLogMean':[],'rExpMin':[],'lengthCorrelatedAperture':[],'ebetaDistribution':[],
'tripleIntersections':[],'layers':[],'stdAperture':[],'ealpha':[],'constantPermeability':[],'rLogMax':[],
'rLogMean':[],'nFamRect':[],'etheta':[],'eLogMax':[],'rphi':[],'outputAllRadii':[],
'r_p32Targets':[],'permOption':[],'userRecByCoord':[],'userEllipsesOnOff':[],'UserEll_Input_File_Path':[],
'rExpMean':[],'rbetaDistribution':[],'aperture':[],'emax':[],'eExpMean':[],'e_p32Targets':[],'eLayer':[],
'domainSizeIncrease':[],'h':[],'outputFinalRadiiPerFamily':[],'rbeta':[],'rLogMin':[],'edistr':[],'domainSize':[],
'eExpMin':[],'ekappa':[],'rLayer':[],'seed':[],'constantAperture':[],'stopCondition':[],'enumPoints':[],
'meanAperture':[],'eLogMin':[],'easpect':[],'outputTriplePoints':[],'rtheta':[],'rdistr':[],
'UserRect_Input_File_Path':[],'rconst':[],'rExpMax':[],'ignoreBoundaryFaces':[],
'visualizationMode':[],'outputAcceptedRadiiPerFamily':[],'apertureFromTransmissivity':[],'rsd':[],'ebeta':[],
'nFamEll':[],'econst':[],'raspect':[],'eAngleOption':[],'emin':[],'ephi':[],'rmax':[],'famProb':[],'disableFram':[],
'ralpha':[],'nPoly':[],'rejectsPerFracture':[],'rkappa':[],'eExpMax':[], 'forceLargeFractures':[]}

unfoundKeys={'stopCondition','nPoly','outputAllRadii','outputAllRadii','outputFinalRadiiPerFamily',
'outputAcceptedRadiiPerFamily','outputTriplePoints','domainSize', 'numOfLayers', 'layers', 'h', 
'tripleIntersections', 'printRejectReasons', 'disableFram', 'visualizationMode', 'seed', 'domainSizeIncrease',
'keepOnlyLargestCluster', 'ignoreBoundaryFaces', 'boundaryFaces', 'rejectsPerFracture', 'famProb', 'insertUserRectanglesFirst',
'nFamEll', 'eLayer', 'edistr', 'ebetaDistribution', 'e_p32Targets', 'easpect', 'enumPoints', 'eAngleOption', 'etheta', 'ephi',
'ebeta', 'ekappa', 'eLogMean', 'esd', 'eLogMin', 'eLogMax', 'eExpMean', 'eExpMin', 'eExpMax', 'econst', 'emin', 'emax',
'ealpha', 'nFamRect', 'rLayer', 'rdistr', 'rbetaDistribution', 'r_p32Targets', 'raspect', 'rAngleOption', 'rtheta', 'rphi',
'rbeta', 'rkappa', 'rLogMean', 'rsd', 'rLogMin', 'rLogMax', 'rmin', 'rmax', 'ralpha', 'rExpMean', 'rExpMin', 'rExpMax',
'rconst', 'userEllipsesOnOff', 'UserEll_Input_File_Path', 'userRectanglesOnOff', 'UserRect_Input_File_Path', 'userRecByCoord',
'RectByCood_Input_File_Path', 'aperture', 'meanAperture', 'stdAperture', 'apertureFromTransmissivity', 'constantAperture',
'lengthCorrelatedAperture', 'permOption', 'constantPermeability', 'forceLargeFractures'}

mandatory = {'stopCondition','domainSize','numOfLayers','outputAllRadii', 'outputFinalRadiiPerFamily',
'outputAcceptedRadiiPerFamily','outputTriplePoints','tripleIntersections','printRejectReasons',
'disableFram','visualizationMode','seed','domainSizeIncrease','keepOnlyLargestCluster','ignoreBoundaryFaces',
'rejectsPerFracture','famProb','insertUserRectanglesFirst','nFamEll','nFamRect','userEllipsesOnOff','userRectanglesOnOff',
'userRecByCoord','aperture','permOption', 'forceLargeFractures'}

noDependancyFlags = ['outputAllRadii','outputFinalRadiiPerFamily',
'outputAcceptedRadiiPerFamily','outputTriplePoints','tripleIntersections','printRejectReasons',
'visualizationMode', 'keepOnlyLargestCluster','insertUserRectanglesFirst', 'forceLargeFractures']

examples = {"Flag":"(0 or 1)", "Float":"(0.5, 1.6, 4.0, etc.)" , "Int":"(0,1,2,3,etc.)"}

ellipseFams = 0
rectFams = 0
numLayers = 0
minFracSize = 99999999.9
        ## WARNING: Index[0] for the following lists should never be used. See edistr() and rdistr() for clarity. 
numEdistribs = [-1,0,0,0,0] ## [0 = no-op, 1 = # log-normal's, 2 = # Truncated Power Law's, 3 = # Exp's, # constant's]  
numRdistribs = [-1,0,0,0,0] ## [0 = no-op, 1 = # log-normal's, 2 = # Truncated Power Law's, 3 = # Exp's, # constant's]
warningFile = open("warningFileDFNGen.txt", 'w')        


## ====================================================================== ##
##                              Parsing Functions                         ##
## ====================================================================== ##
def extractParameters(line):
        if "/*" in line:
                comment = line
                line = line[:line.index("/*")] ## only process text before '/*' comment
                while "*/" not in comment:
                        comment = next(inputIterator) ## just moves iterator past comment

        elif "//" in line:
                line = line[:line.index("//")] ## only process text before '//' comment
                
        return line.strip()


def findVal(line, key):
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
			print 'something went wrong'
                        break
        
        if valList == [] and key in mandatory:
                error("\"{}\" is a mandatory parameter and must be defined.".format(key))
        if key is not None:
                params[key] = valList if valList != [] else [""] ## allows nothing to be entered for unused params 
        if line != "": processLine(line)
                
## Input: line containing a paramter (key) preceding a ":" 
## Returns: key -- if it has not been defined yet and is valid
##          None -- if key does not exist
##          exits -- if the key has already been defined to prevent duplicate confusion        
def findKey(line):
        key = line[:line.index(":")].strip()
        if key in unfoundKeys:
                unfoundKeys.remove(key)
                return key
        try:
                params[key]
                error("\"{}\" has been defined more than once.".format(key))
        except KeyError:
                warning("\"" + key + "\" is not one of the valid parameter names.")

def processLine(line):
        if line.strip != "":
                key = findKey(line)
                if key != None: findVal(line, key)   


## ====================================================================== ##
##                              Verification                              ##
## ====================================================================== ##
## Note: Always provide EITHER a key (ie "stopCondition") 
##         OR inList = True/False (boolean indicating val being checked is inside a list) 

## Input: value - value being checked
##        key - parameter the value belongs to
##        inList - (Optional)
def verifyFlag(value, key = "", inList = False):
        if value is '0' or value is '1':
                return int(value)
        elif inList:
                return None
        else:
                error("\"{}\" must be either '0' or '1'".format(key))

def verifyFloat(value, key = "", inList = False, noNeg = False):
        if type(value) is list:
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
        if type(value) is list:
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
                        
## Verifies input list that come in format {0, 1, 2, 3}
##
## Input:  valList - List of values (flags, floats, or ints) corresponding to a parameter
##         key - the name of the parameter whose list is being verified
##         verificationFn - (either verifyFlag, verifyFloat or verifyInt) checks each list element 
##         desiredLength - how many elements are supposed to be in the list
##         noZeros - (Optional) True for lists than cannot contain 0's, False if 0's are ok  
##         noNegs - (Optional) True for lists than cannot contain negative numbers, False otherwise
## Output: returns negative value of list length to indicate incorrect length and provide meaningful error message
##         Prints error and exits if a value of the wrong type is found in the list
##         returns None if successful
##
def verifyList(valList, key, verificationFn, desiredLength, noZeros=False, noNegs=False):
        if valList == ['']: return 0
        if type(valList) is not list:
                error("\"{}\"'s value must be a list encolsed in curly brackets {{}}.".format(key))
        if desiredLength != 0 and len(valList) != desiredLength:
                return -len(valList)
        for i, value in enumerate(valList):
                value = value.strip() 
                verifiedVal = verificationFn(value, inList = True)
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
        return re.sub("{|}", "", curlyList).strip().split(",")

## [1,2,3] --> '{1,2,3}'   for writing output
def listToCurly(strList):
         curl = re.sub(r'\[','{', strList)
         curl = re.sub(r'\]','}', curl)
         curl = re.sub(r"\'", '', curl)
         return curl 

def hasCurlys(line, key):
        if '{' in line and '}' in line: return True 
        elif '{' in line or '}' in line: 
                error("Line defining \"{}\" contains a single curly brace.".format(key))
        return False

## Use to get key's value in params. writing always false  
def valueOf(key, writing = False):
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
                       (valueOf('userRecByCoord') == '1')

        if ellipseFams + rectFams <= 0 and not userDefExists:
                error("Zero polygon families have been defined. Please create at least one family "\
                      "of ellipses/rectagnles, or provide a user-defined-polygon input file path in "\
                      "\"UserEll_Input_File_Path\", \"UserRect_Input_File_Path\", or "\
                      "\"RectByCood_Input_File_Path\" and set the corresponding flag to '1'.")

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
                                                      ##  whole Zdomain is -zDomainSize to +zDomainSize
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
        ePath = "UserEll_Input_File_Path"
        rPath = "UserRect_Input_File_Path"
        coordPath = "RectByCood_Input_File_Path"
        invalid = "\"{}\" is not a valid path."

        if verifyFlag(valueOf(userEs), userEs) == 1 and not os.path.isfile(valueOf(ePath)):
                error(invalid.format(ePath))
        if verifyFlag(valueOf(userRs), userRs) == 1 and not os.path.isfile(valueOf(rPath)):
                error(invalid.format(rPath))
        if verifyFlag(valueOf(recByCoord), recByCoord) == 1 and not os.path.isfile(valueOf(coordPath)):
                error(invalid.format(coordPath))    

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

def h():
        val = verifyFloat(valueOf('h'), 'h', noNeg=True)
        if val == 0: error("\"h\" cannot be 0.")
        if val < minFracSize/1000.0 and ellipseFams + rectFams > 0: ####### NOTE ----- future developers TODO, delete the 
                                                                    ## "and ellipseFams + rectFams > 0" once you are also
                                                                    ## checking the userInput Files for minimums that could be 
                                                                    ## "minFracSize".  "minFracSize" is initialized to 99999999 so if no 
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
        shape = "ellipse" if prefix is 'e' else "rectangle"
        numFamilies = ellipseFams if prefix is 'e' else rectFams
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
        shape = "ellipse" if prefix is 'e' else "rectangle"
        numFamilies = ellipseFams if prefix is 'e' else rectFams
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
        shape = "ellipse" if prefix is 'e' else "rectangle"
        numFamilies = ellipseFams if prefix is 'e' else rectFams
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
        shape = "ellipse" if prefix is 'e' else "rectangle"
        numFamilies = ellipseFams if prefix is 'e' else rectFams
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
        shape = "ellipse" if prefix is 'e' else "rectangle"
        distribList = numEdistribs if prefix is 'e' else numRdistribs
        numFamilies = ellipseFams if prefix is 'e' else rectFams
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
        shape = "ellipse" if prefix is 'e' else "rectangle"
        distribList = numEdistribs if prefix is 'e' else numRdistribs
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
                        "use the constant distribution (4) instead. Otherwise, make sure \"{}\" " \
                        "only contains values greater than 0.".format(sdParam, sdParam))

        checkMinMax(prefix+"LogMin", prefix+"LogMax", shape)
        checkMean(prefix+"LogMin", prefix+"LogMax", prefix+"LogMean")
        checkMinFracSize(valueOf(prefix+"LogMin"))

## Truncated Power Law Distribution
def tplDist(prefix):
        shape = "ellipse" if prefix is 'e' else "rectangle"
        distribList = numEdistribs if prefix is 'e' else numRdistribs
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
        shape = "ellipse" if prefix is 'e' else "rectangle"
        distribList = numEdistribs if prefix is 'e' else numRdistribs
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
        numFamilies = ellipseFams if prefix is 'e' else rectFams
        distribList = numEdistribs if prefix is 'e' else numRdistribs

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

def checkIOargs(ioPaths):
        try:
                ioPaths["input"] = sys.argv[1]
        except IndexError:
                error("Please provide an input file path as the first command line argument.\n"\
                      "    $ python3 inputParser.py [inputPath] [outputPath (Optional)]")

        try:
                ioPaths["output"] = sys.argv[2]
        except IndexError:
                ioPaths["output"] = "polishedOutput.txt"
                warning("No output path has been provided so output will be written to "\
                        "\"polishedOutput.txt\" in your current working directory.")

def parseInput():
        for line in inputIterator:
                line = extractParameters(line)
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
                elif type(valueOf(param, writing=True)) is list:
                        curl = listToCurly(str(valueOf(param, writing = True)))
                        writer.write(param + ': ' + curl + '\n')
                else:
                        writer.write(param + ': ' + str(valueOf(param, writing=True)) + '\n')              
        
             
if __name__ == '__main__':
        ioPaths = {"input":"", "output":""}
        checkIOargs(ioPaths)
        
	try:
                reader = open(ioPaths["input"], 'r')
                writer = open(ioPaths["output"], 'w')
                inputIterator = iter(reader)
        except FileNotFoundError:
                error("Check that the path of your input file is valid.")
                
        parseInput()
        verifyParams()
        writeBack()


