.. _dfnworks-python-chapter:

pydfnworks: the dfnWorks python package
========================================

The pydfnworks package allows the user to easily run dfnWorks from the command line and  call dfnWorks within other python scripts. Because pydfnworks is a package, users can call individual methods from the package easily.

The pydfnworks must be setup by the user using the following command in the directory dfnWorks-Version2.0/pydfnworks/ :

python setup.py install (if the user has admin privileges), OR:

python setup.py install --user (if the user does not have admin privileges):

The documentation below includes all the methods and classes of the pydfnworks package. 


DFNWORKS
----------
.. autoclass:: pydfnworks.DFNWORKS
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

dfnFlow
--------
.. automodule:: pydfnworks.flow
    :members:

dfnTrans
---------
.. automodule:: pydfnworks.transport
    :members:

LaGriT (meshing)
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

Helper methods
----------------

Mesh helper methods
^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.mesh_dfn_helper
    :members:

Print legal statement
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.legal
    :members:
 
Other helper methods
^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.helper
    :members:


