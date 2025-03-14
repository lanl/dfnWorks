
dfnWorks Introduction and Beginner Tutorial
==============================================

This tutorial serves as an introduction to dfnWorks for new users. It covers the example 4_user_rect, providing a detailed explanation and running instructions. All images are rendered using ParaView, which can be downloaded for free at www.paraview.org. By the end of this tutorial, users should feel confident running additional examples and applying them to their own projects. 

For the Tutorial, you can run dfnWorks using Docker or build it on your own machine. For initial runs, we recommend using Docker, as it simplifies the setup process before committing time to install the full suite. For more information, please refer to the Setup and Installation section at :ref:`pydfnWorks install <pydfnworks-setup>`.
 

The following items are covered in this Tutorial:

.. contents::
   :depth: 2
   :local:


dfnWorks Package Overview
--------------------------


.. figure:: figures/dfnworks_pdf_modules_copy.png
   :scale: 50 % 
   :alt: alternate text
   :align: center


   *dfnWorks modules include dfnGen for meshing with dfnFlow and dfnTrans for simulations.*



dfnWorks is a parallelized computational suite to generate three-dimensional discrete fracture networks (DFN) and simulate flow and transport. To run a workflow using the dfnWorks suite, the python pydfnworks package is used. The package pydfnworks calls
various tools in the dfnWorks suite with the aim to provide a seamless workflow. 

There are 3 main modules in dfnWorks:


dfnGen 
~~~~~~~~~~~~~~~~~

dfnGen primarily involves two steps: FRAM (the feature rejection algorithm for meshing) and LaGriT, the meshing tool box used to create a conforming Delaunay triangulation of the network.

-	FRAM (feature rejection algorithm for meshing) is executed using the dfnGen C++ source code, contained in the dfnGen folder of the dfnWorks repository.
-	The LaGriT meshing toolbox is used to create a high resolution computational mesh representation of the DFN. An algorithm for conforming Delaunay triangulation is implemented so that fracture intersections are coincident with triangle edges in the mesh and Voronoi control volumes are suitable for finite volume flow solvers such as FEHM and PFLOTRAN.

See the docs at :ref:`pydfnWorks: dfnGen <dfngen-chapter>`


dfnFlow 
~~~~~~~~~~~~~~~~~~~~

Setup files and workflow include the use of PFLOTRAN or FEHM to solve for flow using the mesh files from LaGriT.

-	PFLOTRAN is a massively parallel subsurface flow and reactive transport code. PFLOTRAN solves a system of partial differential equations for multiphase, multicomponent and multiscale reactive flow and transport in porous media. 
- FEHM is a subsurface multiphase flow code developed at Los Alamos National Laboratory.

See the docs at :ref:`pydfnWorks: dfnFlow <dfnflow-chapter>`


dfnTrans 
~~~~~~~~~~~~~~~~~~~~~


dfnTrans is a method for resolving solute transport using control volume flow solutions obtained from dfnFlow on the unstructured mesh generated using dfnGen. We adopt a Lagrangian approach and represent a non-reactive conservative solute as a collection of indivisible passive tracer particles.

See the docs at :ref:`pydfnWorks: dfnTrans <dfntrans-chapter>`



Beginner Tutorial 4 User Rectangles
------------------------------------

There are many dfnWorks projects in dfnWorks/examples, this tutorial will use dfnWorks/examples/4_user_rects.

This test case consists of four user defined rectangular fractures within a a cubic domain with sides of length one meter. After running dfnWorks you will view the fracture mesh, the fractures colored by pressure, and the particle tracks as shown in this image. 


.. figure:: figures/4_user_rectangles.png
   :height: 350px 
   :alt: 3 views of 4_user_rect 
   :align: center
	
   *Figure shows 4_user_rect  meshed network of four fractures with views of the mesh (left), pressure (middle), and particle tracks (right).*


dfnWorks is run in a terminal where you will interact with the system using text commands. The command line requires you to type commands and manage files directly, so it can be a bit more challenging initially. However, once you get familiar with the command line, it can offer greater flexibility and automation capabilities, especially for running batch processes or integrating scripts into larger workflows.

This guide will help beginners understand the essential steps involved in setting up and executing dfnWorks. 



Tutorial Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~


- Docker dfnWorks is recommended for new users.
- If you are not using Docker, Ensure that you have Python and the PyDFNworks package installed in your environment.

For Docker and Build Instructions see :ref:`pydfnWorks install <pydfnworks-setup>`
 
- Download a clone of the dfnWorks repository for this example and others 

.. code-block:: bash

    $ git clone https://github.com/lanl/dfnWorks.git



Paraview_ is an open-source visualization software and is used to create images in this document. 
While not required for running dfnWorks, Paraview is very helpful for visualizing the fracture mesh and simulations.
Instructions for downloading and installing Paraview_ can be found at http://www.paraview.org/download/ 

.. _Paraview: http://www.paraview.org




Step 1. Navigate to Example Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From the top of dfnWorks repository, use the `cd` command to move to the folder where input files and driver.py are located. 

.. code-block:: bash

    cd examples/4_user_rects


Familiarize yourself with the structure of your project directory and the expected input files.

`driver.py` is the python script controlling the files and the workflow.
`dfn_explicit.in` is PFLOTRAN control file
`PTDFN_control.dat` is the FEHM control file for particle tracking


Step 2. Execute the `driver.py` script 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the terminal, execute the script using Python.

.. code-block:: bash

    python driver.py


If you are running files within Docker with dfnWorks (no mounted volume):

.. code-block:: bash

    docker pull ees16/dfnworks:latest
    docker run -ti ees16/dfnworks:latest
    python driver.py


If you are running with Docker dfnWorks with the cloned repository as your mounted volume:

.. code-block:: bash

    docker pull ees16/dfnworks:latest
    docker run -v "$(pwd):/app" -w /app ees16/dfnworks:latest python driver.py


While dfnWorks is running, you will see extensive reporting to the screen. This will alert you to errors or missing files. When done a report file is written to `output.log`. This is the first place to check if there were any issues. Look for the first occurrence of Errors as fixing those will likely fix the ones that follow. Warnings can usually be ignored but may be helpful.

The directory `/output` is created and contains files written during the run. Many of the files were created as input for the meshing and simulation portions of the workflow. These files can be helpful in understanding the run and for viewing the mesh and fractures used.
A list of files and their descriptions are at :ref:`dfnWorks Files <output-chapter>`.



Step 3. Understanding the Script 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open the script python `driver.py`. You can open with any text editor or use the unix command ``cat driver.py`` which will display the content to the screen.


Script: Initialization
^^^^^^^^^^^^^^^^^^^^^

The script begins by importing the necessary libraries and setting up paths for input files and the output directory. 

- It creates a DFNWORKS object, specifying paths for the flow and transport control files. 
- It prepares the output environment using make_working_directory(delete=True), which ensures a fresh directory for storing results. 


Script: Define Parameters
^^^^^^^^^^^^^^^^^^^^^

The domain size and hydraulic head are defined. This defines domain to a cube of size 1 unit in all dimensions and sets h (hydraulic head of fluid in domain) to 0.1 unit.

.. code-block:: python

    DFN.params['domainSize']['value'] = [1.0, 1.0, 1.0] 
    DFN.params['h']['value'] = 0.1  


Script: Define Fractures
^^^^^^^^^^^^^^^^^^^^^

The dfnGen module manages and creates the fracture network. Parameters can be set using fracture families (for generated fractures) or set by the user. See a full description of fracture paramters and commands at :ref:`pydfnWorks: dfnGen <dfngen-chapter>`. 

The script for this example uses `add_user_fract` commands to create rectangular-shaped fractures with specified properties such as radius, translation, normal vector, and permeability. Four fractures are created in this example.

    Key fracture parameters include: 
    - Shape : The geometric shape of the fracture (e.g., 'rect' for rectangular). 
    - Radii : The size or extent of the fracture. 
    - Aspect Ratio : The ratio of the length to width for non-circular fractures. 
    - Translation : The position of the fracture in the domain. 
    - Normal Vector : This represents the orientation of the fracture. 
    - Permeability : Describes how easily fluids can pass through the fracture. 


For this example, four fractures are created. Their shape is rectangle, with radii less than the length of the domain of 1. Three fractures are horizontal with normal in positive Z direction and translated  by .4 in the X direction. One fracture is at Z=0, the other horizontal fractures are translated above and below by .2. The 2nd fracture is vertical with a radii of 1, equal to the domain width. 

.. code-block:: python

    DFN.add_user_fract(shape='rect',
        radii=0.6, translation=[-0.4, 0, 0], normal_vector=[0, 0, 1], permeability=1.0e-12)

    DFN.add_user_fract(shape='rect',
        radii=1.0, aspect_ratio=.65, translation=[0, 0, 0], normal_vector=[1, 0, 0], permeability=1.0e-12)

    DFN.add_user_fract(shape='rect',
        radii=.6, translation=[0.4, 0, 0.2], normal_vector=[0, 0, 1], permeability=2.0e-12)

    DFN.add_user_fract(shape='rect',
        radii=.6, translation=[0.4, 0, -0.2], normal_vector=[0, 0, 1], permeability=1.0e-12)



.. figure:: figures/tut1_polys_setup.png
   :width: 500px
   :alt: fracture setup 
   :align: center

   *Figure shows fractures in order of definitions 1 (blue), 2 (green vertical), 3 (orange top), and 4 (red bottom).*


This image was created with Paraview reading the AVS mesh file output/full_mesh.inp. The fractures are colored by Material ID as assigned by dfnGen module. It is a good idea to create the fracture mesh and check it before running the simulations.  




Script: Mesh the Fracture Network
^^^^^^^^^^^^^^^^^^^^^^^^^^

Once parameters and fractures have been defined, the script checks if the inputs are correct and prints the parameters of the domain for verification.  If everything checks ok, the `create_network()` method generates the fracture network based on the defined parameters.

It is recommended that you stop driver.py after `create_network()` but before calling the simulations. Ensure the mesh and all checks are good and as expected.  Observe output screen reports and the output log file, all tests should output "Test passed". Any tests which ouput "TEST FAILED" must be debugged.

Viewing the the mesh and program output files will allow simple mistakes to be fixed. 
Checking the output log file to screen and file `output.log`, the mesh reports look as expected:
 

Script: Run Simulations  
^^^^^^^^^^^^^^^^^^^^^


Once the mesh looks good, executes flow and transport simulations using dfn_flow() and dfn_trans(). Simple runs can  provide insights into the behavior of fluids  within the fractured network.  

View the dfnFlow_file '/dfn_explicit.in'. This is a PFLOTRAN input file.  High pressure (red) Dirichlet boundary conditions are applied on the edge of the single fracture along the boundary x = -0.5, and low pressure (blue) boundary conditions are applied on the edges of the two fractures at the boundary x = 0.5. 


View the dfnTrans_file '/PTDFN_control.dat.  Particles are inserted uniformly along the inlet fracture on the left side of the image. Particles exit the domain through the two horizontal fractures on the right side of the image. 



Step 4. Verify the Fracture Mesh 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Upon completion of the script, output files will be created in the specified `output` directory. Review these files to analyze your DFN simulation results. See full description of files at files.rst

After generation, verify the mesh quality using the mesh quality tools available in the interface. Look for warnings or errors that may indicate issues with element quality or aspect ratios.

Viewing the the mesh and program output files will allow simple mistakes to be fixed.
Checking the output log file to screen and file `output.log`, the mesh reports look as expected:


.. code-block:: bash

     Meshing DFN using LaGriT : Starting
     ================================================================================
     --> Computing mesh resolution function
     --> Variable Mesh Resolution Selected
     *** Minimum distance [m] from intersection with constant resolution h/2 : 0.05
     *** Maximum distance [m] from intersection variable resolution : 1.0
     *** Upper bound on resolution [m] : 1.00


Additional output information and log files are written in the `output` directory. Checking the report in `output/dfngen_logfile.txt` the following information confirms the DFN mesh was created with no Errors. Note extra files are written to aid evaluations if needed.


.. code-block:: bash

    [2025-03-06 17:15:01] INFO: 4 Fractures Accepted (Before Isolated Fracture Removal)
    [2025-03-06 17:15:01] INFO: 4 Final Fractures (After Isolated Fracture Removal)
    [2025-03-06 17:15:01] INFO: /app/output/dfnGen_output
    [2025-03-06 17:15:01] INFO: Writing /app/output/dfnGen_output/../params.txt
    [2025-03-06 17:15:01] INFO: Writing Radii File (radii.dat)
    [2025-03-06 17:15:01] INFO: Writing Rejection Statistics File (rejections.dat)
    [2025-03-06 17:15:01] INFO: Writing Family Definitions File (families.dat)
    [2025-03-06 17:15:02] INFO: Writing Fracture Translations File (translations.dat)
    [2025-03-06 17:15:02] INFO: Writing Connectivity Data (connectivity.dat)
    [2025-03-06 17:15:02] INFO: Writing Rotation Data File (poly_info.dat)
    [2025-03-06 17:15:02] INFO: Writing Normal Vectors into File (normal_vectors.dat)
    [2025-03-06 17:15:02] INFO: Writing Rotation Data File (rejectsPerAttempt.dat)
    [2025-03-06 17:15:02] INFO: DFNGen - Complete


.. figure:: figures/tut1_mesh_lines.png
   :width: 500px 
   :alt: fracture mesh
   :align: center


   *dfnWorks modules include dfnGen for meshing with dfnFlow and dfnTrans for simulations.*


.. figure:: figures/tut1_mesh_no_poly2.png
   :width: 500px 
   :alt: fracture intersections
   :align: center


   *dfnWorks modules include dfnGen for meshing with dfnFlow and dfnTrans for simulations.*



Step 5. Analyze Simulation Results 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

High pressure (red) Dirichlet boundary conditions are applied on the edge of the single fracture along the boundary x = -0.5, and low pressure (blue) boundary conditions are applied on the edges of the two fractures at the boundary x = 0.5. This image is created by loading the file 4_user_defined_rectangles/PFLOTRAN/parsed_vtk/dfn_explicit-001.vtk into Paraview.


View `output.log` to verify the dfnFlow module was successful and result files were written.

.. code-block:: bash

    2025-03-06 17:15:04,156 INFO --> Running PFLOTRAN
    2025-03-06 17:15:04,157 INFO --> Running: /dfnWorks/lib/petsc/arch-linux2-c-debug/bin/mpirun -np 4 /dfnWorks/bin/pflotran -pflotranin dfn_explicit.in
    2025-03-06 17:15:04,924 INFO --> Processing file: dfn_explicit-000.vtk
    2025-03-06 17:15:04,933 INFO --> Processing file: dfn_explicit-001.vtk
    2025-03-06 17:15:04,941 INFO --> Parsing PFLOTRAN output complete
    2025-03-06 17:15:05,112 INFO ====================================================
    2025-03-06 17:15:05,113 INFO dfnFlow Complete
    2025-03-06 17:15:05,113 INFO Time Required for dfnFlow 1.0802464485168457 seconds 


.. figure:: figures/tut1_liq_pressure_002.png
   :width: 500px 
   :alt: fracture pressure
   :align: center


   *Figure shows the fracture surfaces colored by liquid pressure*



Particles are inserted uniformly along the inlet fracture on the left side of the image. Particles exit the domain through the two horizontal fractures on the right side of the image. Due to the stochastic nature of the particle tracking algorithm, your pathlines might not be exactly the same as in this image. Trajectories are colored by the current velocity magnitude of the particle’s velocity. Trajectories can be visualized by loading the files part_*.inp, in the folder 4_user_rectangles/traj/trajectories/ We have used the extract surface and tube filters in paraview for visual clarity.

View `output.log` to verify the dfnTrans module was successful and result files were written. Note directory and file names may change due to code development. Check the log to confirm names used.

.. code-block:: bash

    2025-03-06 17:15:05,119 INFO --> dfnTrans is running from: PTDFN_control.dat
    2025-03-06 17:15:05,120 INFO --> Checking DFNTrans Parameters
    2025-03-06 17:15:05,122 INFO --> All files required for dfnTrans have been found in current directory
    2025-03-06 17:15:05,122 INFO --> Checking Initial Conditions Complete
    2025-03-06 17:15:05,630 INFO ================================================================================
    2025-03-06 17:15:05,630 INFO dfnTrans Complete


.. figure:: figures/tut1_parts_fracture.png
   :width: 500px 
   :alt: fracture intersections
   :align: center


   *Figure shows the fracture surfaces with  particle lines colored by the fracture ID.*






Conclusion
------------------------------------------

You have successfully run a basic simulation using the `driver.py` script in dfnWorks! As you become more familiar with the setup, you can start experimenting with different fracture characteristics, domain sizes, and simulation parameters to further explore subsurface flow dynamics in fractured media.


For Additional Resources you can browse the online docs including examples, module descriptions, and the pydfnworks code descriptions.
The Publications are a good source of applications and discussions. Consider joining community forums and user groups for support and to share experiences with dfnWorks users.

Feel free to reach out if you have any questions or need further assistance with your simulation!


