.. _dfnworks-chapter:

dfnworks: dfnWorks python wrapper
=====================================

The dfnworks module is the main module in dfnWorks which contains classes
and methods to read, manipulate, write and execute PFLOTRAN input files.

dfnworks class
###########

The :class:`.dfnworks` is the main class that wraps the dfnWorks suite. It executes the components of this suite, handles parallel execution, and processes input and output files where necessary. The other classes discussed in this section are defined to increase modularity of class:`.dfnworks`.

.. autoclass:: dfnworks.dfnworks


