import networkx as nx
import numpy as np
import json
import sys
import time 
from itertools import combinations

from pydfnworks.dfnGraph.graph_attributes import add_perm, add_area
from pydfnworks.general.logging import local_print_log


def boundary_index(bc_name):
    """Determines boundary index in intersections_list.dat from name

    Parameters
    ----------
        bc_name : string
            Boundary condition name

    Returns
    -------
        bc_index : in
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
        local_print_log(error,'error')
def create_intersection_graph(inflow, outflow, intersection_file="dfnGen_output/intersection_list.dat"):
    total_start = time.time()
    local_print_log("--> Creating Graph Based on DFN")

    # 1) Load & filter intersections
    load_start = time.time()
    local_print_log("--> Reading intersection file")
    inflow_index = boundary_index(inflow)
    outflow_index = boundary_index(outflow)

    G = nx.Graph(representation="intersection")
    frac_intersections = np.genfromtxt(intersection_file, skip_header=1)

    internal_int = np.where(frac_intersections[:, 1] > 0)
    source_int   = np.where(frac_intersections[:, 1] == inflow_index)
    target_int   = np.where(frac_intersections[:, 1] == outflow_index)
    edges_to_keep = list(internal_int[0]) + list(source_int[0]) + list(target_int[0])
    frac_intersections = frac_intersections[edges_to_keep, :]

    load_end = time.time()
    local_print_log(f"--> Loaded & filtered intersections in {load_end - load_start:.3f} s")

    # 2) Build fracture→node map & add nodes
    nodes_start = time.time()
    max_frac = int(max(frac_intersections[:,0].max(), frac_intersections[:,1].max()))
    frac_list = list(range(1, max_frac+1)) + ['s', 't']
    fracture_node_dict = {f: [] for f in frac_list}

    local_print_log(f"--> There are {max_frac} fractures")
    local_print_log("--> Adding nodes to graph")

    G.add_node('s', frac=('s','s'))
    G.add_node('t', frac=('t','t'))

    for idx, row in enumerate(frac_intersections):
        f1 = int(row[0])
        b = int(row[1])
        f2 = 's' if b == inflow_index else ('t' if b == outflow_index else int(b))

        # add node attributes
        G.add_node(idx, frac=(f1, f2))
        G.nodes[idx]['x']      = float(row[2])
        G.nodes[idx]['y']      = float(row[3])
        G.nodes[idx]['z']      = float(row[4])
        G.nodes[idx]['length'] = float(row[5])

        # register in fracture map
        fracture_node_dict[f1].append(idx)
        fracture_node_dict[f2].append(idx)

        # connect to s/t if needed
        if f2 == 's':
            G.add_edge(idx, 's', frac='s', length=0.0, perm=1, iperm=1)
        if f2 == 't':
            G.add_edge(idx, 't', frac='t', length=0.0, perm=1, iperm=1)

    nodes_end = time.time()
    local_print_log(f"--> Added {len(G.nodes())} nodes in {nodes_end - nodes_start:.3f} s")

    # 3) Add internal edges by fracture
    edges_start = time.time()
    local_print_log("--> Adding internal edges to graph")

    for frac, nodes_on_frac in fracture_node_dict.items():
        if frac in ('s','t'):
            continue
        for u, v in combinations(nodes_on_frac, 2):
            dx = G.nodes[u]['x'] - G.nodes[v]['x']
            dy = G.nodes[u]['y'] - G.nodes[v]['y']
            dz = G.nodes[u]['z'] - G.nodes[v]['z']
            dist = np.sqrt(dx*dx + dy*dy + dz*dz)
            G.add_edge(u, v, frac=frac, length=dist)

    edges_end = time.time()
    local_print_log(f"--> Added {len(G.edges())} edges in {edges_end - edges_start:.3f} s")

    # 4) Final attribute additions
    perm_start = time.time()
    local_print_log("--> Applying permeability and area attributes")
    add_perm(G)
    add_area(G)
    perm_end = time.time()
    local_print_log(f"--> Applied perm & area in {perm_end - perm_start:.3f} s")

    total_end = time.time()
    local_print_log(f"--> Total graph construction time: {total_end - total_start:.3f} s")
    local_print_log("--> Intersection Graph Construction Complete")

    return G