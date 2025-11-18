import networkx as nx
import numpy as np
import json
import sys
import time
from itertools import combinations

from pydfnworks.dfnGraph.graph_attributes import add_perm, add_area
from pydfnworks.general.logging import local_print_log

def boundary_index(bc_name):
    """Determine boundary index in intersections_list.dat from name."""
    bc_dict = {
        "top":    -1,
        "bottom": -2,
        "left":   -3,
        "front":  -4,
        "right":  -5,
        "back":   -6
    }
    try:
        return bc_dict[bc_name]
    except KeyError:
        local_print_log(f"Error. Unknown boundary condition: {bc_name}", 'error')
        sys.exit(1)

def create_intersection_graph(inflow, outflow,
                              intersection_file="dfnGen_output/intersection_list.dat"):
    total_start = time.time()
    local_print_log("--> Starting intersection graph construction")

    # 1) Load & filter intersections
    load_start = time.time()
    inflow_index = boundary_index(inflow)
    outflow_index = boundary_index(outflow)
    frac_intersections = np.genfromtxt(intersection_file, skip_header=1)
    internal_int = np.where(frac_intersections[:, 1] > 0)
    source_int   = np.where(frac_intersections[:, 1] == inflow_index)
    target_int   = np.where(frac_intersections[:, 1] == outflow_index)
    edges_to_keep = list(internal_int[0]) + list(source_int[0]) + list(target_int[0])
    frac_intersections = frac_intersections[edges_to_keep, :]
    load_end = time.time()
    local_print_log(f"--> Loaded & filtered intersections in {load_end - load_start:.3f} s")

    # 2) Build fracture → node map
    map_start = time.time()
    max_frac_index = int(max(frac_intersections[:, 0].max(),
                              frac_intersections[:, 1].max()))
    frac_list = [i for i in range(1, max_frac_index + 1)] + ['s', 't']
    fracture_node_dict = dict(zip(frac_list, ([] for _ in frac_list)))
    map_end = time.time()
    local_print_log(f"--> Built fracture→node map in {map_end - map_start:.3f} s")

    # 3) Add nodes and source/target
    nodes_start = time.time()
    G = nx.Graph(representation="intersection")
    G.add_node('s', frac=('s', 's'))
    G.add_node('t', frac=('t', 't'))

    num_nodes = len(frac_intersections)
    for i in range(num_nodes):
        f1 = int(frac_intersections[i][0])
        raw2 = frac_intersections[i][1]
        if raw2 > 0:
            f2 = int(raw2)
        elif int(raw2) == inflow_index:
            f2 = 's'
        elif int(raw2) == outflow_index:
            f2 = 't'
        else:
            continue

        G.add_node(i, frac=(f1, f2))
        G.nodes[i]['x']      = float(frac_intersections[i][2])
        G.nodes[i]['y']      = float(frac_intersections[i][3])
        G.nodes[i]['z']      = float(frac_intersections[i][4])
        G.nodes[i]['length'] = float(frac_intersections[i][5])

        fracture_node_dict[f1].append(i)
        fracture_node_dict[f2].append(i)

        if f2 == 's':
            G.add_edge(i, 's', frac='s', length=0.0, perm=1, iperm=1)
        if f2 == 't':
            G.add_edge(i, 't', frac='t', length=0.0, perm=1, iperm=1)
    nodes_end = time.time()
    local_print_log(f"--> Added nodes and source/target edges in {nodes_end - nodes_start:.3f} s")

    # 4) Add internal edges
    edges_start = time.time()
    for frac, nodes_on_frac in fracture_node_dict.items():
        if frac in ('s', 't'):
            continue
        for u, v in combinations(set(nodes_on_frac), 2):
            dx = G.nodes[u]['x'] - G.nodes[v]['x']
            dy = G.nodes[u]['y'] - G.nodes[v]['y']
            dz = G.nodes[u]['z'] - G.nodes[v]['z']
            distance = np.sqrt(dx*dx + dy*dy + dz*dz)
            G.add_edge(u, v, frac=frac, length=distance)
    edges_end = time.time()
    local_print_log(f"--> Added internal edges in {edges_end - edges_start:.3f} s")

    # 5) Apply permeability and area
    perm_start = time.time()
    add_perm(G)
    add_area(G)
    perm_end = time.time()
    local_print_log(f"--> Applied perm & area in {perm_end - perm_start:.3f} s")

    # Total time
    total_end = time.time()
    local_print_log(f"--> Total graph construction time: {total_end - total_start:.3f} s")
    local_print_log("--> Intersection Graph Construction Complete")
    return G
