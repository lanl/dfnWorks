import os
import sys
import shutil
sys.path.append('./Test_Inputs');
import Intersection_Shortening_Test1
import Intersection_Shortening_Small_Angle_Test
import Overshorten_Intersection_Test

# These tests require visual inspection 
# of the output meshes to determin if the tests 
# passed of failed

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
			
	print "\nNOTE: Some tests require visual inspection of the output meshes to determine whether the shortening intersection algorithm is operating correctly.\n"
				
	#rename old output folder
	os.rename(output_path, output_path + "_old")
	#remove old output folder
	shutil.rmtree(output_path + '_old')
		
#create output directory
os.makedirs(output_path)

#################  Run Interseciton Shortening Tests  ####################
Intersection_Shortening_Test1.test(output_path)

Intersection_Shortening_Small_Angle_Test.test(output_path)

Overshorten_Intersection_Test.test(output_path)



