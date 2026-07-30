.. _dfnWorks-python-chapter-dfnGraph:

pydfnworks: dfnGraph
========================================

DFN Class functions used in graph analysis and pipe-network simulations

General Graph Functions
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGraph.construction.create_graph
    :members: create_graph

.. automodule:: pydfnworks.dfnGraph.construction.source_target
    :members: add_fracture_source, add_fracture_target

.. automodule:: pydfnworks.dfnGraph.io.serialization
    :members: dump_json_graph, load_json_graph, plot_graph, dump_fractures

.. automodule:: pydfnworks.dfnGraph.algorithms.pruning
    :members: k_shortest_paths_backbone, greedy_edge_disjoint

.. automodule:: pydfnworks.dfnGraph.algorithms.deconstruct
    :members: deconstruct_intersection_graph


Edge Conductance Models
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGraph.attributes.conductance
    :members: add_weight

.. automodule:: pydfnworks.dfnGraph.attributes.perm_area
    :members: fracture_diameter


Graph-Based Flow and Transport
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGraph.flow.graph_flow
    :members: run_graph_flow

.. automodule:: pydfnworks.dfnGraph.flow.metrics
    :members: compute_dQ

.. automodule:: pydfnworks.dfnGraph.transport.graph_transport
    :members: run_graph_transport
