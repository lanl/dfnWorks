.. _dfnWorks-python-chapter:

pydfnworks: the dfnWorks python package
========================================

The pydfnworks package allows the user to run dfnWorks from the command line and  call dfnWorks within other python scripts. Because pydfnworks is a package, users can call individual methods from the package.

The pydfnworks must be setup by the user using the following command in the directory ``dfnWorks-Version2.0/pydfnworks/`` :

``python setup.py install`` (if the user has admin privileges), OR:

``python setup.py install --user`` (if the user does not have admin privileges):

The documentation below includes all the methods and classes of the pydfnworks package. 

DFN Class
----------------

.. automodule:: pydfnworks.dfnworks
    :members:


DFN setup 
----------------

.. automodule:: pydfnworks.create_dfn
    :members:

dfnGen
-------

Processing generator input
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.gen_input
    :members:

.. automodule:: pydfnworks.distributions
    :members:

Running the generator
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.generator
    :members:

Graphing generator output
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.gen_output
    :members:

Meshing - LaGriT
-----------------

Mesh DFN
^^^^^^^^^
.. automodule:: pydfnworks.meshdfn
    :members:

LaGrit scripts
^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.lagrit_scripts
    :members:

Run meshing in parallel
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.run_meshing
    :members:

Mesh helper methods
^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.mesh_dfn_helper
    :members:

dfnFlow
--------

Running Flow
^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.flow
    :members:

Processing Flow
^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.mass_balance
    :members:


dfnTrans
---------

Running Transport 
^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.transport
    :members:

dfn2graph
---------
.. automodule:: pydfnworks.dfn2graph
    :members:

General Workflow functions
--------------------------

Print legal statement
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.legal
    :members:
 
Helper functions
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.general_functions
    :members:
 
Set up run paths
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.paths
    :members:
 
