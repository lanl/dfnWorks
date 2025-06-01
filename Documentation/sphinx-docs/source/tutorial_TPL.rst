
dfnWorks Tutorial for TPL (Truncated Power-Law) 
================================================


.. figure:: figures/tpl_3images.png
   :scale: 100 %
   :alt: alternate text
   :align: center


The TPL (Truncated Power-Law) is a type of distribution ('tpl', 'log_normal', 'exp', or 'constant') that defines the sample distribution for the fracture radius.

This example uses add_fracture_family() to control parameters to create a set of fractures within a domain. Fracture families can also be created using add_user_fract() to define specific fractures or add_user_fract_from_file() to read fractures from a file. 

This example consists of one family of fractures whose sizes have a truncated power law distribution with a minimum radius of 1 meter and a maximum size of 10 meters.  

For a complete list of parameters and functions see [pydfnworks: dfnGen](https://lanl.github.io/dfnWorks/pydfnGen.html)



The following items are covered in this Tutorial:

.. contents::
   :depth: 2
   :local:



Tutorial Prerequisites
--------------------------

- For this Tutorial you do not need to run dfnWorks. You can read through the steps for a basic understanding of the work flow. Images and output examples are included with this tutorial.
- This Tutorial assumes you are familiar with the basics of running dfnWorks.  These basics are covered in the Tutorial  [Introduction and Beginner Tutorial](https://lanl.github.io/dfnWorks/tutorial_intro.html) 
For install and setup instuctions, refer to the section at :ref:`pydfnWorks install <pydfnworks-setup>`.
- TeX Live is needed to write the PDF report summary. Local servers use ```module load texlive```
- Paraview_ is an open-source visualization software and is used to create the mesh and simulation images in this document.  Instructions for downloading and installing Paraview_ can be found at http://www.paraview.org/download/ 



dfnWorks TPL Overview
--------------------------

The Truncated Power-Law (TPL) option for stochastic generation of fractures allows spatially variable mesh resolution while enusring Delaunay triangulation for accuracy and stable solutions. Parameters are set by family groupings and include controls for distribution, orientation, and resolution. 

Understanding these parameters will help you effectively describe the geometry and orientation of fractures within your discrete fracture network in dfnWorks. By adjusting these settings, you can model complex geological configurations and accurately represent the flow behavior in fractured media.

.. figure:: figures/tpl_mesh_material.png
   :scale: 50 %
   :alt: alternate text
   :align: center


This tutorial's main focus will be on **dfnGen** and how to use TPL parameters to generate a network. Evaluations of a network include reports, graphs, and visual inspection. 

Simulations using dfnFlow and dfnTrans are run on the network and are viewed to further evaluate the network and results.


Python add_fracture_family
---------------------------

Open the script python `driver.py`. You can open with any text editor or use the unix command ``cat driver.py`` which will display the content to the screen.  Note the first line of the file imports the `pydfnworks` package. This allows the user to run dfnWorks from the command line and call dfnWorks within other python scripts.

This example creates a single family network. The routine **add_fracture_family()** is assigns all the parameters for a fracture network filling the domain.

.. code-block:: python

    DFN.add_fracture_family(
        shape="ell", distribution="tpl", alpha=1.8, p32=1,
        min_radius=1.0, max_radius=10.0,
        kappa=1.0, theta=0.0, phi=0.0,
        hy_variable='aperture', hy_function='correlated', number_of_points=8,
        hy_params={
            "alpha": 10**-5,
            "beta": 0.5
        })

These parameters help define the characteristics and distribution of fractures within your discrete fracture network.

distribution :
        Definition : This parameter defines the statistical distribution from which the fracture radii will be sampled. Options include:
            'tpl': Truncated Power Law distribution.
            'log_normal': Log-normal distribution.
            'exp': Exponential distribution.
            'constant': A constant value for the fracture radius.
        Usage : Selecting the appropriate distribution allows you to model the variability of fracture sizes in your geological setting. For example, if fractures tend to have a size that follows a log-normal distribution in your study area, you would set this parameter accordingly.


alpha :
        Definition : A parameter used when the distribution is set to tpl. It indicates the power-law exponent of the truncated power-law distribution.
        Default : None
        Usage : Set this parameter to define the specific scaling behavior of the fracture sizes in a power-law context. This can help model situations where smaller fractures are more common than larger ones, which is typical in many geological settings.


p32 :
        Definition : A parameter representing the fracture intensity for the family. It is applicable when using stopCondition = 1, which typically refers to a specified density of fractures.
        Default : None
        Usage : Set this parameter to define how densely the fractures are distributed in space. The value of p32 often relates to the number of fractures per unit volume or area.


shape and radius : 
       Definition : The shape parameter defines the fracture family to 'rect' rectangle or 'ell' ellipse. Their sizes are set with 'min_radius' and 'max_radius'
        Default : None


These parameters enable users to define density and orientations for fractures within a discrete fracture network. This family sets kappa, theta, and phi. Other scenarios may use parameters such as trend, plunge, dip, and strike. 

    kappa :
        Definition : The concentration parameter for the von Mises-Fisher distribution, which is used for modeling directionality of fractures. Higher values indicate a tighter clustering of the fracture orientations around the mean direction.
        Usage : Use this parameter when fractures are expected to have a strongly defined orientation. Adjust kappa to reflect the degree of clustering present in your geological scenario.


   theta :
        Definition : This parameter defines the angle used to specify the orientation of fractures if orientationOption is set to 0 (the default). It typically represents the angle of a fracture in the vertical plane in spherical coordinates.
        Default : None
        Usage : Set this parameter to define the tilt or dip of the fractures. For instance, a value of 0 would represent a horizontal fracture, while a value of π/2 (90 degrees) would indicate a vertical fracture.

    phi :
        Definition : Similar to theta, phi is used in conjunction with orientationOption 0 to specify the azimuthal angle of the fracture in spherical coordinates. This angle defines the rotation around the vertical axis.
        Default : None
        Usage : Specify this parameter to set the direction of the fracture’s orientation in the horizontal plane. For example, a value of 0 for phi would mean the fracture is pointing along the positive x-axis, while a value of π/2 would indicate it’s pointing along the positive y-axis.


These hydraulic parameters—hy_variable, hy_function, and hy_params—are essential for modeling how fluid flows through fractured media. By carefully selecting and defining each parameter, you can create a more accurate and realistic representation of subsurface flow behavior influenced by the fractures present in your geological model.

Here’s a detailed explanation of the hydraulic parameters used in the add_fracture_family function in dfnWorks, which help define the hydraulic properties of fractures within a discrete fracture network.
Hydraulic Parameters for a Fracture Family

    hy_variable :
        Definition : This parameter specifies the hydraulic variable to which values will be assigned for the fractures within the family. The options include:
            'aperture': The opening width of the fractures, which is critical for determining flow rates.
            'permeability': A measure of how easily fluids can pass through the fractures.
            'transmissivity': Represents the ability of the fractured medium to transmit fluid, influenced by both aperture and permeability.
        Usage : Choose the appropriate hydraulic variable based on the specific properties you want to model for the fractures. For example, if you are interested in how the fracture opening impacts fluid flow, you would select 'aperture'.

    hy_function :
        Definition : This parameter describes the relationship between the chosen hydraulic variable and the radius of the fractures. The options include:
            'correlated': Indicates a direct relationship where the hydraulic variable changes in correlation with changes in fracture radius.
            'semi-correlated': Suggests a relationship where the hydraulic variable is influenced by the fracture radius but also incorporates some variability or randomness.
            'constant': Means that the hydraulic variable does not change with fracture radius and remains fixed at a specific value.
            'log-normal': Implies that the hydraulic variable follows a log-normal distribution, with values spread around a mean influenced by the fracture radius.
        Usage : Select the appropriate function depending on the relationship you wish to model. For example, if you expect that larger fractures will have higher permeabilities, you might choose 'correlated'.

    hy_params :
        Definition : This parameter provides the necessary values that define the hydraulic function chosen. The structure of hy_params will vary depending on the hydraulic function selected:
            If hy_function is 'correlated' :
                Expected syntax: {"alpha": value, "beta": value}
                Here, alpha defines the scaling relationship between the hydraulic variable and the fracture radius, while beta can adjust the slope of the correlation.
            If hy_function is 'semi-correlated' :
                Expected syntax: {"alpha": value, "beta": value, "sigma": value}
                In this case, sigma adds variability to the relationship, allowing for some randomness in hydraulic properties.
            If hy_function is 'constant' :
                Expected syntax: {"mu": value}

 

For more details on fracture famililies and a complete list of parameters and functions see [pydfnworks: dfnGen](https://lanl.github.io/dfnWorks/pydfnGen.html)




Network Evaluations
--------------------------

The most immediate feedback for the network are text reports written to the log file. Additional graphs and statistics can be generated into a PDF report. Usually visual inspection will provide a good feel for the network that is generated.

The following commands will check for errors in the parameters and setup, create the fracture network, writee at PDF report, then triangulate and intersect fractures into a Delaunay mesh.


.. code-block:: python

    DFN.check_input()
    DFN.create_network()
    DFN.output_report()
    DFN.mesh_network(min_dist=1, max_dist=5, max_resolution_factor=10)


Log Report
~~~~~~~~~~~~~~~~~~~

See output.log

Observe screen output as dfnWorks is running, error checks and setup results are displayed. This is the first place to check that your network is as expected. The screen output is also written to root_name.log. For this example the output will look like the following.

While dfnWorks is running, you will see extensive reporting to the screen. This will alert you to errors or missing files. When finished, a report is written to to file `output.log`. This is the first place to check if there are any issues. Look for the first occurrence of Errors as later Errors are likely caused by the first. Warnings may exist and can usually be ignored.

A list of dfnWorks files and their descriptions are at :ref:`dfnWorks Files <output-chapter>`.

The log will write a summary that includes default and user defined parameters. Check this is what was expectted for your setup. For this example: 


.. code-block:: bash

    2025-05-22 13:26:52,217 INFO Checking Input File Complete
    2025-05-22 13:26:53,167 INFO [2025-05-22 13:26:52] INFO: Starting DFNGen
    [2025-05-22 13:26:52] INFO: Expecting Theta and phi for orientations
    [2025-05-22 13:26:52] INFO: h: 0.100000
    [2025-05-22 13:26:52] INFO: Shape Families:
    [2025-05-22 13:26:52] INFO: Ellipse Family 1:
    [2025-05-22 13:26:52] INFO: Number of Vertices: 8
    [2025-05-22 13:26:52] INFO: Aspect Ratio: 1.000000
    [2025-05-22 13:26:52] INFO: P32 (Fracture Intensity) Target: 1.000000
    [2025-05-22 13:26:52] INFO: Beta Distribution (Rotation Around Normal Vector): [0, 2PI)
    [2025-05-22 13:26:52] INFO: Theta: 0.000000 rad, 0.000000 deg
    [2025-05-22 13:26:52] INFO: Phi: 0.000000 rad, 0.000000 deg
    [2025-05-22 13:26:52] INFO: Kappa: 1.000000
    [2025-05-22 13:26:52] INFO: Layer: Entire domain
    [2025-05-22 13:26:52] INFO: Region: Entire domain
    [2025-05-22 13:26:52] INFO: Distribution: Truncated Power-Law
    [2025-05-22 13:26:52] INFO: Alpha: 1.800000
    [2025-05-22 13:26:52] INFO: Minimum Radius: 1.000000m
    [2025-05-22 13:26:52] INFO: Maximum Radius: 10.000000m
    [2025-05-22 13:26:52] INFO: Family Insertion Probability: 1.000000
    [2025-05-22 13:26:52] INFO: Estimating number of fractures needed...
    [2025-05-22 13:26:52] INFO: Estimated 167 fractures for Ellipse family 1
    [2025-05-22 13:26:52] INFO: P32 For Family 1 Completed


When fractures are generated, they are checked to ensure intersections and that parameters are satisfied. Fractures are rejected if they are isolated, have edges too short or too close, or outside boundary. When the network is created, summary information helps to describe the result. For this example the log output will look similar to this.

.. code-block:: bash

    [2025-05-22 13:26:52] INFO: ========================================================
    [2025-05-22 13:26:52] INFO:             Network Generation Complete
    [2025-05-22 13:26:52] INFO: ========================================================
    [2025-05-22 13:26:52] INFO: Version of DFNGen: 2.2
    [2025-05-22 13:26:52] INFO: Time Stamp: Thu May 22 13:26:52 2025
    [2025-05-22 13:26:52] INFO: Final p32 values per family:
    [2025-05-22 13:26:52] INFO: Family 1 target P32 = 1.000000, Final P32 = 1.000912
    [2025-05-22 13:26:52] INFO: ________________________________________________________


Statistical Report
~~~~~~~~~~~~~~~~~~~~



Created by DFN.output_report()
see output_output_report.pdf  and directory dfnGen_output_report

output_report(self, verbose=True, output_dir='dfnGen_output_report')[source]

    Creates a PDF output report for the network created by DFNGen. Plots of the fracture lengths, locations, orientations are produced for each family. Files are written into “output_dir/family_{id}/”. Information about the whole network are also created and written into “output_dir/network/”

    Parameters:

            self (object) – DFN Class object

            verbose (bool) – Toggle for the amount of information printed to screen. If true, progress information printed to screen

            output_dir (string) – Name of directory where all plots are saved

    Return type:

        None

    Notes

    Final output report is named “jobname”_output_report.pdf User defined fractures (ellipses, rectangles, and polygons) are not supported at this time.


.. code-block:: bash

    2025-05-22 13:26:53,194 INFO Creating Report of DFN generation
    2025-05-22 13:26:53,194 INFO --> Gathering Network Information
    2025-05-22 13:26:53,196 INFO --> There is 1 Fracture Family
    2025-05-22 13:26:53,200 INFO --> There are 119 fractures in the domain
    2025-05-22 13:26:53,201 INFO --> There are 46 fractures in the final network
    2025-05-22 13:26:53,209 INFO --> Plotting Information
    2025-05-22 13:26:56,949 INFO --> Plotting Fracture Radii Distributions
    2025-05-22 13:26:58,940 INFO --> Plotting Rose Diagrams and Stereonets
    2025-05-22 13:26:58,985 INFO --> Plotting Densities
    2025-05-22 13:27:02,448 INFO --> Combing Images and Making PDF
    2025-05-22 13:27:02,449 INFO --> Making Table of Contents
    2025-05-22 13:27:06,588 INFO --> Output report is written into output_output_report.pdf


.. figure:: figures/tpl_report_page_2.png
   :scale: 50 %
   :alt: alternate text
   :align: center


   *dfnWorks routine DFN.output_report() will generate a PDF summary of the network.*


Visual Inspection
~~~~~~~~~~~~~~~~~~~

Created by DFN.mesh_network()
Meshed network to be used by simulations.
See full_mesh.inp (or reduced_mesh.inp)

If the network has been successfully triangulated and merged, the mesh will be written to an AVS format mesh file. The output log will look like:


.. code-block:: bash

    2025-05-22 13:27:06,589 INFO Meshing DFN using LaGriT : Starting
    2025-05-22 13:27:06,608 INFO --> Variable Mesh Resolution Selected
    2025-05-22 13:27:06,608 INFO *** Minimum distance [m] from intersection with constant resolution h/2 : 0.1
    2025-05-22 13:27:06,608 INFO *** Maximum distance [m] from intersection variable resolution : 0.5
    2025-05-22 13:27:06,608 INFO *** Upper bound on resolution [m] : 1.00
    2025-05-22 13:27:16,061 INFO --> The primary mesh in full_mesh.inp has 36138 nodes and 74279 triangular elements
    2025-05-22 13:27:16,794 INFO Meshing DFN using LaGriT : Complete



View the mesh attributes to check parameters. 
Materials are the fractures generated 1 through n.
Property evol_one are the element volumes
Property dfield is the linear distance from intersections and is used for element size changes.



.. raw:: html

    <div style="display: flex; justify-content: space-between;">

        <div style="flex: 1;">
            <img src="figures/tpl_mesh_material.png" alt="Figure Materials" style="width: 100%;">
        </div>

        <div style="flex: 1;">
            <img src="figures/tpl_mesh_evol_one.png" alt="Figure Volume" style="width: 100%;">
        </div>

        <div style="flex: 1;">
            <img src="figures/tpl_mesh_dfield.png" alt="Figure dfield" style="width: 100%;">
        </div>

    </div>


You can adjust color maps and opacity for views that help show the meshed network.
See examples in file `tpl_paraview_examples.rst <tpl_paraview_examples.rst>`_ 


Run Flow Model
---------------

The pydfnworks commands `dfn_flow()` and `dfn_trans()` are used to run the simulations. These can provide insights into the behavior of fluids within the fractured network.

View the dfnFlow_file 'file.in'. This is a PFLOTRAN input file.  EDIT TEXT High pressure (red) Dirichlet boundary conditions are applied on the edge of the single fracture along the boundary x = -0.5, and low pressure (blue) boundary conditions are applied on the edges of the two fractures at the boundary x = 0.5. 

The solver type is set to PFLOTRAN

.. code-block:: bash

    2025-05-22 13:27:17,476 INFO --> Running PFLOTRAN
    2025-05-22 13:27:17,481 INFO --> Running: /home/jhyman/src/petsc/arch-linux-c-opt/bin/mpirun -np 12 /home/jhyman/src/pflotran/src/pflotran/pflotran -pflotranin dfn_explicit.in
    2025-05-22 13:27:22,210 INFO --> Processing file: dfn_explicit-000.vtk
    2025-05-22 13:27:22,302 INFO --> Processing file: dfn_explicit-001.vtk
    2025-05-22 13:27:22,377 INFO --> Parsing PFLOTRAN output complete



For viewing results see the vtk files written in output/parsed_vtk

Read dfn_explicit-000.vtk see permeability and Liquid Pressure at time 0
Read dfn_explicit-001.vtk for Liquid Pressure at time 1


.. raw:: html

    <div style="display: flex; justify-content: space-between;">

        <div style="flex: 1;">
            <img src="figures/tpl_flow_permeability.png" alt="permeability" style="width: 100%;">
        </div>

        <div style="flex: 1;">
            <img src="figures/tpl_flow_liq_press_vtk0.png" alt="Figure Volume" style="width: 100%;">
        </div>

        <div style="flex: 1;">
            <img src="figures/tpl_flow_liq_press_vtk1.png" alt="Figure dfield" style="width: 100%;">
        </div>

    </div>


Run Transport Model
--------------------

View the dfnTrans_file 'file.dat.  EDIT TEXT Particles are inserted SOMEWHERE 
to exit SOMEWHERE else

.. code-block:: bash

    2025-05-22 13:27:23,021 INFO --> dfnTrans is running from: PTDFN_control.dat
    2025-05-22 13:28:32,671 INFO --> Combining Particle avs files into a single file
    2025-05-22 13:28:32,710 INFO --> Running: /n/modules/Ubuntu-20.04-x86_64/lagrit-gcc-13.2.0/v3.3.3/exodus/lagrit < combine_avs.lgi -log combine_avs.lgi.log -out combine_avs.lgi.out
    2025-05-22 13:29:44,627 INFO --> LaGriT script combine_avs.lgi ran successfully
    2025-05-22 13:29:44,627 INFO --> Particles are in all_particle.inp


Generate particle tracks with call....

NOTE: There are a thousand particle tracks, these can be merged into a single file "all_particles.inp" with the command 

.. raw:: html

    <div style="display: flex; justify-content: space-between;">

        <div style="flex: 1;">
            <img src="figures/tpl_part_1000.png" alt="particles" style="width: 100%;">
        </div>

        <div style="flex: 1;">
            <img src="figures/tpl_part_aperature_mesh.png" alt="aperature" style="width: 100%;">
        </div>

        <div style="flex: 1;">
            <img src="figures/tpl_part_time_threshold_.005.png" alt="time threshold .005" style="width: 100%;">
        </div>

    </div>


Add a Second family
---------------------

Once this network is working well, a more complicated version can be created by adding more families with different paramters from the first.


.. figure:: figures/tpl_f2_families.png
   :scale: 100 %
   :alt: alternate text
   :align: center



Conclusion EDIT this
------------------------------------------

You have successfully run dfnWorks to create a simple fracture network and run  basic simulations using the `driver.py` script in dfnWorks! As you become more familiar with the setup, you can start experimenting with different fracture characteristics, domain sizes, and simulation parameters to further explore subsurface flow dynamics in fractured media.



Additional Resources EDIT these
------------------------------------------

There are more demo runs in the `dfnWorks/examples` directory.  The first two examples are simpler than the last three so it is recommended that the user proceed in the order presented here. 

• 4_user_rects (4_user_defined_rectangles): The example used in this tutorial. 
• 4_user_ell_uniform (4_user_defined_ellipses): User defined elliptical fractures.
• exp (exponential_dist): Use parameters for two families of fractures with an exponential distribution of fracture size.
• lognormal (lognormal_dist): Use parameters for two families of fractures with a lognormal distribution of fracture size.
• TPL (truncated_power_law_dist): Use parameters for two families of fractures with a truncated power-law distribution of fracture size.

See a description of these 5 examples at :ref:`pydfnWorks examples <examples>`.

All examples are available from github at `DFNWorks Examples <https://github.com/lanl/dfnWorks/tree/master/examples>`_

For a short description of all examples see `Examples README file <https://github.com/lanl/dfnWorks/tree/master/examples/README.md>`_

For Additional Resources you can browse the online docs including examples, module descriptions, and the pydfnworks code descriptions.
The Publications are a good source of applications and discussions. Consider joining community forums and user groups for support and to share experiences with dfnWorks users.

Feel free to reach out if you have any questions or need further assistance with your simulation!


