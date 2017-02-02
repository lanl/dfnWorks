#test all possible statistics in output report
import os
import subprocess

# define all path names here
dfn_dir = '/home/nknapp/dfnworks-main/'
python_dir = dfn_dir + 'python_scripts/'
input_dir = dfn_dir + 'test_inputs/'
flow_name = input_dir + '4_fracture_test/dfn_explicit.in'
trans_name = input_dir + '4_fracture_test/PTDFN_control.dat'

def get_means():
	mean_list = []
	for exp in range(-3, 4):
		mean_list.append(pow(10, exp))
	return mean_list

def get_sd_ratios():
	return [0.25, 0.5, 0.75]

def getNameFromParams(param_list):
	min_input = param_list[0]
	max_input = param_list[1]
	mean_input = param_list[2]
	sd_input = param_list[3]
	name = "output_test_min_" + "%f" % (min_input) + "_max_" +  "%f" % (max_input) + "_mean_" + "%f" % (mean_input) + "_sd_" + "%f" % (sd_input)
	return name

def write_lognormal_dat_file(param_list, input_dir):
	os.chdir(input_dir)
	name = getNameFromParams(param_list)
	#subprocess.call('mkdir ' + name, shell=True)
	file_name = os.path.abspath(input_dir + "dat_files/" + name + ".dat")
	dat_file = open(file_name, "w")
	min_input = param_list[0]
	max_input = param_list[1]
	mean_input = param_list[2]
	sd_input = param_list[3]
	# NOTE: using two families of rectangles
	dat_file_string = """
	enumPoints: {8,  12}
	eAngleOption: 0
	userRecByCoord: 0
	eExpMean: {2}
	lengthCorrelatedAperture: {5e-5,  0.5}
	r_p32Targets: {.3}
	e_p32Targets: {}
	famProb: {1}
	removeFracturesLessThan: 0
	seed: 0
	ephi: {0}
	rdistr: {1}
	rLogMax: {%(max)s}
	rExpMean: {3.373}
	printRejectReasons: 0
	raspect: {5.0}
	RectByCoord_Input_File_Path: ./inputFiles/userPolygons/rectCoords.dat
	layers: {40, 50} {-20, 37} {-50, -17}
	econst: {10}
	rmin: {0.5}
	rphi: {26.81}
	nFamEll: 0
	eLayer: {}
	rExpMax: {125.0}
	rconst: {3}
	forceLargeFractures: 0
	rtheta: {1.42}
	keepOnlyLargestCluster: 0
	easpect: {}
	rsd: {%(sd)s}
	ebeta: {}
	esd: {}
	eLogMin: {}
	tripleIntersections: 1
	EllByCoord_Input_File_Path: ./inputFiles/userPolygons/rectCoords.dat
	emax: {}
	aperture: 2
	rbeta: {0}
	eLogMax: {}
	rLogMean: {%(mean)s}
	meanAperture: 3
	etheta: {}
	ralpha: {}
	boundaryFaces: {1, 1, 1, 1, 1, 1}
	eExpMax: {}
	outputAllRadii: 0
	apertureFromTransmissivity: { 1.3681, 1 }
	nPoly: 1000
	rmax: {125, 125, 125, 125, 125}
	ealpha: {}
	UserRect_Input_File_Path: ./inputFiles/userPolygons/uRectInput.dat
	outputAcceptedRadiiPerFamily: 1
	eExpMin: {}
	rbetaDistribution: { 1 }
	stdAperture: 0.8
	UserEll_Input_File_Path: ./inputFiles/userPolygons/uEllInput.dat
	rExpMin: {0.5}
	disableFram: 1
	ekappa: {}
	outputFinalRadiiPerFamily: 1
	permOption: 0
	constantAperture: 1e-5
	domainSize: {100.0, 100.0, 100.0}
	userEllByCoord: 0
	constantPermeability: 1e-12
	visualizationMode: 1
	insertUserRectanglesFirst: 1
	nFamRect: 1
	emin: {}
	userRectanglesOnOff: 0
	h: .05
	radiiListIncrease: 0.1
	edistr: {2, 3}
	rejectsPerFracture: 10000
	eLogMean: {4}
	domainSizeIncrease: {0.0, 0.0, 0.0}
	ebetaDistribution: {0, 0}
	numOfLayers: 0
	stopCondition: 0
	rLogMin: {%(min)s}
	userEllipsesOnOff: 0
	rAngleOption: 1
	ignoreBoundaryFaces: 1
	rLayer: {0}
	rkappa: {32.0}
	""" % {'sd': sd_input, 'mean': mean_input, 'min': min_input, 'max': max_input}
	dat_file.write(dat_file_string)
	dat_file.close()
	return file_name

def write_text_file(param_list, flow_name, trans_name, input_dir, gen_name):
	file_name = os.path.abspath(input_dir  + "txt_files/" + getNameFromParams(param_list) +  ".txt")
	os.chdir(input_dir)
	txt_file = open(file_name, "w")
	txt_file.write("dfnGen " + gen_name)
	txt_file.write("\n")
	txt_file.write("dfnFlow " + flow_name)
	txt_file.write("\n")
	txt_file.write("dfnTrans " + trans_name)
	txt_file.close()
	return file_name

def run_test(param_list, flow_name, trans_name, python_dir, input_dir, input_file_name):
	name_string = "~/" +  getNameFromParams(param_list)
	os.chdir(python_dir)
	arg_string = "python run_dfnworks.py -name " + name_string + " -input " + input_file_name
	print arg_string
	subprocess.call(arg_string, shell=True)

# test 0.5, 1, and 1.5 coeffs of variation for all means
def get_all_param_lists():
	mean_list = get_means()
	sd_ratio_list = get_sd_ratios()
	min_ratio = 0.1
	max_ratio = 5
	list_of_param_lists = []
	for mean in mean_list:
		mn = min_ratio*mean
		mx = max_ratio*mean
		for sd_ratio in sd_ratio_list:
			sd = sd_ratio*mean
			param_list = [mn, mx, mean, sd]
			list_of_param_lists.append(param_list)
	print list_of_param_lists
	return list_of_param_lists

def run_all_tests(flow_name, trans_name, python_dir, input_dir):

	list_of_param_lists = get_all_param_lists()
        for param_list in list_of_param_lists[0:1]:
		dat_file_name = write_lognormal_dat_file(param_list, input_dir)
		input_file_name = write_text_file(param_list, flow_name, trans_name, input_dir, dat_file_name)
		run_test(param_list, flow_name, trans_name, python_dir, input_dir, input_file_name)

run_all_tests(flow_name, trans_name, python_dir, input_dir)
