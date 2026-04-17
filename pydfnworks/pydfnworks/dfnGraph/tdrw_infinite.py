
from scipy import special
import numpy as np 

def t_diff_unlimited(a, tf, xi):
    """
    This function returns one  diffusion time sample for a and tf assuming an unlimited matrix block size.  This is used throughout the limited block size sampling technique. 
    
    Parameters
    -------------------
        a : double
         Constant parameter describing retention in the matrix. a = (matrix_porosity*matrix_diffusion)/aperture_length
        
        tf : double
            Advective travel time
        
        xi : float
            value between [0,1)
   
    Returns
    --------------
        t_diff : float
            Total time diffusing the matrix
            
    Notescx
    -------------
        For a random sample, sample xi from U[0,1). 
        
    """

    return ((a * tf) / special.erfcinv(xi))**2

def unlimited_matrix_diffusion(self, G):
    """ Matrix diffusion with unlimited block size

    Parameters
    ----------
        G : NetworkX graph
            graph obtained from graph_flow

    Returns
    ----------
        None

    Notes
    -----------
        All parameters are attached to the particle class 

    """

    b = G.edges[self.curr_node, self.next_node]['b']
    a_nondim = self.matrix_porosity * np.sqrt(self.matrix_diffusivity) / b
    xi = np.random.uniform(size=1, low=0, high=1)[0]
    self.delta_t_md = ((a_nondim * self.delta_t / special.erfcinv(xi))**2)
