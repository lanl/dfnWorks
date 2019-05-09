# pydfnwork modules
import pydfnworks.dfnGen.gen_input as gen_input
import pydfnworks.dfnGen.gen_input_helper as gen_input_helper

class distr():
    """ 
    Verifies the fracture distribution input parameters for dfnGen.
    
    Attributes:
        params :list
            Parameters for dfnGen
        numEdistribs : int
            Number of ellipse family distributions
        numRdistribs : int
            Number of rectangle family distributions
        minFracSize : double
            Minimum fracture size
    """

    def __init__(self, params, numEdistribs, numRdistribs, minFracSize):
        self.params = params
        global distr_helper_methods  
        distr_helper_methods = gen_input_helper.input_helper(params, minFracSize) 
        self.ellipseFams = distr_helper_methods.value_of('nFamEll')
        self.rectFams = distr_helper_methods.value_of('nFamRect')
        self.numEdistribs = numEdistribs
        self.numRdistribs = numRdistribs

    def beta_distribution(self, prefix):
        """
        Verifies both the "ebetaDistribution" and "rBetaDistribution". If either contain any flags
        indicating contant angle (1) then the corresponding "ebeta" and/or "rbeta" parameters are 
        also verified. 
        
        Parameters:
            prefix : str
                Indicates shapes that the beta distribution describes. 'e' if they are ellipses, 'r' if they are rectangles.
        """
        shape = "ellipse" if prefix is 'e' else "rectangle"
        numFamilies = self.ellipseFams if prefix is 'e' else self.rectFams
        paramName = prefix + "betaDistribution"

        errResult = distr_helper_methods.verify_list(distr_helper_methods.value_of(paramName), paramName, distr_helper_methods.verify_flag, desiredLength = numFamilies)
        if errResult != None:
            distr_helper_methods.error("\"{}\" has defined {} value(s) but there is(are) {} {} family(ies). Need one "\
                  "flag (0 or 1) per {} family.".format(paramName, -errResult, numFamilies, shape, shape))

        numBetas = distr_helper_methods.value_of(paramName).count(1) ## number of 1's in list
        if numBetas == 0: return

        betaParam = prefix + "beta"
        errResult = distr_helper_methods.verify_list(distr_helper_methods.value_of(betaParam), betaParam, distr_helper_methods.verify_float, desiredLength = numBetas)
        if errResult != None:
            distr_helper_methods.error("\"{}\" defined {} constant angle(s) but {} flag(s) was(were) set to 1 "\
                  "in {}. Please define one constant angle (beta value) for each flag set "\
                  "to 1 in \"{}\"".format(betaParam, -errResult, numBetas, paramName, paramName))


    def distr(self, prefix):
        """ 
        Verifies "edistr" and "rdistr" making sure one distribution is defined per family and
        each distribution is either 1 (log-normal), 2 (Truncated Power Law), 3 (Exponential), or 4 (constant).
        Stores how many of each distrib are in use in numEdistribs or numRdistribs lists.  
        """
        shape = "ellipse" if prefix is 'e' else "rectangle"
        distribList = self.numEdistribs if prefix is 'e' else self.numRdistribs
        numFamilies = self.ellipseFams if prefix is 'e' else self.rectFams
        paramName = prefix + "distr"

        errResult = distr_helper_methods.verify_list(distr_helper_methods.value_of(paramName), paramName, distr_helper_methods.verify_int, desiredLength = numFamilies)
        if errResult != None:
            distr_helper_methods.error("\"{}\" has defined {} distributions but there are {} {} families. " \
                "Need one distribution per family (1 = lognormal, 2 = Truncated Power Law, "
                "3 = Exponential, or 4 = constant).".format(paramName, -errResult, numFamilies, shape)) 
        try:
            for dist in distr_helper_methods.value_of(paramName):
                if int(dist) <= 0: raise IndexError()
                distribList[int(dist)] += 1  
        except IndexError:
            distr_helper_methods.error("\"{}\" contains '{}' which is not a valid distribution option. " \
                   "Only values 1 through 4 can define a family's distribution (1 = lognormal, " \
                   "2 = Truncated Power Law, 3 = Exponential, or 4 = constant).".format(paramName, dist))


    def lognormal_dist(self, prefix):
        """
        Verifies all logNormal Parameters for ellipses and Rectangles.
        """ 
        shape = "ellipse" if prefix is 'e' else "rectangle"
        distribList = self.numEdistribs if prefix is 'e' else self.numRdistribs
        paramNames = [prefix + name for name in ["LogMean", "sd", "LogMin", "LogMax"]]
        errString = "\"{}\" has defined {} value(s) but {} lognormal distrbution(s) was(were) " \
                "defined in \"{}\". Please define one value for each lognormal (distrib. #1) family."

        for param in paramNames:
            zTmp = True if "sd" not in param else False  ## Turns off noZeros check only for 'sd' for better error msg
            errResult = distr_helper_methods.verify_list(distr_helper_methods.value_of(param), param, distr_helper_methods.verify_float, desiredLength = distribList[1],
                        noZeros = zTmp, noNegs = True)         
            if errResult != None:
                distr_helper_methods.error(errString.format(param, -errResult, distribList[1], prefix+'distr'))

        sdParam = prefix + "sd"
        if distr_helper_methods.zero_in_std_devs(distr_helper_methods.value_of(sdParam)): 
            distr_helper_methods.error("\"{}\" list contains a standard deviation of 0. If this was intended, " \
                "use the constant distribution (4) instead. Otherwise, _make sure \"{}\" " \
                "only contains values greater than 0.".format(sdParam, sdParam))

        distr_helper_methods.check_min_max(prefix+"LogMin", prefix+"LogMax", shape)
        distr_helper_methods.check_mean(prefix+"LogMin", prefix+"LogMax", prefix+"LogMean")
        distr_helper_methods.check_min_frac_size(distr_helper_methods.value_of(prefix+"LogMin"))

    def tpl_dist(self, prefix):
        """
        Verifies parameters for truncated power law distribution of fractures.
        """
        shape = "ellipse" if prefix is 'e' else "rectangle"
        distribList = self.numEdistribs if prefix is 'e' else self.numRdistribs
        paramNames = [prefix + name for name in ["min", "max", "alpha"]]
        errString = "\"{}\" has defined {} value(s) but {} truncated power-law distrbution(s) was(were) " \
                "defined in \"{}\". Please define one value for each truncated power-law (distrib. #2) family."

        for param in paramNames:
            errResult = distr_helper_methods.verify_list(distr_helper_methods.value_of(param), param, distr_helper_methods.verify_float, desiredLength = distribList[2], 
                        noZeros = True, noNegs = True)
            if errResult != None:
                distr_helper_methods.error(errString.format(param, -errResult, distribList[2], prefix+'distr'))
                
        distr_helper_methods.check_min_max(prefix+"min", prefix+"max", shape)
        distr_helper_methods.check_min_frac_size(distr_helper_methods.value_of(prefix+"min"))
        

    def exponential_dist(self, prefix):
        """
        Verifies parameters for exponential distribution of fractures.
        """
        shape = "ellipse" if prefix is 'e' else "rectangle"
        distribList = self.numEdistribs if prefix is 'e' else self.numRdistribs
        paramNames = [prefix + name for name in ["ExpMean", "ExpMin", "ExpMax"]]
        errString = "\"{}\" has defined {} value(s) but {} exponential distrbution(s) was(were) " \
                "defined in \"{}\". Please define one value for each exponential (distrib. #3) family."

        for param in paramNames:
            errResult = distr_helper_methods.verify_list(distr_helper_methods.value_of(param), param, distr_helper_methods.verify_float, desiredLength = distribList[3], 
                        noZeros = True, noNegs = True)
            if errResult != None:
                distr_helper_methods.error(errString.format(param, -errResult, distribList[3], prefix+'distr'))
                
        distr_helper_methods.check_min_max(prefix+"ExpMin", prefix+"ExpMax", shape)
        distr_helper_methods.check_mean(prefix+"ExpMin", prefix+"ExpMax", prefix+"ExpMean")
        distr_helper_methods.check_min_frac_size(distr_helper_methods.value_of(prefix+"ExpMin"))

    def constant_dist(self, prefix):
        """
        Verifies parameters for constant distribution of fractures
        """
        paramName = prefix + "const"
        numFamilies = self.ellipseFams if prefix is 'e' else self.rectFams
        distribList = self.numEdistribs if prefix is 'e' else self.numRdistribs

        errResult = distr_helper_methods.verify_list(distr_helper_methods.value_of(paramName), paramName, distr_helper_methods.verify_float, desiredLength = distribList[4],
                     noZeros = True, noNegs = True)
        if errResult != None:
            distr_helper_methods.error("\"{}\" has defined {} value(s) but {} constant distrbution(s) was(were) " \
                  "defined in \"{}\". Please define one value for each family with a constant (distrib. "\
                  "#4) distribution.".format(paramName, -errResult, distribList[4], prefix + 'distr'))
         
        distr_helper_methods.check_min_frac_size(distr_helper_methods.value_of(paramName))
        

