.. _dfnWorks-python-chapter-thermal:

pydfnworks: thermal
========================================

Heat extraction from fractured rock for hydraulic-fracture spacing
optimization. Two backends share one ``heat_extraction()`` interface so an
optimizer can call either interchangeably: the Phase 1 analytic surrogate
(Gringarten, Witherspoon and Ohnishi 1975 multiple parallel fractures model)
and the Phase 2 DFN graph-transport backend (interface only in this
version).

Common interface
^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.thermal
    :members: get_backend

Phase 1: Gringarten multiple parallel fractures surrogate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.thermal.mpf_gringarten
    :members: heat_extraction, production_temperature, dimensionless_parameters, dimensionless_drawdown, single_fracture_drawdown, laplace_drawdown

Phase 2: DFN-based heat transport
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.thermal.dfn_heat
    :members: heat_extraction, thermal_to_tdrw_parameters

Spacing optimizer
^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.thermal.optimize_spacing
    :members: optimize_spacing, cumulative_heat, time_to_drawdown
