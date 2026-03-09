"""
  :filename: plot_fracture_orientations.py
  :synopsis: Make plots of fracture orientations for the entire network and by family
  :version: 1.0
  :maintainer: Jeffrey Hyman and Matthew Sweeney
  :moduleauthor: Jeffrey Hyman <jhyman@lanl.gov>, Matthew Sweeney <msweeney2796@lanl.gov>
"""

import numpy as np
import math as m
import mplstereonet
import matplotlib.pyplot as plt
import random
from pydfnworks.general.logging import local_print_log 

def get_normal_vectors(fam, fractures):
    """
    Extract normal vectors for all fractures belonging to a fracture family.

    This function gathers the unit normal vectors of fractures listed in a
    given fracture family definition and returns them as a single NumPy
    array. Each row corresponds to one fracture plane normal.

    Parameters
    ----------
    fam : dict
        Dictionary describing a fracture family. Must contain:
        
        - ``"final_number_of_fractures"`` : int  
          Total number of fractures in the family.
        - ``"fracture list - final"`` : iterable of int  
          Indices of fractures belonging to this family.

    fractures : sequence of dict
        Collection of fracture definitions. Each fracture entry must contain:
        
        - ``"normal"`` : array-like of shape (3,)  
          Unit normal vector of the fracture plane.

    Returns
    -------
    normal_vectors : numpy.ndarray, shape (N, 3)
        Array of fracture normal vectors, where ``N`` is
        ``fam["final_number_of_fractures"]``. Each row corresponds to the
        normal vector of one fracture plane.

    Notes
    -----
    - The function assumes that the indices in
      ``fam["fracture list - final"]`` are valid indices into ``fractures``.
    - No normalization is performed; normals are assumed to already be
      unit vectors.
    - The order of normals in the output array follows the order of
      ``fam["fracture list - final"]``.

    Examples
    --------
    >>> normals = get_normal_vectors(fam, fractures)
    >>> normals.shape
    (fam["final_number_of_fractures"], 3)
    """
    normal_vectors = np.zeros((fam["final_number_of_fractures"], 3))
    for i, j in enumerate(fam["fracture list - final"]):
        normal_vectors[i, :] = fractures[j]["normal"]
    return normal_vectors

def normalise_normals_to_lower_hemisphere(normals):
    """
    Ensures that all normal vectors are in the lower hemisphere by flipping any
    vector with a positive z-component.

    This is useful for plotting poles or orientations on lower-hemisphere
    stereonets, ensuring consistency in directional statistics.

    Parameters
    ----------
    normals : array-like
        A (N, 3) array of normal vectors. Each row is expected to be a 3D vector.

    Returns
    -------
    np.ndarray
        A (N, 3) array of normal vectors, all adjusted to point into the lower hemisphere
        (i.e., z-component ≤ 0).
    """ 
    normals = np.asarray(normals, float)
    # Assuming z is "up". Flip any normal with positive z
    flip = normals[:, 2] > 0
    normals[flip] *= -1.0
    return normals

# ---------- Geometry helpers ----------
def normals_to_strike_dip(normals):
    """
    Convert plane normals to strike and dip (right-hand rule).

    Parameters
    ----------
    normals : (N, 3) array-like
        Normal vectors (nx, ny, nz) in a right-handed ENU system
        (x=East, y=North, z=Up). Need not be normalized.

    Returns
    -------
    strikes : (N,) ndarray
        Strike azimuths in degrees, clockwise from North, 0–360.
    dips : (N,) ndarray
        Dip angles from horizontal in degrees, 0–90.
    dip_dirs : (N,) ndarray
        Dip directions (azimuth of down-dip line) in degrees, 0–360.
    """
    normals = normalise_normals_to_lower_hemisphere(normals)

    n = np.asarray(normals, dtype=float)
    if n.ndim == 1:
        n = n[np.newaxis, :]

    # Normalize
    n /= np.linalg.norm(n, axis=1)[:, np.newaxis]

    nx = n[:, 0]
    ny = n[:, 1]
    nz = n[:, 2]

    # Dip: angle between plane and horizontal
    dip = np.degrees(np.arctan2(np.sqrt(nx**2 + ny**2), np.abs(nz)))

    # Dip direction: opposite horizontal projection of normal
    # Using atan2(East, North) to get azimuth clockwise from North
    dx = -nx
    dy = -ny
    dip_dir = np.degrees(np.arctan2(dx, dy)) % 360.0

    # Strike: 90° CCW from dip direction (right-hand rule)
    strike = (dip_dir - 90.0) % 360.0
    # convert type 
    strike = np.asarray(strike, float)
    dip = np.asarray(dip, float)
    dip_dir = np.asarray(dip_dir, float)

    return strike, dip, dip_dir


def plot_rose_diagram(ax, strikes_deg, color):
    """
    Plot an equal-area rose diagram of fracture strikes on a given polar axis.

    This function plots an axial (0–180°) rose diagram for fracture plane
    strikes using equal-area wedge scaling, where the radial length of each
    wedge is proportional to the square root of the frequency. Axial symmetry
    is represented by duplicating wedges at θ and θ + 180°.

    Parameters
    ----------
    ax : matplotlib.axes._axes.Axes
        A Matplotlib polar axis on which the rose diagram will be drawn.

    strikes_deg : array-like
        Strike angles of fracture planes in degrees. Values may be in the
        range 0–360°; they are internally converted to axial data (0–180°).

    color : str or tuple
        Color specification for the rose diagram wedges (any Matplotlib-
        compatible color format).

    Notes
    -----
    - Strike data are treated as axial (undirected), such that θ and θ + 180°
      represent the same fracture orientation.
    - Equal-area scaling is applied following Sanderson & Peacock (2020),
      where wedge radius is proportional to ``sqrt(frequency)`` rather than
      frequency itself.
    - The bin width is fixed internally at 18°, resulting in 10 bins over the
      0–180° axial range.
    - This function does not modify axis formatting (e.g., tick labels,
      orientation); these should be configured externally.

    Returns
    -------
    None
        The function plots directly to the provided axis and returns nothing.

    Examples
    --------
    >>> fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
    >>> plot_rose_diagram(ax, strikes, color='steelblue')
    >>> ax.set_theta_zero_location('N')
    >>> ax.set_theta_direction(-1)
    """

    bin_width=18
    strikes_deg = np.asarray(strikes_deg, float)

    # Convert to axial 0–180
    axial = strikes_deg % 180.0

    # Bin edges
    bin_edges = np.arange(0, 180 + bin_width, bin_width)

    # Histogram
    counts, _ = np.histogram(axial, bin_edges)

    # Equal-area scaling: radius ~ sqrt(count)
    radii = np.sqrt(counts)

    # Bin centers
    centers_deg = bin_edges[:-1] + bin_width / 2
    centers_rad = np.deg2rad(centers_deg)

    # Plot both θ and θ+180° (axial symmetry)
    for offset in (0, np.pi):
        ax.bar(
            centers_rad + offset,
            radii,
            width=np.deg2rad(bin_width),
            bottom=0,
            color=color,
            edgecolor="k",
        )


    return None  


def plot_stereonet(ax, strike, dip, color, density = True, poles = True, reduce = False):
    """
    Plot fracture orientations as poles and/or density contours on a stereonet.

    Parameters
    ----------
    ax : mplstereonet.stereonet.StereonetAxes
        A stereonet axis created with `projection='stereonet'`.

    strike : array-like
        Strike angles of planes in degrees.

    dip : array-like
        Dip angles of planes in degrees.

    color : str
        Marker color for poles.

    density : bool, optional
        If True, plot density contours using `ax.density_contourf`. Default is True.

    poles : bool, optional
        If True, plot individual pole symbols for each fracture plane. Default is True.

    reduce : bool, optional
        If True, randomly downsample the dataset to 500 poles to reduce clutter. 
        Ignored if number of poles is less than 500. Default is False.

    Notes
    -----
    - Poles are plotted using lower-hemisphere projection.
    - Density contours reflect orientation clustering using kernel density estimation.
    """
    marker_size = 4
    contour_cmap = "Greys"
    if density:
        ax.density_contourf(
            strike,
            dip,
            measurement='poles',
            cmap=contour_cmap,
            alpha=0.75
        )

    if poles:
        num_points = len(strike)
        if reduce:
            idx = random.choices(range(num_points), k=500)
            strike = strike[idx]
            dip = dip[idx]
 
        ax.pole(
            strike,
            dip,
            color=color,
            markersize=marker_size,
            markeredgecolor="black",
            markeredgewidth=0.5,
            alpha=0.8,
            linestyle="none",
        )


def make_single_family_plots(normals, family_id, color):
    """
    Generate a combined stereonet and rose diagram for a single fracture family.

    Parameters
    ----------
    normals : array-like, shape (N, 3)
        Array of normal vectors representing fracture plane orientations.

    family_id : int or str
        Identifier for the fracture family. Used in plot titles.

    color : str
        Color used for both the stereonet poles and the rose diagram bars.

    Notes
    -----
    - The function internally converts normal vectors to strike and dip.
    - The stereonet (left panel) displays fracture poles and optionally density contours.
    - The rose diagram (right panel) shows axial strike distribution using equal-area scaling.
    - The layout consists of a side-by-side (1 row x 2 columns) subplot figure.
    - Axial symmetry (0–180°) is applied in the rose diagram.
    """
    strikes, dip, _ = normals_to_strike_dip(normals)

    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(121, projection='stereonet')
    ax1.grid()
    ax2 = fig.add_subplot(122, projection='polar')

    plot_stereonet(ax = ax1, strike = strikes, 
                   dip = dip, color = color) 

    ax1.set_title(
        f"Family {family_id} - Fracture Poles",
        fontweight="bold",
        pad=20,
        y=1.05
    )

    plot_rose_diagram(ax = ax2, strikes_deg=strikes, 
                      color = color)

    # Formatting
    ax2.set_theta_zero_location("N")
    ax2.set_theta_direction(-1)
    ax2.set_thetagrids(np.arange(0, 360, 30))
    title = f"Rose Diagram (Strike)\nFamily: {family_id}"
    ax2.set_title(title, y=1.10, fontsize=16)


def make_all_family_plots(params, families, fractures):
    """
    Generate a combined stereonet and rose diagram summarizing all fracture families.

    This function:
    - Aggregates orientations of all non-removed fractures.
    - Plots a background density contour from all orientations.
    - Overlays each family’s poles and rose diagram using unique colors.
    - Saves the resulting plot as `network_orientations.png`.

    Parameters
    ----------
    params : dict
        Dictionary of run-time parameters. Must contain:
        - 'output_dir' : str
            Directory path to save the output figure.
        - 'verbose' : bool
            If True, logs progress to console.

    families : list of dict
        List of fracture family definitions. Each dictionary must contain:
        - 'final_number_of_fractures' : int
            Number of accepted fractures in the family.
        - 'fracture list - final' : list[int]
            Indices of fractures belonging to the family.
        - 'color' : str
            Color used for plotting this family’s data.

    fractures : list of dict
        List of individual fracture records. Each must contain:
        - 'removed' : bool
            Whether the fracture was rejected.
        - 'family' : int
            Family ID (should be > 0 if valid).
        - 'normal' : array-like
            3D normal vector of the fracture plane.

    Notes
    -----
    - The stereonet shows:
        - Density contours from all fracture orientations (grayscale).
        - Poles for each family (colored and optionally reduced).
    - The rose diagram shows:
        - Equal-area rose plots for each family, overlaid with different colors.
    - Output file is saved to `{output_dir}/network/network_orientations.png`.
    """
    total_fractures = 0
    for fam in families:
        total_fractures += fam["final_number_of_fractures"]

    normal_vectors = np.zeros((total_fractures, 3))
    accepted_cnt = 0

    for f in fractures:
        if not f["removed"] and f["family"] > 0:
            normal_vectors[accepted_cnt, :] = f["normal"]
            accepted_cnt += 1
    all_strikes, all_dips, _ = normals_to_strike_dip(normal_vectors)

    # Build figure
    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(121, projection='stereonet')
    ax1.grid()
    ax2 = fig.add_subplot(122, projection='polar')

    # Make density contours with all orienations
    plot_stereonet(ax = ax1, strike = all_strikes, 
        dip = all_dips, color = None, poles=False)
        
    for fam in families:
        # plots poles for each fracture
        normal_vectors = get_normal_vectors(fam, fractures)
        strikes, dips, _ = normals_to_strike_dip(normal_vectors)
        plot_stereonet(ax = ax1, strike = strikes, 
                dip = dips, color = fam["color"], density=False, reduce = True)
        # roses for all! 
        plot_rose_diagram(ax = ax2, strikes_deg=strikes, 
                          color = fam["color"])

    # Formatting
    ax1.set_title(
        f"Fracture Poles",
        fontweight="bold",
        pad=20,
        y=1.05
    )

    ax2.set_theta_zero_location("N")
    ax2.set_theta_direction(-1)
    ax2.set_thetagrids(np.arange(0, 360, 30))
    title = f"Rose Diagram (Strike)"
    ax2.set_title(title, y=1.10, fontsize=16)

    fileout = f"network_orientations.png"
    if params["verbose"]:
        local_print_log(f"--> Saving File {fileout}")

    plt.savefig(f"{params['output_dir']}/network/{fileout}")
    plt.clf()
    plt.close()


def plot_fracture_orientations(params, families, fractures):
    """ Creates Stereonets and Rose Diagrams for Fractures by family and the entire network. mplstereonet provides lower-hemisphere equal-area and equal-angle sterenotes for matplotlib. 

    Parameters
    ------------
        params : dictionary
            General dictionary of output analysis code. Contains information on number of families, number of fractures, and colors.

        families: list of fracture family dictionaries
            Created by get_family_information

        fractures: list of fracture dictionaries   
            Created by get_fracture_information

    Returns
    --------
        None

    Notes
    -------
        PDF files are dumped into dfnGen_output_report/figures. There is one figure for all fractures (all_fracture_centers.pdf) and one per family family_{family_id}_fracture_centers.pdf. 
    """

    local_print_log("\n--> Plotting Rose Diagrams and Stereonets: Starting")


    for fam in families:
        family_id = fam["Global Family"]
        if params["verbose"]: local_print_log(f"--> Working on fracture family {family_id}")
        # Gather Fracture information
        normal_vectors = get_normal_vectors(fam, fractures)
        make_single_family_plots(normal_vectors,family_id, fam["color"])

        plt.savefig(f"{params['output_dir']}/family_{family_id}/family_{family_id}_orienations.png")
        plt.clf()
        plt.close()

    if params["verbose"]: local_print_log("--> Plotting Entire Network Stereonet")
    
    make_all_family_plots(params, families, fractures) 

    local_print_log("--> Plotting Rose Diagrams and Stereonets: Complete\n")
