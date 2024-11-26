import networkx as nx
import numpy as np
import json
import sys

from networkx.readwrite import json_graph
import matplotlib

matplotlib.use('Agg')

import matplotlib.pylab as plt

from pydfnworks.dfnGraph.intersection_graph import create_intersection_graph
from pydfnworks.dfnGraph.fracture_graph import create_fracture_graph
from pydfnworks.dfnGraph.bipartite_graph import create_bipartite_graph
from pydfnworks.general.logging import local_print_log

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
        , 'warning')
        return nx.Graph()
    return G


def boundary_index(bc_name):
    """Determines boundary index in intersections_list.dat from name

    Parameters
    ----------
        bc_name : string
            Boundary condition name

    Returns
    -------
        bc_index : int
            integer indexing of cube faces

    Notes
    -----
    top = 1
    bottom = 2
    left = 3
    front = 4
    right = 5
    back = 6
    """
    bc_dict = {
        "top": -1,
        "bottom": -2,
        "left": -3,
        "front": -4,
        "right": -5,
        "back": -6
    }
    try:
        return bc_dict[bc_name]
    except:
        error = f"Error. Unknown boundary condition: {bc_name} \nExiting\n"
        local_print_log(error, 'error')

def add_fracture_source(self, G, source):
    """  
    
    Parameters
    ----------
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


def pull_source_and_target(nodes, source='s', target='t'):
    """Removes source and target from list of nodes, useful for dumping subnetworks to file for remeshing

    Parameters
    ----------
        nodes :list 
            List of nodes in the graph
        source : node 
            Starting node
        target : node
            Ending node
    Returns
    -------
        nodes : list
            List of nodes with source and target nodes removed

    Notes
    -----

"""
    for node in [source, target]:
        try:
            nodes.remove(node)
        except:
            pass
    return nodes


def dump_fractures(self, G, filename):
    """Write fracture numbers assocaited with the graph G out into an ASCII file inputs

    Parameters
    ----------
        self : object
            DFN Class
        G : NetworkX graph
            NetworkX Graph based on the DFN
        filename : string
            Output filename 

    Returns
    -------

    Notes
    ----- 
    """

    if G.graph['representation'] == "fracture":
        nodes = list(G.nodes())
    elif G.graph['representation'] == "intersection":
        nodes = []
        for u, v, d in G.edges(data=True):
            nodes.append(G[u][v]['frac'])
        nodes = list(set(nodes))
    elif G.graph['representation'] == "bipartite":
        nodes = []
        for u, v, d in G.edges(data=True):
            nodes.append(G[u][v]['frac'])
        nodes = list(set(nodes))

    nodes = pull_source_and_target(nodes)
    fractures = [int(i) for i in nodes]
    fractures = sorted(fractures)
    local_print_log(f"--> Dumping {filename}")
    np.savetxt(filename, fractures, fmt="%d")


def plot_graph(self, G, source='s', target='t', output_name="dfn_graph"):
    """ Create a png of a graph with source nodes colored blue, target red, and all over nodes black
    
    Parameters
    ---------- 
        G : NetworkX graph
            NetworkX Graph based on the DFN
        source : node 
            Starting node
        target : node
            Ending node
        output_name : string
            Name of output file (no .png)

    Returns
    -------

    Notes
    -----
    Image is written to output_name.png

    """
    self.print_log("--> Plotting Graph")
    filename = f"{output_name}.png"
    self.print_log(f"--> Output file: {filename}" )
    # get positions for all nodes
    pos = nx.spring_layout(G)
    nodes = list(G.nodes)
    # draw nodes
    nx.draw_networkx_nodes(G,
                           pos,
                           nodelist=nodes,
                           node_color='k',
                           node_size=10,
                           alpha=1.0)
    nx.draw_networkx_nodes(G,
                           pos,
                           nodelist=[source],
                           node_color='b',
                           node_size=50,
                           alpha=1.0)
    nx.draw_networkx_nodes(G,
                           pos,
                           nodelist=[target],
                           node_color='r',
                           node_size=50,
                           alpha=1.0)

    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename)
    plt.clf()
    self.print_log("--> Plotting Graph Complete")


def dump_json_graph(self, G, name):
    """Write graph out in json format
 
    Parameters
    ---------- 
        self : object 
            DFN Class
        G :networkX graph
            NetworkX Graph based on the DFN
        name : string
             Name of output file (no .json)

    Returns
    -------

    Notes
    -----

"""
    filename = f"{name}.json"
    self.print_log(f"--> Dumping Graph into file: {filename} ")
    jsondata = json_graph.node_link_data(G)
    with open(name + '.json', 'w') as fp:
        json.dump(jsondata, fp)
    self.print_log("--> Complete")


def load_json_graph(self, filename):
    """ Read in graph from json format

    Parameters
    ---------- 
        self : object 
            DFN Class
        name : string
             Name of input file (no .json)

    Returns
    -------
        G :networkX graph
            NetworkX Graph based on the DFN
"""
    self.print_log(f"Loading Graph in file: {filename}")
    try:
        fp = open(filename)
    except:
        self.print_log(f"Unable to open file {filename}. Returning empty Graph", "warning")
        return nx.Graph() 
    
    G = json_graph.node_link_graph(json.load(fp))
    self.print_log("Complete")
    return G
