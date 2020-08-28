.. _dfnWorks-python-chapter:

pydfnworks: the dfnWorks python package
========================================

The pydfnworks package allows the user to run dfnWorks from the command line and  call dfnWorks within other python scripts. Because pydfnworks is a package, users can call individual methods from the package.

The pydfnworks must be setup by the user using the following command in the directory ``dfnWorks/pydfnworks/`` :

``python setup.py install`` (if the user has admin privileges), OR:

``python setup.py install --user`` (if the user does not have admin privileges):

The documentation below includes methods and classes of the pydfnworks package. 

DFN Class and Setup
---------------------

.. automodule:: pydfnworks.general.dfnworks
    :members:

dfnGen
-------

Processing generator input
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.generation.gen_input
    :members:

.. automodule:: pydfnworks.dfnGen.generation.distributions
    :members:

Running the generator
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.generation.generator
    :members:

Analysis of generated DFN 
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.generation.gen_output
    :members:

Modification of hydraulic properties of the DFN 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.generation.hydraulic_properties
    :members:

Meshing - LaGriT
-----------------

Primary DFN meshing driver
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.meshing.mesh_dfn
    :members:

Generation LaGrit scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.meshing.lagrit_scripts_poisson_disc
    :members:

Run meshing in parallel
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.meshing.run_meshing
    :members:

Meshing helper methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.meshing.mesh_dfn_helper
    :members:

.. automodule:: pydfnworks.dfnGen.meshing.add_attribute_to_mesh
    :members:

Point Generation : Poisson-Disc Sampling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.meshing.poisson_disc.poisson_class
    :members:

.. automodule:: pydfnworks.dfnGen.meshing.poisson_disc.poisson_functions
    :members:

Creating an upscaled mesh of the DFN
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.meshing.udfm.map2continuum
    :members:

.. automodule:: pydfnworks.dfnGen.meshing.udfm.upscale
    :members:

dfnFlow
--------

Running Flow
^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnFlow.flow
    :members:

Running Flow: PFLOTRAN
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnFlow.pflotran
    :members:

Running Flow: FEHM 
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnFlow.fehm
    :members:

Processing Flow
^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnFlow.mass_balance
    :members:


dfnTrans
---------

Running Transport 
^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnTrans.transport
    :members:

dfnGraph
---------

General Graph Functions
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGraph.dfn2graph
    :members:

Graph-Based Flow and Transport
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGraph.graph_flow
    :members:

.. automodule:: pydfnworks.dfnGraph.graph_transport
    :members:

General Workflow functions
-----------------------------

Print legal statement
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.general.legal
    :members:
 
Helper functions
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.general.general_functions
    :members:
 
Set up run paths
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.general.paths
    :members:
 
