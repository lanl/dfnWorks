.. _dfnworks-chapter:

setup.py: compile the components of dfnWorks
=========================================================

The setup.py script should be run using python setup.py before using dfnWorks. This script compiles the C and C++ components of dfnWorks. Without arguments, the script performs the setup. With the argument 'clean,' the script cleans up C and C++ object files.


.. automodule:: setup
    :members: 


benchmark.py: test dfnWorks using one or more benchamrks
=========================================================

The benchamrk.py script can be used to easily test functionality of dfnWorks. It runs a benchmark suite (input files contained in the benchmarks folder) that test the exponential, power law, and lognormal distributions as well as user-defined ellipses and user-defined rectangle fracture inputs.

.. automodule:: benchmark
    :members: 

run_dfnworks.py: execute a single run of dfnWorks
===================================================

The run_dfnworks.py script allows the user to execute a single run of dfnWorks. The syntax for this script is python run_dfnworks.py -ncpu [NUMBER OF CPUS TO USE] -input [INPUT_FILE_NAME]. 

.. automodule:: run_dfnworks
    :members: 

