import networkx as nx
import numpy as np
import sys
import time
from itertools import combinations

from pydfnworks.dfnGraph.graph_attributes import add_perm, add_area
from pydfnworks.general.logging import local_print_log

def boundary_index(bc_name):
    """Map a boundary name to its index in intersection_list.dat."""
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

def parse_boundary_inputs(inputs):
    """
    Convert inflow/outflow inputs into a list of integer codes.
    Accepts single int, numeric string, boundary name, or list/tuple thereof.
    """
    if not isinstance(inputs, (list, tuple)):
        items = [inputs]
    else:
        items = list(inputs)
    codes = []
    for item in items:
        if isinstance(item, str) and not item.isdigit():
            codes.append(boundary_index(item))
        else:
            codes.append(int(item))
    return codes

def create_intersection_graph(inflow_codes, outflow_codes,
                              intersection_file="dfnGen_output/intersection_list.dat"):
    """
    1) Build full graph with all rows (positive & negative).
    2) For any negative frac matching inflow/outflow, replace with 's'/'t'.
    3) Remove nodes with negative frac not replaced.
    4) Add 's' and 't' nodes and connect edges accordingly.
    """
    t_start = time.time()
    local_print_log("--> Starting full-graph construction")

    # Parse inflow/outflow codes
    inflow_list = parse_boundary_inputs(inflow_codes)
    outflow_list = parse_boundary_inputs(outflow_codes)
    local_print_log(f"--> Inflow codes: {inflow_list}, Outflow codes: {outflow_list}")

    # Load all intersections
    raw = np.genfromtxt(intersection_file, skip_header=1)
    first = raw[:, 0].astype(int)
    second = raw[:, 1].astype(int)

    # Build graph with every row as a node
    G = nx.Graph(representation="intersection")
    max_frac = int(max(abs(first).max(), abs(second).max()))
    frac_map = {i: [] for i in range(1, max_frac+1)}

    for idx, row in enumerate(raw):
        f1_orig, f2_orig = int(row[0]), int(row[1])
        # replace negative codes if they match inflow/outflow
        if f1_orig < 0 and f1_orig in inflow_list:
            f1 = 's'
        elif f1_orig < 0 and f1_orig in outflow_list:
            f1 = 't'
        else:
            f1 = f1_orig
        if f2_orig < 0 and f2_orig in inflow_list:
            f2 = 's'
        elif f2_orig < 0 and f2_orig in outflow_list:
            f2 = 't'
        else:
            f2 = f2_orig

        x, y, z, length = map(float, row[2:6])
        G.add_node(idx, frac=(f1, f2), x=x, y=y, z=z, length=length)

        # register in frac_map only if positive integer fracture
        if isinstance(f1, int) and f1 > 0:
            frac_map[f1].append(idx)
        if isinstance(f2, int) and f2 > 0:
            frac_map[f2].append(idx)
    t_nodes = time.time()
    local_print_log(f"--> Added {len(G.nodes())} nodes (with replaced frac) in {t_nodes - t_start:.3f}s")

    # Add internal edges along positive fractures
    for frac, nodes in frac_map.items():
        for u, v in combinations(nodes, 2):
            dx = G.nodes[u]['x'] - G.nodes[v]['x']
            dy = G.nodes[u]['y'] - G.nodes[v]['y']
            dz = G.nodes[u]['z'] - G.nodes[v]['z']
            dist = np.sqrt(dx*dx + dy*dy + dz*dz)
            G.add_edge(u, v, frac=frac, length=dist)
    t_edges = time.time()
    local_print_log(f"--> Added internal edges in {t_edges - t_nodes:.3f}s")

    # Prune nodes with negative frac not replaced (still negative)
    to_remove = []
    for n, data in list(G.nodes(data=True)):
        f1, f2 = data['frac']
        if (isinstance(f1, int) and f1 < 0) or (isinstance(f2, int) and f2 < 0):
            to_remove.append(n)
    G.remove_nodes_from(to_remove)
    t_prune = time.time()
    local_print_log(f"--> Removed {len(to_remove)} nodes with unwanted negatives in {t_prune - t_edges:.3f}s")

    # Add source and target nodes
    G.add_node('s', frac=('s','s'))
    G.add_node('t', frac=('t','t'))

    # Connect edges to 's' and 't'
    for n, data in G.nodes(data=True):
        if n in ('s', 't'):
            continue
        f1, f2 = data['frac']
        # connect if either frac matches inflow/outflow or is 's'/'t'
        if f1 == 's' or f2 == 's' or (isinstance(f1, int) and f1 in inflow_list) or (isinstance(f2, int) and f2 in inflow_list):
            G.add_edge(n, 's', frac='s', length=0.0, perm=1, iperm=1)
        if f1 == 't' or f2 == 't' or (isinstance(f1, int) and f1 in outflow_list) or (isinstance(f2, int) and f2 in outflow_list):
            G.add_edge(n, 't', frac='t', length=0.0, perm=1, iperm=1)
    t_connect = time.time()
    local_print_log(f"--> Connected source/target in {t_connect - t_prune:.3f}s")

    # Final perm & area attributes
    add_perm(G)
    add_area(G)
    
    # ————————————————————————————————————————————————
    # Relabel internal nodes 1…N while keeping 's' and 't' as-is
    internal = [n for n in G.nodes() if n not in ('s','t')]
    # sort if you care about order (e.g. by original label or x‐coordinate)
    # internal.sort(key=lambda n: (isinstance(n, int), n))
    mapping = {old: new for new, old in enumerate(internal, start=1)}
    # nodes not in mapping (i.e. 's' and 't') will remain unchanged
    G = nx.relabel_nodes(G, mapping)
    total = time.time() - t_start
    local_print_log(f"--> Total create_intersection_graph time: {total:.3f}s")

    return G
