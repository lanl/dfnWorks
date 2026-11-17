"""
.. module:: boundary.py
   :synopsis: Map a boundary-condition name to its index in intersection_list.dat.
"""

import sys

from pydfnworks.general.logging import local_print_log


def boundary_index(bc_name):
    """Determine boundary index in intersections_list.dat from name.

    Parameters
    ----------
        bc_name : string
            Boundary condition name (top, bottom, left, front, right, back)

    Returns
    -------
        bc_index : int
            integer indexing of cube faces

    Notes
    -----
    top = -1, bottom = -2, left = -3, front = -4, right = -5, back = -6
    """
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
