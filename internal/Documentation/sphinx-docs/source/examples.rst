Examples
=============================


This document contains examples for using dfnWorks. All required input files for these examples are contained in the folder dfnWorks/examples/. The focus of this document is to provide visual confirmation that new users of dfnWorks have the code set up correctly, can carry out the following runs and reproduce the following images. All images are rendered using Paraview, which can be obtained for free at http : //www.paraview.org/. The first two examples are simplest so it is recommended that the user proceed in the order presented here. 

All examples are in the examples/ directory. Within each subdirectory are the files required to run the example. The command line input is found in notes.txt. Be sure that you have created ~/test_output_files prior to running the examples. 


4_user_defined_rects
--------------------------

Location: examples/4_user_defined_rects/


This test case consists of four user defined rectangular fractures within a a cubic domain with sides of length one meter. The network of four fractures, each colored by material ID. The computational mesh is overlaid on the fractures. This image is created by loading the file full_mesh.inp. located in the job folder into Paraview.

.. figure:: figures/4_user_rectangles_mesh.png
   :scale: 10 %
   :alt: alternate text
   :align: center
	
   *The meshed network of four rectangular fractures.*

High pressure (red) Dirichlet boundary conditions are applied on the edge of the single fracture along the boundary x = -0.5, and low pressure (blue) boundary conditions are applied on the edges of the two fractures at the boundary x = 0.5.
This image is created by loading the file parsed_vtk/dfn_explicit-001.vtk into Paraview.


.. figure:: figures/4_user_rectangles_pressure.png 
   :scale: 10 %
   :alt: alternate text
   :align: center
   
   *The network of four fractures, colored by pressure solution.*

Particles are inserted uniformly along the inlet fracture on the left side of the image. 
Particles exit the domain through the two horizontal fractures on the right side of the image.  
Due to the stochastic nature of the particle tracking algorithm, your pathlines might not be exactly the same as in this image. 
Trajectories are colored by the current velocity magnitude of the particle's velocity. 
Trajectories can be visualized by loading the files part\_*.inp, in the folder 4_user_rectangles/traj/trajectories/
We have used the extract surface and tube filters in paraview for visual clarity. 

.. figure:: figures/4_user_rectangles_trace.png
   :scale: 8 %
   :alt: alternate text
   :align: center
   
   *Particle trajectories on the network of four fractures.*   


4_user_defined_ell_uniform
--------------------------

Location: examples/4_user_defined_ell_uniform/


This test case consists of four user defined elliptical fractures within a a cubic domain with sides of length one meter. In this case the ellipses are approximated using 8 vertices. We have set the meshing resolution to be uniform by including the argument slope=0 into the mesh_networks function in run_explicit.py. 

.. figure:: figures/4_user_ellipses_mesh.png
   :scale: 10 %
   :alt: alternate text
   :align: center

   *The uniformly meshed network of four circular fractures.*


.. figure:: figures/4_user_ellipses_pressure.png
   :scale: 10 %
   :alt: alternate text
   :align: center

   *The network of four circular fractures, colored by pressure solution. Contours in the pressure are shown as black lines.*


.. figure:: figures/4_user_ellipses_trace.png
   :scale: 10 %
   :alt: alternate text
   :align: center

   *Particle trajectories on the network of four circular fractures.*   



exp: Exponentially Distributed fracture lengths
-----------------------------------------------------

Location: examples/exp/

This test case consists of a family of fractures whose size is exponentially distributed with a minimum size of 1m and a maximum size of 50m. The domain is cubic with an edge length of 10m. All input parameters for the generator can be found in tests/gen_exponential_dist.dat.  We have changed the flow direction to be aligned with the y-axis by modifying the PFLOTRAN input card dfn_explicit.in

.. figure:: figures/exp_mesh.png
   :scale: 10 %
   :alt: alternate text
   :align: center

   *Network with rectangular fractures whose lengths following a exponential distribution.*


.. figure:: figures/exp_pressure.png
   :scale: 10 %
   :alt: alternate text
   :align: center

   *Pressure solution on with rectangular fractures whose lengths following a exponential distribution. Gradient is aligned with the Y-Axis*




TPL: Truncated Power Law
----------------------------------

Location: examples/TPL/

This test case consists of two families whose sizes have a truncated power law distribution with a minimum size of 1m and a maximum size of 5m an exponent 2.6. The domain size is cubic with an edge length of 15m. 

.. figure:: figures/power_mesh.png
   :scale: 20 %
   :alt: alternate text
   :align: center


Graph based pruning
----------------------

Location: examples/pruning/


This example uses a graph representation of a DFN to isolate the 2-core. The pruned DFN has all dead end fractures of the network are removed. This example has two run_explicit.py scripts. The first creates the original DFN and identifies the 2-core using networkx (https://networkx.github.io/). The second meshes the DFN corresponding to the 2-core of the graph and then runs flow and transport. The 2 core network is in a sub-directory 2-core. The original network has 207 fractures and the 2-core has 79 fractures.



.. figure:: figures/dfn_2_core.png
   :scale: 30 %
   :alt: alternate text
   :align: center

   *(left) Graph based on DFN topology. Each vertex is a fracture in the network. The inflow boundary is colored blue and the outflow is colored red. (right) 2-Core of the graph to the left.*

.. figure:: figures/pruned_network.png
   :scale: 5 %
   :alt: alternate text
   :align: center

   *(left) Original DFN (right) DFN corresponding to the 2-core of the DFN to the left.*


In Fracture Variability
------------------------

Location: examples/in_fracture_var/

This example runs the four rectangular fracture case with variable fracture aperture in each plane. The aperture field is modeled as a correlated multi-variant Gaussian random field. The aperture values are in the aper_node.dat file and the permeabilities are in perm_node.dat. The command line argument indicating that there is spatially variable aperture field is -cell.  In fracture variability is not supported for FEHM runs at this time. 

.. figure:: figures/in_fracture_var_perm.png
   :scale: 10 %
   :alt: alternate text
   :align: center

   *The meshed network of four rectangular fractures colored by permeability, which is spatially variable on each fracture.*



.. figure:: figures/in_fracture_var_pressure.png
   :scale: 10 %
   :alt: alternate text
   :align: center

   *The network of four fractures, colored by pressure solution. Black lines are contours in the pressure field.*
