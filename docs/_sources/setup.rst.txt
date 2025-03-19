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

Setup the Docker dfnWorks image 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Check Docker is installed and running correctly. 
If you do not already have Docker installed on your machine, visit `Getting Started with Docker <https://www.docker.com/get-started>`_.


.. code-block:: bash

    $ docker run hello-world
    Hello from Docker!
    This message shows that your installation appears to be working correctly.


Once Docker is installed, pull the dfnWorks Docker image:

.. code-block:: bash

    $ docker pull ees16/dfnworks:latest


After pulling, the dfnWorks Docker image is stored on your machine and can be listed using the command ```docker images```. This contains the dfnWorks repository files, libraries, and dependencies needed to run the dfnWorks application. 


Run the dfnWorks container 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


This method of running the dfnWorks container is useful for exploring the example files or running tests, but it's not ideal for saving your own work or results.
When you run a Docker container without specifying a volume, any files created inside the container during its execution will only exist until you exit the container. Once you type exit, the container stops, and you lose any changes or files generated inside it.


The base command for running the dfnWorks container is:

.. code-block:: bash

    docker run -ti ees16/dfnworks:latest

When you run the command above, you will be inside the container, and your current directory will be set to `/dfnWorks`.
Here’s how to run one of the included examples in the dfnWorks container: 

.. code-block:: bash

    cd examples/4_user_rects
    python driver.py
    

The unix command ```ls``` will display the files written, including `output.log` and result files in `/output`.
After exiting, all the files you created or modified during that session will be lost because they weren't saved outside the container.
 

Run the dfnWorks container with mounted volume
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to exchange files between the host computer and a Docker container, you can mount a volume. Mounting a volume allows the container to access files stored on your local machine. Keep in mind that the mount command may vary depending on your operating system. 

**General Note:**
Use a volume where permissions will not be an issue to ensure smooth operation.



**On LANL Linux Servers**


Docker is available on the local server `es11`. It is important to work from your home directory to avoid permission issues.


Assuming you want to mount a local version of the dfnWorks repository, use the following command to clone it: ```git clone git@github.com:lanl/dfnWorks.git```.
You may want to set more open permissions to ensure there are no issues with file access. You can set these permissions using: ```chmod 777 -R dfnWorks```.


After preparing your local volume, pull the latest dfnWorks Docker image:

.. code-block:: bash

    docker pull ees16/dfnworks:latest


Run the container with a mounted volume.  
Move into the directory where you want to run dfnWorks (e.g., `dfnWorks/examples/4_user_rects`) and use the following command. This example assumes you want to run a script named `driver.py` (you can substitute this with your desired script name):


.. code-block:: bash

    docker run -v "$(pwd):/app" -w /app ees16/dfnworks:latest python driver.py 


In this example, the inner-docker folder /app will share its content with your local current folder. All files will persist after you exit Docker. 


**On macOS:**

On macOS, you can mount a directory on your local machine to the container. Use the following command, replacing `<LOCAL_FOLDER>` with the absolute path to your local directory:

.. code-block:: bash

    docker run -ti -v <LOCAL_FOLDER>:/dfnWorks/work ees16/dfnworks:latest


**In General**

To link the current folder between the host and the container for development, you can use the following command:


.. code-block:: bash

    docker run <image-name> -v $(pwd):<folder-path-in-container> ees16/dfnworks:latest


Replace `<image-name>` with `ees16/dfnworks:latest` and `<folder-path-in-container>` with the desired folder path inside the container.



Native Build 
------------------------------------------

.. _build_section:


These instructions describe how to setup dfnWorks natively on your machine.

For more information about installing dfnWorks, refer to the `dfnWorks README on github <https://github.com/lanl/dfnWorks/blob/master/README.md>`_.


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

Compile The pydfnWorks Package & Install on Your Local Machine:

.. code-block:: bash
    
    $ pip install -r requirements.txt


or

.. code-block:: bash
    
    $ pip install -r requirements.txt --user

if you don't have admin privileges

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

