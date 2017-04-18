# this script ONLY runs the output report script - it assumes the DFN generator output files are in directory [ARG1]
# Usage: python get_output_report.py [dfnGen output file directory name]

import os, sys, subprocess
from pydfnworks import only_gen_output

dir_name = sys.argv[1]
only_gen_output.only_output_report(dir_name)



