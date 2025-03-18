.. _dfnWorks-python-chapter-dfnFlow:

pydfnworks: dfnFlow
========================================


DFN Class functions used in flow simulations (PFLOTRAN and FEHM)

Running Flow : General 
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnFlow.flow
    :members:

Running Flow: PFLOTRAN
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnFlow.pflotran
    :members: lagrit2pflotran, pflotran, parse_pflotran_vtk_python, pflotran_cleanup, write_perms_and_correct_volumes_areas, zone2ex

Running Flow: FEHM 
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnFlow.fehm
    :members: correct_stor_file, fehm

Processing Flow
^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnFlow.mass_balance
    :members: effective_perm
