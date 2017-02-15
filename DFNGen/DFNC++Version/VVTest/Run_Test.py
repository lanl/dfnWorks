import os
import sys
import shutil
sys.path.append('./Test_Inputs');
import Intersection_Close_To_Edge_Test
import Intersection_Close_To_Parallel_Edge_Test
import Small_Intersection_Test
import Triple_Intersection_Angle_Test
import Intersect_On_Edge_Test
import Close_Triple_Points_Test
import Close_Intersection_To_Intersection_Test


#################### MAIN #######################
if len(sys.argv) != 2:
	print "Invalid cmd line options"
	print "Arg 1: Desired output folder path"
	exit()
 
output_path = sys.argv[1]

if os.path.exists(output_path):
	while True:
		print "\nWARNING:  " + output_path + " will be OVERWRITTEN"
		yesOrNo = raw_input ("CONTINUE? (yes/no) \n")
		if yesOrNo == "yes" or yesOrNo == "Yes":
			break;
		elif yesOrNo == "no" or yesOrNo == "No":
			exit()			
	#rename old output folder
	os.rename(output_path, output_path + "_old")
	#remove old output folder
	shutil.rmtree(output_path + '_old')
		
#create output directory
os.makedirs(output_path)

#################  Run DFNGen Tests  ####################
Intersection_Close_To_Edge_Test.test(output_path)

Small_Intersection_Test.test(output_path)

Triple_Intersection_Angle_Test.test(output_path)

# The last test in this section of tests should reject until FRAM is updated
Intersection_Close_To_Parallel_Edge_Test.test(output_path)

# This test should reject until changes are made to FRAM
# and intersectionChecking()
Intersect_On_Edge_Test.test(output_path)

Close_Triple_Points_Test.test(output_path)
 	
Close_Intersection_To_Intersection_Test.test(output_path)
