.. _dfnWorks-python-chapter:

pydfnWorks: the dfnWorks python package
========================================

The pydfnWorks package allows the user to easily run dfnWorks from the command line and  call dfnWorks within other python scripts. Because pydfnWorks is a package, users can call individual methods from the package easily.

The pydfnWorks must be setup by the user using the following command in the directory dfnWorks-Version2.0/pydfnWorks/ :

python setup.py install (if the user has admin privileges), OR:

python setup.py install --user (if the user does not have admin privileges):

The documentation below includes all the methods and classes of the pydfnWorks package. 


dfnWorks
----------
.. autoclass:: pydfnWorks.dfnWorks
    :members:

dfnGen
-------

Processing generator input
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnWorks.gen_input
    :members:

.. automodule:: pydfnWorks.distributions
    :members:

Running the generator
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnWorks.generator
    :members:

Graphing generator output
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnWorks.gen_output
    :members:

dfnFlow
--------
.. automodule:: pydfnWorks.flow
    :members:

dfnTrans
---------
.. automodule:: pydfnWorks.transport
    :members:

LaGriT (meshing)
-----------------

Mesh DFN
^^^^^^^^^
.. automodule:: pydfnWorks.meshdfn
    :members:

LaGrit scripts
^^^^^^^^^^^^^^^
.. automodule:: pydfnWorks.lagrit_scripts
    :members:

Run meshing in parallel
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnWorks.run_meshing
    :members:

Helper methods
----------------

Mesh helper methods
^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnWorks.mesh_dfn_helper
    :members:

Print legal statement
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnWorks.legal
    :members:
 
Other helper methods
^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnWorks.helper
    :members:


