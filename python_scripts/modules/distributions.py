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
            "use the constant distribution (4) instead. Otherwise, _make sure \"{}\" " \
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
    

