.. _dfnWorks-python-chapter:

pydfnworks: the dfnWorks python package
========================================

The pydfnworks package allows the user to run dfnWorks from the command line and  call dfnWorks within other python scripts. Because pydfnworks is a package, users can call individual methods from the package.

The pydfnworks must be setup by the user using the following command in the directory ``dfnWorks-Version2.0/pydfnworks/`` :

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
.. automodule:: pydfnworks.dfnGen.gen_input
    :members:

.. automodule:: pydfnworks.dfnGen.distributions
    :members:

Running the generator
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.generator
    :members:

Analysis of Generated DFN 
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.gen_output
    :members:

Meshing - LaGriT
-----------------

Mesh DFN
^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.mesh_dfn
    :members:

LaGrit scripts
^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.lagrit_scripts
    :members:

Run meshing in parallel
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.run_meshing
    :members:

Mesh helper methods
^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGen.mesh_dfn_helper
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

General Workflow Functions
--------------------------

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
 
