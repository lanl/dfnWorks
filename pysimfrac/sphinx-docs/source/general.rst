.. _simfrac-general:

General Functions
*****************************



Input / Output
=============================

Pickle binary
----------------------


.. automodule:: pysimfrac.src.io.dump_pickle 
    :members: to_pickle
    :noindex:

.. code-block:: python

        myFrac.to_pickle('myfrac.pkl')

.. automodule:: pysimfrac.src.io.dump_pickle 
    :members: from_pickle

.. code-block:: python

        myFrac = SimFrac(pickle_file = "myfrac.pkl" )


ASCII 
----------------------

.. automodule:: pysimfrac.src.io.dump_ascii 
    :members: dump_ascii
    :noindex:

.. code-block:: python

        myFrac.dump_ascii(surface = 'all', filename_prefix = 'myfrac', coordinates = True)


