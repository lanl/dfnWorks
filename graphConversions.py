import networkx as nx
import numpy as np

def intersection_id_generator(length=5):
    from itertools import product
    chars = 'abcdefghijklmnopqrstuvwxyz'
    for p in product(chars, repeat=length):
        yield (''.join(p))

def intersection2fracture(G, inflow, outflow):
    #Create copy of intersection graph with just nodes, no edges
    Gp = nx.create_empty_copy(G)

    #Relabel intersections so as not to conflict with fracture ids
    intersection_id = intersection_id_generator()
    intersection_relabelling = {}
    for n in Gp.nodes:
        if(n=='s' or n=='t'): intersection_relabelling[n] = n
        else: intersection_relabelling[n] = next(intersection_id)
    nx.relabel_nodes(Gp, intersection_relabelling, copy=False)

    # keep track of the sets of fractures and intersections for later bipartite projection
    Gp.fractures = set()
    Gp.intersections = [n for n in Gp.nodes]

    #Add fractures to bipartite graph
    for i in Gp.intersections:
        frac1, frac2 = Gp.nodes[i]['frac']
        Gp.add_edge(i,frac1)
        Gp.add_edge(i,frac2)
        Gp.fractures.add(frac1)
        Gp.fractures.add(frac2)

    #Project onto fractures
    Gp = nx.projected_graph(Gp, Gp.fractures)

    from pydfnworks.dfnGraph import create_fracture_graph
    F = create_fracture_graph(inflow, outflow)
    #Induced subgraph of F
    Gp = F.subgraph(Gp.nodes)

    return Gp

def fracture2intersection(G, inflow, outflow):
    #Create copy of fracture graph with just nodes, no edges
    Gp = nx.create_empty_copy(G)

    # keep track of the sets of fractures and intersections for later bipartite projection
    Gp.fractures = [n for n in Gp.nodes]
    Gp.intersections = set() 

    from pydfnworks.dfnGraph import create_intersection_graph
    I = create_intersection_graph(inflow, outflow)

    #Relabel intersections so as not to conflict with fracture ids
    intersection_id = intersection_id_generator()
    intersection_relabelling = {}
    for i in I.nodes:
        if(i=='s' or i=='t'): intersection_relabelling[i] = i
        else: intersection_relabelling[i] = next(intersection_id)
    nx.relabel_nodes(I, intersection_relabelling, copy=False)

    #Add appropriate intersections to bipartite graph
    for n, i in I.nodes(data='frac'):
        if(np.isin(i[0], Gp.fractures) and np.isin(i[1], Gp.fractures)):
            Gp.add_edge(i[0],n)
            Gp.add_edge(i[1],n)
            Gp.intersections.add(n)

    #Project onto intersections
    Gp = nx.projected_graph(Gp, Gp.intersections)
    
    #Induced subgraph of I
    Gp = I.subgraph(Gp.nodes)

    return Gp
