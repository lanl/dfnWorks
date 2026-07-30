"""
.. module:: create_graph.py
   :synopsis: Header dispatcher that builds a DFN graph of the requested type
              (fracture, intersection, or bipartite).
"""

import networkx as nx

from pydfnworks.dfnGraph.construction.fracture_graph import create_fracture_graph
from pydfnworks.dfnGraph.construction.intersection_graph import create_intersection_graph
from pydfnworks.dfnGraph.construction.bipartite_graph import create_bipartite_graph
from pydfnworks.general.logging import local_print_log, print_log


def create_graph(self, graph_type, inflow, outflow):
    """ Header function to create a graph based on a DFN. Particular algorithms are in files.

    Parameters
    ----------
        self : object
            DFN Class object 
        
        graph_type : string
            Option for what graph representation of the DFN is requested. Currently supported are fracture, intersection, and bipartitie 
        
        inflow : string
            Name of inflow boundary (connect to source)
        
        outflow : string
            Name of outflow boundary (connect to target)

    Returns
    -------
        G : NetworkX Graph
            Graph based on DFN 

    Notes
    -----

"""
    ## write hydraulic properties to file.
    self.dump_hydraulic_values()
    if graph_type == "fracture":
        G = create_fracture_graph(inflow, outflow)
    elif graph_type == "intersection":
        G = create_intersection_graph(inflow, outflow)
    elif graph_type == "bipartite":
        G = create_bipartite_graph(inflow, outflow)
    else:
        self.print_log(
            f"Warning. Unknown graph type.\nType provided: {graph_type}.\nAccetable names: fracture, intersection, bipartite.\nReturning empty graph."
        , 'warning', 'warning')
        return nx.Graph()
    return G


