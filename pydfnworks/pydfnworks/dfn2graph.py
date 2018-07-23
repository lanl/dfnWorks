import networkx as nx
import numpy as np
import json

from networkx.algorithms.flow.shortestaugmentingpath import *
from networkx.algorithms.flow.edmondskarp import *
from networkx.algorithms.flow.preflowpush import *
from networkx.readwrite import json_graph
import matplotlib.pylab as plt
from itertools import islice

def create_graph(self, graph_type, inflow, outflow):
#def create_graph(graph_type, inflow, outflow):

    if graph_type == "fracture":
        G = create_graph_fracture(inflow, outflow)
    elif graph_type == "intersection":
        G = create_graph_intersection(inflow, outflow)
    elif graph_type == "bipartite":
        G = create_graph_bipartite(inflow, outflow)
    else:
        print("ERROR! Unknown graph type")
        return [] 
    return G

def create_graph_fracture(inflow, outflow, topology_file = "connectivity.dat"):
    ''' Create a graph based on topology of network. Fractures 
    are represented as nodes and if two fractures intersect 
    there is an edge between them in the graph. 
    
    Source and Target node are added to the graph. 
    
    Inputs: 
    inflow: name of inflow boundary 
        (connect to source)
    outflow: name of outflow boundary 
        (connect to target)
    topology_file: default=connectivity.dat  
    Output: G (NetworkX Graph)
    ''' 
    print("Loading Graph based on topology in "+topology_file)
    G = nx.Graph(representation="fracture")
    with open(topology_file, "r") as infile:
        for i,line in enumerate(infile):
            conn = [int(n) for n in line.split()]
            for j in conn:
                G.add_edge(i,j-1) 
    ## Create Source and Target and add edges
    inflow_filename = inflow + ".dat"
    outflow_filename = outflow + ".dat"
    inflow = np.genfromtxt(inflow_filename) - 1
    outflow = np.genfromtxt(outflow_filename) - 1
    inflow = list(inflow)
    outflow = list(outflow)
    G.add_node('s')
    G.add_node('t')
    G.add_edges_from(zip(['s']*(len(inflow)),inflow))
    G.add_edges_from(zip(outflow,['t']*(len(outflow))))    
    print("Graph loaded")
    return G

def boundary_index(bc):
    ''' determines boundary index in intersections_list.dat from name

    input : bc name
    output : bc index

    top = -1
    bottom = -2
    left = -3
    front = -4
    right = -5
    back = -6
    ''' 
    if bc == 'top':
        return -1
    elif bc == 'bottom':
        return -2
    elif bc == 'left':
        return -3
    elif bc == 'front':
        return -4
    elif bc == 'right':
        return -5
    elif bc == 'back':
        return -6
    else:
        sys.exit("unknown boundary condition: %s\nExiting"%bc)

def create_graph_intersection(inflow, outflow, intersection_file="intersection_list.dat"):
    ''' Create a graph based on topology of network.
    Edges are represented as nodes and if two intersections
    are on the same fracture, there is an edge between them in the graph. 
    
    Source and Target node are added to the graph. 
    
    Inputs: intersection_file: File containing intersection information
    --> File Format
    fracture 1, fracture 2, x center, y center, z center, intersection length

    Output: G (NetworkX Graph)
    ''' 

    print("Creating Graph Based on DFN")
    print("Intersections being mapped to nodes and Fractures to Edges")
    inflow_index=boundary_index(inflow)
    outflow_index=boundary_index(outflow)

    f=open(intersection_file)
    f.readline()
    frac_edges = []
    for line in f:
        frac_edges.append(line.rstrip().split())
    f.close()

    # Tag mapping
    G = nx.Graph(representation="intersection")
    remove_list=[]

    # each edge in the DFN is a node in the graph
    for i in range(len(frac_edges)):
        f1 = int(frac_edges[i][0]) - 1
        keep=True
        if frac_edges[i][1] is 's' or frac_edges[i][1] is 't':
            f2 = frac_edges[i][1]
        elif int(frac_edges[i][1]) > 0:
            f2 = int(frac_edges[i][1]) - 1  
        elif int(frac_edges[i][1]) == inflow_index:
            f2 = 's'
        elif int(frac_edges[i][1]) == outflow_index:
            f2 = 't'
        elif int(frac_edges[i][1]) < 0:
            keep=False

        if keep: 
            # note fractures of the intersection 
            G.add_node(i,frac=(f1,f2))
            # keep intersection location and length
            G.node[i]['x'] = float(frac_edges[i][2])
            G.node[i]['y'] = float(frac_edges[i][3])
            G.node[i]['z'] = float(frac_edges[i][4])
            G.node[i]['length'] = float(frac_edges[i][5])
    
    nodes = list(nx.nodes(G))    
    f1 = nx.get_node_attributes(G,'frac') 
    # identify which edges are on whcih fractures
    for i in nodes:
        e = set(f1[i])
        for j in nodes:
            if i != j:
                tmp = set(f1[j])
                x = e.intersection(tmp)
                if len(x) > 0:
                    x = list(x)[0]
                    # Check for Boundary Intersections
                    # This stops boundary fractures from being incorrectly
                    # connected 
                    # If not, add edge between
                    if x != 's' and x != 't':
                        xi = G.node[i]['x']
                        yi = G.node[i]['y']
                        zi = G.node[i]['z']

                        xj = G.node[j]['x']
                        yj = G.node[j]['y']
                        zj = G.node[j]['z']
            
                        distance = np.sqrt((xi-xj)**2 + (yi-yj)**2 + (zi-zj)**2)
                        G.add_edge(i,j,frac = x, length = distance)

    # Add Sink and Source nodes
    G.add_node('s')
    G.add_node('t')

    for i in nodes:
        e = set(f1[i])
        if len(e.intersection(set('s'))) > 0 or len(e.intersection(set([-1]))) > 0:
            G.add_edge(i,'s',frac='s', length=0.0)
        if len(e.intersection(set('t'))) > 0 or len(e.intersection(set([-2]))) > 0:
            G.add_edge(i,'t',frac='t', length=0.0)     
    print("Graph Construction Complete")
    return G

def create_graph_bipartite(inflow, outflow):
    print("Not supported yet, returning empty graph")
    return nx.Graph()

def k_shortest_paths(G, k, source, target, weight):
    return list(islice(nx.shortest_simple_paths(G, source, target, weight=weight), k))

def k_shortest_paths_backbone(self, G, k, source='s', target='t', weight=None):
    print("\n--> Determining %d shortest paths in the network"%k)
    H = G.copy()
    k_shortest= set([])
    for path in k_shortest_paths(G, k, source, target, weight):
        k_shortest |= set(path)
    path_nodes = sorted(list(k_shortest))
    nodes = list(G.nodes())
    secondary = list(set(nodes) - set(path_nodes)) 
    for n in secondary:
        H.remove_node(n)
    return H
    print("--> Complete\n")

def pull_source_and_target(nodes,source='s',target='t'):
    for node in [source, target]:
        try:
           nodes.remove(node)
        except:
            pass 
    return nodes 

def dump_fractures(self, G, filename):
    '''Write fracture numbers assocaited with the graph G out into an ASCII file
    inputs 
    G: networkX graph
    filename: output filename 
    outputs
    none
    '''
     
    if G.graph['representation'] == "fracture":
        nodes = list(G.nodes())
    elif G.graph['representation'] == "intersection":
        nodes = []
        for u,v,d in G.edges(data=True):
            nodes.append(G[u][v]['frac'])
        nodes = list(set(nodes))
    nodes = pull_source_and_target(nodes) 
    fractures = [int(i) + 1 for i in nodes] 
    fractures = sorted(fractures)
    print("--> Dumping %s"%filename)
    np.savetxt(filename, fractures, fmt = "%d")

def greedy_edge_disjoint(self, G, source='s', target='t', weight='None'):
    '''
    Greedy Algorithm to find edge disjoint subgraph from s to t. 
    See Hyman et al. 2018 SIAM MMS

    Inputs: 
    networkX Graph G
    source: source nodes
    target: target nodes
    weight: edge weight
    Output: Subgraph composed of edge-disjoint paths
    '''
    print("--> Identifying edge disjoint paths")
    if G.graph['representation'] == "fracture":
        print("--> ERROR!!! Wrong type of DFN graph represenation\nRepresentation must be intersection\nReturning Empty Graph\n")
        return nx.Graph()
    Gprime = G.copy()
    Hprime = nx.Graph()
    Hprime.graph['representation'] = G.graph['representation']
    while nx.has_path(Gprime, source, target):
        path = nx.shortest_path(Gprime, source, target, weight=weight)
        H = Gprime.subgraph(path)
        Hprime.add_edges_from(H.edges(data=True))
        for u,v,d in H.edges(data = True):
            Gprime.remove_edge(u,v)
    print("--> Complete")
    return Hprime

def plot_graph(G, source='s', target='t',output_name="dfn_graph"):
    ''' Create a png of a graph with source nodes colored blue, target red, and all over nodes black
    
    Inputs: 
    G: networkX graph
    source: source nodes
    target: target nodes
    output_name: name of output file (no .png)
    ''' 
    print("\n--> Plotting Graph")
    print("--> Output file: %s.png"%output_name)
    # get positions for all nodes
    pos=nx.spring_layout(G)
    nodes=list(G.nodes)
    # draw nodes
    nx.draw_networkx_nodes(G,pos,
                           nodelist=nodes,
                           node_color='k',
                           node_size=10,
                       alpha=1.0)
    nx.draw_networkx_nodes(G,pos,
                           nodelist=[source],
                           node_color='b',
                           node_size=10,
                       alpha=1.0)
    nx.draw_networkx_nodes(G,pos,
                           nodelist=[target],
                           node_color='r',
                           node_size=10,
                       alpha=1.0)
    
    nx.draw_networkx_edges(G,pos,width=1.0,alpha=0.5)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_name+".png")
    plt.clf()
    print("--> Plotting Graph Complete") 

def dump_json_graph(self, G, name):
    print("Dumping Graph into file: "+name+".json")
    jsondata = json_graph.node_link_data(G)
    with open(name+'.json', 'w') as fp:
        json.dump(jsondata, fp)
    print("Complete")

def load_json_graph(self,name):
    print("Loading Graph in file: "+name+".json")
    fp = open(name+'.json')
    G = json_graph.node_link_graph(json.load(fp))
    print("Complete")
    return G

def add_perm(self,G):
    ''' Add fracture permeability to Graph. If Graph represenation is
    fracture, then permeability is a node attribute. If graph represenation 
    is intersection, then permeability is an edge attribute '''

    perm = np.genfromtxt('fracture_info.dat', skip_header =1)[:,1]
    if G.graph['representation'] == "fracture":
        nodes = list(nx.nodes(G))
        for n in nodes:
            if n != 's' and n != 't':
                G.node[n]['perm'] = perm[n]
                G.node[n]['iperm'] = 1.0/perm[n]
            else:
                G.node[n]['perm'] = 1.0
                G.node[n]['iperm'] = 1.0

    elif G.graph['representation'] == "intersection":
        edges = list(nx.edges(G))
        for u,v in edges:
            x = G[u][v]['frac']
            if x != 's' and x != 't':
                G[u][v]['perm'] = perm[x]
                G[u][v]['iperm'] = 1.0/perm[x]
            else:   
                G[u][v]['perm'] = 1.0
                G[u][v]['iperm'] = 1.0

 


