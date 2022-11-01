"""
  :filename: gen_output.py
  :synopsis: Main driver for dfnGen output report
  :version: 1.0
  :maintainer: Jeffrey Hyman 
  :moduleauthor: Jeffrey Hyman <jhyman@lanl.gov>
"""

import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pylab as plt
from matplotlib import rc

rc('text', usetex=True)

import pydfnworks.dfnGen.generation.generator
from pydfnworks.dfnGen.generation.output_report.gather_information import *
from pydfnworks.dfnGen.generation.output_report.plot_fracture_orientations import plot_fracture_orientations
from pydfnworks.dfnGen.generation.output_report.plot_fracture_radii import plot_fracture_radii
from pydfnworks.dfnGen.generation.output_report.plot_fracture_centers import plot_fracture_centers
from pydfnworks.dfnGen.generation.output_report.plot_fram_information import plot_fram_information
from pydfnworks.dfnGen.generation.output_report.plot_intersection_lengths import plot_intersection_lengths
from pydfnworks.dfnGen.generation.output_report.make_pdf import make_pdf


def setup_output_directory(params):
    """ Create working dictionary for plots. There is one directory for the entire network information and one for each family.

  Parameters
  ------------
    params : dictionary
      Output report dictionary containing general parameters. See output_report for more details

  Returns
  ---------
    None

  Notes
  --------
    None


  """

    if not os.path.isdir(params["output_dir"]):
        os.mkdir(params["output_dir"])
    if not os.path.isdir(f"{params['output_dir']}/network"):
        os.mkdir(f"{params['output_dir']}/network")
    for i in range(1, params["num_families"] + 1):
        if not os.path.isdir(f"{params['output_dir']}/family_{i}"):
            os.mkdir(f"{params['output_dir']}/family_{i}")


def output_report(self, verbose=True, output_dir="dfnGen_output_report"):
    """ Creates a PDF output report for the network created by DFNGen. Plots of the fracture lengths, locations, orientations are produced for each family. Files are written into "output_dir/family_{id}/". Information about the whole network are also created and written into "output_dir/network/"

  Parameters
  ----------
      self : object
        DFN Class object
      verbose : bool
        Toggle for the amount of information printed to screen. If true, progress information printed to screen
      output_dir : string
        Name of directory where all plots are saved

  Returns
  --------
    None

  Notes
  ---------
    Final output report is named "jobname"_output_report.pdf
    User defined fractures (ellipses, rectangles, and polygons) are not supported at this time. 


  """
    cwd = os.getcwd()
    print("=" * 80)
    print('Creating Report of DFN generation')
    print("=" * 80 + "\n")
    print('--> Gathering Network Information')
    # Create a list of dictionaries with information about fracture family
    families = get_family_information()
    # Create a list of dictionaries with information about fracture
    fractures = get_fracture_information()
    # Combine information of the families and fractures, e.g., which fracture are in each family, and create a dictionary with parameters used throughout the output report
    families, fractures, params = combine_family_and_fracture_information(
        families, fractures, self.num_frac, self.domain)
    params, families = parse_dfn_output(params, families)

    params["verbose"] = verbose
    params["jobname"] = self.local_jobname
    params["output_dir"] = output_dir

    setup_output_directory(params)

    # Create Plots
    if len(families) > 0:
        print('--> Plotting Information')
        plot_fracture_centers(params, families, fractures)
        plot_fracture_radii(params, families, fractures)
        plot_fracture_orientations(params, families, fractures)
        plot_fram_information(params)
        # # Combine plots into a pdf
        make_pdf(params, families, fractures)
        print(
            f"--> Output report is written into {self.local_jobname}_output_report.pdf\n"
        )

    else:
        print(
            "--> There are no stochastic families. An output PDF will not be generated.\n"
        )

    # Return to main directory
    print("=" * 80)
    print("Creating Report of DFN generation complete")
    print("=" * 80 + "\n")
    os.chdir(self.jobname)
