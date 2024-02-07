.. _dfnWorks-python-chapter-dfnGen:

pydfnworks: dfnGen
========================================

DFN Class functions used in network generation and meshing

dfnGen
-------

Adding Fracture Families
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.generation.input_checking
    :members: add_fracture_family
    :noindex:

Example:

.. code-block:: python

    DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        alpha=1.8,
                        min_radius=1.0,
                        max_radius=5.0,
                        kappa=1.0,
                        theta=0.0,
                        phi=0.0,
                        aspect=2,
                        beta_distribution=1,
                        beta=45.0,
                        p32=1.1,
                        hy_variable='aperture',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 10**-5,
                            "beta": 0.5
                        })


Adding User Fractures
^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pydfnworks.dfnGen.generation.input_checking.user_defined_fracture_functions
    :members: add_user_fract
    :noindex:

Example:

.. code-block:: python

    DFN.add_user_fract(shape='ell',
                   radii=.4,
                   aspect_ratio=1,
                   translation=[0.2, 0, 0.2],
                   normal_vector=[0, 0, 1],
                   number_of_vertices=8,
                   aperture=1.0e-5)

Adding User Fractures From a File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                   
.. automodule:: pydfnworks.dfnGen.generation.input_checking.user_defined_fracture_functions
    :members: add_user_fract_from_file
    :noindex:

Example:

.. code-block:: python

    DFN.add_user_fract_from_file(shape="poly",
                   filename = f'{src_path}/polygons.dat',
                   permeability = 1e-12)


Print Parameter Information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Note: Some of these functions are automatically called when processing the input.

.. automodule:: pydfnworks.dfnGen.generation.input_checking.user_defined_fracture_functions
    :members: print_user_fracture_information

.. automodule:: pydfnworks.dfnGen.generation.input_checking
    :members: print_domain_parameters, print_family_information

Processing Generator Input
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pydfnworks.dfnGen.generation.input_checking
    :members: check_input
    :noindex:
     
Running the Generator
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.generation.generator
    :members: dfn_gen, make_working_directory, create_network, grab_polygon_data

Analysis of Generated DFN 
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.generation.output_report.gen_output
    :members: output_report

Additional Information on the Modification of Hydraulic Properties of the DFN 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Hydraulic properties can be assigned to fractures based on four different models. One can assign hydraulic aperture :math:`b`, permeability, :math:`k`, or transmissivity :math:`T`. Below we present the functions for hydraulic aperture, but the equations for other values are the same.

The first is a perfectly correlated model where the hydraulic property is a function of the fracture radius

.. math:: 
    b = \alpha r^\beta

The keyword for this model is correlated.

The second is a semi-correlated correlated model where the hydraulic property is a function of the fracture radius

.. math:: 
    \log_{10}(b) = \log_{10}(\alpha r^\beta) + \sigma \mathcal{N}(0,1)

where a stochastic term is included into the correlated model 
to account for uncertainty and variability between fractures of the same size. The strength of the stochastic term is determined by the variance of a log-normal distribution :math:`\sigma` and the stochastic term is an independent identically distributed random variable sampled from a normal distribution with mean 0 and variance 1, :math:`\mathcal{N}(0,1)`. This model results in a log-normal distribution of fracture transmissivities around a positively cor- related power law mean. We refer to this model as semicorrelated.

The keyword for this model is semi-correlated.

The third model assumes that there is no correlation between the fracture size and transmissivity and all values are independent identically distributed random variables from a log-normal distribution with speci- fied mean :math:`\mu` and variance :math:`\sigma`,

.. math:: 
    \log_{10}(b) = \mu + \sigma \mathcal{N}(0,1)

The keyword for this model is log-normal.

The fourth model represents an assumption that in addition to no relationship between size and hydraulic properties, there is no variation between fractures

.. math:: 
    b = \mu

The keyword for this model is constant.

Notes:

See Hyman et al. 2016 “Fracture size and transmissivity correlations: Implications for transport simulations in sparse three-dimensional discrete fracture networks following a truncated power law distribution of fracture size” Water Resources Research for more details

Changes in hydraulic properties are assigned when defining a fracture family or user defined fracture. User defined fractures currently only support constant hydraulic properties.


Modification of hydraulic properties of the DFN based on background stress field
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pydfnworks.dfnGen.generation.stress
    :members: stress_based_apertures 

Meshing - LaGriT
-----------------

Primary DFN meshing driver
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.meshing.mesh_dfn.mesh_dfn
    :members: mesh_network


Meshing helper methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.meshing.mesh_dfn.mesh_dfn_helper
    :members: inp2gmv, inp2vtk_python, create_mesh_links, run_lagrit_script

.. automodule:: pydfnworks.dfnGen.meshing.add_attribute_to_mesh
    :members: add_variable_to_mesh



UDFM 
--------

Creating an upscaled mesh of the DFN (UDFM)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.meshing.udfm.map2continuum
    :members: map_to_continuum

.. automodule:: pydfnworks.dfnGen.meshing.udfm.upscale
    :members: upscale

.. automodule:: pydfnworks.dfnGen.meshing.udfm.false_connections
    :members: check_false_connections

Map-DFN upscaling  
--------------------------
.. automodule:: pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_ecpm
    :members: mapdfn_ecpm

DFM 
--------

Creating a conforming DFM mesh DFN
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.meshing.dfm.mesh_dfm
    :members:  mesh_dfm



