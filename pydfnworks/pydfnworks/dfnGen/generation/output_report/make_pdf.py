"""
:filename: make_pdf.py
:synopsis: Combines figures and network information to make the output report pdf
:version: 1.0
:maintainer: Jeffrey Hyman 
:moduleauthor: Jeffrey Hyman <jhyman@lanl.gov>
"""

from fpdf import FPDF
import os

# paths for icons.
absolute_path = os.path.dirname(os.path.abspath(__file__))
relative_path = "/figures/dfnWorks.all.black.png"
dfnworks_image_black = absolute_path + relative_path

absolute_path = os.path.dirname(os.path.abspath(__file__))
relative_path = "/figures/lanl-logo-footer.png"
lanl_image = absolute_path + relative_path

from pydfnworks.general.logging import local_print_log 



class PDF(FPDF):
    """
    Custom PDF class for dfnGen output report, extending FPDF to include
    a consistent header and footer for each page.
    """
    global name

    def header(self):
        """
        Override of FPDF.header()

        Adds logos and a title to the top of each page.

        The dfnWorks logo is placed at the top-left, the LANL footer logo
        at the top-right, and the report title with the job name is centered.
        """
        self.image(dfnworks_image_black, x=5, y=8, w=50)
        self.set_font('Times', 'B', 18)
        self.text(x=100, y=10, txt=f'dfnGen Output Report: {name}')
        self.image(lanl_image, x=240, y=2, w=50)

    def footer(self):
        """
        Override of FPDF.footer()

        Adds a page number at the bottom-center of each page.

        Positions the cursor 1.5 cm from the bottom, sets an italic font, 
        and writes 'Page X'.
        """
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Times', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')


def add_table_of_contents(params, pdf):
    """Creates the Table of Contents page in the PDF.

    Parameters
    ------------
        params : dict
            General dictionary of output report parameters. Contains information
            on number of families, output directory, and verbosity.
        pdf : FPDF
            The current PDF object to which the TOC will be added.

    Returns
    ---------
        FPDF
            The PDF object with the TOC page appended.

    Notes
    ------
        None
    """

    if params["verbose"]:
        local_print_log("--> Making Table of Contents")

    pdf.add_page()
    pdf.image(f"{params['output_dir']}/network/network_orientations.png",
              x=90,
              y=50,
              w=200)
    pdf.text(x=10, y=50, txt="Page 1: Table of Contents")
    pdf.text(x=10, y=60, txt="Page 2: Network Summary")
    for i in range(1, params["num_families"] + 1):
        pdf.text(x=10, y=60 + i * 10, txt=f"Page {2+i}: Family Number {i}")
    pdf.text(x=10,
             y=60 + (params["num_families"] + 1) * 10,
             txt=f"Page {3+params['num_families']}: FRAM information")

    return pdf


def create_network_text(params):
    """Creates the descriptive text block for the overall network summary.
    
    Parameters
    -------------
        params : dictionary
            Output report dictionary containing general network parameters.

    Returns
    -----------
        text : string
            A multi-line string detailing job name, counts, P30/P32 metrics, and domain extents.

    Notes
    --------
        None

    """
    text = f'Jobname: {params["jobname"]}\n\
Number of fracture families:\t{params["num_families"]}\n\
Total number of fractures:\t{params["num_total_fractures"]}\n\
Fractures in connected network:\t{params["num_accepted_fractures"]}\n\
Domain (m)\n\
    x : {-0.5 * params["domain"]["x"]} x {0.5 * params["domain"]["x"]}\
  y : {-0.5 * params["domain"]["y"]} x {0.5 * params["domain"]["y"]} \
  z : {-0.5 * params["domain"]["z"]} x {0.5 * params["domain"]["z"]}\n'

    text += f'Entire Network:\n'
    text += f'    P30: {params["Pre-Iso Total Fracture Density   (P30)"]:0.2e}  /  '
    text += f'P32 : {params["Pre-Iso Total Fracture Intensity (P32)"]:0.2e}  /  '
    # text += f'P33: {params["Pre-Iso Total Fracture Porosity  (P33)"]:0.2e}\n'

    text += f'Connected Network:\n'
    text += f'    P30: {params["Post-Iso Total Fracture Density   (P30)"]:0.2e}  /  '
    text += f'P32: {params["Post-Iso Total Fracture Intensity (P32)"]:0.2e}  /  '
    # text += f'P33: {params["Post-Iso Total Fracture Porosity  (P33)"]:0.2e}\n'

    return text


def add_network_page(params, pdf):
    """Adds the network summary page to the PDF.

    Parameters
    ------------
        params : dictionary
            General dictionary of output report parameters.
        
        pdf : FPDF
            The current PDF object to which the page will be added.

    Returns
    ---------
        FPDF
            The PDF object with the network summary page appended.

    Notes
    ------
        None
    """

    # All Fractures
    if params["verbose"]:
        local_print_log(f"--> Working on Entire Network")
    pdf.add_page()
    pdf.text(x=120, y=20, txt=f'Network Summary')

    pdf.image(f"{params['output_dir']}/network/all_fracture_centers.png",
              x=10,
              y=30,
              w=140)
    pdf.image(f"{params['output_dir']}/network/network_all_radii.png",
              x=150,
              y=27,
              w=140)
    pdf.image(f"{params['output_dir']}/network/network_orientations.png",
              x=0,
              y=130,
              w=150)

    text = create_network_text(params)

    pdf.set_xy(x=165, y=110)
    pdf.set_font('Times', size=14)
    pdf.multi_cell(0, 7, text, 1)

    return pdf


def create_family_text(family):
    """Creates the descriptive text block for a single fracture family.
    

    Parameters
    -------------
        family : dictionary
            Dictionary of parameters for the fracture family.

    Returns
    -----------
        text : string
            A multi-line string detailing counts, shape, distribution parameters, orientation, and P32 results. 

    Notes
    --------
        None

    """
    keys = family.keys()
    dist = family["Distribution"]
    text = f'Number of Fractures: {family["final_number_of_fractures"]}, Shape: {family["Shape"]}\n'
    text += f'Radii Distribution: {dist}\n'
    if dist == 'Truncated Power-Law':
        text += f'\t - alpha: {family["Alpha"]}\n'
    elif dist == 'Lognormal':
        text += f'\t - mu: {family["Mean"]}, sigma: {family["Standard Deviation"]}\n'
    elif dist == 'Exponential':
        text += f'\t - lambda: {family["Lambda"]}\n'
    if dist != "Constant":
        text += f'\t - Min. Radius: {family["Minimum Radius (m)"]} m, Max. Radius: {family["Maximum Radius (m)"]} m\n'
    if "Kappa2" in keys:
        if "Theta-deg" in keys:
            text += f'Bingham Distribution\nOrientation - Kappa1: {family["Kappa1"]}, Kappa2: {family["Kappa2"]}\nTheta-deg: {family["Theta-deg"]}, Phi-deg: {family["Phi-deg"]}\n'
        elif "Trend-deg" in keys:
            text += f'Bingham Distribution\nOrientation - Kappa1: {family["Kappa1"]}, Kappa2: {family["Kappa2"]}\nTrend-deg: {family["Trend-deg"]}, Plunge-deg: {family["Plunge-deg"]}\n'
        elif "Dip-deg" in keys:
            text += f'Bingham Distribution\nOrientation - Kappa1: {family["Kappa1"]}, Kappa2: {family["Kappa2"]}\nDip-deg: {family["Dip-deg"]}, Strike-deg: {family["Strike-deg"]}\n'
    else:
        if "Theta-deg" in keys:
            text += f'Fisher Distribution\nOrientation - Kappa: {family["Kappa"]}\nTheta-deg: {family["Theta-deg"]}, Phi-deg: {family["Phi-deg"]}\n'
        elif "Trend-deg" in keys:
            text += f'Fisher Distribution\nOrientation - Kappa: {family["Kappa"]}\nTrend-deg: {family["Trend-deg"]}, Plunge-deg: {family["Plunge-deg"]}\n'
        elif "Dip-deg" in keys:
            text += f'Fisher Distribution\nOrientation - Kappa: {family["Kappa"]}\nDip-deg: {family["Dip-deg"]}, Strike-deg: {family["Strike-deg"]}\n'
    if "P32 (Fracture Intensity) Target" in keys:
        text += f'Target P32: {family["P32 (Fracture Intensity) Target"]}, Final P32: {family["Post-Iso Fracture Intensity (P32)"]}'
    else:
        text += f'Final P32: {family["Post-Iso Fracture Intensity (P32)"]}\n'
    return text


def add_family_page(params, family, i, pdf):
    """Adds a page for a single fracture family to the PDF.

    Parameters
    ------------
        params : dict
            General dictionary of output report parameters.
        family : dict
            Dictionary of information about a specific fracture family.
        i : int
            Family index (1-based) used for titling and file paths.
        pdf : FPDF
            The current PDF object to which the page will be added.

    Returns
    ---------
        FPDF
            The PDF object with the family page appended.

    Notes
    ------
        None
    """

    if params["verbose"]:
        local_print_log(f"--> Working on Family {family['Global Family']}")
    pdf.add_page()
    pdf.text(x=120, y=20, txt=f'Fracture Family Number {i}')
    pdf.image(f"{params['output_dir']}/family_{i}/family_{i}_centers.png",
              x=5,
              y=30,
              w=140)
    if family["Distribution"] != "Constant":
        pdf.image(f"{params['output_dir']}/family_{i}/family_{i}_radii.png",
                  x=160,
                  y=30,
                  w=140)
    pdf.image(f"{params['output_dir']}/family_{i}/family_{i}_orienations.png",
              x=0,
              y=130,
              w=140)
    text = create_family_text(family)
    pdf.set_xy(x=165, y=130)
    pdf.set_font('Times', size=14)
    pdf.multi_cell(0, 7, text, 1)
    return pdf


def add_fram_page(params, pdf):
    """Adds a page displaying FRAM algorithm information.

    Parameters
    ------------
        params : dict
            General dictionary of output report parameters.
        pdf : FPDF
            The current PDF object to which the page will be added.

    Returns
    ---------
        FPDF
            The PDF object with the FRAM information page appended.

    Notes
    ------
        None
    """

    if params["verbose"]:
        local_print_log("--> FRAM information")

    pdf.add_page()
    pdf.text(x=120, y=20, txt=f'FRAM Information')
    pdf.image(f"{params['output_dir']}/network/fram_information.png",
              x=20,
              y=40,
              w=280)
    return pdf


def make_pdf(params, families, fractures):
    """Combines plots and information to generate the final output report PDF.

    Parameters
    ------------
        params : dict
            General dictionary of output report parameters.
        families : list of dict
            List of fracture family dictionaries, as returned by get_family_information().
        fractures : list of dict
            List of fracture dictionaries, as returned by get_fracture_information().

    Returns
    --------
        None

    Notes
    -------
        The generated PDF is written to '{jobname}_output_report.pdf' in the current directory.

    """

    local_print_log("--> Combing Images and Making PDF")
    # print(absolute_path)
    # print("here")
    # name needs to be a global so it's in the header of each page in the PDF
    global name
    name = params["jobname"]

    pdf = PDF(orientation="L")
    pdf = add_table_of_contents(params, pdf)
    pdf = add_network_page(params, pdf)

    # Family Information
    for i in range(1, params["num_families"] + 1):
        pdf = add_family_page(params, families[i - 1], i, pdf)

    pdf = add_fram_page(params, pdf)

    # Save PDF
    pdf.output(f"{name}_output_report.pdf", "F")

