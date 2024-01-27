#"""
#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

src_path = os.getcwd()
jobname = src_path + "/output"
dfnFlow_file = src_path + '/dfn_explicit_multi_material.in'

DFN = DFNWORKS(jobname,
               dfnFlow_file=dfnFlow_file,
               flow_solver="PFLOTRAN",
               ncpu=8)

DFN.params['domainSize']['value'] = [1.0, 1.0, 1.0]
DFN.params['h']['value'] = 0.1
DFN.params['visualizationMode']['value'] = True

DFN.add_user_fract(shape='rect',
                   radii=0.6,
                   translation=[-0.4, 0, 0],
                   normal_vector=[0, 0, 1],
                   permeability=1.0e-12)

DFN.add_user_fract(shape='rect',
                   radii=1.0,
                   aspect_ratio=.65,
                   translation=[0, 0, 0],
                   normal_vector=[1, 0, 0],
                   permeability=1.0e-12)

DFN.add_user_fract(shape='rect',
                   radii=0.6,
                   translation=[0.4, 0, 0.2],
                   normal_vector=[0, 0, 1],
                   permeability=2.0e-12)

DFN.add_user_fract(shape='rect',
                   radii=0.6,
                   translation=[0.4, 0, -0.2],
                   normal_vector=[0, 0, 1],
                   permeability=1.0e-12)

DFN.make_working_directory(delete=True)
DFN.check_input()
# define_paths()
DFN.create_network()
DFN.mesh_network()

DFN.map_to_continuum(l=0.3, orl=3)
DFN.upscale(mat_perm=1e-15, mat_por=0.01)

DFN.zone2ex(zone_file='all')

DFN.pflotran()
DFN.parse_pflotran_vtk_python()
DFN.pflotran_cleanup()
