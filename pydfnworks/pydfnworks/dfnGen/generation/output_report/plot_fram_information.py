"""
  :filename: gen_output.py
  :synopsis: Main driver for dfnGen output report
  :version: 1.0
  :maintainer: Jeffrey Hyman 
  :moduleauthor: Jeffrey Hyman <jhyman@lanl.gov>
"""

import matplotlib.pylab as plt
import numpy as np
from pydfnworks.general.logging import local_print_log

def plot_fram_information(params):
    """ Gathers information from the file 'rejections.dat' about FRAM and creates a bar-chart named fram_information.png 

    Parameters
    -------------
        params : dictionary
            Output report dictionary containing general parameters. See output_report for more details

    Returns
    -----------
        None

    Notes
    --------
        Output image is named fram_information.png in the network sub-directory
        
    """
    # Gather Data
    if params["verbose"]:
        local_print_log("--> Plotting FRAM information")

    rejections = {}
    with open('dfnGen_output/rejections.dat', "r") as fp:
        for line in fp.readlines():
            parsed_line = line.split(": ")
            variable = parsed_line[0]
            value = parsed_line[1].rstrip()
            rejections[variable] = int(value)
    total_number_of_rejections = float(sum(rejections.values()))
    fig, axs = plt.subplots(figsize=(16, 8))
    plt.title("FRAM information")

    labels = []
    cnts = []
    for key in rejections.keys():
        labels.append(key)
        cnts.append(rejections[key])

    cnts = np.asarray(cnts)
    sort_index = np.argsort(cnts)[::-1]
    cnts = cnts[sort_index]
    new_labels = []
    for i in sort_index:
        new_labels.append(labels[i])
    labels = new_labels

    # Make a bar chart!
    y_pos = np.arange(len(labels))
    h = 0.8
    horizBar = axs.barh(y_pos,
                        cnts,
                        color="k",
                        alpha=0.6,
                        height=h,
                        align='center')

    axs.set_yticks(y_pos)
    axs.set_yticklabels(labels, fontsize=14)
    axs.invert_yaxis()  # labels read top-to-bottom
    axs.set_xlabel('Number of re-samples', fontsize=14)
    values_list = axs.get_xticks().astype(int)
    axs.xaxis.set_ticks(values_list)
    axs.set_xticklabels(values_list, fontsize=16)
    axs.grid(alpha=0.1)
    if max(cnts) > 0:
        axs.axis([0, 1.1 * max(cnts), axs.get_ylim()[0], axs.get_ylim()[1]])
    else:
        axs.axis([0, 1, axs.get_ylim()[0], axs.get_ylim()[1]])
    axs.set_title("Re-sampling Histogram", fontsize=18)

    # Add notes to the end of bars
    for bar in horizBar:
        width = bar.get_width()
        if total_number_of_rejections > 0:
            label = f"  {int(width):d}\n  {100*width/total_number_of_rejections:0.2f}\%"
        else:
            label = f"  {int(width):d}\n  0\%" 
        axs.text(bar.get_width() + 2,
                 bar.get_y() + 0.5 * h,
                 label,
                 va='center',
                 fontsize=16)
    plt.savefig(f"{params['output_dir']}/network/fram_information.png")
