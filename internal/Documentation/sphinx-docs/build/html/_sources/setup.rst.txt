Settting up dfnWorks
=============================

This document contains instructions for setting up dfnWorks on you machine, 

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

Fix the pathnames for all files in the folder /tests/ . This can be done automatically by running the script fix_paths.py:

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

