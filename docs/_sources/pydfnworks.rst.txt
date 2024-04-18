.. _dfnWorks-python-chapter:

pydfnworks: the dfnWorks python package
========================================

The pydfnworks package allows the user to run dfnWorks from the command line and  call dfnWorks within other python scripts. Because pydfnworks is a package, users can call individual methods from the package.

pydfnworks must be installed by the user prior to running dfnworks (:ref:`pydfnWorks install <pydfnworks-setup>`)


Running dfnWorks from the command line using pydfnWorks
---------------------------------------------------------
The recommended way to run dfnWorks is using a python call on the command line, or running the script in your favorite IDE. 

.. code-block:: bash

    $ python driver.py


The script ``driver.py`` is the python control file that contains the workflow of the particular simulation. Below is a basic example taken from the 4_user_rects_example example:

.. code-block:: python

        from pydfnworks import *
        import os

        src_path = os.getcwd()
        jobname = src_path + "/output"
        dfnFlow_file = src_path+ '/dfn_explicit.in'
        dfnTrans_file = src_path + '/PTDFN_control.dat'

        DFN = DFNWORKS(jobname,
                       dfnFlow_file=dfnFlow_file,
                       dfnTrans_file=dfnTrans_file,
                       ncpu=8)

        DFN.params['domainSize']['value'] = [1.0, 1.0, 1.0]
        DFN.params['h']['value'] = 0.050

        DFN.add_user_fract(shape='rect',
                           radii=0.6,
                           translation=[-0.4, 0, 0],
                           normal_vector=[0, 0, 1],
                           permeability=1.0e-12)

        DFN.add_user_fract(shape='rect',
                           radii=1.0,
                           aspect_ratio=.65,
                           translation=[0, 0, 0],
                           normal_vector=[1, 0, 0],
                           permeability=1.0e-12)

        DFN.add_user_fract(shape='rect',
                           radii=.6,
                           translation=[0.4, 0, 0.2],
                           normal_vector=[0, 0, 1],
                           permeability=2.0e-12)

        DFN.add_user_fract(shape='rect',
                           radii=.6,
                           translation=[0.4, 0, -0.2],
                           normal_vector=[0, 0, 1],
                           permeability=1.0e-12)

        DFN.make_working_directory(delete=True)
        DFN.check_input()
        DFN.print_domain_parameters()

        DFN.create_network()
        DFN.mesh_network()

        DFN.dfn_flow()
        DFN.dfn_trans()


The DFNWORKS class
---------------------------

Within the python script, a DFN (discrete fracture network) object is created to control the model workflow. Data and model functions are stored on this object, allowing the user to both access information about the DFN while debugging, as well as call functions for modelling everything from network generation to transport modelling. Arguments for creating the DFN object are listed below. Additional arguments and functions required to create the DFN are discussed in other sections of this manual.

Default Arguments:

.. code-block:: python

    from pydfnworks import *

    DFN = DFNWORKS(jobname = None, #required
                   ncpu = 4,
                   dfnGen_file = None, #automatically generated
                   dfnFlow_file = None, #required for DFN.dfn_flow()
                   dfnTrans_file = None, #required for DFN.dfn_trans()
                   path = None,
                   prune_file = None,
                   flow_solver = 'PFLOTRAN',
                   inp_file = 'full_mesh.inp',
                   uge_file = 'full_mesh.uge',
                   mat_file = 'materialid.dat',
                   stor_file = None,
                   vtk_file = None,
                   num_nodes = None,
                   mesh_type = 'dfn',
                   cell_based_aperture = False)


jobname
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: (Mandatory) Path of the simulation directory. Must be a valid path. The path is stored in ``DFN.jobname`` of the DFN object

Type: string

Example:

.. code-block:: python
        
        import os
        src_path = os.getcwd()
        jobname = src_path + "/output"

ncpu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Number of processors to be used in the simulation. Stored as ``DFN.ncpu``.

Type: integer

Example:

.. code-block:: python

    ncpu = 8


dfnFlow_file/dfnGen_file/dfnTrans_file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note:: dfnGen_file is depreciated, file name is automatically specified

Description: (Mandatory) Path of the input file containing run files for dfnGen, dfnFlow (PFLOTRAN/FEHM/AMANZI), and dfnTrans. This file is parsed and the paths contained within are stored as ``DFN.dfnGen_file``, ``DFN.dfnFlow_file``, and ``DFN.dfnTrans_file``. The local path for the files (string after the final ``/`` are stored as ``DFN.local_dfnGen_file``, ``DFN.local_dfnFlow_file``, and ``DFN.local_dfnTrans_file``.

Type: string

Example: 

.. code-block:: python

        dfnGen_file = 'gen_4_user_rectangles.dat'
        dfnFlow_file = 'dfn_explicit.in'
        dfnTrans_file = 'PTDFN_control.dat'


path
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Path to parent directory. Useful for multiple runs using the same network with different meshing techniques, hydraulic properties, flow simulations, or pruned networks. Path is stored as ``DFN.path``.

Type: string

Example:

.. code-block:: python

    path = '/dfnWorks/work/4_user_rects_example' 

prune_file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Path to ascii file of fractures to be retained (not removed) in the network after pruning. See the pruning example for a workflow demonstration.

Type: string

Example:

.. code-block:: python

    prune_file = '/dfnWorks/work/pruning_example/2_core.dat'

.. note:: To prune the network, include ``DFN.mesh_network(prune=True)`` in the python run file. 


flow_solver 
^^^^^^^^^^^^^^^
Description: Either 'PFLOTRAN' or 'FEHM'

Example:

.. code-block:: python

    flow_solver = 'PFLOTRAN'


cell_based_aperture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Toggle if the fracture apertures are cell based. If the option is included, then the workflow will assign cell-based apertures and permeabilities from the files ``aper_node.dat`` and ``perm_node.dat``. These files consist of two columns, with a single line header value. The first column is the node number. The second column is the aperture/permeability value. See the See the in_fracture_var example for a workflow demonstration.

Type: Boolean

Example:

.. code-block:: python

   cell_based_aperture = True

additional arguments
^^^^^^^^^^^^^^^^^^^^^
Descriptions: additional arguments that have not been described here will likely not be changed by the user. 


pydfnWorks : Modules
------------------------
Information about the various pieces of pydfnworks is found in

:ref:`pydfnGen <dfnWorks-python-chapter-dfnGen>` - Network generation, meshing, and analysis 

:ref:`pydfnFlow <dfnWorks-python-chapter-dfnFlow>` - Flow simulations using PFLOTRAN and FEHM

:ref:`pydfnTrans <dfnWorks-python-chapter-dfnTrans>` - Particle Tracking

:ref:`pydfnGraph <dfnWorks-python-chapter-dfnGraph>` - Graph-based analysis and pipe-network simulations

:ref:`Well-Package <dfnWorks-python-chapter-well-package>` - Well simulations

.. note:: There are additional required arguments for network generation described in :ref:`dfnGen <dfngen-chapter>` 

Detailed Doxygen Documentation
----------------------------------
Doxygen_

.. _Doxygen: pydfnWorks_docs/index.html

