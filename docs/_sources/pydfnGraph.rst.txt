.. _dfnWorks-python-chapter-dfnGraph:

pydfnworks: dfnGraph
========================================

DFN Class functions used in graph analysis and pipe-network simulations.

The ``pydfnworks.dfnGraph`` package is organized into subpackages:

* ``construction`` -- build intersection, fracture, and bipartite graphs from a DFN and attach source/target nodes.
* ``attributes`` -- edge permeability, area, and conductance (weight) models.
* ``flow`` -- steady-state pressure-driven flow on the graph and post-processing metrics.
* ``transport`` -- particle tracking on the graph, including time domain random walk (TDRW) matrix diffusion models.
* ``algorithms`` -- pruning and graph deconstruction.
* ``io`` -- reading, writing, and plotting graphs.

All public functions are re-exported from ``pydfnworks.dfnGraph`` so ``from pydfnworks.dfnGraph import <name>`` keeps working. The functions below are also methods of the DFN object, e.g., ``G = DFN.create_graph('intersection', 'left', 'right')``.

General Graph Functions
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGraph.construction.create_graph
    :members: create_graph

.. automodule:: pydfnworks.dfnGraph.construction.source_target
    :members: add_fracture_source, add_fracture_target

.. automodule:: pydfnworks.dfnGraph.io.serialization
    :members: dump_json_graph, load_json_graph, plot_graph, dump_fractures

Graph Pruning
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGraph.algorithms.pruning
    :members: k_shortest_paths_backbone, greedy_edge_disjoint, current_flow_threshold


Graph-Based Flow
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGraph.flow.graph_flow
    :members: run_graph_flow

.. automodule:: pydfnworks.dfnGraph.flow.metrics
    :members: compute_dQ

Edge Conductance Models
------------------------

The edge ``weight`` used in the graph Laplacian is the hydraulic conductance of the fracture surface represented by that edge. ``run_graph_flow`` selects the model with ``conductance_model``:

* ``'doolaeghe'`` (default since v2.12) -- the size-aware trapezoid conductance of Doolaeghe et al. (2020) with a correction for the redundant paths formed by fractures with many intersections. The fracture diameter comes from ``diameter_from='area'`` (area-equivalent, default) or ``'max_radius'``. Extra keyword arguments are forwarded to the model:

  * ``B`` -- close-intersection coefficient, default 1.5.
  * ``mp_correction`` -- multiple-paths correction: ``'divide'`` (default, Doolaeghe et al. 2020), ``'additive'`` (adapted from Doolaeghe et al. 2021), or ``'none'``.

* ``'karra'`` -- the model of Karra et al. (2018), :math:`w = K A / L`. This was the default before v2.12; pass ``conductance_model='karra'`` to reproduce earlier results.

Setting ``simplify=True`` removes redundant crossing edges on each fracture with the deconstructed-graph method of Doolaeghe et al. (2021) before the flow solve.

.. code-block:: python

    G = DFN.create_graph("intersection", "left", "right")
    H = DFN.run_graph_flow("left", "right", 2e6, 1e6, G=G,
                           conductance_model="doolaeghe", mp_correction="divide")

.. automodule:: pydfnworks.dfnGraph.attributes.conductance
    :members: add_weight


Graph-Based Transport
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGraph.transport.graph_transport
    :members: run_graph_transport

Particle trajectories are seeded from ``DFN.params['seed']``, so repeated runs with the same seed give the same particle paths. See :ref:`seed`.

Matrix Diffusion (TDRW)
------------------------

Setting ``tdrw_flag=True`` adds matrix diffusion to graph transport with a time domain random walk. Each particle's time on a fracture is increased by a random trapping time in the surrounding rock matrix. ``matrix_porosity`` and ``matrix_diffusivity`` [m\ :sup:`2`/s] are required. ``tdrw_model`` selects the matrix geometry:

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - ``tdrw_model``
     - Description
   * - ``'infinite'``
     - Default. Diffusion into a semi-infinite matrix (unlimited block size).
   * - ``'dentz'``
     - Finite slab between parallel fractures. Return times are sampled from the first-passage time distribution of diffusion in a slab, inverted from the Laplace domain with the Stehfest algorithm.
   * - ``'annulus'``
     - Finite annular (cylindrical) matrix block, also inverted from the Laplace domain with Stehfest.
   * - ``'roubinet'``
     - The limited-block model used before v2.12 (Roubinet et al.).
   * - ``'from_file'``
     - User-supplied return-time CDF. ``tdrw_filename`` points to a two-column ASCII file of return times and CDF values.

All finite models (``dentz``, ``annulus``, ``roubinet``, ``from_file``) require ``fracture_spacing`` [m], the distance between adjacent parallel fractures. The matrix block half-width is ``fracture_spacing/2``. If ``fracture_spacing`` is given and ``tdrw_model`` is left at ``'infinite'``, the ``'dentz'`` model is used and a message is written to the log.

.. code-block:: python

    particles = DFN.run_graph_transport(H, nparticles=10**5,
                                        partime_file="partime.dat",
                                        tdrw_flag=True,
                                        matrix_porosity=0.005,
                                        matrix_diffusivity=1e-13,
                                        tdrw_model="dentz",
                                        fracture_spacing=1.0)

Three timescales describe the effect of a finite matrix block with half-aperture :math:`b_f`, matrix porosity :math:`\phi_m`, and diffusivity :math:`D_m`:

* departure from advective transport: :math:`t^* \sim (b_f/\phi_m)^2 / D_m`
* finite-block cutoff: :math:`\tau_D = (s/2)^2 / D_m`, where :math:`s` is the fracture spacing
* equilibrium retardation: :math:`R = 1 + \phi_m (s/2) / b_f`

See ``examples/tdrw`` and ``examples/finite_matrix_diffusion`` for complete workflows.
