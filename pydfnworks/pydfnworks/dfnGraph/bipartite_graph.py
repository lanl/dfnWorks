import networkx as nx
import numpy as np
from itertools import islice

from pydfnworks.dfnGraph.intersection_graph import boundary_index


def create_bipartite_graph(
        inflow,
        outflow,
        intersection_list='dfnGen_output/intersection_list.dat',
        fracture_info='dfnGen_output/fracture_info.dat'):
    """Creates a bipartite graph of the DFN.
    Nodes are in two sets, fractures and intersections, with edges connecting them.


    Parameters
    ----------
        inflow : str
            name of inflow boundary
        outflow : str
            name of outflow boundary
        intersection_list: str
             filename of intersections generated from DFN
        fracture_infor : str
                filename for fracture information

    Returns
    -------
        B : NetworkX Graph

    Notes
    -----
    See Hyman et al. 2018 "Identifying Backbones in Three-Dimensional Discrete Fracture Networks: A Bipartite Graph-Based Approach" SIAM Multiscale Modeling and Simulation for more details 
"""

    print("--> Creating Bipartite Graph")

    # generate sequential letter sequence as ids for fractures
    # e..g aaaaa aaaaab aaaaac
    from itertools import product

    def intersection_id_generator(length=5):
        chars = 'abcdefghijklmnopqrstuvwxyz'
        for p in product(chars, repeat=length):
            yield (''.join(p))

    B = nx.Graph(representation="bipartite")
    # keep track of the sets of fractures and intersections
    B.fractures = set()
    B.intersections = set()
    intersection_id = intersection_id_generator()

    inflow_index = boundary_index(inflow)
    outflow_index = boundary_index(outflow)

    with open(intersection_list) as f:
        header = f.readline()
        data = f.read().strip()
        for line in data.split('\n'):
            fracture1, fracture2, x, y, z, length = line.split(' ')
            fracture1 = int(fracture1)
            fracture2 = int(fracture2)
            if fracture2 < 0:
                if fracture2 == inflow_index:
                    fracture2 = 's'
                elif fracture2 == outflow_index:
                    fracture2 = 't'
            intersection = next(intersection_id)
            # add intersection node explicitly to include intersection properties
            B.add_node(intersection,
                       x=float(x),
                       y=float(y),
                       z=float(z),
                       length=float(length))
            B.intersections.add(intersection)

            B.add_edge(intersection, fracture1, frac=fracture1)
            B.fractures.add(fracture1)

            if type(fracture2) == str:
                if fracture2 == 's' or fracture2 == 't':
                    B.add_edge(intersection, fracture2, frac=fracture2)
                    B.fractures.add(fracture2)
            elif type(fracture2) == int:
                if fracture2 > 0:
                    B.add_edge(intersection, fracture2, frac=fracture2)
                    B.fractures.add(fracture2)

    # add  source and sink for intersections so they will appear in intersection projection
    B.add_edge('intersection_s', 's')
    B.add_edge('intersection_t', 't')

    # add fracture info
    with open(fracture_info) as f:
        header = f.readline()
        data = f.read().strip()
        for fracture, line in enumerate(data.split('\n'), 1):
            c, perm, aperture = line.split(' ')
            B.nodes[fracture]['perm'] = float(perm)
            B.nodes[fracture]['aperture'] = float(aperture)

    print("--> Complete")

    return B
