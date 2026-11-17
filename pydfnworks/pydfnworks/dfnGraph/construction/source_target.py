"""
.. module:: source_target.py
   :synopsis: Add/replace source ('s') and target ('t') connections on a DFN graph.
"""

import networkx as nx

from pydfnworks.general.logging import local_print_log, print_log


def add_fracture_source(self, G, source):
    """  
    
    Parameters
    ----------
        self : object 
            DFN Class

        G : NetworkX Graph
            NetworkX Graph based on a DFN 
        
        source_list : list
            list of integers corresponding to fracture numbers
        
        remove_old_source: bool
            remove old source from the graph

    Returns 
    -------
        G : NetworkX Graph

    Notes
    -----
        bipartite graph not supported
         
    """

    if not type(source) == list:
        source = [source]

    self.print_log("--> Adding new source connections", 'warning')
    self.print_log("--> Warning old source will be removed!!!", 'warning')

    if G.graph['representation'] == "fracture":
        # removing old source term and all connections
        G.remove_node('s')
        # add new source node
        G.add_node('s')

        G.nodes['s']['perm'] = 1.0
        G.nodes['s']['iperm'] = 1.0

        for u in source:
            G.add_edge(u, 's')

    elif G.graph['representation'] == "intersection":
        # removing old source term and all connections
        nodes_to_remove = ['s']
        for u, d in G.nodes(data=True):
            if u != 's' and u != 't':
                f1, f2 = d["frac"]
                #print("node {0}: f1 {1}, f2 {2}".format(u,f1,f2))
                if f2 == 's':
                    nodes_to_remove.append(u)

        self.print_log("--> Removing nodes: ", nodes_to_remove)
        G.remove_nodes_from(nodes_to_remove)

        # add new source node
        G.add_node('s')
        for u, d in G.nodes(data=True):
            if u != 's' and u != 't':
                f1 = d["frac"][0]
                f2 = d["frac"][1]
                if f1 in source:
                    self.print_log(
                        "--> Adding edge between {0} and new source / fracture {1}"
                        .format(u, f1))
                    G.add_edge(u, 's', frac=f1, length=0., perm=1., iperm=1.)
                elif f2 in source:
                    self.print_log(
                        "--> Adding edge between {0} and new source / fracture {1}"
                        .format(u, f2))
                    G.add_edge(u, 's', frac=f2, length=0., perm=1., iperm=1.)

    elif G.graph['representation'] == "bipartite":
        self.print_log("--> Not supported for bipartite graph", 'warning')
        self.print_log("--> Returning unchanged graph", 'warning')
    return G


def add_fracture_target(self, G, target):
    """ 
    
    Parameters
    ----------
        self : object 
            DFN Class

        G : NetworkX Graph
            NetworkX Graph based on a DFN 
        
        target : list
            list of integers corresponding to fracture numbers
    Returns 
    -------
        G : NetworkX Graph

    Notes
    -----
        bipartite graph not supported
         
    """

    if not type(target) == list:
        source = [target]

    self.print_log("--> Adding new target connections", 'warning')
    self.print_log("--> Warning old target will be removed!!!", 'warning')

    if G.graph['representation'] == "fracture":
        # removing old target term and all connections
        G.remove_node('t')
        # add new target node
        G.add_node('t')

        G.nodes['t']['perm'] = 1.0
        G.nodes['t']['iperm'] = 1.0

        for u in target:
            G.add_edge(u, 't')

    elif G.graph['representation'] == "intersection":
        # removing old target term and all connections
        nodes_to_remove = ['t']
        for u, d in G.nodes(data=True):
            if u != 's' and u != 't':
                f1, f2 = d["frac"]
                #print("node {0}: f1 {1}, f2 {2}".format(u,f1,f2))
                if f2 == 't':
                    nodes_to_remove.append(u)

        self.print_log("--> Removing nodes: ", nodes_to_remove)
        G.remove_nodes_from(nodes_to_remove)

        # add new target node
        G.add_node('t')
        for u, d in G.nodes(data=True):
            if u != 's' and u != 't':
                f1 = d["frac"][0]
                f2 = d["frac"][1]
                if f1 in target:
                    self.print_log(
                        "--> Adding edge between {0} and new target / fracture {1}"
                        .format(u, f1))
                    G.add_edge(u, 't', frac=f1, length=0., perm=1., iperm=1.)
                elif f2 in target:
                    self.print_log(
                        "--> Adding edge between {0} and new target / fracture {1}"
                        .format(u, f2))
                    G.add_edge(u, 't', frac=f2, length=0., perm=1., iperm=1.)

    elif G.graph['representation'] == "bipartite":
        self.print_log("--> Not supported for bipartite graph", 'warning')
        self.print_log("--> Returning unchanged graph", 'warning')

    return G


