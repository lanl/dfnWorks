import numpy as np
import networkx as nx

from networkx.algorithms.flow.shortestaugmentingpath import *
from networkx.algorithms.flow.edmondskarp import *
from networkx.algorithms.flow.preflowpush import *

from itertools import islice


def current_flow_threshold(self, G, source = "s", target = "t", weight = None, thrs = 0.0):
    """ Runs current flow (Potential drop between source and target) on the Graph G, and returns a subgraph such that the current on the edges is greater than the threshold value (thrs).
    
    Parameters
    ----------
        G : NetworkX Graph
            NetworkX Graph based on a DFN 
        source : node 
            Starting node
        target : node
            Ending node
        weight : string
            Resistance term used in the solution of Laplace's Equation
        thrs: float
            Threshold value for pruning the graph

    Returns 
    -------
        H : NetworkX graph
            Subgraph such that the current on the edges is greater than the threshold value

    Notes
    -----
        Graph attributes (node and edge) are not retained on the subgraph H. 
    """



    print(f'--> Running Current Flow with weight : {weight} and threshold {thrs}')
    cf = nx.edge_current_flow_betweenness_centrality_subset(G,sources=[source],targets=[target],weight=weight)
    print("Current Flow Complete")
    currentflow_edges = [(u,v) for (u,v),d in cf.items() if d > thrs]
    H = nx.Graph(currentflow_edges, representation=G.graph["representation"])
    print(f"--> Of the {G.number_of_nodes()} in the original graph,  {H.number_of_nodes()} are in the thresholded network")
    print("--> Running Current Flow Complete")
    return H

def k_shortest_paths(G, k, source, target, weight):
    """Returns the k shortest paths in a graph 
    
    Parameters
    ----------
        G : NetworkX Graph
            NetworkX Graph based on a DFN 
        k : int
            Number of requested paths
        source : node 
            Starting node
        target : node
            Ending node
        weight : string
            Edge weight used for finding the shortest path

    Returns 
    -------
        paths : sets of nodes
            a list of lists of nodes in the k shortest paths

    Notes
    -----
    Edge weights must be numerical and non-negative
"""
    return list(
        islice(nx.shortest_simple_paths(G, source, target, weight=weight), k))


def k_shortest_paths_backbone(self, G, k, source='s', target='t', weight=None):
    """Returns the subgraph made up of the k shortest paths in a graph 
   
    Parameters
    ----------
        G : NetworkX Graph
            NetworkX Graph based on a DFN 
        k : int
            Number of requested paths
        source : node 
            Starting node
        target : node
            Ending node
        weight : string
            Edge weight used for finding the shortest path

    Returns 
    -------
        H : NetworkX Graph
            Subgraph of G made up of the k shortest paths 

    Notes
    -----
        See Hyman et al. 2017 "Predictions of first passage times in sparse discrete fracture networks using graph-based reductions" Physical Review E for more details
"""

    print("\n--> Determining %d shortest paths in the network" % k)
    H = G.copy()
    k_shortest = set([])
    for path in k_shortest_paths(G, k, source, target, weight):
        k_shortest |= set(path)
    k_shortest.remove('s')
    k_shortest.remove('t')
    path_nodes = sorted(list(k_shortest))
    path_nodes.append('s')
    path_nodes.append('t')
    nodes = list(G.nodes())
    secondary = list(set(nodes) - set(path_nodes))
    for n in secondary:
        H.remove_node(n)
    return H
    print("--> Complete\n")


def greedy_edge_disjoint(self, G, source='s', target='t', weight='None', k=''):
    """
    Greedy Algorithm to find edge disjoint subgraph from s to t. 
    See Hyman et al. 2018 SIAM MMS

    Parameters
    ----------
        self : object 
            DFN Class Object
        G : NetworkX graph
            NetworkX Graph based on the DFN
        source : node 
            Starting node
        target : node
            Ending node
        weight : string
            Edge weight used for finding the shortest path
        k : int
            Number of edge disjoint paths requested
    
    Returns
    -------
        H : NetworkX Graph
            Subgraph of G made up of the k shortest of all edge-disjoint paths from source to target

    Notes
    -----
        1. Edge weights must be numerical and non-negative.
        2. See Hyman et al. 2018 "Identifying Backbones in Three-Dimensional Discrete Fracture Networks: A Bipartite Graph-Based Approach" SIAM Multiscale Modeling and Simulation for more details 

    """
    print("--> Identifying edge disjoint paths")
    if G.graph['representation'] != "intersection":
        print(
            "--> ERROR!!! Wrong type of DFN graph representation\nRepresentation must be intersection\nReturning Empty Graph\n"
        )
        return nx.Graph()
    Gprime = G.copy()
    Hprime = nx.Graph()
    Hprime.graph['representation'] = G.graph['representation']
    cnt = 0

    # if a number of paths in not provided k will equal the min cut between s and t
    min_cut = len(nx.minimum_edge_cut(G, 's', 't'))
    if k == '' or k > min_cut:
        k = min_cut

    while nx.has_path(Gprime, source, target):
        path = nx.shortest_path(Gprime, source, target, weight=weight)
        H = Gprime.subgraph(path)
        Hprime.add_edges_from(H.edges(data=True))
        Gprime.remove_edges_from(list(H.edges()))

        cnt += 1
        if cnt > k:
            break
    print("--> Complete")
    return Hprime


