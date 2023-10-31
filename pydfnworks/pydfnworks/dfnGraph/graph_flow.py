import networkx as nx
import numpy as np
import sys
import scipy.sparse
import h5py

# pydfnworks modules
from pydfnworks.dfnGraph.intersection_graph import create_intersection_graph
from pydfnworks.dfnGraph.graph_attributes import add_perm, add_area, add_weight


def get_laplacian_sparse_mat(G,
                             nodelist=None,
                             weight=None,
                             dtype=None,
                             format='lil'):
    """ Get the matrices D, A that make up the Laplacian sparse matrix in desired sparsity format. Used to enforce boundary conditions by modifying rows of L = D - A

    Parameters
    ----------
        G : object
            NetworkX graph equipped with weight attribute

        nodelist : list
            list of nodes of G for which laplacian is desired. Default is None in which case, all the nodes
        
        weight : string
            For weighted Laplacian, else all weights assumed unity
        
        dtype :  default is None, cooresponds to float
        
        format: string
            sparse matrix format, csr, csc, coo, lil_matrix with default being lil

    Returns
    -------
        D : sparse 2d float array       
            Diagonal part of Laplacian
            
        A : sparse 2d float array
            Adjacency matrix of graph
    """

    # A = nx.to_scipy_sparse_matrix(G,
    #                               nodelist=nodelist,
    #                               weight=weight,
    #                               dtype=dtype,
    #                               format=format)
    A = nx.to_scipy_sparse_array(G,
                                nodelist=nodelist,
                                weight=weight,
                                dtype=dtype,
                                format=format)

    (n, n) = A.shape
    data = np.asarray(A.sum(axis=1).T)
    D = scipy.sparse.spdiags(data, 0, n, n, format=format)
    return D, A


def prepare_graph_with_attributes(inflow, outflow, G=None):
    """ Create a NetworkX graph, prepare it for flow solve by equipping edges with  attributes, renumber vertices, and tag vertices which are on inlet or outlet
    
    Parameters
    ----------
        inflow : string
            name of file containing list of DFN fractures on inflow boundary

        outflow: string
            name of file containing list of DFN fractures on outflow boundary

    Returns
    -------
        Gtilde : NetworkX graph
    """

    if G == None:
        G = create_intersection_graph(inflow, outflow)

        Gtilde = G.copy()
        # need to add aperture
        add_perm(Gtilde)
        add_area(Gtilde)
        add_weight(Gtilde)

    else:
        Gtilde = G
        #add_perm(Gtilde)
        #add_area(Gtilde)
        add_weight(Gtilde)

    for v in nx.nodes(Gtilde):
        Gtilde.nodes[v]['inletflag'] = False
        Gtilde.nodes[v]['outletflag'] = False

    if len(list(nx.neighbors(Gtilde, 's'))) == 0:
        error = "Error. There are no nodes in the inlet.\nExiting"
        sys.stderr.write(error)
        sys.exit(1)

    for v in nx.neighbors(Gtilde, 's'):
        Gtilde.nodes[v]['inletflag'] = True

    if len(list(nx.neighbors(Gtilde, 't'))) == 0:
        error = "Error. There are no nodes in the outlet.\nExiting"
        sys.stderr.write(error)
        sys.exit(1)

    for v in nx.neighbors(Gtilde, 't'):
        Gtilde.nodes[v]['outletflag'] = True

    Gtilde.remove_node('s')
    Gtilde.remove_node('t')

    Gtilde = nx.convert_node_labels_to_integers(Gtilde,
                                                first_label=0,
                                                ordering="sorted",
                                                label_attribute="old_label")

    return Gtilde


def solve_flow_on_graph(G, pressure_in, pressure_out, fluid_viscosity, phi):
    """ Given a NetworkX graph prepared  for flow solve, solve for vertex pressures, and equip edges with attributes (Darcy) flux  and time of travel

    Parameters
    ----------
        G : NetworkX graph

        pressure_in : double
            Value of pressure (in Pa) at inlet
        
        pressure_out : double
            Value of pressure (in Pa) at outlet
        
        fluid_viscosity : double
            optional, in Pa-s, default is for water

        phi : double
            Porosity, default is 1

    Returns
    -------
        H : Acyclic Directed NetworkX graph 
            H is updated with vertex pressures, edge fluxes and travel times. The only edges that exists are those with postive flow rates. 

    Notes
    ----------
        None

    """

    print("--> Starting Graph flow")

    Inlet = [v for v in nx.nodes(G) if G.nodes[v]['inletflag']]
    Outlet = [v for v in nx.nodes(G) if G.nodes[v]['outletflag']]

    if not set(Inlet).isdisjoint(set(Outlet)):
        error = "Incompatible graph: Vertex connected to both source and target\n"
        sys.stderr.write(error)
        sys.exit(1)

    D, A = get_laplacian_sparse_mat(G, weight='weight', format='lil')

    b = np.zeros(G.number_of_nodes())

    for v in Inlet:
        b[v] = pressure_in
        A[v, :] = 0
        D[v, v] = 1.0
    for v in Outlet:
        b[v] = pressure_out
        A[v, :] = 0
        D[v, v] = 1.0
    L = D - A  # automatically converts to csr when returning L

    print("--> Solving Linear System for pressure at nodes")
    pressure = scipy.sparse.linalg.spsolve(L, b)
    print("--> Updating graph edges with flow solution")

    for v in nx.nodes(G):
        G.nodes[v]['pressure'] = pressure[v]

    H = nx.DiGraph()
    H.add_nodes_from(G.nodes(data=True))

    for u, v in nx.edges(G):
        # Find direction of flow
        if G.nodes[u]['pressure'] > G.nodes[v]['pressure']:
            upstream = u
            downstream = v
        elif G.nodes[v]['pressure'] >= G.nodes[u]['pressure']:
            upstream = v
            downstream = u

        delta_p = G.nodes[upstream]['pressure'] - G.nodes[downstream][
            'pressure']
        if delta_p > 1e-16:
            ## Create new edge in DiGraph
            H.add_edge(upstream, downstream)
            # Transfer edge attributes
            for att in [
                    'perm', 'iperm', 'length', 'weight', 'area', 'frac', 'b'
            ]:
                H.edges[upstream, downstream][att] = G.edges[upstream,
                                                             downstream][att]

            H.edges[upstream, downstream]['flux'] = (
                H.edges[upstream, downstream]['perm'] / fluid_viscosity) * (
                    delta_p / H.edges[upstream, downstream]['length'])

            H.edges[upstream, downstream]['vol_flow_rate'] = H.edges[
                upstream, downstream]['flux'] * H.edges[upstream,
                                                        downstream]['area']

            # H.edges[downstream, upstream]['vol_flow_rate'] =  -1*H.edges[upstream, downstream]['vol_flow_rate']

            H.edges[upstream,
                    downstream]['velocity'] = H.edges[upstream,
                                                      downstream]['flux'] / phi
            H.edges[upstream,
                    downstream]['time'] = H.edges[upstream, downstream][
                        'length'] / (H.edges[upstream, downstream]['velocity'])

    print("--> Graph flow complete")
    return H


def compute_dQ(self, G):
    """ Computes the DFN fracture intensity (p32) and flow channeling density indicator from the graph flow solution on G

    Parameters
    -----------------
        self : object
            DFN Class

        G : networkX graph 
            Output of run_graph_flow

    Returns
    ---------------
        p32 : float
            Fracture intensity
        dQ : float flow channeling density indicator 

    Notes
    ------------
        For definitions of p32 and dQ along with a discussion see " Hyman, Jeffrey D. "Flow channeling in fracture networks: characterizing the effect of density on preferential flow path formation." Water Resources Research 56.9 (2020): e2020WR027986. "

    """
    print(
        "--> Computing fracture intensity (p32) and flow channeling density indicator (dQ)"
    )

    fracture_surface_area = 2*self.surface_area
    domain_volume = self.domain['x'] * self.domain['y'] * self.domain['z']

    Qf = np.zeros(self.num_frac)
    ## convert to undirected
    H = G.to_undirected()
    ## walk through fractures
    for curr_frac in range(1, self.num_frac + 1):
        # print(f"\nstarting on fracture {curr_frac}")
        # Gather nodes on current fracture
        current_nodes = []
        for u, d in H.nodes(data=True):
            for f in d["frac"]:
                if f == curr_frac:
                    current_nodes.append(u)
        # cycle through nodes on the fracture and get the outgoing / incoming
        # volumetric flow rates
        for u in current_nodes:
            neighbors = H.neighbors(u)
            for v in neighbors:
                if v not in current_nodes:
                    # outgoing vol flow rate
                    Qf[curr_frac - 1] += abs(H[u][v]['vol_flow_rate'])
                    for f in H.nodes[v]['frac']:
                        if f != curr_frac and f != 's' and f != 't':
                            # incoming vol flow rate
                            Qf[f - 1] += abs(H[u][v]['vol_flow_rate'])
    # Divide by 1/2 to remove up double counting
    Qf *= 0.5
    p32 = fracture_surface_area.sum() / domain_volume
    top = sum(fracture_surface_area * Qf)**2
    bottom = sum(fracture_surface_area * Qf**2)
    print(top, bottom)
    dQ = (1.0 / domain_volume) * (top / bottom)
    print(f"--> P32: {p32:0.2e} [1/m]")
    print(f"--> dQ: {dQ:0.2e} [1/m]")
    print(f"--> Active surface percentage {100*dQ/p32:0.2f}")
    print(f"--> Geometric equivalent fracture spacing {1/p32:0.2e} m")
    print(f"--> Hydrological equivalent fracture spacing {1/dQ:0.2e} m")
    print("--> Complete \n")
    return p32, dQ, Qf


def dump_graph_flow_values(G):

    num_edges = G.number_of_edges()
    velocity = np.zeros(num_edges)
    lengths = np.zeros_like(velocity)
    vol_flow_rate = np.zeros_like(velocity)
    area = np.zeros_like(velocity)
    aperture = np.zeros_like(velocity)
    volume = np.zeros_like(velocity)

    for i, val in enumerate(G.edges(data=True)):
        u, v, d = val
        velocity[i] = d['velocity']
        lengths[i] = d['length']
        vol_flow_rate[i] = d['vol_flow_rate']
        area[i] = d['area']
        aperture[i] = d['b']
        volume[i] = area[i] * aperture[i]

    with h5py.File(f"graph_flow.hdf5", "w") as f5file:
        h5dset = f5file.create_dataset('velocity', data=velocity)
        h5dset = f5file.create_dataset('length', data=lengths)
        h5dset = f5file.create_dataset('vol_flow_rate', data=vol_flow_rate)
        h5dset = f5file.create_dataset('area', data=area)
        h5dset = f5file.create_dataset('aperture', data=aperture)
        h5dset = f5file.create_dataset('volume', data=volume)
    f5file.close()


def run_graph_flow(self,
                   inflow,
                   outflow,
                   pressure_in,
                   pressure_out,
                   fluid_viscosity=8.9e-4,
                   phi=1,
                   G=None):
    """ Solve for pressure driven steady state flow on a graph representation of the DFN. 

    Parameters
    ----------
        self : object
            DFN Class

        inflow : string
            name of file containing list of DFN fractures on inflow boundary

        outflow: string
            name of file containing list of DFN fractures on outflow boundary

        pressure_in : double
            Value of pressure at inlet [Pa]
        
        pressure_out : double
            Value of pressure at outlet [Pa]

        fluid_viscosity : double
            optional,  default is for water. [Pa*s]
            
        phi : double
            Fracture porosity, default is 1 [-]

        G : Input Graph 

    Returns
    -------
        Gtilde : NetworkX graph 
            Gtilde is a directed acyclic graph with vertex pressures, fluxes, velocities, volumetric flow rates, and travel times

    """
    if G == None:
        G = self.create_graph("intersection", inflow, outflow)

    Gtilde = prepare_graph_with_attributes(inflow, outflow, G)
    Gtilde = solve_flow_on_graph(Gtilde, pressure_in, pressure_out,
                                 fluid_viscosity, phi)

    dump_graph_flow_values(Gtilde)
    return Gtilde
