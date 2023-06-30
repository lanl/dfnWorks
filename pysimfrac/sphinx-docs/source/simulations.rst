.. _simfrac-simulatons:

Integration with Flow Simulators
========================================

In addition to the generation methods and analysis toolkits, we have developed seamless handoffs with several open-source flow and transport simulators ranging from multi-phase lattice Boltzman methods to three-dimensional discrete fracture network simulators. 

Single-Phase : MP-LBM 
^^^^^^^^^^^^^^^^^^^^^^^^^^

MPLBM (Santos et al. 2022) is a specialized lattice-Boltzmann library that significantly simplifies the process of running single-phase flow through complex  porous media. MPLBM uses the high-performance, highly parallel library Palabos as the solver backend, making it easily deployable in a variety of systems, from laptops to supercomputer clusters. The SmartFracs library aims to facilitate seamless integration between complex fracture geometry generation and single-phase flow simulation to enable the study of how realist fracture heterogeneities affect the permeability of a fracture domain. Once the MPLBM library is installed, a simulation can be run and post-processed as follows:


Example
--------------------
An example of the resultant flow field using the integration with MPLBM is shown in the example Figure, The completion of a full simulation utilizing this feature required roughly 15 seconds of computing time on a standard laptop. We anticipate that the incorporation of this capability will streamline the research process, making various aspects of investigation more straightforward and productive for both researchers and practitioners. Understanding the relationship between geometry and permeability may offer innovative perspectives, potentially leading to the refinement of correlations that can be applied at the field scale. Furthermore, it could shed light on the effects of phenomena such as compaction, cementation, and dissolution on this critical parameter.

.. code-block:: python

        lbm = write_MPLBM(
                  frac_obj = myfrac, 
                  buffer_layers = 2,
                  cpus = 4,
                  num_hrs = 1,
                  )
		

Example Figure:

Multiphase-Phase : MF-LBM 
^^^^^^^^^^^^^^^^^^^^^^^^^^

`MF-LBM <https://github.com/lanl/MF-LBM>`_ is an open source high-performance lattice Boltzmann code developed at Los Alamos National Laboratory. It  combines the continuum-surface-force based color-gradient multiphase model with the geometrical wetting model.  The code is extensively parallelized and optimized for CPUs and GPUs and is ideal for running large (billion of nodes) multiphase simulations. 
We have integrated MF-LBM within pysimfrac allowing users to not only specify fracture properties as part of the core pySimfrac but also to specify multiphase flow parameters such as viscosity ratios, capillary number, contact angle, and interfacial tension. This allows for users to seamlessly conduct simulations on a variety of fracture properties with varied simulation parameters.


Example
------------------------------
The same fracture properties in the MP-LBM integration were used to generate a fracture for simulation with MF-LBM. The initial condition in the fracture began with 100\% occupancy by the blue phase, which was also the wetting phase. The contact angle was set to 50 degree. Fluid viscosity ratio was set as 1.0, while the capillary number was set at 10\ :sup:`-4`. The red phase (non-wetting phase) was introduced from the bottom. With the snapshots shown in example Figure, we see an increase in the occupancy of the red phase as injection proceeds. We also estimated the corresponding saturation of both phases for each time step. At the last time step, we notice the majority of the fracture is occupied by the red phase with as saturation of 87.6\%. 

Example
------------------------------

.. figure:: figures/Fig_ex_MFLBM_handshake.png
   :alt: Figure Not Found
   :align: center
    
dfnWorks
^^^^^^^^^^^^^^^^^^^^^^^^^^

`dfnWorks <https://dfnworks.lanl.gov/>`_  is an open source three-dimensional discrete fracture network (DFN) modeling suite. 
In a DFN mode, each fracture's size, shape, orientation, location, as well as other hydrological properties are sampled from distributions whose parameters are determined from a site characterization.
Once the network is produced, as computational mesh representation is generated, on which flow and transport can be resolved.
A key capability of dfnWorks is the ability to include variable aperture values into a 3D DFN simulation. 

We developed a handshake between pySimFrac and dfnWorks to map pySimFrac generated aperture fields directly onto dfnWorks fractures.  An example of these is shown below. The network is composed of thirty-eight two meter square fractures in a 10 meter cube.  Each fracture has a unique aperture field generated using the pySimFrac spectral method. Each node in the mesh is assigned an aperture value from a pySimFrac fracture (see inset).

Example
------------------------------

.. figure:: figures/DFN_mesh.png
   :alt: Figure Not Found
   :align: center
    
   *A three-dimensional discrete fracture network generated with {\sc dfnWorks} that includes internal aperture variability generated using the pySimFrac spectral method*
