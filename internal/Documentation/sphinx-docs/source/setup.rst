Setting up dfnWorks
=============================

This document contains instructions for setting up dfnWorks natively on your
machine. To setup dfnWorks using Docker instead, see the next section.

Turn on X forwarding if on server
----------------------------------

Ensure that X forwarding is turned on if you are running dfnWorks from an ssh connection. This requires that the ssh login have the -X option:

.. code-block:: bash
   
    $ ssh -X SERVER_NAME 

Go to the dnfWorks repository
------------------------------------------

.. code-block:: bash

    $ cd ~/dfnWorks/

Fix paths in test directory 
----------------------------

Fix the pathnames for all files in the folder ``/tests/`` . This can be done automatically by running the script ``fix_paths.py``:

.. code-block:: bash

    $ cd /pydfnworks/bin/
    $ python fix_paths.py 

Set the PETSC, PFLOTRAN, Python, and LaGriT paths 
----------------------------------------------------------------

**Before executing dfnWorks,** the following paths must be set:

- dfnWorks_PATH: the dfnWorks repository folder
- PETSC_DIR and PETSC_ARCH: PETSC environmental variables
- PFLOTRAN_EXE:  Path to PFLOTRAN executable 
- PYTHON_EXE:  Path to python executable 
- LAGRIT_EXE:  Path to LaGriT executable 

.. code-block:: bash
    
    $ vi /pydfnworks/pydfnworks/paths.py

For example:

.. code-block:: python
    
    os.environ['dfnWorks_PATH'] = '/home/username/dfnWorks/'    

Setup the Python package pydfnworks
-------------------------------------

Go up a directory:

.. code-block:: bash
    
    $ cd ..

**If the user has admin privelges**:

.. code-block:: bash
    
    $ python setup.py install

**If the user DOES NOT have admin priveleges**:

.. code-block:: bash
   
    $ python setup.py install --user


Running dfnWorks from Docker
============================

If you do not already have Docker installed on your machine,
visit `Getting Started with Docker <https://www.docker.com/get-started>`_.

The dfnWorks Docker image can be pulled from DockerHub using:

.. code-block:: bash

    $ docker pull ees16/dfnworks:latest

Setting Up X-Forwarding
-----------------------

**On macOS:**

To setup X-forwarding on macOS, you will need ``homebrew``,``socat`` and ``xquartz``.
To install homebrew visit `https://brew.sh/ <https://brew.sh/>`_. or run 

.. code-block:: bash

    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"


To install, ``socat`` and ``xquartz`` run:

.. code-block:: bash

    brew install socat
    brew cask install xquartz

``socat`` is used to expose the local XQuartz socker over a TCP port, enabling the
Docker container to exchange display information with your local machine.

**On Linux:**

.. code-block:: bash

    TODO

Running the dfnWorks container
------------------------------

The base command for running the dfnWorks container is:

.. code-block:: bash

    docker run -ti ees16/dfnworks:latest

However, to exchange files between the host and container, we will need to mount
a volume.

The option ``-v LOCAL_FOLDER:/dfnWorks/work`` will allow all files present in the
container folder ``dfnWorks/work`` to be exposed to ``LOCAL_FOLDER``, where
``LOCAL_FOLDER`` is the absolute path to a folder on your machine.

In order to exchange display information, we will need to pass in the DISPLAY
variable from host to container.

On macOS, this is ``-e DISPLAY=docker.for.mac.host.internal:0``. On Linux, it is
``TODO``.

With this is place, the final command for running the Docker container is:

**On macOS:**

.. code-block:: bash

    open -a XQuartz
    socat TCP-LISTEN:6000,reuseaddr,fork UNIX-CLIENT:\"$DISPLAY\"
    docker run -ti \
           -e DISPLAY=docker.for.mac.host.internal:0 \
           -v /Users/yourname/dfnworks-example:/dfnWorks/work \
           dfnworks:latest

**On Linux:**

.. code-block:: bash

    TODO

Troubleshooting
---------------

If you recieve a warning that port 6000 is in use, run either ``lsof -i TCP:6000``
or ``netstat -vanp tcp | grep 6000`` to isolate the process listening on this port.

Then, use ``kill -i <PID>`` to kill the process and re-run ``xquartz``, ``socat``,
and ``docker run``.

