.. _scripts-chapter:

Scripts
========

The pydfnworks package has three Python scripts that assist with compiling, testing, and running the software. These scripts are all in the folder dfnworks-main/pydfnworks/bin/ . 

compile.py: compile dfnWorks components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The compile.py script is called by run.py, but can also be called on its own. This script compiles the C and C++ components of dfnWorks. Without arguments, the script performs the compiling. With the argument 'clean,' the script cleans up C and C++ object files, before compiling.


test.py: test dfnWorks 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The benchmark.py script can be used to easily test functionality of dfnWorks. It runs a benchmark suite (input files contained in the benchmarks folder) that test the exponential, power law, and lognormal distributions as well as user-defined ellipses and user-defined rectangle fracture inputs.


run.py: run dfnWorks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The run.py script allows the user to execute a single run of dfnWorks. The syntax for this script is:

python run.py -name [JOBNAME] -input [INPUT_FILE_NAME] -ncpu [NUMBER OF CPUS TO USE] -input [INPUT_FILE_NAME] -large_network

Please refer to the tutorial section (the next section for a detailed description of how to run dfnWorks. 


