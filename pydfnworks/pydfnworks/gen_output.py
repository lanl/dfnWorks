import generator
from scipy import stats, special 
import numpy as np
import re
import matplotlib.pylab as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.mlab as mlab

def output_report(self, radiiFile = 'radii.dat', famFile ='families.dat', transFile='translations.dat', rejectFile = 'rejections.dat', output_name = ''):
	"""
	Create PDF report of generator 
        
        Notes:
            * Set the number of histogram buckets (bins) by changing numBuckets variable in his graphing functions
            * Also change number of x-values used to plot lines by changing numXpoints variable in appropriate funcs
            * Set show = True to show plots immediately and still make pdf
            * NOTE future developers of this code should add functionality for radiiList of size 0. 

	"""
	print '--> Creating Report of DFN generation'
	families = {'all':[], 'notRemoved':[]} ## families['all'] contains all radii.   
					       ## families['notRemoved'] contains all non-isolated fractures. 
					       ##   Isolated fracs get removed from DFN and have 'R' at end  
					       ##   of input file line
					       ## families['1','2','3' etc] correspond to a polyFam object\
	output_name = self.local_jobname + '_output_report.pdf'
	print 'Writing output into: ', output_name
	outputPDF = PdfPages(output_name) ## TODO to make this cmd line option --> outputPDF = PdfPages(sys.argv[5])
	show = False ## Set to true for showing plots immediately instead of having to open pdf. Still makes pdf

	class polyFam:
		""" A data structure describing a family of fractures (that all must be either ellipses or rectangles
                Attributes:
                    * globFamNum (int): a unique integer describing the family
                    * radiiList (list): a list of doubles describing the radii of all fractures in the family
                    * distrib (str): the type of distribution of the family (lognormal, exponential, constant, or user-defined)
                    * infoStr (str): an informative string describing the family
                    * parameters (dict): a dictionary containing the values of parameters for the family
                """
                
                def __init__(self, globFamNum, radiiList, distrib, infoStr, parameters):
			self.globFamNum = globFamNum
			self.radiiList = radiiList
			self.distrib = distrib
			self.infoStr = infoStr
			self.parameters = parameters

		def print_poly_fam(self):
			print("famNum:\n", self.globFamNum)
			print("\nradiiList:\n",self.radiiList)
			print("\ndistrib:\n", self.distrib)
			print("\ninfoStr:\n", self.infoStr)
			print("\nparameters:\n", self.parameters)
			print("\n\n")
		       

	def graph_rejections():
		"""
                Graph the fractures that were rejected by the Feature Rejection Algorithm for Meshing (FRAM) in dfnGen, using a histogram of rejection reasons.
	        Rejection File line format:   "118424 Short Intersections" --> {"Short Intersections": 118424}
                """
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


	def trans_hist(prefix, allList, unRemovedList):
	        """ Histogram making helper function for graph_translations()"""
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

        def graph_translations():
                """ Graphs position of fractures as histogram for x, y and z dimensions
                Input file format:    Xpos Ypos Zpos (R) [R is optional, indicates it was removed due to isolation]
                """
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

		trans_hist('X', xAll, xUnremoved)
		trans_hist('Y', yAll, yUnremoved)
		trans_hist('Z', zAll, zUnremoved)
		

	def collect_family_info():
   		""" Read in information from families.dat file that lists the data for each fracture family.
                """
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
                        if "UserDefined Ellipse" in line:
                            famNum = '0'
                            famObj.globFamNum = famNum
                            families[famNum] = famObj
		        if "UserDefined Rectangle" in line:
                            famNum = '-1'
                            famObj.globFamNum = famNum
                            families[famNum] = famObj
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

			## ======== Jeffrey, this is where you can add the family building parser code ====== #
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
				if famNum not in families: 
                                        families[famNum] = []
                                        families[famNum].radiiList = [radius]
				else:
					families[famNum].radiiList.append(radius)
			except ValueError:
				continue

		for fam in families:
			if fam != 'all' and fam != 'notRemoved':
				pass # families[fam].print_poly_fam()

	def hist_and_p_d_f(radiiSizes, pdfArray, xmin, xmax, xVals):
	        """
                Histogram of sizes (from data) and PDF (from input parameters
	        returns histHeights (height of all hist bars) for plotting cdf
	        & list of x values of binCenters (also for cdf).
                Args:
                    radiiSizes (list): list of radii sizes.
                    pdfArray (list): list of pdf values for given xVals.
                    xmin (double): minimum value of x on plot.. 
                    xmax (double): maximum value of x on plot.
		""" 
                numBuckets = 100
		fig, histo = plt.subplots()
		### fig = plt.figure(figsize=(8., 6.), dpi=500)  ## comment out if you dont want pdf
		## histo = plt.ax_stack()

		## plot hist, set xtick labels
	        weights = np.ones_like(radiiSizes)/float(len(radiiSizes))	
                histHeights, binEdges, patches = histo.hist(radiiSizes, numBuckets, weights=weights, normed=1, color='r',
									alpha=0.75, label='Empirical data')
	
                binCenters = [((binEdges[x] + binEdges[x+1]) / 2.0) for x in range(len(binEdges)-1)] ## need for cdf
			     ## ^ -1 to prevent Index Error when calculating last bin Center
		histo.set_xticks(binEdges)
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

	def cdfs(histHeights, binCenters, pdf, xmin, xmax, xVals):
		""" Plots 2 cdfs, analytical (from pdf from given mu and sigma) and empirical (from histogram).
                Args:
                    histHeights (list): list of histogram heights
                    binCenters (list): binCenters for each histogram bin.
                    pdf (list): list of corresponding pdf values 
                    xmin (double): minimum value of x
                    xmax (double): maximum value of x
                    xVals (list): values of x
                """
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

	def qq(trueVals, histHeights):
		"""  Histogram values (x) vs. analytical PDF values (y) & a line showing ideal 1 to 1 ratio
                Args:
                    trueVals (list): ordered list of analytical values.
                    histHeights (list): ordered list of generator values.
                """
                fig, ax = plt.subplots()
		qq = plt.scatter(histHeights, trueVals, c='r', marker='o', 
				 label="x=Empirical value\ny=Analtical PDF value")
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

	def lognorm_c_d_f(x, mu, sigma):
		"""Get the lognnormal distribution value for the given x.
                Args:
                    x (double): the value of x
                    mu (double): the mean  parameter of the lognormal distribution
                    sigma (double): the standard deviation of the lognromal distribution
                """
                return 0.5 + (0.5 * special.erf( (np.log(x) - mu) / (np.sqrt(2) * sigma) ) )
	       
        def lognormal_pdf(x, sigma, mu):
		"""Get the analytical lognormal PDF value corresponding to x.
                Args:
                    xVals: values of x at which to calculate the lognormal PDF
                    sigma: the standard deviation of the corresponding normal distribution
                    mu: the mean of the corresponding normal distribution
                """
                constant = 1 / ( x * sigma * np.sqrt(2*3.14159))
                exp_term = -0.5*(pow((np.log(x) - mu) / sigma, 2.0))
                return constant*np.exp(exp_term)
        
        def lognormal_pdf_list(xVals, sigma, mu):
		"""Get a list of the analytical lognormal PDF values corresponding to xVals.
                Args:
                    xVals: values of x at which to calculate the lognormal PDF
                    sigma: the standard deviation of the corresponding normal distribution
                    mu: the mean of the corresponding normal distribution
                """
                lst = []
                for x in xVals:
                    lst.append(lognormal_pdf(x, sigma, mu))
                return lst
        
        def graph_lognormal(famObj):
		"""Graph the PDF, CDF and QQ plot of the lognormal  distribution agianst the expected analytical lognormal  values.
                Args:
                    famObj (polyFam class): the polyFam object describing the truncated power law distribution.
                """
		numXpoints = 1000
		xmin = min(famObj.radiiList) ##parameters["Minimum Radius"] Use list max because distrib doesnt always get
		xmax = max(famObj.radiiList) ##parameters["Maximum Radius"]   the desired max value.
		xVals = np.linspace(xmin, xmax, numXpoints)
		mu, sigma = famObj.parameters["Mean"], famObj.parameters["Standard Deviation"]
                if (mu < 0):
                    print 'ERROR: mean must be positive'
                    exit()
		try:       
		    normConstant = 1.0 / (lognorm_c_d_f(xmax, mu, sigma) - lognorm_c_d_f(xmin, mu, sigma))
		except ZeroDivisionError: ## happens when there is only one fracture in family so ^ has 0 in denominator
		    pass  
                lognormPDFVals = [x * normConstant for x in lognormal_pdf_list(xVals, sigma, mu)]
                #lognormPDFVals = [x * normConstant for x in stats.lognorm.pdf(xVals, sigma, loc=mu)]
                adj_factor = np.trapz(lognormPDFVals, xVals)
                lognormPDFVals /= adj_factor
		histHeights, binCenters = hist_and_p_d_f(famObj.radiiList, lognormPDFVals, xmin, xmax, xVals) 
		plt.title("Histogram of Obtained Radii Sizes & Lognormal Distribution PDF."\
			  "\nFamily #" + famObj.globFamNum)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()

		cdfs(histHeights, binCenters, lognormPDFVals, xmin, xmax, xVals)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()
                
                trueVals = [lognormal_pdf(binCenters[i], sigma, mu) for i in range(len(binCenters))]
		#trueVals = [stats.lognorm.pdf(binCenters[i], sigma, loc=mu) for i in range(len(binCenters))]
		qq(trueVals, histHeights)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()
	  
	      
	def pow_law_p_d_f(normConst, xmin, x, a):
		""" Get the analytical power laws PDF value for a given x.
                Args:
                    normConst (double): The normalization constant for the PDF.
                    xmin (double): The minimum value for the truncated power-law distribution.
                    x (double): The value of x. 
                    a (double): The alpha parameter for the power-law distribution.
                """
                return normConst * ( (a*(xmin**a)) / float(x**(a+1)) ) 

	def pow_law_c_d_f(x, xmin, a):
		""" Get the analytical power law CDF value for a given x.
                Args:
                    x (double): The value of x.
                    xmin (double): The lower bound of the truncated power law distribution.
                    a (double): The alpha parameter in the power law distribution.
                """
                return 1 - ( (xmin / float(x))**a ) 

	def graph_trunc_power_law(famObj):
		"""Graph the PDF, CDF and QQ plot of the power law distribution agianst the expected analytical power law values.
                Args:
                    famObj (polyFam class): the polyFam object describing the truncated power law distribution.
                """
                numBuckets = 100
		numXpoints = 1000
		alpha = famObj.parameters["Alpha"]
		radiiSizes = famObj.radiiList
		xmin = min(famObj.radiiList) ##parameters["Minimum Radius"] Use list max because distrib doesnt always get
		xmax = max(famObj.radiiList) ##parameters["Maximum Radius"]   the desired max value.
		xVals = np.linspace(xmin, xmax, numXpoints)
		normConst = 1.0
		try:
			normConst = 1.0 / (pow_law_c_d_f(xmax, xmin, alpha) - pow_law_c_d_f(xmin, xmin, alpha))
		except ZeroDivisionError: ## happens when there is only one fracture in family so ^ has 0 in denominator
			pass        
		powLawPDFVals = [pow_law_p_d_f(normConst, xmin, x, alpha) for x in xVals]

		histHeights, binCenters = hist_and_p_d_f(radiiSizes, powLawPDFVals, xmin, xmax, xVals)
		plt.title("Histogram of Obtained Radii Sizes & Truncated Power Law Distribution PDF."\
			  "\n Family #" + famObj.globFamNum)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()

		cdfs(histHeights, binCenters, powLawPDFVals, xmin, xmax, xVals)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()

		trueVals = [pow_law_p_d_f(normConst, xmin, binCenters[i], alpha) for i in range(len(binCenters))]

		qq(trueVals, histHeights)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()



	def exp_p_d_f(normConst, eLambda, x):
		""" Get the analytical exponential PDF value for a given x.
                Args:
                    x (double): The value of x.
                    eLambda (double): The lambda value for the exponential distribution.
                    normConst (double): The normalization constnat for the exponential distribution.
                """
                return normConst * eLambda * np.e**(-eLambda*x)

	def exp_c_d_f(eLambda, x):
		""" Get the analytical exponential CDF value for a given x.
                Args:
                    x (double): the value of x for which to find the exponential CDF value.
                    eLambda (double): the lambda value for the exponential distribution.
                """
                return 1 - (np.e**(-eLambda*x))
		
	def graph_exponential(famObj):
	        """ Graph exponential distribution of fractures  against the analytical exponential distributions, using a PDF, CDF, and QQ plot.
                """
                numXpoints = 1000
		numBuckets = 100
		radiiSizes = famObj.radiiList
		eLambda = famObj.parameters["Lambda"]
		xmin = min(famObj.radiiList) ##parameters["Minimum Radius"] Use list max because distrib doesnt always get
		xmax = max(famObj.radiiList) ##parameters["Maximum Radius"]   the desired max value.
		xVals = np.linspace(xmin, xmax, numXpoints)
		normConst = 1.0
		try:
			normConst = 1.0 / ( exp_c_d_f(eLambda, xmax) - exp_c_d_f(eLambda, xmin) )
		except ZeroDivisionError: ## happens when there is only one fracture in family so ^ has 0 in denominator
			pass          
		expPDFVals = [exp_p_d_f(normConst, eLambda, x) for x in xVals]

		histHeights, binCenters = hist_and_p_d_f(radiiSizes, expPDFVals, xmin, xmax, xVals)
		plt.title("Histogram of Obtained Radii Sizes & Exponential Distribution PDF."\
			  "\nFamily #" + famObj.globFamNum) 
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()

		cdfs(histHeights, binCenters, expPDFVals, xmin, xmax, xVals)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()

		trueVals = [exp_p_d_f(normConst, eLambda, binCenters[i]) for i in range(len(binCenters))]
		qq(trueVals, histHeights)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()


	def graph_constant(famObj):
		""" Does nothing. Constnat distributions are not graphed.
                """
                #print("  Family #" + famObj.globFamNum + " is a constant distribution and only contains one radius size.")
		pass

	def graph_all_and_not_removed():
		""" Graph fractures from all the families. If some fractures have been removed, also graph the fractures that remain after removal. 
                """
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
			
		
	def graph_distribs():
                """Graph the distribution of each fracture family except user defined families, using a dictionary to reference different distributions' graphing function.
                """
                famNum = 1
		updateStr = "Graphing Family #{} which contains {} fractures."
		graphDistFuncs = {"Lognormal" : graph_lognormal,              ## dict of graph functions
				  "Truncated Power-Law" : graph_trunc_power_law,
				  "Exponential" : graph_exponential,
				  "Constant" : graph_constant }
		
		try: 
			while famNum > 0:
				famObj = families[str(famNum)]
				print(updateStr.format(famObj.globFamNum, len(famObj.radiiList)))

				## give info string from families file its own figure
				fig = plt.figure()
				fig.text(.1,.2,famObj.infoStr, fontsize=15, bbox=dict(facecolor='red', alpha=0.5))
				plt.savefig(outputPDF, format='pdf')

				## then graph info 
				graphDistFuncs[famObj.distrib](famObj) ## families' keys are strings
				plt.close("all")
				famNum += 1
		except KeyError: ## throws key error when we've finished the last family number
			pass


	
	
	collect_family_info()
	graph_translations()
	graph_distribs()
	graph_all_and_not_removed()
	graph_rejections()
	outputPDF.close()

