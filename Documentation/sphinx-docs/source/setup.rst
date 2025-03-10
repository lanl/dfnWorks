.. _pydfnworks-setup:

Setup and Running dfnWorks
================================

These options are available for running dfnWorks:

* Use Docker dfnWorks to run and view files. The Docker dfnWorks contains all the tools and examples needed. Files created within Docker will not persist past the exit. Except for Docker, no installation is needed.

* Use Docker and mount a volume. Files will be read and written in your local directory. Files will persist past the exit.

* Clone and build dfnWorks on your machine. This will give full access and control of all the tools and files for your project. Installation will include Python, dfnWorks, LaGriT, PFLOTRAN, and FEHM.

* Linux dfnWorks module. Some servers use the module system and may have dfnWorks available. You will still need to clone dfnWorks for the files, but you can skip the build process.


Docker
------------------------------

.. _docker_section:


The easiset way to get started with dfnWorks is by Using Docker. You will not need to install any software or manage your enviornment. All the tools and the dfnWorks repository are contained in the Docker image. 

Check Docker is installed and running correctly. 

If you do not already have Docker installed on your machine, visit `Getting Started with Docker <https://www.docker.com/get-started>`_.

.. code-block:: bash

    $ docker run hello-world
    Hello from Docker!
    This message shows that your installation appears to be working correctly.


Before running the dfnWorks container, pull the dfnWorks Docker image using:

.. code-block:: bash

    $ docker pull ees16/dfnworks:latest


Now you can run the dfnWorks container using the dfnWorks repository included, or by mounting a volume for the container to share with your host. Note files written inside the container do not persist past the Docker ```exit```.


Run the dfnWorks container 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The base command for running the dfnWorks container is:

.. code-block:: bash

    docker run -ti ees16/dfnworks:latest

Your current directory will be /dfnWorks. You can run one of the included examples and run dfnWorks. For example:


.. code-block:: bash

    cd examples/4_user_rects
    python driver.py


Files are written to the /output directory. Without a mounted volume, the files will not exist outside of Docker and after you ```exit```.
 

Run the dfnWorks container with mounted volume
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to exchange files between the host and Docker container you can mount a volume. The mount command may work differently depending on your machine. Use a volume where permissions will not be an issue.
These examples use a cloned version of dfnWorks for the local files. 


**On LANL Linux Servers**

Docker is available on local server es11 and you must work from your home directory to avoid permission issues. After you have cloned the dfnWorks repository, open permissions:

.. code-block:: bash

    chmod 777 -R dfnWorks 
    docker pull ees16/dfnworks:latest


Once built, the inner-docker folder /app will share its content with your local current folder. Move into the directory where you want to run dfnWorks then copy the following command. (assuming driver.py is your dfnWorks driver script). 

.. code-block:: bash

    docker run -v "$(pwd):/app" -w /app ees16/dfnworks:latest python driver.py 


**On macOS:**

The option ``-v LOCAL_FOLDER:/dfnWorks/work`` will allow all files present in the
container folder ``dfnWorks/work`` to be exposed to ``LOCAL_FOLDER``, where
``LOCAL_FOLDER`` is the absolute path to a folder on your machine.

With this is place, the final command for running the Docker container is:


.. code-block:: bash

    docker run -ti -v <LOCAL_FOLDER>:/dfnWorks/work ees16/dfnworks:latest


**In General**


To link current folder between host and container for development:

```docker run <image-name> -v $(pwd):<folder-path-in-container> ees16/dfnworks:latest``` 


To copy a file from the running container to host mechine:

```docker cp <container-id>:<path/to/file> <host/copy/path>```



Native Build 
------------------------------------------

.. _build_section:

These instructions describe how to setup dfnWorks natively on your
machine. 

Clone the dnfWorks repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: bash

    $ git clone https://github.com/lanl/dfnWorks.git


Fix paths in test directory 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Fix the pathnames in files throughout pydfnworks. This can be done automatically by running the script ``fix_paths.py``:

.. code-block:: bash

    $ cd dfnWorks/pydfnworks/bin/
    $ python fix_paths.py 

Set the LagriT, PETSC, PFLOTRAN, Python, and FEHM paths 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Before executing dfnWorks,** the following paths must be set:

- dfnWorks_PATH: the dfnWorks repository folder
- PETSC_DIR and PETSC_ARCH: PETSC environmental variables
- PFLOTRAN_EXE:  Path to PFLOTRAN executable 
- PYTHON_EXE:  Path to python executable 
- LAGRIT_EXE:  Path to LaGriT executable 

.. code-block:: bash
    
    $ vi dfnWorks/pydfnworks/pydfnworks/paths.py

For example:

.. code-block:: python
    
    os.environ['dfnWorks_PATH'] = '/home/username/dfnWorks/'    

Alternatively, you can create a ``.dfnworksrc`` file in your home directory with the following format

.. code-block:: bash

    {
        "dfnworks_PATH": "<your-home-directory>/src/dfnworks-main/",
        "PETSC_DIR": "<your-home-directory>/src/petsc",
        "PETSC_ARCH": "arch-darwin-c-debug",
        "PFLOTRAN_EXE": "<your-home-directory>/src/pflotran/src/pflotran/pflotran",
        "PYTHON_EXE": "<your-home-directory>/anaconda3/bin/python",
        "LAGRIT_EXE": "<your-home-directory>/bin/lagrit",
        "FEHM_EXE": "<your-home-directory>//src/xfehm_v3.3.1"
    }


Installing pydfnworks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Go up into the pydfnworks sub-directory:

.. code-block:: bash
    
    $ cd dfnWorks/pydfnworks/

Complie The pydfnWorks Package:

.. code-block:: bash
    
    $ python setup.py bdist_wheel


Install on Your Local Machine:

.. code-block:: bash
    
    $ python -m pip install dist/pydfnworks-2.6-py3-none-any.whl

**Note that the python version in dist/ needs to be consistent with the current release**

Installation Requirements for Native Build
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Tools that you will need to run the dfnWorks work flow are described in 
this section. VisIt and ParaView, which enable visualization of desired 
quantities on the DFNs, are optional, but at least one of them is highly 
recommended for visualization. CMake is also optional but allows faster IO 
processing using C++. 

Operating Systems
*****************************

dfnWorks currently runs on Macs and Unix machine running Ubuntu. 

Python 
*****************************

pydfnworks uses Python 3. We recommend using 
the Anaconda 3 distribution of Python, available at https://www.continuum.io/. 
pydfnworks requires the following python modules: ``numpy``, ``h5py``, ``scipy``, ``matplotlib``,  ``multiprocessing``, ``argparse``, ``shutil``, ``os``, ``sys``, ``networkx``, ``subprocess``, ``glob``, ``networkx``, ``fpdf``, and ``re``.


LaGriT
******
The LaGriT_ meshing toolbox is used to create a high resolution computational 
mesh representation of the DFN in parallel. An algorithm for conforming 
Delaunay triangulation is implemented so that fracture intersections are 
coincident with triangle edges in the mesh and Voronoi control volumes are 
suitable for finite volume flow solvers such as FEHM and PFLOTRAN.

.. _LaGriT: https://lagrit.lanl.gov

PFLOTRAN
********
PFLOTRAN_  is a massively parallel subsurface flow and reactive transport 
code. PFLOTRAN solves a system of partial differential equations for 
multiphase, multicomponent and multi-scale reactive flow and transport in 
porous media. The code is designed to run on leadership-class supercomputers 
as well as workstations and laptops.

.. _PFLOTRAN: http://pflotran.org

FEHM
****
FEHM_ is a subsurface multiphase flow code developed at Los Alamos National 
Laboratory.

.. _FEHM: https://fehm.lanl.gov

CMake
*****************************
CMake_ is an open-source, cross-platform family of tools designed to build, 
test and package software. It is needed to use C++ for processing files at a 
bottleneck IO step of dfnWorks. Using C++ for this file processing optional 
but can greatly increase the speed of dfnWorks for large fracture networks. 
Details on how to use C++ for file processing are in the scripts section of 
this documentation.

.. _CMake: https://cmake.org

Paraview
*****************************

Paraview_ is a parallel, open-source visualisation software. PFLOTRAN can 
output in ``.xmf`` and ``.vtk`` format. These can be imported in Paraview 
for visualization. While not required for running dfnWorks, Paraview is
very helpful for visualizing dfnWorks simulations.

Instructions for downloading and installing Paraview_ can be found at 
http://www.paraview.org/download/ 

.. _Paraview: http://www.paraview.org

