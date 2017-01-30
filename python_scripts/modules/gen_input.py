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


    #
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
            elif type(valueOf(param, writing=True)) is list:
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
