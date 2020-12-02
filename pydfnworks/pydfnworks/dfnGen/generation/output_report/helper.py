"""
  :filename: helper.py
  :synopsis: Helper function for output report generation. 
  :version: 1.0
  :maintainer: Jeffrey Hyman
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
"""


def load_colors():
    """ Loads a preselected list of colors for the output report. 

    Parameters
    -----------
      None

    Returns
    ---------
      colors : list
        list of 20 colors

    Notes
    ------
      None

    """
    colors = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
              (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
              (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
              (227, 119, 194), (247, 182, 210), (127, 127, 127),
              (199, 199, 199), (188, 189, 34), (219, 219, 141), (23, 190, 207),
              (158, 218, 229)]

    # Rescale to values between 0 and 1
    for i in range(len(colors)):
        r, g, b = colors[i]
        colors[i] = (r / 255., g / 255., b / 255.)

    return colors
