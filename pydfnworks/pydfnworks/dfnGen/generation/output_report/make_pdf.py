"""
  :filename: make_pdf.py
  :synopsis: Combines figures and network information to make the output report pdf
  :version: 1.0
  :maintainer: Jeffrey Hyman 
  :moduleauthor: Jeffrey Hyman <jhyman@lanl.gov>
"""

from fpdf import FPDF

# NEED TO BE SET TO /Users/jhyman/src
dfnworks_image_black = "DUMMY/dfnworks-main/pydfnworks/pydfnworks/dfnGen/generation/output_report/figures/dfnWorks.all.black.png"
lanl_image = "DUMMY/dfnworks-main/pydfnworks/pydfnworks/dfnGen/generation/output_report/figures/lanl-logo-footer.png"

class PDF(FPDF):
    global name

    def header(self):
        # Logo
        self.image(dfnworks_image_black, x=5, y=8, w=50)
        self.set_font('Times', 'B', 18)
        self.text(x=100, y=10, txt=f'dfnGen Output Report: {name}')
        self.image(lanl_image, x=240, y=2, w=50)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Times', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')


def add_table_of_contents(params, pdf):
    """ Creates Table of contents

    Parameters
    ------------
        params : dictionary
            General dictionary of output analysis code. Contains information on number of families, number of fractures, and colors.
        pdf : fpdf object
            Current working pdf

    Returns
    ---------
        pdf : fpdf object
            Current working pdf

    Notes
    ------
        None
    """

    if params["verbose"]:
        print("--> Making Table of Contents")

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
    """ Creates block text for the entire network.
    

    Parameters
    -------------
        params : dictionary
            Output report dictionary containing general parameters. See output_report for more details

    Returns
    -----------
        text : string
            Block of text with information about the network. 

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
    text += f'P33: {params["Pre-Iso Total Fracture Porosity  (P33)"]:0.2e}\n'

    text += f'Connected Network:\n'
    text += f'    P30: {params["Post-Iso Total Fracture Density   (P30)"]:0.2e}  /  '
    text += f'P32: {params["Post-Iso Total Fracture Intensity (P32)"]:0.2e}  /  '
    text += f'P33: {params["Post-Iso Total Fracture Porosity  (P33)"]:0.2e}\n'

    return text


def add_network_page(params, pdf):
    """ Add page about the entire network
    Parameters
    ------------
        params : dictionary
            General dictionary of output analysis code. Contains information on number of families, number of fractures, and colors.
        pdf : fpdf object
            Current working pdf

    Returns
    ---------
        pdf : fpdf object
            Current working pdf

    Notes
    ------
        None
    """

    # All Fractures
    if params["verbose"]:
        print(f"--> Working on Entire Network")
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
    """ Creates block text for one family
    

    Parameters
    -------------
        family : dictionary
            Fracture family dictionary

    Returns
    -----------
        text : string
            Block of text with information about the family. 

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
    text += f'Orientation - Kappa: {family["Kappa"]}, Theta-deg: {family["Theta-deg"]}, Phi-deg: {family["Phi-deg"]}\n'

    if "P32 (Fracture Intensity) Target" in keys:
        text += f'Target P32: {family["P32 (Fracture Intensity) Target"]}, Final P32: {family["Post-Iso Fracture Intensity (P32)"]}'
    else:
        text += f'Final P32: {family["Post-Iso Fracture Intensity (P32)"]}\n'
    return text


def add_family_page(params, family, i, pdf):
    """ Add page about fracture family. 

    Parameters
    ------------
        params : dictionary
            General dictionary of output analysis code. Contains information on number of families, number of fractures, and colors.
        family : dictionary 
            Dictionary of information about a fracture family
        i : int
            Fracture family id
        pdf : fpdf object
            Current working pdf

    Returns
    ---------
        pdf : fpdf object
            Current working pdf

    Notes
    ------
        None
    """

    if params["verbose"]:
        print(f"--> Working on Family {family['Global Family']}")
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
    """ Add Page about FRAM information 

    Parameters
    ------------
        params : dictionary
            General dictionary of output analysis code. Contains information on number of families, number of fractures, and colors.
        pdf : fpdf object
            Current working pdf

    Returns
    ---------
        pdf : fpdf object
            Current working pdf

    Notes
    ------
        None
    """

    if params["verbose"]:
        print("--> FRAM information")

    pdf.add_page()
    pdf.text(x=120, y=20, txt=f'FRAM Information')
    pdf.image(f"{params['output_dir']}/network/fram_information.png",
              x=20,
              y=40,
              w=280)
    return pdf


def make_pdf(params, families, fractures):
    """ Combines plots and information to make the final output report pdf. 

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
        None

    """

    print("\n--> Combing Images and Making PDF")
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
