.. _dfnWorks-python-chapter-dfnGraph:

pydfnworks: dfnGraph
========================================

DFN Class functions used in graph analysis and pipe-network simulations

General Graph Functions
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGraph.dfn2graph
    :members: create_graph, dump_json_graph, load_json_graph, plot_graph, dump_fractures, add_fracture_source, add_fracture_target

.. automodule:: pydfnworks.dfnGraph.pruning
    :members:  k_shortest_paths_backbone, greedy_edge_disjoint





Graph-Based Flow and Transport
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pydfnworks.dfnGraph.graph_flow
    :members: run_graph_flow

.. automodule:: pydfnworks.dfnGraph.graph_transport
    :members: run_graph_transport
