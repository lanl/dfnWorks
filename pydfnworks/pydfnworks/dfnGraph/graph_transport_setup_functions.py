
import networkx as nx
import numpy as np

from pydfnworks.general.logging import local_print_log

def _get_initial_posititions(G, initial_positions, nparticles):
    """ Distributes initial particle positions 

        Parameters
        ----------
                
            G : NetworkX graph 
                obtained from graph_flow

            initial_positions : str
                distribution of initial conditions. options are uniform and flux (flux-weighted)

            nparticles : int
                requested number of particles

        Returns
        -------
            ip : numpy array
                array nparticles long. Each element is the initial position for each particle

        """

    inlet_nodes = [v for v in nx.nodes(G) if G.nodes[v]['inletflag']]
    cnt = len(inlet_nodes)
    local_print_log(f"--> There are {cnt} inlet nodes")
    if cnt == 0:
        error = "Error. There are no nodes in the inlet.\nExiting"
        local_print_log(error, 'error')

    # Uniform Distribution for particles
    if initial_positions == "uniform":
        local_print_log("--> Using uniform initial positions.")
        ip = np.zeros(nparticles).astype(int)
        n = int(np.ceil(nparticles / cnt))
        local_print_log(f"--> {n} particles will be placed at every inflow node.\n")
        ## this could be cleaned up using clever indexing
        inflow_idx = 0
        inflow_cnt = 0
        for i in range(nparticles):
            ip[i] = inlet_nodes[inflow_idx]
            inflow_cnt += 1
            if inflow_cnt >= n:
                inflow_idx += 1
                inflow_cnt = 0

    ## flux weighted initial positions for particles
    elif initial_positions == "flux":
        local_print_log("--> Using flux-weighted initial positions.\n")
        flux = np.zeros(cnt)
        for i, u in enumerate(inlet_nodes):
            for v in G.successors(u):
                flux[i] += G.edges[u, v]['flux']
        flux /= flux.sum()
        flux_cnts = [np.ceil(nparticles * i) for i in flux]
        nparticles = int(sum(flux_cnts))
        ip = np.zeros(nparticles).astype(int)
        ## Populate ip with Flux Cnts
        ## this could be cleaned up using clever indexing
        inflow_idx = 0
        inflow_cnt = 0
        for i in range(nparticles):
            ip[i] = inlet_nodes[inflow_idx]
            inflow_cnt += 1
            if inflow_cnt >= flux_cnts[inflow_idx]:
                inflow_idx += 1
                inflow_cnt = 0

    # Throw error if unknown initial position is provided
    else:
        error = f"Error. Unknown initial_positions input {initial_positions}. Options are uniform or flux \n"
        local_print_log(error, 'error')

    return ip, nparticles


def _create_neighbor_list(G):
    """ Create a list of downstream neighbor vertices for every vertex on NetworkX graph obtained after running graph_flow

    Parameters
    ----------
        G: NetworkX graph 
            Directed Graph obtained from output of graph_flow

    Returns
    -------
        dict : nested dictionary.

    Notes
    -----
        dict[n]['child'] is a list of vertices downstream to vertex n
        dict[n]['prob'] is a list of probabilities for choosing a downstream node for vertex n
    """

    nbrs_dict = {}

    for u in nx.nodes(G):

        if G.nodes[u]['outletflag']:
            continue

        node_list = []
        prob_list = []
        nbrs_dict[u] = {}

        for v in G.successors(u):
            node_list.append(v)
            prob_list.append(G.edges[u, v]['vol_flow_rate'])

        if node_list:
            nbrs_dict[u]['child'] = node_list
            nbrs_dict[u]['prob'] = np.asarray(prob_list) / sum(prob_list)
        else:
            nbrs_dict[u]['child'] = None
            nbrs_dict[u]['prob'] = None

    return nbrs_dict

def _check_control_planes(control_planes, direction):
    """
    Validate the control plane configuration and primary direction for a simulation.

    This function performs basic validation on the provided `control_planes` and `direction`
    inputs used to define spatial control planes in a model or simulation. It logs errors
    and diagnostic messages through `local_print_log` but does not raise exceptions directly.
    The function returns a flag indicating whether the control planes list passed basic
    validation checks.

    Parameters
    ----------
    control_planes : list
        A list defining the positions or indices of control planes along the specified
        primary direction. Must be of type `list`. If validation succeeds, a flag is set
        to indicate that control planes are active.
    direction : str
        The primary coordinate direction associated with the control planes. Must be one
        of `'x'`, `'y'`, or `'z'`. Used to orient control plane processing.

    Returns
    -------
    bool
        `True` if the provided `control_planes` input is a list and passes validation,
        otherwise `False`.

    Logging Behavior
    ----------------
    Uses `local_print_log` to record:
      * Errors if inputs are missing or invalid.
      * Informational messages showing the provided control planes and direction.

    Notes
    -----
    - The function does not modify the `control_planes` list.
    - It is expected that higher-level routines handle program termination or recovery
      in response to logged errors.
    - The inclusion of `None` to mark the end of the control plane list should be
      handled outside this function, if applicable.
    """
    control_plane_flag = False

    # Validate control_planes
    if not isinstance(control_planes, list):
        local_print_log("Error: Provided control planes are not a list.", "error")
    else:
        control_plane_flag = True

    # Validate direction
    allowed_dirs = {"x", "y", "z"}
    if direction is None:
        local_print_log("Error: Primary direction not provided. Required for control planes.", "error")
    elif direction not in allowed_dirs:
        local_print_log("Error: Primary direction is not known. Acceptable values are x, y, and z.", "error")

    # Diagnostics
    local_print_log(f"Control planes: {control_planes}")
    local_print_log(f"Direction: {direction}")

    return control_plane_flag