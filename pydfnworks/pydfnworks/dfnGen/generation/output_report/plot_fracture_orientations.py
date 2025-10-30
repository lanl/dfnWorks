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


def convert_to_trend_and_plunge(normal_vectors):
    """ Convert fracture normal vectors to trend and plunge

    Parameters
    -----------
        normal_vectors : numpy array
            Array of fracture normal vectors (n-fractures x 3)

    Returns
    ----------
        trends : numpy array
            Array of fracture trends (0–360° azimuths)
        
        plunges : numpy array
            Array of fracture plunges (0–90° below horizontal)

    Notes
    -------
        - Trend: azimuth (clockwise from North) of horizontal projection
        - Plunge: angle below horizontal
        - Assumes input coordinates are (East, North, Up)
    """
    # Normalize all vectors
    norms = np.linalg.norm(normal_vectors, axis=1)
    if np.any(norms == 0):
        raise ValueError("Zero-length vector found in normal_vectors.")
    normal_vectors = normal_vectors / norms[:, np.newaxis]

    # Break up components
    x = normal_vectors[:, 0]  # East
    y = normal_vectors[:, 1]  # North
    z = normal_vectors[:, 2]  # Up

    # Plunge (positive downward)
    plunges = np.degrees(np.arcsin(-z))

    # Trend (azimuth)
    trends = np.degrees(np.arctan2(x, y))
    trends[trends < 0] += 360.0

    return trends, plunges

# def convert_to_trend_and_plunge(normal_vectors):
#     """ Convert Fracture normal vectors to trend and plunge

#     Parameters
#     -----------
#         normal_vectors : numpy array
#             Array of fracture normal vectors (n-fractures x 3)

#     Returns
#     ----------
#         trends : numpy array
#             Array of fracture trends 
        
#         plunge : numpy array
#             Array of fracture plunge

#     Notes
#     -------
#         Conversion is based on the information found at http://www.geo.cornell.edu/geology/faculty/RWA/structure-lab-manual/chapter-2.pdf 

#     """

#     # break up normal vector components
#     n_1 = normal_vectors[:, 0]
#     n_2 = normal_vectors[:, 1]
#     n_3 = normal_vectors[:, 2]

#     # calculate trends and plunges
#     trends = np.zeros(len(n_1))
#     plunges = np.zeros(len(n_1))
#     for i in range(len(n_1)):
#         plunges[i] = m.degrees(m.asin(n_3[i]))
#         if n_1[i] > 0.0:
#             trends[i] = m.degrees(m.atan(n_2[i] / n_1[i]))
#         elif n_1[i] < 0.0:
#             trends[i] = 180.0 + m.degrees(m.atan(n_2[i] / n_1[i]))
#         elif n_1[i] == 0.0 and n_2[i] >= 0.0:
#             trends[i] = 90.0
#         elif n_1[i] == 0.0 and n_2[i] < 0.0:
#             trends[i] = 270.0

#     return trends, plunges


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

    local_print_log("--> Plotting Rose Diagrams and Stereonets")

    # plot all families
    # build stereonets
    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(121, projection='stereonet')
    ax1.grid()
    ax2 = fig.add_subplot(122, projection='polar')

    if params["verbose"]:
        local_print_log("--> Plotting Entire Network Stereonet")
    for fam in families:
        family_id = fam["Global Family"]
        # Gather Fracture information
        normal_vectors = np.zeros((fam["final_number_of_fractures"], 3))
        for i, j in enumerate(fam["fracture list - final"]):
            normal_vectors[i, :] = fractures[j]["normal"]
        ###

        trends, plunges = convert_to_trend_and_plunge(normal_vectors)
        # stuff for rose diagram
        bin_edges = np.arange(-5, 366, 10)
        num_of_trends, bin_edges = np.histogram(trends, bin_edges)
        num_of_trends[0] += num_of_trends[-1]

        half = np.sum(np.split(num_of_trends[:-1], 2), 0)
        two_halves = np.concatenate([half, half])

        ax1.line(plunges[0],
                 trends[0],
                 'o',
                 color=fam["color"],
                 markersize=5,
                 alpha=1.0,
                 label=f"Family \# {family_id}")

        if len(plunges) > 500:
            local_print_log("Too Many Fractures, plotting a subset", 'warning')
            idx = random.choices(range(len(plunges)), k=500)
            ax1.line(plunges[idx],
                     trends[idx],
                     'o',
                     color=fam["color"],
                     markersize=5,
                     alpha=0.5)
        else:
            ax1.line(plunges,
                     trends,
                     'o',
                     color=fam["color"],
                     markersize=5,
                     alpha=0.5)
    if params["verbose"]:
        local_print_log("--> Plotting Densities")

    total_fractures = 0
    for fam in families:
        total_fractures += fam["final_number_of_fractures"]

    normal_vectors = np.zeros((total_fractures, 3))
    accepted_cnt = 0

    for f in fractures:
        if not f["removed"] and f["family"] > 0:
            normal_vectors[accepted_cnt, :] = f["normal"]
            accepted_cnt += 1

    trends, plunges = convert_to_trend_and_plunge(normal_vectors)
    ax1.density_contourf(plunges, trends, measurement='lines', cmap='Greys')
    ax1.set_title('Density contour of trends and plunges (lower-hemisphere)',
                  y=1.10,
                  fontsize=24)
    #ax1.legend(loc="lower left", fontsize=14)

    # plot all families
    # build Rose Diagrams
    if params["verbose"]:
        local_print_log("--> Plotting Entire Network Rose Diagram")
    for fam in families:
        family_id = fam["Global Family"]
        # Gather Fracture information
        normal_vectors = np.zeros((fam["final_number_of_fractures"], 3))
        for i, j in enumerate(fam["fracture list - final"]):
            normal_vectors[i, :] = fractures[j]["normal"]
        ###
        trends, plunges = convert_to_trend_and_plunge(normal_vectors)

        # stuff for rose diagram
        bin_edges = np.arange(-5, 366, 10)
        num_of_trends, bin_edges = np.histogram(trends, bin_edges)
        num_of_trends[0] += num_of_trends[-1]

        half = np.sum(np.split(num_of_trends[:-1], 2), 0)
        two_halves = np.concatenate([half, half])

        ax2.bar(np.deg2rad(np.arange(0, 360,10)), two_halves, \
            width=np.deg2rad(10), bottom = 0.0, color=fam["color"], edgecolor='k')

    ax2.set_theta_zero_location('N')
    ax2.set_theta_direction(-1)
    ax2.set_thetagrids(np.arange(0, 360, 10), labels=np.arange(0, 360, 10))
    ax2.set_title('Rose diagram of trends', y=1.10, fontsize=24)

    fileout = f"network_orientations.png"
    if params["verbose"]:
        local_print_log(f"--> Saving File {fileout}")

    plt.savefig(f"{params['output_dir']}/network/{fileout}")
    plt.clf()
    plt.close()

    # Plot individual families
    for fam in families:
        family_id = fam["Global Family"]
        if params["verbose"]:
            local_print_log(f"--> Working on fracture family {family_id}")

        # Gather Fracture information
        normal_vectors = np.zeros((fam["final_number_of_fractures"], 3))
        for i, j in enumerate(fam["fracture list - final"]):
            normal_vectors[i, :] = fractures[j]["normal"]
        ###
        trends, plunges = convert_to_trend_and_plunge(normal_vectors)

        # stuff for rose diagram
        bin_edges = np.arange(-5, 366, 10)
        num_of_trends, bin_edges = np.histogram(trends, bin_edges)
        num_of_trends[0] += num_of_trends[-1]

        half = np.sum(np.split(num_of_trends[:-1], 2), 0)
        two_halves = np.concatenate([half, half])

        # build stereonets
        fig = plt.figure(figsize=(16, 8))

        ax = fig.add_subplot(121, projection='stereonet')
        ax.grid()
        ax.line(plunges,
                trends,
                'o',
                color=params["final_color"],
                markersize=10,
                alpha=0.7)
        ax.density_contourf(plunges, trends, measurement='lines', cmap='Greys')
        ax.set_title('Density contour of trends and plunges',
                     y=1.10,
                     fontsize=24)
        #ax.grid()

        ax = fig.add_subplot(122, projection='polar')
        ax.bar(np.deg2rad(np.arange(0, 360, 10)),
               two_halves,
               width=np.deg2rad(10),
               bottom=0.0,
               color=params["final_color"],
               edgecolor='k')
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.arange(0, 360, 10), labels=np.arange(0, 360, 10))
        #ax.set_rgrids(np.arange(1, two_halves.max() + 1, two_halves.max()/15), angle=0, weight='black')
        ax.set_title('Rose diagram of trends', y=1.10, fontsize=24)

        if family_id > 0:
            fileout = f"family_{family_id}_orienations.png"
        else:
            tmp = fam["Distribution"]
            fileout = f"family_{family_id}_orienations.png"

        if params["verbose"]:
            local_print_log(f"--> Saving File {fileout}")

        plt.savefig(f"{params['output_dir']}/family_{family_id}/{fileout}")
        plt.clf()
        plt.close()
