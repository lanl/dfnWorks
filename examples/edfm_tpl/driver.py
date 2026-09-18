#"""
#   :synopsis: Driver run file for EDFN matrix meshing of a TPL network
#   :version: 2.12.1
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

# Define directory for output
jobname = os.getcwd() + "/output"

DFN = DFNWORKS(jobname, ncpu=4)

# Set domain and edge length parameters for the network
DFN.params['domainSize']['value'] = [15, 15, 15]
DFN.params['h']['value'] = 0.1

# Define a temporary buffer space around the domain
DFN.params['domainSizeIncrease']['value'] = [0.5, 0.5, 0.5]

DFN.params['keepOnlyLargestCluster']['value'] = True
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [1, 1, 0, 0, 0, 0]
DFN.params['seed']['value'] = 2

# Single family network
# alpha is the TPL parameter
# kappa concentration param of the von Mises-Fisher distribution
DFN.add_fracture_family(
    shape="ell",
    distribution="tpl",
    alpha=1.8,
    min_radius=1.0,
    max_radius=10.0,
    orientation_distribution = "fisher",
    kappa=1.0,
    theta=0.0,
    phi=0.0,
    p32=1,
    hy_variable='aperture',
    hy_function='correlated',
    number_of_points=8,
    hy_params={
        "alpha": 10**-5,
        "beta": 0.5
    })

# create the network and write report
DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.create_network()
DFN.output_report()

# This will mesh the network for use in simulations
DFN.mesh_network(min_dist=1, max_dist=5, max_resolution_factor=10)

# Hex/tet matrix mesh with 16 nodes per axis (1 m cells on the 15 m domain).
# Tags every DFN node with the matrix control volume containing it and writes
# matrix.uge, matrix_outside.zone, matrix_cells.dat, matrix_to_dfn_nodes.dat
DFN.mesh_edfn(nx=16, ny=16, nz=16)
