import numpy as np
import networkx as nx
import sys

def add_perm(G, fracture_info="fracture_info.dat"):
    """ Add fracture permeability to Graph. If Graph representation is
    fracture, then permeability is a node attribute. If graph representation 
    is intersection, then permeability is an edge attribute


    Parameters
    ---------- 
        G :networkX graph
            NetworkX Graph based on the DFN
   
        fracture_infor : str
                filename for fracture information
    Returns
    -------
 
    Notes
    -----

"""

    perm = np.genfromtxt(fracture_info, skip_header=1)[:, 1]
    if G.graph['representation'] == "fracture":
        nodes = list(nx.nodes(G))
        for n in nodes:
            if n != 's' and n != 't':
                G.nodes[n]['perm'] = perm[n - 1]
                G.nodes[n]['iperm'] = 1.0 / perm[n - 1]
            else:
                G.nodes[n]['perm'] = 1.0
                G.nodes[n]['iperm'] = 1.0

    elif G.graph['representation'] == "intersection":
        edges = list(nx.edges(G))
        for u, v in edges:
            x = G[u][v]['frac']
            if x != 's' and x != 't':
                G[u][v]['perm'] = perm[x - 1]
                G[u][v]['iperm'] = 1.0 / perm[x - 1]
            else:
                G[u][v]['perm'] = 1.0
                G[u][v]['iperm'] = 1.0
    elif G.graph['representation'] == "bipartite":
        # add fracture info
        with open(fracture_info) as f:
            f.readline()
            data = f.read().strip()
            for fracture, line in enumerate(data.split('\n'), 1):
                c, perm, aperture = line.split(' ')
                G.nodes[fracture]['perm'] = float(perm)
                G.nodes[fracture]['iperm'] = 1.0 / float(perm)
                G.nodes[fracture]['aperture'] = float(aperture)


def add_area(G, fracture_info="fracture_info.dat"):
    ''' Read Fracture aperture from fracture_info.dat and 
    load on the edges in the graph. Graph must be intersection to node
    representation
    
    Parameters
    ----------
        G : NetworkX Graph
            networkX graph 
        fracture_info : str
            filename for fracture information
    
    Returns
    -------
        None
'''

    aperture = np.genfromtxt(fracture_info, skip_header=1)[:, 2]
    edges = list(nx.edges(G))
    for u, v in edges:
        x = G.edges[u, v]['frac']
        if x != 's' and x != 't':
            G.edges[u,
                    v]['area'] = aperture[x - 1] * (G.nodes[u]['length'] +
                                                    G.nodes[v]['length']) / 2.0
        else:
            G.edges[u, v]['area'] = 1.0
    return


def add_weight(G):
    '''Compute weight w = K*A/L associated with each edge 
    Parameters
    ----------
        G : NetworkX Graph
            networkX graph 
    
    Returns
    -------
        None
    '''
    for u, v in nx.edges(G):
        if G.edges[u, v]['length'] > 0:
            G.edges[u, v]['weight'] = G.edges[u, v]['perm'] * G.edges[
                u, v]['area'] / G.edges[u, v]['length']
    return

