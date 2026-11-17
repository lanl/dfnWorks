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
    :members: lagrit2pflotran, pflotran, parse_pflotran_vtk, parse_pflotran_h5, dump_h5_files, pflotran_cleanup, write_perms_and_correct_volumes_areas, zone2ex

PFLOTRAN output can be written as VTK or HDF5. ``dfn_flow(dump_vtu=True, dump_h5=False)`` controls which is converted after the run. Both ``parse_pflotran_vtk`` and ``parse_pflotran_h5`` write one XML ``.vtu`` file per output time and a ``.pvd`` time series into ``pflotran_vtu_outputs/``. Open ``pflotran_vtu_outputs/<base>.pvd`` in ParaView.

The simulation times in the ``.pvd`` file are in seconds. For VTK output they are read from the PFLOTRAN log (``<base>.out``); for HDF5 output they come from the HDF5 time group names. Data arrays are base64-encoded binary by default; pass ``binary=False`` for ASCII.

.. note:: ``parse_pflotran_vtk_python``, ``inp2vtk_python``, ``dfn_flow(dump_vtk=...)``, and the ``vtk_file`` constructor argument are deprecated aliases of ``parse_pflotran_vtk``, ``inp2vtu``, ``dump_vtu``, and ``vtu_file``. They now write XML ``.vtu`` files.

Mesh Geometry Checks (UGE)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before PFLOTRAN runs, the explicit unstructured grid file (``full_mesh.uge``) is scanned for invalid cell volumes and connection areas (negative, ``NaN``, or infinite). Such values can appear when the mesh is built with relaxed constraints (:ref:`rFram`), mostly in dense networks and near triple intersections.

Two kinds of small values are not counted as invalid:

* **Round-off.** Values within :math:`10^{-8} h` of zero for connection areas (:math:`10^{-8} h^2` for cell volumes) are zero to working precision and are left unchanged without a message.
* **Degenerate Voronoi edges.** When the four nodes around a triangle edge are cocircular, the dual Voronoi edge has zero length and LaGriT can return a tiny area of either sign. Connection areas within :math:`10^{-5} h` of zero are accepted as zero, left unchanged, and listed in the log as warnings, one line per connection. This can happen in fully conforming meshes, with rFram off.

Values more negative than these tolerances, and ``NaN`` or infinite values, are invalid. The following policy is applied to them:

* :ref:`rFram` off and any invalid value: the run stops with an error. A conforming mesh should not produce invalid coefficients.
* rFram unknown (no parameter file was parsed, e.g., a flow-only restart) and any invalid value: the run stops and asks for ``DFN.r_fram`` to be set.
* More than 1% of the cells or more than 1% of the connections invalid: the run stops, regardless of rFram.
* Otherwise: negative values are replaced by their absolute value, non-finite values by the smallest positive value, and every corrected cell and connection is written to the log.

For ``dim=3`` (default) the corrected volumes and areas are multiplied by the fracture aperture and written to ``full_mesh_vol_area.uge``. For ``dim=2`` the aperture conversion is skipped.

.. automodule:: pydfnworks.dfnFlow.uge_tools
    :members: correct_uge_file

Running Flow: FEHM 
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnFlow.fehm
    :members: correct_stor_file, fehm

Processing Flow
^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnFlow.mass_balance
    :members: effective_perm
