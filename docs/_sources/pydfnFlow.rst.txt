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
    :members: lagrit2pflotran, pflotran, parse_pflotran_vtk_python, parse_pflotran_h5, dump_h5_files, pflotran_cleanup, write_perms_and_correct_volumes_areas, zone2ex

PFLOTRAN output can be written as VTK or HDF5. ``dfn_flow(dump_vtk=True, dump_h5=False)`` controls which is parsed after the run. Both ``parse_pflotran_vtk_python`` and ``parse_pflotran_h5`` write per-time-step VTK files into ``pflotran_vtk_outputs/``.

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
