import networkx as nx
import numpy as np

def intersection_id_generator(length=5):
    from itertools import product
    chars = 'abcdefghijklmnopqrstuvwxyz'
    for p in product(chars, repeat=length):
        yield (''.join(p))

def intersection_to_fracture(G, inflow, outflow):
    """ Convert an intersection graph representation of a DFN
    to a fracture graph representation by embedding into a larger
    bipartite graph representation, then projecting onto the
    fracture nodes.

   
    Parameters
    ----------
        G: NetworkX Graph
            Intersection graph, where nodes correspond to fracture intersections.
        
        inflow: str
            Name of inflow boundary
        
        outflow: str
            Name of outflow boundary

    Returns
    -------
        Gp: NetworkX Graph
            Fracture graph corresponding to G.

    Notes
    -----
    See 'fracture_graph.py', 'intersection_graph.py', and 'bipartite_graph.py' for further details on graph representations.
    """
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

def fracture_to_intersection(G, inflow, outflow):
    """ Convert an intersection graph representation of a DFN
    to a fracture graph representation by embedding into a larger
    bipartite graph representation, then projecting onto the
    intersection nodes.

   
    Parameters
    ----------
        G: NetworkX Graph
            Fracture graph, where nodes correspond to fractures.
        
        inflow: str
            Name of inflow boundary
        
        outflow: str
            Name of outflow boundary

    Returns
    -------
        Gp: NetworkX Graph
            Intersection graph corresponding to G.

    Notes
    -----
    See 'fracture_graph.py', 'intersection_graph.py', and 'bipartite_graph.py' for further details on graph representations.
    """
    
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

def convert_graph(G, inflow, outflow, output):
    """ Driver function subsuming fracture_to_intersection() and
    intersection_to_fracture() into a single function that converts 
    between fracture and intersection DFN graph representations.

    Parameters
    ----------
         G: NetworkX Graph
            Either a fracture graph, where nodes correspond to fractures,
            or an intersection graph, where nodes correspond to fracture
            intersections.
        
        inflow: str
            Name of inflow boundary
        
        outflow: str
            Name of outflow boundary
        
        output: str
            Output type of the graph conversion. 
            Accepted values include "fracture", "frac", or "f" to call
            intersection_to_fracture(), and "intersection", "inter", or "i"
            to call fracture_to_intersection().

    Returns
    -------
        Gp: NetworkX Graph
           Converted graph. Either an intersection graph if G is a fracture
           graph or a fracture graph if G is an intersection graph.

    Notes
    -----
    See 'fracture_graph.py', 'intersection_graph.py', and 'bipartite_graph.py' for further details on graph representations.
    """
    if(output=='fracture' or output=='frac' or output=='f'):
        Gp = intersection_to_fracture(G, inflow, outflow)

    elif(output=='intersection' or output=='inter' or output=='i'):
        Gp = fracture_to_intersection(G, inflow, outflow)

    else:
        exit('Invalid output option \''+str(output)+'\' for function convert_graph. See docstring for list of valid options.')

    return Gp
