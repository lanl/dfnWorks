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
    :members: dfn_gen, make_working_directory, create_network

Processing Generator Output
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After the generator runs, ``dfn_gen`` reads its output into the DFN object (fracture centers, radii, normals, polygons, families, and hydraulic properties). These functions are called automatically but can also be used to reload a network.

.. automodule:: pydfnworks.dfnGen.generation.process_generator_output
    :members: parse_params_file, gather_dfn_gen_output, assign_hydraulic_properties, grab_polygon_data

Analysis of Generated DFN 
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.generation.output_report.gen_output
    :members: output_report

The report includes, for each family, stereonets of the fracture normals and equal-area rose diagrams of strike and dip.

Fracture Orientations
^^^^^^^^^^^^^^^^^^^^^^^^^

The strike, dip, dip direction, trend, and plunge of every fracture normal are computed from ``DFN.normal_vectors`` when the network is loaded and stored as ``DFN.strike``, ``DFN.dip``, ``DFN.dip_direction``, ``DFN.trend``, and ``DFN.plunge`` (in degrees).

.. automodule:: pydfnworks.dfnGen.generation.orientations
    :members: get_fracture_orientations

Fracture Intensity (P21)
^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pydfnworks.dfnGen.generation.process_generator_output
    :members: compute_fracture_p21
    :noindex:

Example:

.. code-block:: python

    DFN.compute_fracture_p21()
    print(DFN.p21_table)

Additional Information on the Modification of Hydraulic Properties of the DFN 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Hydraulic properties can be assigned to fractures based on five different models. One can assign hydraulic aperture :math:`b`, permeability, :math:`k`, or transmissivity :math:`T`. Below we present the functions for hydraulic aperture, but the equations for other values are the same.

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

The fifth model draws values that are independent of fracture size from an exponential distribution with rate parameter :math:`\lambda`,

.. math::
    f(b) = \lambda e^{-\lambda b}, \quad b \geq 0

so the mean value is :math:`1/\lambda`. The keyword for this model is exponential and the parameter dictionary is ``{"lam": value}``.

Notes:

See Hyman et al. 2016 “Fracture size and transmissivity correlations: Implications for transport simulations in sparse three-dimensional discrete fracture networks following a truncated power law distribution of fracture size” Water Resources Research for more details

Changes in hydraulic properties are assigned when defining a fracture family or user defined fracture. User defined fractures currently only support constant hydraulic properties.

Hydraulic properties can also be regenerated or overwritten after the network is created. ``generate_hydraulic_values`` draws new values for the whole network or for one family, ``set_fracture_hydraulic_values`` sets values on a list of fractures, and the ``dump_*`` functions write the current values to file.

.. automodule:: pydfnworks.dfnGen.generation.hydraulic.dfn_methods
    :members: generate_hydraulic_values, set_fracture_hydraulic_values

.. automodule:: pydfnworks.dfnGen.generation.hydraulic.io
    :members: dump_hydraulic_values, dump_aperture, dump_perm, dump_transmissivity, dump_fracture_info

Example:

.. code-block:: python

    # draw new log-normal apertures for family 1, then write all values to file
    DFN.generate_hydraulic_values(variable="aperture",
                                  relationship="log-normal",
                                  params={"mu": 1e-4, "sigma": 0.5},
                                  family_id=1)
    DFN.dump_hydraulic_values()


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
    :members: inp2gmv, inp2vtu, create_mesh_links, run_lagrit_script

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

``upscale`` writes an anisotropic permeability field. ``mesh_permeability.h5`` contains ``PermeabilityX``, ``PermeabilityY``, and ``PermeabilityZ`` datasets (for PFLOTRAN, use ``PERMEABILITY ANISOTROPIC`` in the material property card), and ``perm_fehm.dat`` contains directional :math:`k_x, k_y, k_z` values for FEHM.

.. automodule:: pydfnworks.dfnGen.meshing.udfm.false_connections
    :members: check_false_connections

Map-DFN upscaling  
--------------------------
.. automodule:: pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_ecpm
    :members: mapdfn_ecpm

``mapdfn_ecpm`` calls the following steps, which can also be run individually.

.. automodule:: pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_tag_cells
    :members: mapdfn_tag_cells

.. automodule:: pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_upscale
    :members: mapdfn_upscale

.. automodule:: pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_effective_perm
    :members: mapdfn_effective_perm

DFM 
--------

Creating a conforming DFM mesh DFN
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.meshing.dfm.mesh_dfm
    :members:  mesh_dfm



