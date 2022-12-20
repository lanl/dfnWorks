.. _dfnWorks-python-chapter:

pydfnworks: the dfnWorks python package
========================================

The pydfnworks package allows the user to run dfnWorks from the command line and  call dfnWorks within other python scripts. Because pydfnworks is a package, users can call individual methods from the package.

pydfnworks must be installed by the user prior to running dfnworks (:ref:`pydfnWorks install <pydfnworks-setup>`)


Running dfnWorks from the command line using pydfnWorks
---------------------------------------------------------
The recommended way to run dfnWorks is using a python call on the command line. 

.. code-block:: bash

    $ python run.py -name /dfnWorks/work/4_user_rects_example -input 4_user_defined_rectangles_run_file.txt


.. tip:: Examples of command line calls for running simulations are provided in ascii files named ``notes.txt`` within each of the example directories.


The script ``run.py`` is the python control file that contains the workflow of the particular simulation. Below is a basic example taken from the 4_user_rects_example example:

.. code-block:: python

        from pydfnworks import *

        DFN = create_dfn()
        # General Work Flow
        DFN.dfn_gen()
        DFN.dfn_flow()
        DFN.dfn_trans()


Command Line Arguments:
---------------------------

Along with the python script, each simulation is controlled by a set of command line arguments, which are described flow. 



-name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: (Mandatory) Path of the simulation directory. Must be a valid path. The path is stored in ``DFN.jobname`` of the DFN object created by ``create_dfn()``

Type: string

Example:


.. code-block:: bash

    -name /dfnWorks/work/4_user_rects_example 

.. note:: If the directory does not exist, ``DFN.make_working_directory()`` will create it.


-input
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: (Mandatory) Path of the input file containing run files for dfnGen, dfnFlow (PFLOTRAN/FEHM/AMANZI), and dfnTrans. This file is parsed and the paths contained within are stored as ``DFN.dfnGen_file``, ``DFN.dfnFlow_file``, and ``DFN.dfnTrans_file``. The local path for the files (string after the final ``/`` are stored as ``DFN.local_dfnGen_file``, ``DFN.local_dfnFlow_file``, and ``DFN.local_dfnTrans_file``.

Type: string

Example:

.. code-block:: bash

    -input 4_user_defined_rectangles_run_file.txt

Example of input run file: 

.. code-block:: bash

    dfnGen /dfnWorks/examples/4_user_rects/gen_4_user_rectangles.dat
    dfnFlow /dfnWorks/examples/4_user_rects/dfn_explicit.in
    dfnTrans /dfnWorks/examples/4_user_rects/PTDFN_control.dat

.. note:: The input file cannot have an empty line after dfnTrans.



-ncpu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Number of processors to be used in the simulation. Stored as ``DFN.ncpu``. 

Type: integer

Example:

.. code-block:: bash

    -ncpu 8

.. note:: Default is 4. 


-path
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Path to parent directory. Useful for multiple runs using the same network with different meshing techniques, hydraulic properties, flow simulations, or pruned networks. Path is stored as ``DFN.path``.

Type: string

Example:

.. code-block:: bash

    -path /dfnWorks/work/4_user_rects_example 


-prune_file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Path to ascii file of fractures to be retained (not removed) in the network after pruning. See the pruning example for a workflow demonstration.

Type: string

Example:

.. code-block:: bash

    -prune_file /dfnWorks/work/pruning_example/2_core.dat

.. note:: To prune the network, include ``DFN.mesh_network(prune=True)`` in the python run file. 

-cell
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Toggle if the fracture apertures are cell based. If the option is included on the command line, then the workflow will assign cell-based apertures and permeabilities from the files ``aper_node.dat`` and ``perm_node.dat``. These files consist of two columns, with a single line header value. The first column is the node number. The second column is the aperture/permeability value. See the See the in_fracture_var example for a workflow demonstration.

Type: Boolean

Example: 

.. code-block:: bash

    -cell 



pydfnWorks : Modules
------------------------
Information about the various pieces of pydfnworks is found in

:ref:`pydfnGen <dfnWorks-python-chapter-dfnGen>` - Network generation, meshing, and analysis 

:ref:`pydfnFlow <dfnWorks-python-chapter-dfnFlow>` - Flow simulations using PFLOTRAN and FEHM

:ref:`pydfnTrans <dfnWorks-python-chapter-dfnTrans>` - Particle Tracking

:ref:`pydfnGraph <dfnWorks-python-chapter-dfnGraph>` - Graph-based analysis and pipe-network simulations

:ref:`Well-Package <dfnWorks-python-chapter-well-package>` - Well simulations


DFN Class and setup
^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pydfnworks.general.dfnworks
    :members: create_dfn

Detailed Doxygen Documentation
----------------------------------
Doxygen_

.. _Doxygen: pydfnWorks_docs/index.html

