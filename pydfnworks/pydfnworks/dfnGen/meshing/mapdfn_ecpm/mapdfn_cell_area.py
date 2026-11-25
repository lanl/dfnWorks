"""
   mapdfn_cell_area.py

   Fracture--cell area weights for the mapdfn ECPM upscaling.

   The flat-cut mapping assigns every fracture in a tagged cell the full
   face area d**2. The functions here return ``w = A_ic / d**2``, the fraction
   of a cell face actually covered by fracture i in cell c, using only the
   fracture normal and plane position (no polygon clipping).

   * ``"normal"``: ``w = 1 / ||n||_1``, the mean section area of a plane through a cube.
   * ``"section"``: exact area of the plane inside the cube (infinite-plane approximation within each tagged cell).

   Author: Jeffrey Hyman
"""

import itertools
import time
import numpy as np

# corners of the unit cube and the inclusion-exclusion signs (-1)^|v|
_CORNERS = np.array(list(itertools.product([0, 1], repeat=3)), dtype=float)
_SIGNS = np.where(_CORNERS.sum(axis=1) % 2 == 0, 1.0, -1.0)

# below this normal component the closed form is ill-conditioned
_DEGENERATE_TOL = 1e-3


def _section_area_closed(n, t):
    """ Closed-form area of the plane n.x = t inside the unit cube.

    Parameters
    -------------
        n : numpy array (3,)
            unit normal with non-negative components, all > _DEGENERATE_TOL
        t : numpy array (m,)
            plane offsets in ``[0, ||n||_1]``

    Returns
    -------------
        area : numpy array (m,)
    """
    s = t[:, None] - _CORNERS @ n  # (m, 8)
    s = np.clip(s, 0, None)**2
    return (s @ _SIGNS) / (2.0 * n[0] * n[1] * n[2])


def _section_area_edges(n, t):
    """ Area of the plane n.x = t inside the unit cube from its intersections
    with the twelve cube edges. Robust for any unit normal.
    """
    # in-plane basis
    a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(n, a)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    area = np.zeros(len(t))
    for m, tm in enumerate(t):
        pts = []
        for ax in range(3):
            if n[ax] <= 1e-14:
                continue
            o1, o2 = [b for b in range(3) if b != ax]
            for c1 in (0.0, 1.0):
                for c2 in (0.0, 1.0):
                    val = (tm - n[o1] * c1 - n[o2] * c2) / n[ax]
                    if -1e-12 <= val <= 1 + 1e-12:
                        p = np.zeros(3)
                        p[ax] = val
                        p[o1] = c1
                        p[o2] = c2
                        pts.append(p)
        if len(pts) < 3:
            continue
        pts = np.array(pts)
        xy = np.stack([pts @ u, pts @ v], axis=1)
        center = xy.mean(axis=0)
        order = np.argsort(
            np.arctan2(xy[:, 1] - center[1], xy[:, 0] - center[0]))
        xy = xy[order]
        x, y = xy[:, 0], xy[:, 1]
        area[m] = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
    return area


def section_area(normal, t):
    """ Area of the plane normal.x = t inside the unit cube [0,1]^3.

    Parameters
    -------------
        normal : array-like (3,)
            unit normal of the plane (any sign; reflected internally)
        t : array-like (m,)
            plane offsets measured from the cube corner that minimizes
            ``|normal| . x``, so the plane meets the cube for ``0 <= t <= ||normal||_1``

    Returns
    -------------
        area : numpy array (m,)
            section area as a fraction of the cube face area

    Notes
    -------------
        Closed form ``A(t) = sum_v (-1)^|v| (t - n.v)_+^2 / (2 n1 n2 n3)``, the
        derivative of the inclusion-exclusion volume below the plane. Falls
        back to edge intersection when a normal component is near zero.
    """
    n = np.abs(np.asarray(normal, dtype=float))
    n /= np.linalg.norm(n)
    t = np.atleast_1d(np.asarray(t, dtype=float))
    if n.min() > _DEGENERATE_TOL:
        area = _section_area_closed(n, t)
    else:
        area = _section_area_edges(n, t)
    area[(t <= 0) | (t >= n.sum())] = 0.0
    return np.clip(area, 0.0, None)


def mapdfn_cell_weights(self, cell_fracture_id, origin, nx, ny, cell_size,
                        mode):
    """ Fracture--cell area weights w = A_ic / d**2 for each tagged pair.

    Parameters
    -----------------
        self : dfnWorks object
            uses self.normal_vectors and self.centers (a point on each
            fracture plane)
        cell_fracture_id : dict
            cell index -> list of fractures, from mapdfn_tag_cells
        origin : list
            min x, y, z corner of the ECPM domain
        nx, ny : int
            number of cells in x and y
        cell_size : float
            hexahedron edge length d
        mode : string
            "normal" (``1/||n||_1`` per fracture) or "section" (exact plane-cube
            section area per cell)

    Returns
    -----------------
        cell_fracture_weight : dict
            cell index -> list of weights, parallel to cell_fracture_id
    """
    t0 = time.time()
    self.print_log(f"--> Computing fracture-cell area weights ({mode})")
    normals = np.asarray(self.normal_vectors, dtype=float).reshape(-1, 3)
    normals = normals / np.linalg.norm(normals, axis=1)[:, None]
    l1 = np.abs(normals).sum(axis=1)

    cell_fracture_weight = {}
    if mode == "normal":
        for cell, fracs in cell_fracture_id.items():
            cell_fracture_weight[cell] = [1.0 / l1[f] for f in fracs]
        return cell_fracture_weight

    if mode != "section":
        raise ValueError(
            f"Unknown cell_area mode '{mode}'. Use 'flat', 'normal', or 'section'."
        )

    # gather (cell, slot, fracture) triples for vectorized evaluation per fracture
    cells, slots, fracs = [], [], []
    for cell, flist in cell_fracture_id.items():
        cell_fracture_weight[cell] = [0.0] * len(flist)
        for slot, f in enumerate(flist):
            cells.append(cell)
            slots.append(slot)
            fracs.append(f)
    if not cells:
        return cell_fracture_weight
    cells = np.array(cells)
    slots = np.array(slots)
    fracs = np.array(fracs)

    # cell centers from the linear index i + nx*j + nx*ny*k
    k = cells // (nx * ny)
    j = (cells - k * nx * ny) // nx
    i = cells - k * nx * ny - j * nx
    centers = np.stack([
        origin[0] + (i + 0.5) * cell_size, origin[1] +
        (j + 0.5) * cell_size, origin[2] + (k + 0.5) * cell_size
    ],
                       axis=1)

    weights = np.zeros(len(cells))
    points = np.asarray(self.centers, dtype=float)
    for f in np.unique(fracs):
        idx = np.where(fracs == f)[0]
        n = normals[f]
        # signed distance from cell center to the fracture plane along n
        s = (points[f] - centers[idx]) @ n
        # plane offset in unit-cube coordinates after reflecting the cube so
        # that n -> |n| (the reflection leaves t = |n|_1/2 + s/d unchanged)
        t = 0.5 * l1[f] + s / cell_size
        weights[idx] = section_area(n, t)

    for c, sl, w in zip(cells, slots, weights):
        cell_fracture_weight[c][sl] = w

    self.print_log(
        f"--> Area weights complete: mean w = {weights.mean():0.3f}, "
        f"{np.sum(weights == 0)} of {len(weights)} tagged pairs have zero area. "
        f"Time {time.time() - t0:0.2f} s")
    return cell_fracture_weight
