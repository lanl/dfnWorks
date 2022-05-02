#"""
#   :synopsis: Run file for stressed aperture example
#   :version: 1.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor::  Matthew Sweeney <msweeney2796@lanl.gov> & Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *

DFN = create_dfn()
# create and mesh DFN
DFN.make_working_directory()
DFN.check_input()
DFN.create_network()
DFN.output_report()
DFN.mesh_network()

# Set initial apertures based on a perfectly correlated relationship
variable = "aperture"
function = "correlated"
params = {"alpha": 2 * 10**-5, "beta": 0.5}
b, perm, T = DFN.generate_hydraulic_values(variable, function, params)
DFN.dump_hydraulic_values(b, perm, T)

# create values of the stress tensor
s1 = 5e6
s2 = 1e6
s3 = 1e6
sigma_mat = x = [[s1, 0, 0], [0, s2, 0], [0, 0, s3]]
# modify apertures basedon the stress field
DFN.stress_based_apertures(sigma_mat)
# add apertures to mesh
DFN.add_variable_to_mesh("init_aper", "aperture.dat", "full_mesh.inp",
                         "stress.inp")
DFN.add_variable_to_mesh("stress_aper", "stress_aperture.dat", "stress.inp")

# assign new names of aperture files
DFN.aper_file = "stress_aperture.dat"
DFN.perm_file = "stress_perm.dat"

# dfnFlow()
DFN.lagrit2pflotran()
DFN.pflotran()
DFN.parse_pflotran_vtk_python()
DFN.pflotran_cleanup()

# dfnTrans
DFN.copy_dfn_trans_files()
DFN.check_dfn_trans_run_files()
DFN.run_dfn_trans()

