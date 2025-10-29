"""
  :filename: plot_fracture_centers.py
  :synopsis: Make plots of fracture centers for the entire network and by family
  :version: 1.0
  :maintainer: Jeffrey Hyman
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
"""

import matplotlib.pylab as plt
from pydfnworks.general.logging import local_print_log 


def plot_fracture_centers(params, families, fractures):
    """ Creates histogram plots of fracture centers in the domain. First all fractures are plotted, then by family.

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

    local_print_log("--> Plotting Fracture Locations")

    for fam in families:
        family_id = fam["Global Family"]
        if params["verbose"]:
            local_print_log(f"--> Working on fracture family {family_id}")
        fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(10, 7))

        for coord in ["x", "y", "z"]:
            values_all = []
            values_accepted = []
            if params["verbose"]:
                local_print_log(f"--> Working on {coord} coordinates ")

            for i in fam["fracture list - all"]:
                values_all.append(fractures[i]["center"][coord])

            for i in fam["fracture list - final"]:
                values_accepted.append(fractures[i]["center"][coord])

            # Come up with some smart way to get a good number of bins.
            # This seems okay for now
            num_bins = max(35, int(len(values_accepted) / 100))
            # Pick axis for each component.
            if coord == "x":
                i = 0
                j = 0
            elif coord == "y":
                i = 0
                j = 1
            elif coord == "z":
                i = 1
                j = 0

            tmp = [min(values_all), -0.5 * params["domain"][coord]]
            min_val = min(tmp)
            tmp = [max(values_all), 0.5 * params["domain"][coord]]
            max_val = max(tmp)

            # Create and plot histograms
            axs[i, j].hist(values_all,
                           bins=num_bins,
                           color=params["all_color"],
                           range=(min_val, max_val),
                           alpha=0.7,
                           edgecolor="k",
                           linewidth=0.5)

            axs[i, j].hist(values_accepted,
                           bins=num_bins,
                           color=params["final_color"],
                           range=(min_val, max_val),
                           alpha=0.7,
                           edgecolor="k",
                           linewidth=0.5)

            # Put in family region boundaries
            if fam["Layer"]:
                if coord == "z":
                    axs[i, j].axvline(fam[f"{coord}_min"], c="k", ls="--")
                    axs[i, j].axvline(fam[f"{coord}_max"], c="k", ls="--")

            elif fam["Region"]:
                axs[i, j].axvline(fam[f"{coord}_min"], c="k", ls="--")
                axs[i, j].axvline(fam[f"{coord}_max"], c="k", ls="--")

            # Always include domain boundaries
            axs[i, j].axvline(-0.5 * params["domain"][coord], c="k")
            axs[i, j].axvline(0.5 * params["domain"][coord], c="k")

            # Title and Axis
            axs[i, j].set_title(f"Fracture Centers: {coord}-Coordinate",
                                fontsize=18)
            axs[i, j].set_xlabel("Location [m]", fontsize=14)
            axs[i, j].set_ylabel("Number of Fractures", fontsize=14)
            # Clean up memory
            del values_all, values_accepted

        # Create Legend in final subplot (lower right)
        axs[1, 1].set_frame_on(False)
        axs[1, 1].get_xaxis().set_visible(False)
        axs[1, 1].get_yaxis().set_visible(False)
        if fam["Region"]:
            axs[1, 1].plot(0, 0, "k--", label="Region Boundary")
        elif fam["Layer"]:
            axs[1, 1].plot(0, 0, "k--", label="Layer Boundary")

        axs[1, 1].plot(0, 0, "k", label="Domain Boundary")

        axs[1, 1].plot(0,
                       0,
                       params["all_color"],
                       alpha=0.7,
                       linewidth=10,
                       label="All Accepted Fractures")
        axs[1, 1].plot(0,
                       0,
                       params["final_color"],
                       alpha=0.7,
                       linewidth=10,
                       label="Fractures in the Connected Network")
        axs[1, 1].legend(loc="center", fontsize=14, frameon=False)

        fig.tight_layout()
        if family_id > 0:
            fileout = f"family_{family_id}_centers.png"
        else:
            tmp = fam["Distribution"]
            fileout = f"family_{tmp}_centers.png"

        if params["verbose"]:
            local_print_log(f"--> Saving File {fileout}")
        plt.savefig(f"{params['output_dir']}/family_{family_id}/{fileout}")
        plt.clf()
        plt.close()

        if params["verbose"]:
            local_print_log("--> Complete")

    # Make plots of all fractures
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(10, 7))
    for coord in ["x", "y", "z"]:
        if params["verbose"]:
            local_print_log(f"--> Working on {coord} coordinates ")

        for fam in families:
            values_all = []
            values_accepted = []

            family_id = fam["Global Family"]

            # for i in fam["fracture list - all"]:
            #     values_all.append(fractures[i]["center"][coord])

            for i in fam["fracture list - final"]:
                values_accepted.append(fractures[i]["center"][coord])

            # Come up with some smart way to get a good number of bins.
            # This seems okay for now
            num_bins = max(35, int(len(values_accepted) / 100))
            # Pick axis for each component.
            if coord == "x":
                i = 0
                j = 0
            elif coord == "y":
                i = 0
                j = 1
            elif coord == "z":
                i = 1
                j = 0

            min_val = -0.5 * params["domain"][coord]
            max_val = 0.5 * params["domain"][coord]
            # Create and plot histograms
            axs[i, j].hist(values_accepted,
                           bins=num_bins,
                           color=fam["color"],
                           range=(min_val, max_val),
                           alpha=0.7,
                           edgecolor="k",
                           linewidth=0.5)

            # Always include domain boundaries
            axs[i, j].axvline(-0.5 * params["domain"][coord], c="k")
            axs[i, j].axvline(0.5 * params["domain"][coord], c="k")

            # Title and Axis
            axs[i, j].set_title(f"Fracture Centers: {coord}-Coordinate",
                                fontsize=18)
            axs[i, j].set_xlabel("Location [m]", fontsize=14)
            axs[i, j].set_ylabel("Number of Fractures", fontsize=14)
            # Clean up memory
            del values_all, values_accepted

    # Create Legend in final subplot (lower right)
    axs[1, 1].set_frame_on(False)
    axs[1, 1].get_xaxis().set_visible(False)
    axs[1, 1].get_yaxis().set_visible(False)

    xy_coords = []
    for i in range(8, 0, -1):
        for j in [1, 3.5, 6]:
            xy_coords.append((j, i))

    axs[1, 1].plot([2, 3], [9, 9], "k", linewidth=5)
    axs[1, 1].text(x=3.25, y=8.9, s=f"Domain Boundary", fontsize="14")

    for i, fam in enumerate(families):
        xx = [xy_coords[i][0], xy_coords[i][0] + 1.5]
        yy = [xy_coords[i][1], xy_coords[i][1]]
        axs[1, 1].plot(xx, yy, linewidth=20, alpha=0.4, color=fam["color"])
        axs[1, 1].text(x=xy_coords[i][0] + 0.15,
                       y=xy_coords[i][1] - 0.15,
                       s=f"Family {fam['Global Family']}",
                       fontsize="14")

    axs[1, 1].axis([0.5, 8.5, xy_coords[i][1] - 1, 10])

    fig.tight_layout()

    fileout = f"all_fracture_centers.png"

    if params["verbose"]:
        local_print_log(f"--> Saving File {fileout}")
    plt.savefig(f"{params['output_dir']}/network/{fileout}")
    plt.clf()
    plt.close()

    if params["verbose"]:
        local_print_log("--> Complete")
