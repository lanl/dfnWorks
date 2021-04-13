"""
  :filename: plot_fracture_radii.py
  :synopsis: Make plots of fracture radii for the entire network and by family. Plots of the expected analytic distributions are included in the plots for each family
  :version: 1.0
  :maintainer: Jeffrey Hyman 
  :moduleauthor: Jeffrey Hyman <jhyman@lanl.gov>
"""

import numpy as np
import matplotlib.pylab as plt

from pydfnworks.dfnGen.generation.output_report.distributions import create_ecdf, tpl, lognormal, exponential


def plot_fracture_radii(params, families, fractures, num_bins=20):
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
        PDF files are dumped into family/figures. There is one figure for all fractures dfnGen_output_report/networks/all_fracture_centers.pdf and one per family dfnGen_output_report/family_{family_id}/family_{family_id}_fracture_centers.pdf. 
    """

    # This keep track of the max/min radius in the entire network
    min_radius = None
    max_radius = None

    print("--> Plotting Fracture Radii Distributions")

    for fam in families:
        if fam["Distribution"] != "Constant" and fam["Global Family"] > 0:
            family_id = fam["Global Family"]
            dist = fam["Distribution"]
            if params["verbose"]:
                print(
                    f"--> Working on family {family_id} which has a {dist} distribution of radii."
                )

            # Get analytic distributions
            if fam["Distribution"] == 'Truncated Power-Law':
                x, pdf, cdf = tpl(fam["Alpha"], fam["Minimum Radius (m)"],
                                  fam["Maximum Radius (m)"])

            elif fam["Distribution"] == 'Lognormal':
                x, pdf, cdf = lognormal(fam["Mean"], fam["Standard Deviation"],
                                        fam["Minimum Radius (m)"],
                                        fam["Maximum Radius (m)"])

            elif fam["Distribution"] == 'Exponential':
                x, pdf, cdf = exponential(fam["Lambda"],
                                          fam["Minimum Radius (m)"],
                                          fam["Maximum Radius (m)"])

            # Gather family radii
            radii_all = []
            for i in fam["fracture list - all"]:
                radii_all.append(fractures[i]["x-radius"])
            radii_accepted = []
            for i in fam["fracture list - final"]:
                radii_accepted.append(fractures[i]["x-radius"])

            #print(f"Mean: {np.mean(radii_all)}, Variance: {np.var(radii_all)}")
            min_val = min(min(radii_all), min(radii_accepted))
            max_val = max(max(radii_all), max(radii_accepted))
            # Get global min/max radius
            if min_radius is None:
                min_radius = min_val
            else:
                min_radius = min(min_radius, min_val)

            if max_radius is None:
                max_radius = max_val
            else:
                max_radius = max(max_radius, max_val)

            fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(10, 7))
            # Create and plot histograms
            axs[0, 0].hist(radii_all,
                           bins=num_bins,
                           color=params["all_color"],
                           range=(min_val, max_val),
                           alpha=0.7,
                           edgecolor="k",
                           linewidth=0.5,
                           density=True,
                           label=f"All Accepted Fractures")

            axs[0, 0].plot(x,
                           pdf,
                           params["analytic_color"],
                           label="Analytical PDF")

            #axs[0, 0].legend(loc="upper right", fontsize=14)
            axs[0, 0].grid(True, alpha=0.5)
            axs[0, 0].set_xlabel("Fracture Radius [m]", fontsize=18)
            axs[0, 0].set_ylabel("Density", fontsize=18)

            ticks = axs[0, 0].get_xticks()
            labels = [f"{val:0.2f}" for val in ticks]
            axs[0, 0].set_xticks(ticks)
            axs[0, 0].set_xticklabels(labels, fontsize=14)
            axs[0, 0].set_xlim((0.9*fam["Minimum Radius (m)"], 1.05*fam["Maximum Radius (m)"]))
  
            ticks = axs[0, 0].get_yticks()
            labels = [f"{val:0.2f}" for val in ticks]
            axs[0, 0].set_yticklabels(labels, fontsize=14)

            # Histogram of final values
            axs[0, 1].hist(radii_accepted,
                           bins=num_bins,
                           color=params["final_color"],
                           range=(min_val, max_val),
                           alpha=0.7,
                           edgecolor="k",
                           linewidth=0.5,
                           density=True,
                           label=f"Fractures in the Connected Network")

            axs[0, 1].plot(x,
                           pdf,
                           params["analytic_color"],
                           label="Analytical PDF")
            #axs[0, 1].legend(loc="upper right", fontsize=14)
            axs[0, 1].grid(True, alpha=0.5)
            axs[0, 1].set_xlabel("Fracture Radius [m]", fontsize=18)
 
            ticks = axs[0, 1].get_xticks()
            labels = [f"{val:0.2f}" for val in ticks]
            axs[0, 1].set_xticks(ticks)
            axs[0, 1].set_xticklabels(labels, fontsize=14)
            axs[0, 1].set_xlim((0.9*fam["Minimum Radius (m)"], 1.05*fam["Maximum Radius (m)"]))
  
            ticks = axs[0, 1].get_yticks()
            labels = [f"{val:0.2f}" for val in ticks]
            axs[0, 1].set_yticklabels(labels, fontsize=14)

            # ECDF
            axs[1, 0].plot(x,
                           cdf,
                           params["analytic_color"],
                           label="Analytical CDF")
            y, ecdf = create_ecdf(radii_all)
            axs[1, 0].plot(y,
                           ecdf,
                           label="All Fractures CDF",
                           color=params["all_color"])
            y, ecdf = create_ecdf(radii_accepted)
            axs[1, 0].plot(y,
                           ecdf,
                           label="Final Fractures CDF",
                           color=params["final_color"])

            #axs[1, 0].legend(loc="lower right", fontsize=14)
            axs[1, 0].grid(True, alpha=0.5)
            axs[1, 0].set_xlabel("Fracture Radius [m]", fontsize=18)
            axs[1, 0].set_ylabel("Cumulative Density", fontsize=18)
            # Set Tick Labels
            ticks = axs[1, 0].get_xticks()
            labels = [f"{val:0.2f}" for val in ticks]
            axs[1, 0].set_xticks(ticks)
            axs[1, 0].set_xticklabels(labels, fontsize=14)
            axs[1, 0].set_xlim((0.9*fam["Minimum Radius (m)"], 1.05*fam["Maximum Radius (m)"]))
  
            ticks = axs[1, 0].get_yticks()
            labels = [f"{val:0.2f}" for val in ticks]
            axs[1, 0].set_yticklabels(labels, fontsize=14)

            ###### Legend it plotted in the bottom right corner rather than in each subplot.
            axs[1, 1].set_frame_on(False)
            axs[1, 1].get_xaxis().set_visible(False)
            axs[1, 1].get_yaxis().set_visible(False)
            axs[1, 1].plot(0,
                           0,
                           params["all_color"],
                           linewidth=4,
                           label="All Accepted Fractures")
            axs[1, 1].plot(0,
                           0,
                           params["final_color"],
                           linewidth=4,
                           label="Fractures in the Connected Network")
            axs[1, 1].plot(0,
                           0,
                           params["analytic_color"],
                           linewidth=4,
                           label="Analytic Value")
            axs[1, 1].legend(loc="center", fontsize=18, frameon=False)

            fig.tight_layout()
            if family_id > 0:
                fileout = f"family_{family_id}_radii.png"
            else:
                tmp = fam["Distribution"]
                fileout = f"family_{tmp}_radii.png"

            if params["verbose"]:
                print(f"--> Saving File {fileout}")
            plt.savefig(f"{params['output_dir']}/family_{family_id}/{fileout}")
            plt.clf()
            plt.close()

    # Plotting all fractures
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))
    for fam in families:
        if fam["Global Family"] > 0 and fam["Distribution"] != "Constant":
            family_id = fam["Global Family"]

            # Gather family radii
            radii_all = []
            for i in fam["fracture list - all"]:
                radii_all.append(fractures[i]["x-radius"])
            radii_accepted = []
            for i in fam["fracture list - final"]:
                radii_accepted.append(fractures[i]["x-radius"])

            min_val = min(min(radii_all), min(radii_accepted))
            max_val = max(max(radii_all), max(radii_accepted))

            # Create and plot histograms
            axs[0].hist(radii_all,
                        bins=num_bins,
                        color=fam["color"],
                        range=(min_radius, max_radius),
                        alpha=0.7,
                        edgecolor="k",
                        linewidth=0.5,
                        label=f"Family \# {family_id}")

            # Histogram of final values
            axs[1].hist(radii_accepted,
                        bins=num_bins,
                        color=fam["color"],
                        range=(min_radius, max_radius),
                        alpha=0.7,
                        edgecolor="k",
                        linewidth=0.5,
                        label=f"Family \# {family_id}")

    axs[0].grid(True, alpha=0.5)
    axs[0].set_title("All Accepted Fractures", fontsize=24)
    axs[0].set_xlabel("Fracture Radius [m]", fontsize=24)
    axs[0].set_ylabel("Fracture Count", fontsize=24)
    axs[0].set_xticklabels(axs[0].get_xticks().astype(int), fontsize=14)
    axs[0].set_yticklabels(axs[0].get_yticks().astype(int), fontsize=14)

    axs[1].grid(True, alpha=0.5)
    axs[1].set_title("Fractures in the Connected Network", fontsize=24)
    axs[1].set_xlabel("Fracture Radius [m]", fontsize=24)
    axs[1].set_xticklabels(axs[1].get_xticks().astype(int), fontsize=14)
    axs[1].set_yticklabels(axs[1].get_yticks().astype(int), fontsize=14)
    axs[1].axis([
        axs[0].get_xlim()[0], axs[0].get_xlim()[1], axs[0].get_ylim()[0],
        axs[0].get_ylim()[1]
    ])
    plt.savefig(f"{params['output_dir']}/network/network_all_radii.png")
    plt.clf()
    plt.close()
