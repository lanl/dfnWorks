#!/usr/bin/env python
import os,sys
import time 

#try:
#	correct_uge = os.environ['correct_uge_path']
#	#dfnworks_python_dir = os.environ['dfnworks_python']
#except KeyError:
#    print('dfnworks_python must point to the dfnworks-python installation directory and be defined in system environmental variables.')
#    sys.exit(1)
#
#sys.path.append(dfnworks_python_dir)

from dfnworks_v3 import *

dfn = dfnworks(inp_file='full_mesh.inp',perm_file='perm.dat',aper_file='aperture.dat')
t = time.time()
dfn.lagrit2pflotran()
elapsed = time.time() - t
print '--> Time for UGE file: ', elapsed

dfn.zone2ex(zone_file='pboundary_back_n.zone',face='north')
dfn.zone2ex(zone_file='pboundary_front_s.zone',face='south')
dfn.zone2ex(zone_file='pboundary_left_w.zone',face='west')
dfn.zone2ex(zone_file='pboundary_right_e.zone',face='east')
dfn.zone2ex(zone_file='pboundary_top.zone',face='top')
dfn.zone2ex(zone_file='pboundary_bottom.zone',face='bottom')
dfn.parse_pflotran_vtk()
