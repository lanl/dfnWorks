
Tutorials
==========================================

dfnWorks is a parallelized computational suite to generate three-dimensional discrete fracture networks (DFN) and simulate flow and transport. Developed at Los Alamos National Laboratory, it has been used to study flow and transport in fractured media at scales ranging from millimeters to kilometers. The networks are created and meshed using dfnGen, which combines FRAM (the feature rejection algorithm for meshing) methodology to stochastically generate three-dimensional DFNs with the LaGriT meshing toolbox to create a high-quality computational mesh representation. The representation produces a conforming Delaunay triangulation suitable for high-performance computing finite volume solvers in an intrinsically parallel fashion. Flow through the network is simulated with dfnFlow, which utilizes the massively parallel subsurface flow and reactive transport finite volume code PFLOTRAN. A Lagrangian approach to simulating transport through the DFN is adopted within dfnTrans to determine pathlines and solute transport through the DFN. Applications of the dfnWorks suite include nuclear waste repository science, hydraulic fracturing and CO2 sequestration.

To run a workflow using the dfnWorks suite, the pydfnworks package is highly recommended. pydfnworks calls various tools in the dfnWorks suite with the aim to provide a seamless workflow for scientific applications of dfnWorks.

The pydfnworks package allows the user to run dfnWorks from the command line and call dfnWorks within other python scripts. Because pydfnworks is a package, users can call individual methods from the package.

These tutorials and examples are useful to demonstrate dfnWorks capabilitties, as well as tests to ensure consistency and ensure quality. New users should carry out the Introduction Tutorial which covers setup, input files, and output files. Additional examples can be run in dfnWorks/examples. 



.. toctree::
   :maxdepth: 1

   tutorial_intro
   examples


Tutorial Setup
------------------------------

These options are available for running Tutorials and examples, see details at :ref:`Setup <pydfnworks-setup>` 

* Use Docker dfnWorks to run and view files. The Docker dfnWorks contains all the tools and examples needed. Files created within Docker will not persist past the exit. Except for Docker, no installation is needed.  

* Use Docker and mount a local clone of dfnWorks. Files will be read and written in your local version of dfnWorks. Files will persist past the exit. 

* Clone and build dfnWorks on your machine. This will give full access and control of all the tools and files for your project. Installation will include Python, dfnWorks, LaGriT, PFLOTRAN, and FEHM. 

* Linux dfnWorks module. Some servers use the module system and may have dfnWorks available. You will still need to clone dfnWorks for the files, but you can skip the build process.


Optional but recommended is a visualization tool. VisIt and ParaView can read the output files. Paraview is open-source. Instructions for downloading and installing Paraview_ can be found at
http://www.paraview.org/download/

.. _Paraview: http://www.paraview.org



For instructions on how to setup and run dfnWorks, follow the link below:

.. toctree::
   :maxdepth: 1

   setup

For a description of the dfnWorks python package, follow the link below:

.. toctree::
   :maxdepth: 1

   pydfnworks
~
