# DFNWorks Example: Two Intersecting Fractures with Flow and Transport

## Overview

This example demonstrates how to:

1.  Build a simple, user-defined discrete fracture network (DFN)
2.  Generate and mesh the network
3.  Solve steady-state flow with **PFLOTRAN**
4.  Compute effective permeability
5.  Perform particle tracking using **DFNTrans**

The setup consists of two rectangular fractures embedded in a 3D domain
with imposed pressure boundary conditions in the x-direction.

------------------------------------------------------------------------

## File Structure

    driver.py              # Main workflow script
    pflotran.in            # PFLOTRAN flow input file
    PTDFN_control.dat      # DFNTrans particle tracking control file

During execution, an `output/` directory is created containing generated
meshes, PFLOTRAN results, and particle tracking outputs.

------------------------------------------------------------------------

## Physical Setup

### Domain

-   Size: **\[2.0, 1.0, 1.0\]**
-   Mesh resolution (`h`): **0.05**

### Fractures

Two rectangular fractures are defined:

**Fracture 1** - Centered at x = -0.5 - Normal vector: \[0, 0, 1\] -
Radius: 0.6 - Aperture: 1e-4 m

**Fracture 2** - Centered at x = 0.5 - Normal vector: \[0, 1, 0\] -
Radius: 0.6 - Aperture: 1e-4 m

The fractures intersect and form a connected network.

------------------------------------------------------------------------

## Flow Configuration (PFLOTRAN)

### Model

-   Simulation type: Subsurface
-   Mode: Richards
-   Steady-state
-   Gravity disabled

### Boundary Conditions

-   Left boundary (inflow): **2.0 MPa**
-   Right boundary (outflow): **1.0 MPa**
-   Initial pressure: **1.5 MPa**
-   Flow direction: **x-axis**

### Outputs

-   Liquid pressure
-   Permeability
-   Mass balance
-   VTK files for visualization

------------------------------------------------------------------------

## Particle Tracking (DFNTrans)

Particle tracking uses the PFLOTRAN Darcy velocity field.

### Key Settings

-   Inflow boundary: left (boundary ID 3)
-   Outflow boundary: right (boundary ID 5)
-   10 particles per inflow fracture edge
-   Flux-weighted particle initialization
-   Control planes enabled
-   Flow direction: x (0)

### Outputs

-   AVS visualization files
-   Particle travel times
-   Control plane breakthrough data
-   Trajectories in `traj/trajectories`

------------------------------------------------------------------------

## Workflow Steps (driver.py)

The driver performs:

1.  Initialize DFNWORKS object
2.  Set domain parameters
3.  Add user-defined fractures
4.  Create working directory
5.  Validate input
6.  Create network geometry
7.  Mesh network
8.  Convert mesh to PFLOTRAN format
9.  Run PFLOTRAN
10. Clean PFLOTRAN output
11. Parse VTK results
12. Compute effective permeability
13. Run DFNTrans particle tracking

Effective permeability is computed in the x-direction using:

-   Inflow pressure: 2e6 Pa
-   Outflow pressure: 1e6 Pa

------------------------------------------------------------------------

## Requirements

-   dfnWorks installed
-   PFLOTRAN compiled and accessible
-   LaGriT available
-   MPI configured (`ncpu=4` in driver)

Ensure environment variables are properly configured before running.

------------------------------------------------------------------------

## How to Run

From the directory containing `driver.py`:

``` bash
python driver.py
```

This will:

-   Create an `output/` directory
-   Build and mesh the DFN
-   Run PFLOTRAN
-   Compute effective permeability
-   Run particle tracking

------------------------------------------------------------------------

## Expected Results

After completion:

-   Pressure gradient across fractures
-   Darcy velocity field
-   Effective permeability in the x-direction
-   Particle trajectories from left to right
-   Control plane crossing data

Results can be visualized in ParaView using generated VTK files.

