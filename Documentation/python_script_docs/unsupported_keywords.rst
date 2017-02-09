.. _keywords-chapter:

Unsupported PFLOTRAN keywords
=============================

As of Oct. 18, 2016

PFLOTRAN keywords not currently supported by PyFLOTRAN:

* BRINE

* COMPUTE_STATISTICS

* DEBUG

* PROC

* USE_TOUCH_OPTIONS

* VELOCITY_DATASET

* WALLCLOCK_STOP

Keywords that are supported, but not 100%, listing attributes for keywords that are not supported:

* CHEMISTRY
	- REDOX_SPECIES
	- COLLOIDS

* GRID
	- INVERT_Z

* LINEAR_SOLVER
	- Only SOLVER_TYPE works - Does not support data validation checking

* NEWTON_SOLVER
	- INEXACT_NEWTON
	- NO_PRINT_CONVERGENCE
	- NO_INF_NORM (NO_INFINITY_NORM)
	- NO_FORCE_ITERATION
	- PRINT_DETAILED_CONVERGENCE
	- ITOL_UPDATE (INF_TOL_UPDATE)
	- ITOL_SEC (ITOL_RES_SEC, INF_TOL_SEC)
	- MAX_NORM

* OUTPUT
	- NO_PRINT_INITIAL
	- NO_PRINT_FINAL
	- VOLUME
	- FLUXES

* FLUID
	- DIFFUSION_ACTIVATION_ENERGY

