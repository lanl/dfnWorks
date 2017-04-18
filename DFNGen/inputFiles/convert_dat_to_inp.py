import glob
import os

files = glob.glob('*.dat')
for file in files:
	fname = file[:-4]
	new_fname = fname + '.inp'
	os.system('mv ' + file + ' ' + new_fname)
