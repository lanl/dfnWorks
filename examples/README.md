
# Example Descriptions
 

- ### 4_user_ell_uniform (4_user_defined_ell_uniform)

   This test case consists of four user defined elliptical fractures within a a cubic domain with sides of length one meter. Resolution is uniform and slope = 0.

   See [Example Description](https://lanl.github.io/dfnWorks/examples.html)

   See [Example Run](https://lanl.github.io/dfnWorks/pydfnworks.html)


- ### 4_user_rects (4_user_defined_rects)

   Simple example with  four user defined rectangular fractures within a a cubic domain. 

   See [Example Description](https://lanl.github.io/dfnWorks/examples.html)

   See dfnworks_overview_short.pdf



- ### ade_example


    Uses DFN.add_fracture_family to create rectangle fractures and runs PFLOTRAN for Transport simulation with files dfn_explicit.in and  dfn_restart.in


- ### calibrate_p32_from_p10

    This examples shows one method to calibirate p32 using p10 data. A fake well is put into the center of the domain.
    We then create a network with a p32 value and count the number of fractures that intersect that well. We then use a root finding method to find the p32 value that provides the desired p10 value.


- ### constant

    Uses DFN.add_fracture_family(shape="rect" calls to create DFN. Uses PFLOTRAN for flow and FEHM for particle tracking.


- ### dfm_4_frac

    Uses DFN.add_user_fract(shape='rect' to create 4 rectangle fractures for uniform mesh. No simulations.


- ### exp (Exponentially Distributed fracture lengths)

   This test case creates a family of fractures whose size is exponentially distributed with a minimum size of 1m and a maximum size of 50m. The domain is cubic with an edge length of 10m. PFLOTRAN and FEHM simulations are run.

   See [Example Description](https://lanl.github.io/dfnWorks/examples.html)


- ### faults

    Defines a 100x100x100 domain using DFN.add_user_fract(shape='ell', filename=f'{src_path}/user_defined_faults.dat', radii=100 to create ellipse fractures. No simulations.


- ### fehm_example

   Creates ellipse fractures with constant distribution. Runs FEHM Water/CO2 on fracture mesh.


- ### graph_transport

    Creates ellipse fractures with tpl distribution. Simulations use DFN.run_graph_flow and DFN.run_graph_transport with ```10**4``` particles.


- ### hy_test

    Uses DFN.add_fracture_family(shape="rect", distribution="exp" fracture distribution with parameters  hy_variable='permeability', hy_function='semi-correlated', hy_params={"alpha": 10**-8,"beta": 0.5,"sigma": 1.0}. PFLOTRAN and FEHM simulations are run.


- ### layers


    Create ellipse fracture with 2 layers. 


- ### lognormal


    Uses DFN.add_fracture_family(shape="rect", distribution="log_normal" to create fractures and run flow and transport simulations.


- ### mapdfn

    Creates ellipse fractures with tpl distribution plus user defined fractures. Runs PFLOTRAN simulations defined in files cpm_pflotran.in and cpm_pflotran.in.


- ### polygon_domain_boundary

    Uses file vertices.dat for boundary. No simulations but PFLOTRAN input file is in directory.


- ### pruning (Graph-based pruning)

    This is an example of using pruning to remove all dead end fractures. There are 2 runs, the first creates the DFN and the network to use. The second meshes the DFN and runs flow and transport.

    See [Example Description](https://lanl.github.io/dfnWorks/examples.html)


- ### regions

    Uses parameter 'regions']['value'] = [[-5, 5, -5, 5, -5, 5] with rectangle fractures.


- ### stress

    Creates ellipse fractures and adds stress based aperature variables to the mesh. Simulations from dfnFlow and dfnTrans using PFLOTRAN and FEHM. 


- ### tdrw

    Create rectangle fractures and run FEHM simulation using PFLOTRAN flow solutions as input. Various options for particles are used.


- ### TPL (Truncated Power-Law)

    This example consists of two families whose sizes have a truncated power law distribution with a minimum size of 1m and a maximum size of 5m an exponent 2.6.

    See [Example Description](https://lanl.github.io/dfnWorks/examples.html)


- ### udfm

    Create four rectangle fractures. Uses DFN.map_to_continuum and DFN.upscale. Runs PFLOTRAN simulation.

- ### user_polygons


    Uses polygons defined in polygons.dat to create 9 fractures. Flow simulation is run.


- ### well_example

    Creates 400 ellispse fractures with tpl distribution. Intersections along well path are defined. PFLOTRAN is run with well injection and well extraction.

