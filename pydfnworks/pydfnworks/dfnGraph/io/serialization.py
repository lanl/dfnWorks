"""
.. module:: serialization.py
   :synopsis: Graph IO and plotting -- JSON dump/load, PNG plot, fracture-id dump.
"""

import json

import networkx as nx
import numpy as np
from networkx.readwrite import json_graph

import matplotlib

matplotlib.use('Agg')

import matplotlib.pylab as plt

from pydfnworks.general.logging import local_print_log, print_log


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
    self.print_log(f"--> Dumping {filename}")
    np.savetxt(filename, fractures, fmt="%d")


def plot_graph(self, G, source='s', target='t', output_name="dfn_graph"):
    """ Create a png of a graph with source nodes colored blue, target red, and all over nodes black
    
    Parameters
    ---------- 
        self : object 
            DFN Class

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
