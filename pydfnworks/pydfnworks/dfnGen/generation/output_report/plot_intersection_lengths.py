"""
  :filename: gen_output.py
  :synopsis: Main driver for dfnGen output report
  :version: 1.0
  :maintainer: Jeffrey Hyman 
  :moduleauthor: Jeffrey Hyman <jhyman@lanl.gov>
"""

import matplotlib.pylab as plt
import seaborn as sns
import numpy as np


def plot_intersection_lengths(params, families):
    """ Creates PDF plots of fracture intersection lengths in the domain. First all fractures are plotted, then by family.

    Parameters
    ------------
        params : dictionary
            General dictionary of output analysis code. Contains information on number of families, number of fractures, and colors.

        families: list of fracture family dictionaries
            Created by get_family_information


    Returns
    --------
        None

    Notes
    -------
        For larger networks, it can take a long time to sort intersections by family. 

        This function is only called with robust = True

        PDF files are dumped into family/figures. There is one figure for all fractures dfnGen_output_report/networks/ and one per family dfnGen_output_report/family_{family_id}

        Information about intersection modification during generation has not been include yet, but it should be. 
    """

    print("--> Plotting Intersection Distributions")

    # intersection_params = ["    Number of Intersections","    Intersections Shortened",
    # "    Original Intersection (Before Intersection Shrinking) Length",
    # "    Intersection Length Discarded","    Final Intersection Length"]

    data = np.genfromtxt("intersection_list.dat", skip_header=1)
    f1 = data[:, 0]
    f2 = data[:, 1]
    intersection_lengths = data[:, -1]
    f1 = f1.astype(int)
    f2 = f2.astype(int)
    num_intersections = len(f1)
    if params["verbose"]:
        print(f"There are {num_intersections} intersections")
    fig, axs = plt.subplots(figsize=(10, 7))
    sns.kdeplot(intersection_lengths, color="k")
    labs = ["Entire Network"]

    # search for families
    idx = []
    for i in range(num_intersections):
        if params["verbose"] and i % 1000 == 0:
            print(f"--> Intersection number {i}")
        i1 = 0
        i2 = 0
        for fam in families:
            if f1[i] > 0 and f2[i] > 0:
                if f1[i] in fam["fracture list - final"]:
                    i1 = fam['Global Family']
                if f2[i] in fam["fracture list - final"]:
                    i2 = fam['Global Family']
            else:
                i1 = 0
                i2 = 0
        idx.append((i1, i2))

    for fam in families:
        if params["verbose"]:
            print(f"--> Working on family {fam['Global Family']}")
        family_lengths = []
        for i in range(num_intersections):
            if idx[i][0] == fam['Global Family'] or idx[i][1] == fam[
                    'Global Family']:
                family_lengths.append(intersection_lengths[i])

        labs += [f"Family: {fam['Global Family']}"]
        sns.kdeplot(family_lengths, color=fam["color"])

    plt.legend(loc="upper right", labels=labs, fontsize=14)
    plt.xlabel("Intersection Length [m]", fontsize=24)
    plt.ylabel("Density", fontsize=24)
    axs.set_xticklabels(axs.get_xticks().astype(int), fontsize=14)
    ticks = axs.get_yticks()
    labels = [f"{val:0.2f}" for val in ticks]
    axs.set_yticklabels(labels, fontsize=14)
    plt.savefig(f"{params['output_dir']}/network/network_intersections.png")
    plt.close()

    if params["verbose"]:
        print(f"--> Individual Family Plots")

    # individual family plots
    for fam in families:
        fig, axs = plt.subplots(figsize=(10, 7))

        if params["verbose"]:
            print(f"--> Working on family {fam['Global Family']}")
        family_lengths = []
        for i in range(num_intersections):
            if idx[i][0] == fam['Global Family'] or idx[i][1] == fam[
                    'Global Family']:
                family_lengths.append(intersection_lengths[i])

        sns.kdeplot(family_lengths, color=params["final_color"])
        plt.xlabel("Intersection Length [m]", fontsize=24)
        plt.ylabel("Density", fontsize=24)
        axs.set_xticklabels(axs.get_xticks().astype(int), fontsize=16)
        ticks = axs.get_yticks()
        labels = [f"{val:0.2f}" for val in ticks]
        axs.set_yticklabels(labels, fontsize=16)
        plt.savefig(
            f"{params['output_dir']}/family_{fam['Global Family']}/family_{fam['Global Family']}_intersections.png"
        )
        plt.close()
