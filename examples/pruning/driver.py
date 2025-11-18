# Pruning Example Summary
# This example demonstrates the complete workflow of DFN generation, analysis, and pruning using the truncated power law (TPL) fracture size distribution in pydfnworks. It shows how to configure domain parameters, add multiple fracture families, and generate a discrete fracture network (DFN). The script constructs a network graph representation of the DFN, identifies and extracts the hydraulic backbone (i.e., the connected flow network), and then prunes the original DFN to retain only those flow-connected fractures. Finally, it rebuilds and meshes the pruned backbone network for further simulation or visualization.

# Key steps illustrated include:
# 	•	Setting up the DFNWORKS environment and parameters
# 	•	Adding fracture families with TPL size distributions
# 	•	Generating and graphing the DFN
# 	•	Computing and visualizing the flow backbone
# 	•	Saving and reloading the DFN from a pickle file
# 	•	Creating and meshing the pruned DFN for downstream modeling

## to run from the command line 
## >> python driver.py 

from pydfnworks import *
import os
import networkx as nx

# Get the current working directory
home = os.getcwd()

# Define the job name and output directory for the DFN simulation
# This directory will store all generated files for the "pruned" network
jobname = os.getcwd() + "/output_prune"

# Initialize the DFNWORKS object
# ncpu defines how many CPU cores to use for parallel operations
DFN = DFNWORKS(jobname, ncpu=8)

# -------------------------------
# Define simulation parameters
# -------------------------------

# Domain size in x, y, z directions (in meters)
DFN.params['domainSize']['value'] = [25, 25, 25]

# Grid resolution (spacing for numerical mesh)
DFN.params['h']['value'] = 0.1

# Amount to expand the domain beyond the specified size (in each direction)
DFN.params['domainSizeIncrease']['value'] = [0.5, 0.5, 0.5]

# Keep only the largest connected cluster of fractures
# This removes isolated or disconnected fractures
DFN.params['keepOnlyLargestCluster']['value'] = True

# Define active boundary faces:
# [xmin, xmax, ymin, ymax, zmin, zmax]
# 1 = open (flow boundary), 0 = closed (no flow)
DFN.params['boundaryFaces']['value'] = [1, 1, 0, 0, 0, 0]

# ---------------------------------------------------------
# Define fracture families using a truncated power-law (TPL)
# ---------------------------------------------------------

# Add the first fracture family
# Each fracture family defines a statistical population of fractures
# characterized by geometry, orientation, size distribution, and hydraulic properties.
DFN.add_fracture_family(
    shape="ell",                 # Fracture shape: "ell" = elliptical
    distribution="tpl",          # Fracture size distribution: truncated power law
    kappa=0.1,                   # Fisher parameter controlling spread of orientations (0 = uniform)
    aspect=1,                    # Aspect ratio of fractures (1 = circular)
    beta_distribution=0,         # 0 = fixed beta orientation, 1 = sampled distribution
    beta=0.0,                    # Rotation about the fracture normal
    theta=0.0,                   # Polar (colatitude) angle in spherical coordinates
    phi=0.0,                     # Azimuthal (longitude) angle in spherical coordinates
    alpha=2.1,                   # Power-law exponent controlling fracture size frequency
    min_radius=1.0,              # Minimum fracture radius
    max_radius=10.0,             # Maximum fracture radius
    p32=0.5,                     # Fracture intensity (area per unit volume)
    hy_variable='aperture',      # Hydraulic property being assigned
    hy_function='constant',      # Function defining property distribution (constant value here)
    hy_params={"mu": 2e-6}       # Aperture value (meters)
)

# Add a second fracture family with a different hydraulic property
# This shows how to define multiple fracture populations with distinct apertures.
DFN.add_fracture_family(
    shape="ell",
    distribution="tpl",
    kappa=0.1,
    aspect=1,
    beta_distribution=0,
    beta=0.0,
    theta=0.0,
    phi=0.0,
    alpha=2.1,
    min_radius=1.0,
    max_radius=10.0,
    p32=0.5,
    hy_variable='aperture',
    hy_function='constant',
    hy_params={"mu": 1e-6}       # Smaller mean aperture than the first family
)

# ---------------------------------------------------------
# Create the DFN geometry and network
# ---------------------------------------------------------

# Create a fresh working directory for this DFN run
# Setting delete=True clears any existing output directory
DFN.make_working_directory(delete=True)

# Validate the DFN configuration to ensure inputs are consistent
DFN.check_input()

# Generate the discrete fracture network geometry and associated data
DFN.create_network()

# Build a graph from the DFN using fractures as nodes and intersections as edges
G = DFN.create_graph("fracture", "left", "right")

# Plot the full DFN graph for inspection
DFN.plot_graph(G, output_name="full_dfn")

# Remove dead end features and weak connections from the network
# s and t are the source and target boundary sets
# weight=None uses unweighted edges
# thrs is the minimum flow threshold used to keep an edge
H = DFN.current_flow_threshold(G, "s", "t", weight=None, thrs=1e-16)

# Save the set of fractures that form the flow backbone
DFN.dump_fractures(H, "backbone.dat")

# Plot the backbone graph to visualize the reduced network
DFN.plot_graph(H, output_name="backbone")

# Persist the full DFN state to a pickle for reuse
DFN.to_pickle()

# Release the original DFN object to free memory
del DFN

# -----------------------------------------------------
# Create a new DFN object from the saved state
# and use the backbone to prune and mesh
# -----------------------------------------------------

# Return to the original working directory
os.chdir(home)

# Define a new job for the backbone workflow
jobname = os.getcwd() + os.sep + "output_backbone"

# Source path that contains the previously saved DFN data
src_path = os.getcwd() + "/output_prune/"

# Recreate the DFN object from the pickle of the first run
BACKBONE = DFNWORKS(
    jobname=jobname,
    pickle_file=src_path + "output_prune.pkl"
)

# Provide the list of retained fractures that define the backbone
BACKBONE.prune_file = src_path + "/backbone.dat"

# Set paths and names used by the DFNWORKS workflow
BACKBONE.path = src_path
BACKBONE.jobname = jobname + os.sep
BACKBONE.local_jobname = "output_backbone"

# Enable plotting and visual outputs for this run
BACKBONE.visual_mode = True

# Prepare a fresh working directory for the backbone job
BACKBONE.make_working_directory(delete=True)

# Create the mesh for the pruned backbone network
BACKBONE.mesh_network()
