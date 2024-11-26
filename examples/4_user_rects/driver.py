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
dfnFlow_file = src_path + '/dfn_explicit.in'
dfnTrans_file = src_path + '/PTDFN_control.dat'

DFN = DFNWORKS(jobname,
               dfnFlow_file=dfnFlow_file,
               dfnTrans_file=dfnTrans_file,
               ncpu=4)

DFN.params['domainSize']['value'] = [1.0, 1.0, 1.0]
DFN.params['h']['value'] = 0.1

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
                   radii=.6,
                   translation=[0.4, 0, 0.2],
                   normal_vector=[0, 0, 1],
                   permeability=2.0e-12)

DFN.add_user_fract(shape='rect',
                   radii=.6,
                   translation=[0.4, 0, -0.2],
                   normal_vector=[0, 0, 1],
                   permeability=1.0e-12)

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.print_domain_parameters()

DFN.create_network()

DFN.mesh_network()
DFN.dfn_flow()
DFN.dfn_trans()
