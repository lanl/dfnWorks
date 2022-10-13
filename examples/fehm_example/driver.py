#"""
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



DFN.params['domainSize']['value'] = [100, 100, 100]
DFN.params['h']['value'] = 1.0
DFN.params['stopCondition']['value'] = 0
DFN.params['nPoly']['value'] = 100
DFN.params['tripleIntersections']['value'] = True
DFN.params['domainSizeIncrease']['value'] = [10, 10, 10]
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [0,0,0,0,1,1]
DFN.params['seed']['value'] = 3081976507

DFN.add_fracture_family(shape="ell",
                        distribution="constant",
                        kappa=20.0,
                        probability=.5,
                        aspect=1,
                        beta_distribution=1,
                        beta=0.0,
                        theta=0.0,
                        phi=90.0,
                        constant = 25,
                        number_of_points = 12,
                        hy_variable = 'aperture',
                        hy_function = 'log-normal',
                        hy_params = {"mu":1e-5,"sigma":1})

DFN.add_fracture_family(shape="ell",
                        distribution="constant",
                        kappa=20.0,
                        probability=.5,
                        aspect=1,
                        beta_distribution=1,
                        beta=0.0,
                        theta=90.0,
                        phi=0.0,
                        constant=25,
                        number_of_points = 12,
                        hy_variable = 'aperture',
                        hy_function = 'log-normal',
                        hy_params = {"mu":1e-5,"sigma":1})

DFN.print_family_information(1)

DFN.make_working_directory(delete=True)

DFN.check_input()

for key in DFN.params.keys():
    print(key, DFN.params[key]['value'])

# define_paths()
DFN.create_network()
# DFN.output_report()
DFN.mesh_network(coarse_factor=10)

DFN.set_flow_solver("FEHM")
DFN.correct_stor_file()
DFN.fehm()


print("*"*80)
print(DFN.jobname+' complete')
print("Thank you for using dfnWorks")
