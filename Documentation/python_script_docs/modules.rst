dfnworks: dfnWorks python wrapper
=====================================

DFNWORKS class
################

The :class:`.DFNWORKS` is the main class that wraps the dfnWorks suite. It executes the components of this suite, handles parallel execution, and processes input and output files where necessary. The other classes discussed in this section are defined to increase modularity of class:`.DFNWORKS`.

.. autoclass:: modules.DFNWORKS.DFNWORKS
.. automethod:: modules.DFNWORKS.create_dfn(dfnGen_file="", dfnFlow_file="", dfnTrans_file="")

dfnFlow class
##############

The :class:'.dfnFlow` is the class containing methods that execute PFLOTRAN and perform IO processing on PFLOTRAN input and output. 

.. autoclass:: modules.flow.dfnFlow
  :members:

dfnTrans class
###############

The :class:'.dfnTrans' is the class containing methods that execute dfnTrans and perform IO processing on dfnTrans input and output. 

.. autoclass:: modules.transport.dfnTrans
  :members:
