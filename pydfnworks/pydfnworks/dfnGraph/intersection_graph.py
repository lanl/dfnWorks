from tkinter import W
import networkx as nx
import numpy as np
import json
import sys
from itertools import combinations

from pydfnworks.dfnGraph.graph_attributes import add_perm


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
        sys.stderr.write(error)
        sys.exit(1)


def create_intersection_graph(inflow,
                              outflow,
                              intersection_file="intersection_list.dat",
                              fracture_info="fracture_info.dat"):
    """ Create a graph based on topology of network.
    Edges are represented as nodes and if two intersections
    are on the same fracture, there is an edge between them in the graph. 
    
    Source and Target node are added to the graph. 
   
    Parameters
    ----------
        inflow : string
            Name of inflow boundary
        outflow : string
            Name of outflow boundary
        intersection_file : string
             File containing intersection information
             File Format:
             fracture 1, fracture 2, x center, y center, z center, intersection length
        fracture_info : str
                filename for fracture information
    Returns
    -------
        G : NetworkX Graph
            Vertices have attributes x,y,z location and length. Edges has attribute length

    Notes
    -----
    Aperture and Perm on edges can be added using add_app and add_perm functions
    """

    print("--> Creating Graph Based on DFN")
    print("--> Intersections being mapped to nodes and fractures to edges")
    inflow_index = boundary_index(inflow)
    outflow_index = boundary_index(outflow)

    G = nx.Graph(representation="intersection")
    # Load edges from intersection file
    frac_intersections = np.genfromtxt(intersection_file, skip_header=1)
    # Grab indices of internal edges
    internal_int = np.where(frac_intersections[:, 1] > 0)
    # Grab indices of source edges
    source_int = np.where(frac_intersections[:, 1] == inflow_index)
    # Grab indices of target edges
    target_int = np.where(frac_intersections[:, 1] == outflow_index)
    # combine those indices from waht to keep
    edges_to_keep = list(internal_int[0]) + list(source_int[0]) + list(
        target_int[0])
    # keep only the edges we care about
    frac_intersections = frac_intersections[edges_to_keep, :]

    max_frac_index = max(max(frac_intersections[:, 0]),
                         max(frac_intersections[:, 1])).astype(int)
    frac_list = [i for i in range(1, max_frac_index + 1)]
    frac_list.append('s')
    frac_list.append('t')
    fracture_node_dict = dict(zip(frac_list, ([] for _ in frac_list)))
    print(f"--> There are {max_frac_index} fractures")
    num_edges = len(edges_to_keep)
    print("--> Adding Nodes to Graph")
    # Add Sink and Source nodes
    G.add_node('s', frac=('s', 's'))
    G.add_node('t', frac=('t', 't'))

    for i in range(num_edges):

        frac_1 = int(frac_intersections[i][0])

        if frac_intersections[i][1] > 0:
            frac_2 = int(frac_intersections[i][1])
        elif int(frac_intersections[i][1]) == inflow_index:
            frac_2 = 's'
        elif int(frac_intersections[i][1]) == outflow_index:
            frac_2 = 't'
        # note fractures of the intersection
        G.add_node(i, frac=(frac_1, frac_2))
        # keep intersection location and length
        G.nodes[i]['x'] = float(frac_intersections[i][2])
        G.nodes[i]['y'] = float(frac_intersections[i][3])
        G.nodes[i]['z'] = float(frac_intersections[i][4])
        G.nodes[i]['length'] = float(frac_intersections[i][5])

        fracture_node_dict[frac_1].append(i)
        fracture_node_dict[frac_2].append(i)

        if frac_2 == 's':
            G.add_edge(i, 's', frac='s', length=0.0, perm=1, iperm=1)
        if frac_2 == 't':
            G.add_edge(i, 't', frac='t', length=0.0, perm=1, iperm=1)

    print("--> Adding Nodes to Graph Complete")

    print("--> Adding edges to Graph: Starting")
    # nodes = list(nx.nodes(G))
    # fractures = nx.get_node_attributes(G, 'frac')
    # nodes.remove('s')
    # nodes.remove('t')
    # # identify which edges are on which fractures
    # for i in nodes:
    #     # get the fractures the node is on.
    #     node_1_fracs = fractures[i]
    #     # if the node is on the source / target, add an edge
    #     if 's' in node_1_fracs:
    #         G.add_edge(i, 's', frac='s', length = 0.0, perm = 1, iperm = 1)
    #     if 't' in node_1_fracs:
    #         G.add_edge(i, 't', frac='t', length = 0.0, perm = 1, iperm = 1)

    #     for j in nodes[i+1:]:
    #         # walk through the other nodes and find matching intersecitons
    #         frac_int = list(set(node_1_fracs).intersection(set(fractures[j])))
    #         # Check if the intersection is empty
    #         if 's' in frac_int:
    #             frac_int.remove('s')
    #         if 't' in frac_int:
    #             frac_int.remove('t')

    #         if len(frac_int) > 0:
    #             distance = np.sqrt(
    #                     (G.nodes[i]['x'] - G.nodes[j]['x'])**2 +
    #                     (G.nodes[i]['y'] - G.nodes[j]['y'])**2 +
    #                     (G.nodes[i]['z'] - G.nodes[j]['z'])**2 )
    #             G.add_edge(i, j, frac = frac_int[0], length = distance)

    frac_list.remove('s')
    frac_list.remove('t')

    for frac in frac_list:
        nodes = list(set(fracture_node_dict[frac]))
        res = list(combinations(nodes, 2))
        for u, v in res:
            distance = np.sqrt((G.nodes[u]['x'] - G.nodes[v]['x'])**2 +
                               (G.nodes[u]['y'] - G.nodes[v]['y'])**2 +
                               (G.nodes[u]['z'] - G.nodes[v]['z'])**2)
            G.add_edge(u, v, frac=frac, length=distance)

    print("--> Adding edges to Graph: Complete")
    add_perm(G, fracture_info)
    print("--> Intersection Graph Construction Complete")
    return G
