import pickle
import numpy as np

def save_network(self, filename=None):
    """ Save current DFNWORKS object to pickled binary. 

    Parameters
    ----------------
      self : object
          DFN Class object
      filename : string
          name of pickled file. If no option is provided, the local jobname will be the prefix


    Returns
    --------
      None

    Notes
    ---------
      Final output report is named "jobname"_output_report.pdf
      User defined fractures (ellipses, rectangles, and polygons) are not supported at this time. 

    """
    if filename is None:
        filename = f"{self.local_jobname}.p"
    print(f"--> Saving dfnWorks object to file {filename}")
    pickle.dump(self, open(filename, 'wb'))
    print(f"--> Completed Saving dfnWorks object to file {filename}")


def load_network(filename):
    """ Load DFNWORKS object from pickled binary. 

    Parameters
    ----------------
      filename : string
          name of pickled file. 

    Returns
    --------
      None

    Notes
    ---------
      None
    """
    from pydfnworks import define_paths
    print(f"--> Loading dfnWorks object from file {filename}")
    define_paths()
    DFN = pickle.load(open(filename, "rb"))
    print(f"--> Loading dfnWorks object from file {filename} complete")
    return DFN

