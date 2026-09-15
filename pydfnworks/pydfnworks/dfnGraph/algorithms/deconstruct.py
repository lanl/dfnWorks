"""
.. module:: deconstruct.py
   :synopsis: Simplify an intersection graph by removing crossing (redundant)
              edges on each fracture -- the "deconstructed intersection graph"
              of Doolaeghe et al. (2021), Section 4.
"""

import math

import networkx as nx

from pydfnworks.general.logging import local_print_log


def _plane_basis(n):
    """Two orthonormal in-plane vectors for a fracture normal n."""
    nx_, ny_, nz_ = float(n[0]), float(n[1]), float(n[2])
    norm = math.sqrt(nx_ * nx_ + ny_ * ny_ + nz_ * nz_)
    if norm == 0:
        return (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)
    nx_, ny_, nz_ = nx_ / norm, ny_ / norm, nz_ / norm
    # reference axis least aligned with n, to avoid a degenerate cross product
    if abs(nx_) <= abs(ny_) and abs(nx_) <= abs(nz_):
        a = (1.0, 0.0, 0.0)
    elif abs(ny_) <= abs(nz_):
        a = (0.0, 1.0, 0.0)
    else:
        a = (0.0, 0.0, 1.0)
    e1 = (ny_ * a[2] - nz_ * a[1],
          nz_ * a[0] - nx_ * a[2],
          nx_ * a[1] - ny_ * a[0])
    m = math.sqrt(e1[0] ** 2 + e1[1] ** 2 + e1[2] ** 2) or 1.0
    e1 = (e1[0] / m, e1[1] / m, e1[2] / m)
    e2 = (ny_ * e1[2] - nz_ * e1[1],
          nz_ * e1[0] - nx_ * e1[2],
          nx_ * e1[1] - ny_ * e1[0])
    return e1, e2


def _proj(p, e1, e2):
    return (p[0] * e1[0] + p[1] * e1[1] + p[2] * e1[2],
            p[0] * e2[0] + p[1] * e2[1] + p[2] * e2[2])


def _proper_cross(a, b, c, d):
    """True if 2D segments ab and cd properly cross (strict interior crossing)."""
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1 = orient(a, b, c)
    o2 = orient(a, b, d)
    o3 = orient(c, d, a)
    o4 = orient(c, d, b)
    return (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)


def deconstruct_intersection_graph(G, normal_vectors):
    """Remove crossing (redundant) edges on each fracture, keeping the higher-
    conductance edge of each crossing pair (Doolaeghe et al. 2021, Sec 4).

    Operates in place on an intersection graph whose nodes carry 'x','y','z' and
    whose edges carry 'frac' and 'weight'. Edge pairs sharing a node are never
    treated as crossing (they meet at a vertex). Source/target edges (frac
    's'/'t') are ignored.

    Parameters
    ----------
        G : NetworkX Graph
            intersection graph (must already have edge 'weight')

        normal_vectors : array-like
            per-fracture unit normals, indexed by fracture number - 1

    Returns
    -------
        None

    Notes
    -----
        O(m^2) in the number of edges m on a fracture, so slow for fractures with
        very many intersections -- the authors note the same limitation.
    """
    frac_edges = {}
    for u, v, d in G.edges(data=True):
        f = d.get('frac')
        if isinstance(f, int):
            frac_edges.setdefault(f, []).append((u, v))

    removed = set()
    # live per-node degree (across the whole graph) so we never remove a node's
    # last edge and isolate it -- which would make the flow Laplacian singular.
    deg = dict(G.degree())
    for f, elist in frac_edges.items():
        if len(elist) < 2:
            continue
        e1, e2 = _plane_basis(normal_vectors[f - 1])
        seg = {}
        for (u, v) in elist:
            pu = _proj((G.nodes[u]['x'], G.nodes[u]['y'], G.nodes[u]['z']), e1, e2)
            pv = _proj((G.nodes[v]['x'], G.nodes[v]['y'], G.nodes[v]['z']), e1, e2)
            seg[(u, v)] = (pu, pv)
        m = len(elist)
        for i in range(m):
            ea = elist[i]
            if ea in removed:
                continue
            for j in range(i + 1, m):
                eb = elist[j]
                if eb in removed:
                    continue
                if set(ea) & set(eb):  # share an intersection node
                    continue
                a, b = seg[ea]
                c, d = seg[eb]
                if _proper_cross(a, b, c, d):
                    wa = G.edges[ea[0], ea[1]].get('weight', 0.0)
                    wb = G.edges[eb[0], eb[1]].get('weight', 0.0)
                    loser = ea if wa < wb else eb
                    x, y = loser
                    # keep the crossing if removing the loser would isolate a node
                    if deg[x] <= 1 or deg[y] <= 1:
                        continue
                    removed.add(loser)
                    deg[x] -= 1
                    deg[y] -= 1
                    if loser == ea:
                        break  # ea gone; advance to the next edge

    for (u, v) in removed:
        if G.has_edge(u, v):
            G.remove_edge(u, v)
    isolated = [n for n in G.nodes() if G.degree(n) == 0]
    if isolated:
        local_print_log(
            f"--> Warning: deconstruction left {len(isolated)} isolated node(s).",
            'warning')
    local_print_log(
        f"--> Deconstructed intersection graph: removed {len(removed)} "
        "crossing edges")
    return
