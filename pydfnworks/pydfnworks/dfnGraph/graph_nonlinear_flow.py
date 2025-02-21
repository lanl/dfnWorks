import networkx as nx
import numpy as np
import sys
import scipy.sparse

# pydfnworks modules
from pydfnworks.dfnGraph.intersection_graph import create_intersection_graph
from pydfnworks.dfnGraph.graph_attributes import add_perm, add_area, add_weight
from pydfnworks.general.logging import local_print_log, print_log
from pydfnworks.dfnGraph.graph_flow import get_laplacian_sparse_mat





def linear_solve(G, weight, pressure_in, pressure_out, inlet, outlet):
    D, A = get_laplacian_sparse_mat(G, weight=weight, format='lil')

    b = np.zeros(G.number_of_nodes())

    for v in inlet:
        b[v] = pressure_in
        A[v, :] = 0
        D[v, v] = 1.0
    for v in outlet:
        b[v] = pressure_out
        A[v, :] = 0
        D[v, v] = 1.0
    L = D - A  # automatically converts to csr when returning L

    local_print_log("--> Solving Linear System for pressure at nodes")
    pressure = scipy.sparse.linalg.spsolve(L, b)
    local_print_log("--> Solving Linear System for pressure at nodes complete") 
    return pressure 

def flow_rate_PFC(dP, R, L, n, gammac, mu):
    """
    Calculates the flowrate and non-linear conductivity along conduits for a
    given pressure gradient
    ----------
    Parameters
    ----------
    dP : pressure drop along conduit.
    R : conduit radius.
    L : conduit length.
    n : exponent of power-law fluid.
    gammac : critical shear rate.

    Returns
    -------
    Q : flow rate.
    cond : non-linear conductance.
    rc : critical radius.
    """
    dPabs = np.abs(dP)
    G = dPabs/L  # pressure gradient
    rc = 2*mu*gammac/G

    # Set rc = R if rc >= R
    mask = rc >= R
    rc[mask] = R[mask]

    vc = n*G*rc**(1-1/n)/(2*mu*(n+1))*(R**(1+1/n)-rc**(1+1/n))
    Q = np.pi*rc**2*vc + np.pi*G*rc**4/(8*mu) + np.pi*G*rc**(1-1/n)/(2*mu*(n+1))\
        * ((R**2 - rc**2)*R**(1+1/n) - 2*n/(3*n+1)*(R**(3+1/n) - rc**(3+1/n)))

    # mask to identify conduits with 0 pressure drop
    maskP = dPabs == 0
    '''
    set pressure drop at conduits with zero pressure drop equal to one to avoid
    singularity when calculating the non-linear conductivity. This does not
    represent a problem because these conduits are connecting boundary nodes
    '''
    dPabs[maskP] = 1
    cond = Q/dPabs

    return Q, cond, rc

def solve_nonlinear_flow_on_graph(G, pressure_in, pressure_out, fluid_viscosity, phi, flow_model):
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

    local_print_log("--> Starting Graph flow")

    inlet = [v for v in nx.nodes(G) if G.nodes[v]['inletflag']]
    outlet = [v for v in nx.nodes(G) if G.nodes[v]['outletflag']]

    if not set(inlet).isdisjoint(set(outlet)):
        error = "Incompatible graph: Vertex connected to both source and target\n"
        local_print_log(error, 'error')

    max_iterations = 100
    w = 1 # relaxation parameter 
    for i in range(max_iterations):
        if i == 0:
            for u, v in nx.edges(G):
                if G.edges[u, v]['length'] > 0:
                    # G.edges[u, v]['conductance'] = G.edges[u, v]['perm'] * G.edges[
                    #     u, v]['area'] / G.edges[u, v]['length']
                    # np.pi*R**(4)/(8*L*mu)
                    G.edges[u, v]['conductance'] = (np.pi * G.edges[u, v]['b']**2*G.edges[u, v]['area'])/(8*G.edges[u, v]['length'])

            pressure = linear_solve(G, 'conductance', pressure_in, pressure_out, inlet, outlet) 

            # From Marco 
            # Qabs, conductance, rc = flowratePFC(dP, R, L, n, gammac)
            # dP = np.diff(P).squeeze()
            # Q = dP*conductance
            # v = np.abs(Q)/throat_area
            # residual = A*P - b
            # res = np.max(np.abs(residual))

        else:

            pressure_new = linear_solve(G, 'conductance', pressure_in, pressure_out, inlet, outlet) 

            pressure = w * pressure_new + (1 - w) * pressure
            # From Marco 


            # dP = np.diff(P).squeeze()
            # Q = dP*conductance
            # v = np.abs(Q)/throat_area
            # residual = A*P - b
            # res = np.max(np.abs(residual))
            #Qabs, conductance, rc = flowratePFC(dP, R, L, n, gammac)


        # if bool(np.max(np.abs(res)) < f_rtol and np.max(dQ) < x_rtol*np.max(Qabs)):
        #         break

        #     Q = conductance*dP
        #     v = np.abs(Qabs) / throat_area
        #     end = time.time()


    local_print_log("--> Nonlinear graph flow complete")
    return None


