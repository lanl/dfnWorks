"""
#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

jobname = os.getcwd() + "/output"
dfnFlow_file = os.getcwd() + '/dfn_explicit.in'
dfnTrans_file = os.getcwd() + '/PTDFN_control.dat'

DFN = DFNWORKS(jobname,
               dfnFlow_file=dfnFlow_file,
               dfnTrans_file=dfnTrans_file,
               ncpu=8)

DFN.params['domainSize']['value'] = [10, 10, 10]
DFN.params['h']['value'] = 0.1
DFN.params['stopCondition']['value'] = 0
DFN.params['nPoly']['value'] = 200
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [1, 1, 0, 0, 0, 0]

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=20.0,
                        probability=.33,
                        aspect=1,
                        beta_distribution=1,
                        beta=0.0,
                        theta=0.0,
                        phi=0.0,
                        alpha=2.5,
                        min_radius=1.0,
                        max_radius=5.0,
                        p32=0.5,
                        hy_variable="aperture",
                        hy_function="correlated",
                        hy_params={
                            "alpha": 2e-5,
                            "beta": .5
                        })

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=20.0,
                        probability=.33,
                        aspect=1,
                        beta_distribution=1,
                        beta=0.0,
                        theta=90.0,
                        phi=0.0,
                        alpha=2.5,
                        min_radius=1.0,
                        max_radius=5.0,
                        p32=0.5,
                        hy_variable="aperture",
                        hy_function="correlated",
                        hy_params={
                            "alpha": 2e-5,
                            "beta": .5
                        })

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=20.0,
                        probability=.34,
                        aspect=1,
                        beta_distribution=1,
                        beta=0.0,
                        theta=90.0,
                        phi=90.0,
                        alpha=2.5,
                        min_radius=1.0,
                        max_radius=5.0,
                        hy_variable="aperture",
                        hy_function="correlated",
                        hy_params={
                            "alpha": 2e-5,
                            "beta": .5
                        })

DFN.make_working_directory(delete=True)

DFN.check_input()
DFN.create_network()
DFN.mesh_network(max_dist=20, max_resolution_factor=40)

# create values of the stress tensor
s1 = 5e6
s2 = 1e6
s3 = 1e6
sigma_mat = x = [[s1, 0, 0], [0, s2, 0], [0, 0, s3]]
DFN.dump_hydraulic_values()
DFN.add_variable_to_mesh("init_aper", "aperture.dat", "full_mesh.inp",
                         "stress.inp")
# modify apertures basedon the stress field
DFN.stress_based_apertures(sigma_mat)
# add final apertures to mesh
DFN.dump_hydraulic_values()
DFN.add_variable_to_mesh("stress_aper", "aperture.dat", "stress.inp")

# assign new names of aperture files
DFN.aper_file = "stress_aperture.dat"
DFN.perm_file = "stress_perm.dat"
DFN.dump_hydraulic_values()

# dfnFlow()
DFN.lagrit2pflotran()
DFN.pflotran()
DFN.parse_pflotran_vtk_python()
DFN.pflotran_cleanup()

# dfnTrans
DFN.copy_dfn_trans_files()
DFN.check_dfn_trans_run_files()
DFN.run_dfn_trans()
