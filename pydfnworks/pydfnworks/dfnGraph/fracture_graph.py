import networkx as nx
import numpy as np

from pydfnworks.dfnGraph.graph_attributes import add_perm

def create_fracture_graph(inflow,
                          outflow,
                          topology_file="connectivity.dat",
                          fracture_info="fracture_info.dat"):
    """ Create a graph based on topology of network. Fractures
    are represented as nodes and if two fractures intersect 
    there is an edge between them in the graph. 
    
    Source and Target node are added to the graph. 
    
    Parameters
    ----------
        inflow : string
            Name of inflow boundary (connect to source)
        outflow : string
            Name of outflow boundary (connect to target)
        topology_file : string
            Name of adjacency matrix file for a DFN default=connectivity.dat  
        fracture_infor : str
                filename for fracture information

    Returns
    -------
        G : NetworkX Graph
            NetworkX Graph where vertices in the graph correspond to fractures and edges indicated two fractures intersect  

    Notes
    -----
    """
    print("--> Loading Graph based on topology in " + topology_file)
    G = nx.Graph(representation="fracture")
    with open(topology_file, "r") as infile:
        for i, line in enumerate(infile):
            conn = [int(n) for n in line.split()]
            for j in conn:
                G.add_edge(i + 1, j)
    ## Create Source and Target and add edges
    inflow_filename = inflow + ".dat"
    outflow_filename = outflow + ".dat"
    inflow = np.genfromtxt(inflow_filename).astype(int)
    outflow = np.genfromtxt(outflow_filename).astype(int)

    try:
        if len(inflow) > 1:
            inflow = list(inflow)
    except:
        inflow = [inflow.tolist()]

    try:
        if len(outflow) > 1:
            outflow = list(outflow)
    except:
        outflow = [outflow.tolist()]

    G.add_node('s')
    G.add_node('t')
    G.add_edges_from(zip(['s'] * (len(inflow)), inflow))
    G.add_edges_from(zip(outflow, ['t'] * (len(outflow))))
    add_perm(G, fracture_info)
    print("--> Graph loaded")
    return G

