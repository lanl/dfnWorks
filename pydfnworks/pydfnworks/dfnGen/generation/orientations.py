"""
.. module:: orientations.py
   :synopsis: Convert fracture normal vectors into the orientation conventions
              used in structural geology -- strike / dip / dip direction of the
              fracture plane, and trend / plunge of the pole (normal).

All functions use a right-handed ENU coordinate system (x = East, y = North,
z = Up), and report the lower-hemisphere representation, which is the standard
convention for stereonet plotting.
"""

import numpy as np


def normals_to_lower_hemisphere(normals):
    """ Return normals flipped, as needed, into the lower hemisphere.

    Parameters
    ----------
        normals : array-like
            (N, 3) array of normal vectors. A single (3,) vector is accepted and
            promoted to (1, 3).

    Returns
    -------
        normals : numpy array
            (N, 3) array of normals, all with a non-positive z component.

    Notes
    -----
        A copy is returned; the input array is never modified in place.
    """
    normals = np.array(normals, dtype=float, copy=True)
    if normals.ndim == 1:
        normals = normals[np.newaxis, :]
    # z is "up": flip any normal pointing into the upper hemisphere
    flip = normals[:, 2] > 0
    normals[flip] *= -1.0
    return normals


def normals_to_strike_dip(normals):
    """ Convert fracture plane normals to strike and dip (right-hand rule).

    Parameters
    ----------
        normals : array-like
            (N, 3) array of normal vectors (nx, ny, nz) in a right-handed ENU
            system (x = East, y = North, z = Up). Need not be normalized.

    Returns
    -------
        strikes : numpy array
            Strike azimuths in degrees, clockwise from North, 0 - 360.

        dips : numpy array
            Dip angles from horizontal in degrees, 0 - 90.

        dip_dirs : numpy array
            Dip directions (azimuth of the down-dip line) in degrees, 0 - 360.

    Notes
    -----
        Strike follows the right-hand rule: it is 90 degrees counter-clockwise
        from the dip direction.
    """
    n = normals_to_lower_hemisphere(normals)
    n /= np.linalg.norm(n, axis=1)[:, np.newaxis]

    nx = n[:, 0]
    ny = n[:, 1]
    nz = n[:, 2]

    # dip: angle between the plane and horizontal
    dip = np.degrees(np.arctan2(np.sqrt(nx**2 + ny**2), np.abs(nz)))
    # dip direction: opposite the horizontal projection of the normal.
    # arctan2(East, North) gives an azimuth clockwise from North.
    dip_dir = np.degrees(np.arctan2(-nx, -ny)) % 360.0
    # strike: 90 degrees counter-clockwise from dip direction
    strike = (dip_dir - 90.0) % 360.0

    return strike, dip, dip_dir


def normals_to_trend_plunge(normals):
    """ Convert fracture plane normals to the trend and plunge of the pole.

    Parameters
    ----------
        normals : array-like
            (N, 3) array of normal vectors (nx, ny, nz) in a right-handed ENU
            system (x = East, y = North, z = Up). Need not be normalized.

    Returns
    -------
        trends : numpy array
            Trend (azimuth) of the pole in degrees, clockwise from North,
            0 - 360.

        plunges : numpy array
            Plunge of the pole below horizontal in degrees, 0 - 90.

    Notes
    -----
        The pole of a plane is its normal. Because the lower-hemisphere
        convention is used, the returned values satisfy
        plunge = 90 - dip and trend = (dip direction + 180) % 360.
    """
    n = normals_to_lower_hemisphere(normals)
    n /= np.linalg.norm(n, axis=1)[:, np.newaxis]

    nx = n[:, 0]
    ny = n[:, 1]
    nz = n[:, 2]

    # nz <= 0 by construction, so the plunge is non-negative.
    # adding 0.0 turns the -0.0 of a horizontal pole into 0.0
    plunge = np.degrees(np.arcsin(np.clip(-nz, -1.0, 1.0))) + 0.0
    trend = np.degrees(np.arctan2(nx, ny)) % 360.0

    return trend, plunge


def get_fracture_orientations(self):
    """ Compute the orientation of every fracture in the network and attach the
    results to the DFN object.

    Parameters
    ----------
        self : object
            DFN Class

    Returns
    -------
        None

    Notes
    -----
        Sets the following attributes, each a numpy array with one entry per
        fracture, ordered to match self.normal_vectors:

        * self.strike : strike azimuth of the fracture plane [degrees, 0 - 360]
        * self.dip : dip of the fracture plane below horizontal [degrees, 0 - 90]
        * self.dip_direction : azimuth of the down-dip line [degrees, 0 - 360]
        * self.trend : trend of the pole (normal) [degrees, 0 - 360]
        * self.plunge : plunge of the pole (normal) [degrees, 0 - 90]

        Uses the lower-hemisphere convention, so plunge = 90 - dip. The
        fracture normals are not modified.
    """
    normals = getattr(self, "normal_vectors", None)
    if normals is None:
        self.print_log(
            "Error. Fracture normal vectors are not defined. Orientations "
            "require normal_vectors, which is set when the network is created.",
            'error')
        return

    self.print_log("--> Computing fracture orientations")
    self.strike, self.dip, self.dip_direction = normals_to_strike_dip(normals)
    self.trend, self.plunge = normals_to_trend_plunge(normals)
    self.print_log(
        "--> Computing fracture orientations: Complete. Attributes set: "
        "strike, dip, dip_direction, trend, plunge")
