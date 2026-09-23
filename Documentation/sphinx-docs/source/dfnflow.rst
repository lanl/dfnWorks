.. _dfnflow-chapter:


dfnFlow
========


*dfnFlow* involves using flow solver such as PFLOTRAN or FEHM. PFLOTRAN is recommended if a large number of fractures ( > O(1000)) are involved in a network. Using the function calls that are part of pydfnworks, one can create the mesh files needed to run PFLOTRAN. This will involve creating unstructured mesh file ``*uge`` as well as the boundary  ``*ex`` files. Please see the PFLOTRAN user manual at http://www.pflotran.org under unstructured *explicit* format usage for further details. An example input file for PFLOTRAN is provided in the repository. Please use this as a starting point to build your input deck.

Below is a sample input file. Refer to the PFLOTRAN user manual at http://www.pflotran.org for input parameter descriptions. 

.. code-block:: c

	# Jan 13, 2014
	# Nataliia Makedonska, Satish Karra, LANL
	#================================================

	SIMULATION
	  SIMULATION_TYPE SUBSURFACE
	  PROCESS_MODELS
	    SUBSURFACE_FLOW flow
	      MODE RICHARDS
	    /
	  /
	END
	SUBSURFACE

	DFN

	#=========================== discretization ===================================
	GRID
	  TYPE unstructured_explicit full_mesh_vol_area.uge 
	  GRAVITY 0.d0 0.d0 0.d0
	END


	#=========================== fluid properties =================================
	FLUID_PROPERTY
	  DIFFUSION_COEFFICIENT 1.d-9
	END

	DATASET Permeability
	  FILENAME dfn_properties.h5
	END

	#=========================== material properties ==============================
	MATERIAL_PROPERTY soil1
	  ID 1
	  POROSITY 0.25d0
	  TORTUOSITY 0.5d0
	  CHARACTERISTIC_CURVES default
	  PERMEABILITY
	    DATASET Permeability
	  /
	END


	#=========================== characteristic curves ============================
	CHARACTERISTIC_CURVES default
	  SATURATION_FUNCTION VAN_GENUCHTEN
	    M 0.5d0
	    ALPHA  1.d-4
	    LIQUID_RESIDUAL_SATURATION 0.1d0
	    MAX_CAPILLARY_PRESSURE 1.d8
	  /
	  PERMEABILITY_FUNCTION MUALEM_VG_LIQ
	    M 0.5d0
	    LIQUID_RESIDUAL_SATURATION 0.1d0
	  /
	END

	#=========================== output options ===================================
	OUTPUT
	  TIMES s 0.01 0.05 0.1 0.2 0.5 1
	#  FORMAT TECPLOT BLOCK
	  PRINT_PRIMAL_GRID
	  FORMAT VTK
	  MASS_FLOWRATE
	  MASS_BALANCE
	  VARIABLES
	    LIQUID_PRESSURE
	    PERMEABILITY
	  /
	END

	#=========================== times ============================================
	TIME
	  INITIAL_TIMESTEP_SIZE  1.d-8 s
	  FINAL_TIME 1.d0 d==
	  MAXIMUM_TIMESTEP_SIZE 10.d0 d
	  STEADY_STATE
	END

	# REFERENCE_PRESSURE 1500000.

	#=========================== regions ==========================================
	REGION All
	  COORDINATES
	    -1.d20 -1.d20 -1.d20
	    1.d20 1.d20 1.d20
	  /
	END 

	REGION inflow
	  FILE pboundary_left_w.ex
	END

	REGION outflow
	  FILE pboundary_right_e.ex
	END

	#=========================== flow conditions ==================================
	FLOW_CONDITION initial
	  TYPE
	     PRESSURE dirichlet 
	  /
	  PRESSURE 1.01325d6
	END


	FLOW_CONDITION outflow 
	  TYPE 
	     PRESSURE dirichlet
	  /
	  PRESSURE 1.d6
	END

	FLOW_CONDITION inflow
	  TYPE
	    PRESSURE dirichlet
	  /
	  PRESSURE 2.d6
	END

	#=========================== condition couplers ===============================
	# initial condition
	INITIAL_CONDITION
	  FLOW_CONDITION initial
	  REGION All
	END


	BOUNDARY_CONDITION INFLOW 
	  FLOW_CONDITION inflow
	  REGION inflow
	END

	BOUNDARY_CONDITION OUTFLOW
	  FLOW_CONDITION outflow 
	  REGION outflow
	END

	#=========================== stratigraphy couplers ============================
	STRATA
	  REGION All 
	  MATERIAL soil1
	END

	END_SUBSURFACE

MOOSE / Falcon
--------------

To launch an existing MOOSE input deck with Falcon, select ``MOOSE`` as the
flow solver. The job directory must exist before launching::

    from pydfnworks import DFNWORKS

    dfn = DFNWORKS(
        jobname="/absolute/path/to/existing/job",
        dfnFlow_file="/absolute/path/to/input.in",
        flow_solver="MOOSE",
        ncpu=96,
    )
    dfn.dfn_flow()

For an existing DFN object, use ``dfn.set_flow_solver("MOOSE")`` and assign
``dfn.dfnFlow_file`` to the absolute input-deck path before calling
``dfn.dfn_flow()`` or ``dfn.moose()``.

The launcher copies the input deck into the job directory and runs
``mpiexec -n <ncpu> <executable> -i <input basename>`` there. It prepares a
child Bash login shell by purging modules when the module command is available,
unsetting the ``mpirun`` function and ``LD_LIBRARY_PATH``, sourcing Conda,
setting ``OPENBLAS_NUM_THREADS`` and ``OMP_NUM_THREADS`` to 1, and activating
``falcon-moose``. The calling Python process keeps its environment.

Defaults and environment overrides are:

* ``MOOSE_EXE``: ``~/projects/falcon/falcon-opt``
* ``MOOSE_CONDA_SH``: ``~/miniforge/etc/profile.d/conda.sh``
* ``MOOSE_CONDA_ENV``: ``falcon-moose``

Direct calls can also override these with
``dfn.moose(executable=..., conda_sh=..., conda_env=...)``.
Solver output streams to the terminal or batch-job log. A failed launch or
solver run raises an exception instead of reporting successful completion.
Run within a scheduler allocation with enough resources for ``ncpu`` ranks.

This integration launches a prepared MOOSE model. It does not convert dfnWorks
meshes or material/boundary data into a MOOSE model, or parse MOOSE output for
dfnTrans. Mesh files, included input files, and other relative dependencies
must be available in the job directory at the paths used by the copied deck.
The ``dump_vtk`` and ``dump_h5`` options of ``dfn_flow`` apply only to PFLOTRAN;
MOOSE output is controlled by the input deck.
