#"""
#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

src_path = os.getcwd()
jobname = f"{src_path}/output"

DFN = DFNWORKS(jobname)

DFN.params['domainSize']['value'] = [100, 100, 100]
DFN.params['h']['value'] = 1
DFN.params['visualizationMode']['value'] = True

DFN.add_user_fract(shape='ell',
                   filename=f'{src_path}/user_defined_faults.dat',
                   radii=100,
                   translation=[0, 0, 25],
                   orientation_option='trend_plunge',
                   angle_option='degree',
                   trend_plunge=[45, 35],
                   number_of_vertices=8,
                   permeability=1e-12)

DFN.add_user_fract(shape='ell',
                   radii=100,
                   translation=[0, 25, 0],
                   orientation_option='trend_plunge',
                   angle_option='degree',
                   trend_plunge=[111, 57],
                   number_of_vertices=8,
                   permeability=1e-13)

DFN.make_working_directory(delete=True)

DFN.check_input()
DFN.create_network()
DFN.mesh_network()
