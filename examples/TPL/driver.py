#"""
#   :synopsis: Driver run file for TPL Tutorial
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os
import numpy as np

# Example run will create a one family network
# Change output and uncomment 2nd family for 2 family network

# Define directory for output
jobname = os.getcwd() + "/output"
#jobname = os.getcwd() + "/output2"

# These are the input files for PFLOTRAN Flow and Particles
dfnFlow_file = os.getcwd() + '/dfn_explicit.in'
dfnTrans_file = os.getcwd() + '/PTDFN_control.dat'

DFN = DFNWORKS(jobname,
               dfnFlow_file=dfnFlow_file,
               dfnTrans_file=dfnTrans_file,
               ncpu=12)

# Set domain and edge length parameters for the network
DFN.params['domainSize']['value'] = [15, 15, 15]
DFN.params['h']['value'] = 0.1

# Define a temporary buffer space around the domain
DFN.params['domainSizeIncrease']['value'] = [0.5, 0.5, 0.5]

DFN.params['keepOnlyLargestCluster']['value'] = True
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [1, 1, 0, 0, 0, 0]
DFN.params['seed']['value'] = 2

# CHECK shapes before meshing 
# NOTE this will write reduced_mesh.inp instead of full_mesh.inp
# DFN.params['visualizationMode']['value'] = TRUE 

# Single family network
# alpha is the TPL parameter
# kappa concentration param of the von Mises-Fisher distribution
# beta angle rotation around fracture axis
# spherical theta for Z and phi for XY plane
DFN.add_fracture_family(
    shape="ell",
    distribution="tpl",
    alpha=1.8,
    min_radius=1.0,
    max_radius=10.0,
    kappa=1.0,
    theta=0.0,
    phi=0.0,
    #aspect=2,
    p32=1,
    hy_variable='aperture',
    hy_function='correlated',
    number_of_points=8,
    hy_params={
        "alpha": 10**-5,
        "beta": 0.5
    })

# Add a second family 
# Change output directory first
#
# DFN.add_fracture_family(
#     shape="ell",
#     distribution="tpl",
#     alpha=1.8,
#     min_radius=1.0,
#     max_radius=10.0,
#     kappa=1.0,
#     theta=1.42,
#     phi=26.81,
#     p32=1,
#     hy_variable='aperture',
#     hy_function='correlated',
#     number_of_points=8,
#     hy_params={
#         "alpha": 10**-5,
#         "beta": 0.5
#     })

# create the network and write report
DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.create_network()
DFN.output_report()

# This will mesh the network for use in simulations
DFN.mesh_network(min_dist=1, max_dist=5, max_resolution_factor=10)

# CHECK the mesh before simulations
# exit()

# run PFLOTRAN flow simulation
DFN.dfn_flow()

# run particle simulation and combine 1000 part*inp files
DFN.dfn_trans(combine_avs = True)

