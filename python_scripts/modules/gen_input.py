from helper import *
import os
import sys
import shutil
import distributions as distr_module

def check_input(_dfnGen_file, _jobname,  input_file='',output_file=''):

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
    global params 
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
    'tripleIntersections', 'printRejectReasons', 'disableFram', 'visualizationMode', 'seed', 'domainSizeIncrease',
    'keepOnlyLargestCluster', 'ignoreBoundaryFaces', 'boundaryFaces', 'rejectsPerFracture', 'famProb', 'insertUserRectanglesFirst',
    'nFamEll', 'eLayer', 'edistr', 'ebetaDistribution', 'e_p32Targets', 'easpect', 'enumPoints', 'eAngleOption', 'etheta', 'ephi',
    'ebeta', 'ekappa', 'eLogMean', 'esd', 'eLogMin', 'eLogMax', 'eExpMean', 'eExpMin', 'eExpMax', 'econst', 'emin', 'emax',
    'ealpha', 'nFamRect', 'rLayer', 'rdistr', 'rbetaDistribution', 'r_p32Targets', 'raspect', 'rAngleOption', 'rtheta', 'rphi',
    'rbeta', 'rkappa', 'rLogMean', 'rsd', 'rLogMin', 'rLogMax', 'rmin', 'rmax', 'ralpha', 'rExpMean', 'rExpMin', 'rExpMax',
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
    global jobname
    jobname = _jobname

    input_helper_methods=input_helper(params, minFracSize)

    ## ===================================================================== ##
    ##                      Mandatory Parameters                             ##
    ## ===================================================================== ##

    ## Each of these should be called in the order they are defined in to accomadate for dependecies 
    def nFamEll():
        global ellipseFams 
        ## input_helper_methods.verifyNumValsIs(1, 'nFamEll')
        ellipseFams = input_helper_methods.verifyInt(input_helper_methods.valueOf('nFamEll', params), 'nFamEll', noNeg = True)
        if ellipseFams == 0:
            input_helper_methods.warning("You have set the number of ellipse families to 0, no ellipses will be generated.", params)

    def nFamRect():
        global rectFams
        ## input_helper_methods.verifyNumValsIs(1, 'nFamRect')
        rectFams = input_helper_methods.verifyInt(input_helper_methods.valueOf('nFamRect', params), 'nFamRect', noNeg = True)
        if rectFams == 0:
            input_helper_methods.warning("You have set the number of rectangle families to 0, no rectangles will be generated.", params)

    def stopCondition():
        ## input_helper_methods.verifyNumValsIs(1, 'stopCondition')
        if input_helper_methods.verifyFlag(input_helper_methods.valueOf('stopCondition', params), 'stopCondition') == 0: 
            nPoly()
        else:
            p32Targets()


    def checkNoDepFlags():
        for flagName in noDependancyFlags:
            input_helper_methods.verifyFlag(input_helper_methods.valueOf(flagName, params), flagName)
        

    ## domainSize MUST have 3 non-zero values to define the 
    ## size of each dimension (x,y,z) of the domain 
    def domainSize():
        errResult = input_helper_methods.verifyList(input_helper_methods.valueOf('domainSize', params), 'domainSize', input_helper_methods.verifyFloat, desiredLength = 3,
                       noZeros = True, noNegs=True)
        if errResult != None:
            input_helper_methods.error("\"domainSize\" has defined {} value(s) but there must be 3 non-zero "\
                  "values to represent x, y, and z dimensions".format(-errResult))

    def domainSizeIncrease():
        errResult = input_helper_methods.verifyList(input_helper_methods.valueOf('domainSizeIncrease', params), domainSizeIncrease, input_helper_methods.verifyFloat, desiredLength = 3)
        if errResult != None:
            input_helper_methods.error("\"domainSizeIncrease\" has defined {} value(s) but there must be 3 non-zero "\
                  "values to represent extensions in the x, y, and z dimensions".format(-errResult))

        for i,val in enumerate(input_helper_methods.valueOf('domainSizeIncrease', params)):
            if val >= input_helper_methods.valueOf('domainSize', params)[i]/2:
                input_helper_methods.error("\"domainSizeIncrease\" contains {} which is more than half of the domain's "
                      "range in that dimension. Cannot change the domain's size by more than half of "
                      "that dimension's value defined in \"domainSize\". This risks collapsing or "
                      "doubling the domain.".format(val))

    def numOfLayers():
        global numLayers
        numLayers = input_helper_methods.verifyInt(input_helper_methods.valueOf('numOfLayers', params), 'numOfLayers', noNeg = True)
        if numLayers > 0:
            if numLayers != len(params['layers']):
                input_helper_methods.error("\"layers\" has defined {} layers but \"numLayers\" was defined to "\
                      "be {}.".format(len(params['layers']), numLayers))
            else: layers()

    def layers():
        halfZdomain = params['domainSize'][0][2]/2.0  ## -index[2] becaue domainSize = [x,y,z]
                                  ## -center of z-domain at z = 0 so 
                                  ##  whole Zdomain is -zDomainSize to +zDomainSize
        for i, layer in enumerate(params['layers']):
            errResult = input_helper_methods.verifyList(layer, "layer #{}".format(i+1), input_helper_methods.verifyFloat, desiredLength = 2)
            if errResult != None:
                input_helper_methods.error("\"layers\" has defined layer #{} to have {} element(s) but each layer must "\
                      "have 2 elements, which define its upper and lower bounds".format(i+1, -errResult))
            if params['layers'].count(layer) > 1:
                input_helper_methods.error("\"layers\" has defined the same layer more than once.")
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

         
    def disableFram():
        if input_helper_methods.verifyFlag(input_helper_methods.valueOf('disableFram', params), 'disableFram') == 0:
            h()

    def seed():
        val = input_helper_methods.verifyInt(input_helper_methods.valueOf('seed', params), 'seed', noNeg = True)
        if val == 0:
            input_helper_methods.warning("\"seed\" has been set to 0. Random generator will use current wall "\
                "time so distribution's random selection will not be as repeatable. "\
                "Use an integer greater than 0 for better repeatability.", params)
        params['seed'][0] = val
        

    def ignoreBoundaryFaces():
        if input_helper_methods.verifyFlag(input_helper_methods.valueOf('ignoreBoundaryFaces', params), 'ignoreBoundaryFaces') == 0:
            boundaryFaces()

    def rejectsPerFracture():
        val = input_helper_methods.verifyInt(input_helper_methods.valueOf('rejectsPerFracture', params), 'rejectsPerFracture', noNeg = True)
        if val == 0:
            val = 1
            input_helper_methods.warning("changing \"rejectsPerFracture\" from 0 to 1. Can't ensure 0 rejections.", params)

        params['rejectsPerFracture'][0] = val 
        
    def famProb():
        errResult = input_helper_methods.verifyList(input_helper_methods.valueOf('famProb', params), 'famProb', input_helper_methods.verifyFloat,
                       desiredLength = ellipseFams + rectFams, noZeros = True, noNegs = True)
        if errResult != None:
            input_helper_methods.error("\"famProb\" must have {} (nFamEll + nFamRect) non-zero elements,"\
                  "one for each family of ellipses and rectangles. {} probabiliies have "\
                  "been defined.".format(ellipseFams + rectFams, -errResult))

        probList = [float(x) for x in input_helper_methods.valueOf('famProb', params)]
        if sum(probList) != 1:
            scale(probList, warningFile)

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

        if input_helper_methods.verifyFlag(input_helper_methods.valueOf(ellByCoord, params), ellByCoord) == 1:
            if not os.path.isfile(input_helper_methods.valueOf(ecoordPath, params)):
                input_helper_methods.error(invalid.format(ecoordPath))
            else:
                shutil.copy(input_helper_methods.valueOf(ecoordPath, params), _jobname)

        if input_helper_methods.verifyFlag(input_helper_methods.valueOf(userEs, params), userEs) == 1:
            if not os.path.isfile(input_helper_methods.valueOf(ePath, params)):
                input_helper_methods.error(invalid.format(ePath))
            else:
                shutil.copy(input_helper_methods.valueOf(ePath, params), _jobname)
            
        if input_helper_methods.verifyFlag(input_helper_methods.valueOf(userRs, params), userRs) == 1:
            if not os.path.isfile(input_helper_methods.valueOf(rPath, params)):
                input_helper_methods.error(invalid.format(rPath))
            else:
                shutil.copy(input_helper_methods.valueOf(rPath, params), _jobname)
            
        if input_helper_methods.verifyFlag(input_helper_methods.valueOf(recByCoord, params), recByCoord) == 1:
            if not os.path.isfile(input_helper_methods.valueOf(coordPath, params)):
                input_helper_methods.error(invalid.format(coordPath))    
            else:
                shutil.copy(input_helper_methods.valueOf(coordPath, params), _jobname)

    def aperture():
        apOption = input_helper_methods.verifyInt(input_helper_methods.valueOf('aperture', params), 'aperture')

        if apOption == 1:
            if input_helper_methods.verifyFloat(input_helper_methods.valueOf('meanAperture', params), 'meanAperture', noNeg=True) == 0:
                input_helper_methods.error("\"meanAperture\" cannot be 0.")
            if input_helper_methods.verifyFloat(input_helper_methods.valueOf('stdAperture', params), 'stdAperture', noNeg=True) == 0:
                input_helper_methods.error("\"stdAperture\" cannot be 0. If you wish to have a standard deviation "\
                      "of 0, use a constant aperture instead.") 

        elif apOption == 2:
            input_helper_methods.verifyList(input_helper_methods.valueOf('apertureFromTransmissivity', params), 'apertureFromTransmissivity', 
                   input_helper_methods.verifyFloat, desiredLength = 2, noNegs=True)
            if input_helper_methods.valueOf('apertureFromTransmissivity', params)[0] == 0:
                input_helper_methods.error("\"apertureFromTransmissivity\"'s first value cannot be 0.")
            if input_helper_methods.valueOf('apertureFromTransmissivity', params)[1] == 0:
                input_helper_methods.warning("\"apertureFromTransmissivity\"'s second value is 0, which will result in a constant aperature.", params)

        elif apOption == 3:
            if input_helper_methods.verifyFloat(input_helper_methods.valueOf('constantAperture', params), 'constantAperture', noNeg=True) == 0:

                params['constantAperture'][0] = 1e-25
                input_helper_methods.warning("\"constantAperture\" was set to 0 and has been changed "\
                      "to 1e-25 so fractures have non-zero thickness.", params)

        elif apOption == 4:
            input_helper_methods.verifyList(input_helper_methods.valueOf('lengthCorrelatedAperture', params), 'lengthCorrelatedAperture', 
                   input_helper_methods.verifyFloat, desiredLength = 2, noNegs=True)
            if input_helper_methods.valueOf('lengthCorrelatedAperture', params)[0] == 0:
                input_helper_methods.error("\"lengthCorrelatedAperture\"'s first value cannot be 0.")
            if input_helper_methods.valueOf('lengthCorrelatedAperture', params)[1] == 0:
                input_helper_methods.warning("\"lengthCorrelatedAperture\"'s second value is 0, which will result in a constant aperature.", params) 
                
        else:
            input_helper_methods.error("\"aperture\" must only be option 1 (log-normal), 2 (from transmissivity), "\
                  "3 (constant), or 4 (length correlated).")

    def permeability():
        if input_helper_methods.verifyFlag(input_helper_methods.valueOf('permOption'), 'permOption') == 1:
            if input_helper_methods.verifyFloat(input_helper_methods.valueOf('constantPermeability', params), 'constantPermeability') == 0:
                params['constantPermeability'][0] = 1e-25
                input_helper_methods.warning("\"constantPermeability\" was set to 0 and has been changed "\
                      "to 1e-25 so fractures have non-zero permeability.", params)
                

    ## ========================================================================= ##
    ##                      Non-Mandatory Parameters                             ##
    ## ========================================================================= ##

    def nPoly():
        val = input_helper_methods.verifyInt(input_helper_methods.valueOf('nPoly', params), 'nPoly', noNeg = True)
        if val == 0: input_helper_methods.error("\"nPoly\" cannot be zero.")
        params['nPoly'][0] = val

    def p32Targets():
        global ellipseFams, rectFams
        errResult = None if (ellipseFams == 0) else input_helper_methods.verifyList(input_helper_methods.valueOf('e_p32Targets', params), 'e_p32Targets', \
                                  input_helper_methods.verifyFloat, desiredLength =  ellipseFams, noNegs=True, noZeros=True)
        if errResult != None:
            input_helper_methods.error("\"e_p32Targets\" has defined {} p32 values but there is(are) {} ellipse family(ies). "\
                  "Need one p32 value per ellipse family.".format(-errResult, ellipseFams))

        errResult = None if (rectFams == 0) else input_helper_methods.verifyList(input_helper_methods.valueOf('r_p32Targets', params), "r_p32Targets", \
                                input_helper_methods.verifyFloat, desiredLength =  rectFams, noNegs=True, noZeros=True)
        if errResult != None:
            input_helper_methods.error("\"r_p32Targets\" has defined {} p32 value(s) but there is(are) {} rectangle "\
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
        shape = "ellipse" if prefix is 'e' else "rectangle"
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
                    input_helper_methods.error(shape + " family #{} has defined a shape with features too small for meshing. Increase the aspect "\
                             "ratio or minimum radius so that no 2 points of the polygon create a line of length less "\
                             "than 3h".format(numAspect+1))
                     
                numAspect += 1 ## this counts the family number 

    def h():
        val = input_helper_methods.verifyFloat(input_helper_methods.valueOf('h', params), 'h', noNeg=True)
        if val == 0: input_helper_methods.error("\"h\" cannot be 0.")
        if val < minFracSize/1000.0 and ellipseFams + rectFams > 0: ####### NOTE ----- future developers TODO, delete the 
                                        ## "and ellipseFams + rectFams > 0" once you are also
                                        ## checking the userInput Files for minimums that could be 
                                        ## "minFracSize".  "minFracSize" is initialized to 99999999 so if no 
                                        ## ellipse/rect fams are defined and the only polygons come from user 
                                        ## Input, the warning message says the min Frac size is 99999999 
                                        ## since it never gets reset by one of the distribution minima.  
            input_helper_methods.warning("\"h\" (length scale) is smaller than one 1000th of the minimum "\
                  "fracture size ({}). The generated mesh will be extremely fine and will likely be "\
                  "computationally exhausting to create. Computation may take longer than usual.".format(minFracSize))
        if val > minFracSize/10.0:
            input_helper_methods.warning("\"h\" (length scale) is greater than one 10th of the minimum "\
                  "fracture size ({}). The generated mesh will be very coarse and there will likely "\
                  "be a high rate of fracture rejection.".format(minFracSize))

        comparePtsVSh('e',val)
        comparePtsVSh('r',val)
        
        params['h'][0] = val


    ## Must be a list of flags of length 6, one for each side of the domain
    ## ie {1, 1, 1, 0, 0, 1} represents --> {+x, -x, +y, -y, +z, -z}
    ## DFN only keeps clusters with connections to domain boundaries set to 1
    def boundaryFaces():
        errResult = input_helper_methods.verifyList(input_helper_methods.valueOf('boundaryFaces', params), 'boundaryFaces', input_helper_methods.verifyFlag, 6)
        if errResult != None:
            input_helper_methods.error("\"boundaryFaces\" must be a list of 6 flags (0 or 1), {} have(has) been defined. Each flag "\
                  "represents a side of the domain, {{+x, -x, +y, -y, +z, -z}}.".format(-errResult))

    def enumPoints():
        errResult = input_helper_methods.verifyList(input_helper_methods.valueOf('enumPoints', params), 'enumPoints', input_helper_methods.verifyInt, 
                       desiredLength=ellipseFams, noZeros=True, noNegs=True)
        if errResult != None:
            input_helper_methods.error("\"enumPoints\" has defined {} value(s) but there is(are) {} families of ellipses. Please "\
                  "define one enumPoints value greater than 4 for each ellipse family.".format(-errResult, ellipseFams))
        for val in input_helper_methods.valueOf("enumPoints"):
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
        shape = "ellipse" if prefix is 'e' else "rectangle"
        numFamilies = ellipseFams if prefix is 'e' else rectFams
        paramName = prefix + "aspect"

        errResult = input_helper_methods.verifyList(input_helper_methods.valueOf(paramName), paramName, input_helper_methods.verifyFloat, 
                desiredLength = numFamilies, noZeros = True, noNegs = True)
        if errResult != None:
            input_helper_methods.error("\"{}\" has defined {} value(s) but there is(are) {} {} families. Please define one "\
                  "aspect ratio for each family.".format(paramName, -errResult, numFamilies, shape))

    def angleOption(prefix):
        paramName = prefix + "AngleOption"
        input_helper_methods.verifyFlag(input_helper_methods.valueOf(paramName), paramName)

    def layer(prefix):
        shape = "ellipse" if prefix is 'e' else "rectangle"
        numFamilies = ellipseFams if prefix is 'e' else rectFams
        paramName = prefix + "Layer"

        errResult = input_helper_methods.verifyList(input_helper_methods.valueOf(paramName), paramName, input_helper_methods.verifyInt, desiredLength = numFamilies)
        if errResult != None:
            input_helper_methods.error("\"{}\" has defined {} layer(s) but there is(are) {} {} families. "\
                  "Need one layer per {} family. Layers are numbered by the order they "\
                  "are defined in 'layers' parameter. Layer 0 is the whole domain."\
                  .format(paramName, -errResult, numFamilies, shape, shape))

        for layer in input_helper_methods.valueOf(paramName):
            if input_helper_methods.isNegative(int(layer)):
                input_helper_methods.error("\"{}\" contains a negative layer number. Only values from 0 to "\
                      "{} (numOfLayers) are accepted. Layer 0 corresponds to the entire"\
                      "domain.".format(paramName, numLayers))
            if int(layer) > numLayers:
                input_helper_methods.error("\"{}\" contains value '{}' but only {} layer(s) is(are) defined. Make sure the "\
                      "layer numbers referenced here are found in that same postion in \"layers\" "\
                      "parameter.".format(paramName, layer, numLayers))

    def thetaPhiKappa(prefix):
        shape = "ellipse" if prefix is 'e' else "rectangle"
        numFamilies = ellipseFams if prefix is 'e' else rectFams
        paramNames = [prefix + name for name in ["theta", "phi", "kappa"]]
        errString = "\"{}\" has defined {} angle(s) but there is(are) {} {} family(ies)."\
                "Please defined one angle for each {} family."
        
        for param in paramNames:
            errResult = input_helper_methods.verifyList(input_helper_methods.valueOf(param), param, input_helper_methods.verifyFloat, desiredLength = numFamilies)
            if errResult != None:
                input_helper_methods.error(errString.format(param, -errResult, numFamilies, shape, shape))


    #
    ## ========================================================================= ##
    ##                      Main for I/O Checkin and Writing                     ##
    ## ========================================================================= ##
###
#        def checkIOargs(ioPaths):
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
    def parseInput():
        for line in inputIterator:
            line = input_helper_methods.extractParameters(line, inputIterator) ## this strips comments
            if (line != "" and ":" in line):
                input_helper_methods.processLine(line, unfoundKeys, inputIterator, warningFile)
        needed = [unfound for unfound in unfoundKeys if unfound in mandatory]
        if needed != []:
            errString = ""
            for key in needed: errString += "\t\"" + key + "\"\n"
            input_helper_methods.error("Missing the following mandatory parameters: \n{}".format(errString))    
     
        
    def verifyParams():
        distributions = distr_module.distr(params, numEdistribs, numRdistribs, minFracSize)
        firstPriority = [nFamEll, nFamRect, stopCondition, domainSize, numOfLayers, 
                 seed, domainSizeIncrease, ignoreBoundaryFaces, rejectsPerFracture, 
                 userDefined, input_helper_methods.checkFamCount, checkNoDepFlags, famProb]
        generalized = [layer, aspect, angleOption, thetaPhiKappa, distributions.betaDistribution, distributions.distr]
        distribs = [distributions.lognormalDist, distributions.tplDist, distributions.exponentialDist, distributions.constantDist]
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
                    writer.write(input_helper_methods.listToCurly(str(layer)) + " ")
                writer.write('\n')    
            elif type(input_helper_methods.valueOf(param, writing=True)) is list:
                curl = input_helper_methods.listToCurly(str(input_helper_methods.valueOf(param, writing = True)))
                writer.write(param + ': ' + curl + '\n')
            else:
                writer.write(param + ': ' + str(input_helper_methods.valueOf(param, writing=True)) + '\n')              
        
    #print "--> Checking input files"    
    try:
        if not os.path.exists(os.getcwd()):
            print "ERROR: cwd: ", os.getcwd(), " does not exist"
        if not os.path.exists(os.path.abspath(_dfnGen_file)):
            print "ERROR: dfnGen input file path: ", os.path.abspath(_dfnGen_file), " does not exist"
        shutil.copy(os.path.abspath(_dfnGen_file), os.getcwd())
    except:
        print "copying ", os.path.abspath(_dfnGen_file), " to ", os.getcwd()
        sys.exit("Unable to copy dfnGen input file\n%s\nExiting"%_dfnGen_file)

    ioPaths = {"input":"", "output":""}
    try:
        ioPaths["input"] = _dfnGen_file
    except IndexError:
        input_helper_methods.error("Please provide an input file path as the first command line argument.\n"\
              "    $ python3 inputParser.py [inputPath] [outputPath (Optional)]")
    try:
        ioPaths["output"] = _jobname +  '/' + _dfnGen_file.rsplit('/',1)[-1][:-4] + '_clean.dat'
        print "clean file path is ", ioPaths["output"]   
    except IndexError:
        ioPaths["output"] = "polishedOutput.txt"
        input_helper_methods.warning("No output path has been provided so output will be written to "\
            "\"polishedOutput.txt\" in your current working directory.", params)
    try:
        reader = open(ioPaths["input"], 'r')
        writer = open(ioPaths["output"], 'w')
        inputIterator = iter(reader)
    except:
        input_helper_methods.error("Check that the path of your input file is valid.")
      
    print '--> Checking input data'
    print '--> Input Data: ', ioPaths["input"] 
    print '--> Output File: ',ioPaths["output"] 

    parseInput()
    verifyParams()
    writeBack()

    print '--> Checking Input Data Complete'
