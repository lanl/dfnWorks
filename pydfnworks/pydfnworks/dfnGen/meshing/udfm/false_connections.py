"""
.. module:: false_connections.py
   :synopsis: Checks for false connections between fractures in upscaled mesh
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import pickle
import os


def check_false_connections(self, path="../"):
    """ 

    Parameters
    ----------
        self : object
            DFN Class
        fmc_filname : string
            name of the pickled dictionary of mesh and fracture intersections 

    Returns
    -------
        num_false_connections : int
            number of false connections
        num_cell_false : int
            number of Voronoi cells with false connections
        false_connections : list
            list of tuples of false connections created by upscaling

    Notes
    -----
        map2continuum and upscale must be run first to create the fracture/mesh intersection
        dictionary. Thus must be run in the main job directory which contains connectivity.dat


    """
    print("--> Checking for false connections in the upscaled mesh.")
    # Create symbolic links to create fracture graph
    files = ["connectivity.dat", "left.dat", "right.dat", "fracture_info.dat"]
    for f in files:
        try:
            os.symlink(path + f, f)
        except:
            print(f"--> Warning!!! Unable to make symbolic link to {path+f}")
            pass

    # create fracture graph, with arbitrary source/target
    G = self.create_graph("fracture", "left", "right")
    # remove source and target
    G.remove_node("s")
    G.remove_node("t")

    # Make a copy of G and remove all edges
    H = G.copy()
    for u, v in H.edges():
        H.remove_edge(u, v)

    # load the fracture_mesh_connection dictionary
    print("--> Loading mesh intersection information")
    fmc = pickle.load(open("connections.p", "rb"))
    print("--> Complete")
    # Get cell ids for the cells that fractures intersect
    cells = [key for key in fmc.keys()]

    # walk through the cells and add edges to graph H
    # if two fractures are in the same cell
    cell_false = [False] * len(cells)
    for i, cell in enumerate(cells):
        num_conn = len(fmc[cell])
        # If more than one fracture intersects the mesh cell
        # add edges
        if num_conn > 1:
            # add edges between all fractures in a cell
            for j in range(num_conn):
                id1 = fmc[cell][j][0]
                for k in range(j + 1, num_conn):
                    id2 = fmc[cell][k][0]
                    H.add_edge(id1, id2)
                    cell_false[i] = True

    ## check for false connections
    print("--> Checking for false connections")
    false_connections = []
    for u, v, in H.edges():
        if not G.has_edge(u, v):
            print(f"--> False connection between fractures {u} and {v}")
            false_connections.append((u, v))

    if len(false_connections) > 0:
        num_false_connections = len(false_connections)
        print(
            f"--> There are {num_false_connections} false connections between fractures"
        )
        num_false_cells = sum(cell_false)
        print(f"--> These occur in {num_false_cells} Voronoi cells")
    else:
        print(f"--> No false connections found")
        num_false_cells = 0
        num_false_connections = 0

    return (num_false_connections, num_false_cells, false_connections)
