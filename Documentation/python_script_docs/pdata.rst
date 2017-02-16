.. _pdata-chapter:

pdata: PFLOTRAN input file generation
=====================================

The pdata  module is the main module in PyFLOTRAN which contains classes
and methods to read, manipulate, write and execute PFLOTRAN input files.

pdata class
###########

The :class:`.pdata` is the main class that does the reading, writing, manipulation and execution of the PFLOTRAN input files. The other classes discussed in this section are defined to increase modularity and are used to set the attributes of :class:`.pdata`.

.. autoclass:: pdata.pdata

Attributes
^^^^^^^^^^

Simulation
----------
.. autoclass:: pdata.psimulation

Grid
----
.. autoclass:: pdata.pgrid

Material 
--------
.. autoclass:: pdata.pmaterial

Time
----
.. autoclass:: pdata.ptime

Uniform Velocity
----------------
.. autoclass:: pdata.puniform_velocity

Nonuniform Velocity
-------------------
.. autoclass:: pdata.pnonuniform_velocity

Timestepper
-----------
.. autoclass:: pdata.ptimestepper

Linear Solver
-------------
.. autoclass:: pdata.plsolver

Newton Solver
-------------
.. autoclass:: pdata.pnsolver

Output
------
.. autoclass:: pdata.poutput

Fluid Properties
----------------
.. autoclass:: pdata.pfluid

Saturation Function
-------------------
.. autoclass:: pdata.psaturation

Region
------
.. autoclass:: pdata.pregion

Observation
-----------
.. autoclass:: pdata.pobservation

Flow
----
.. autoclass:: pdata.pflow

Flow Variable
-------------
.. autoclass:: pdata.pflow_variable

Flow Variable List
------------------
.. autoclass:: pdata.pflow_variable_list

Initial Condition
-----------------
.. autoclass:: pdata.pinitial_condition

Boundary Condition
------------------
.. autoclass:: pdata.pboundary_condition

Source Sink
-----------
.. autoclass:: pdata.psource_sink

Stratigraphy Coupler
--------------------
.. autoclass:: pdata.pstrata

Checkpoint
----------
.. autoclass:: pdata.pcheckpoint

Restart
-------
.. autoclass:: pdata.prestart

Chemistry
---------
.. autoclass:: pdata.pchemistry

Chemistry Mineral Kinetic
-------------------------
.. autoclass:: pdata.pchemistry_m_kinetic

Transport Condition
-------------------
.. autoclass:: pdata.ptransport

Constraint Condition
--------------------
.. autoclass:: pdata.pconstraint

Constraint Condition Concentration
----------------------------------
.. autoclass:: pdata.pconstraint_concentration

Constraint Condition Mineral
----------------------------
.. autoclass:: pdata.pconstraint_mineral

Regression
----------
.. autoclass:: pdata.pregression

Dataset
-------
.. autoclass:: pdata.pdataset

QK3
---
.. autoclass:: pdata.pquake


Methods
^^^^^^^
.. automethod:: pdata.pdata.read
.. automethod:: pdata.pdata.write
.. automethod:: pdata.pdata.run
.. automethod:: pdata.pdata.add
.. automethod:: pdata.pdata.delete
.. automethod:: pdata.pdata.paraview
.. automethod:: pdata.pdata.apply_traction
.. automethod:: pdata.pdata.generate_geomech_grid

Line plots using Matplotlib
^^^^^^^^^^^^^^^^^^^^^^^^^^^
To plot time histories of variables at various observation points, the following function can be used: 

.. automethod:: pdata.pdata.plot_observation

To compare spatial profiles (1D) of the multiple realizations at one instant of time or for the same realization at different instants of time, one can use the following function:

.. automethod:: pdata.pdata.plot_data_from_tec
