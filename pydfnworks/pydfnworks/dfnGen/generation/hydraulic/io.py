"""
File I/O functions for hydraulic property data.
"""
import numpy as np


def dump_aperture(self, filename, format=None):
    """ Write aperture values to file.
    
    Parameters
    -----------
        self : DFN object

        filename : string
            name of file

        format : string
            format type with options None, fehm, FEHM. Default is None
    """
    if format is None:
        np.savetxt(filename, self.aperture)
    elif format == "fehm" or format == "FEHM":
        self.print_log(f"--> Writing {filename}")
        with open(filename, 'w+') as fp:
            fp.write('aperture\n')
            for i, b in enumerate(self.aperture):
                fp.write(f'-{i+7:d} 0 0 {b:0.5e}\n')
    else:
        self.print_log("--> Warning. Unknown format requested.\nOptions are None and fehm/FEHM (case sensitive)")


def dump_perm(self, filename, format=None):
    """ Write permeability values to file.
    
    Parameters
    -----------
        self : DFN object

        filename : string
            name of file

        format : string
            format type with options None, fehm, FEHM. Default is None
    """
    if format is None:
        np.savetxt(filename, self.perm)
    elif format == "fehm" or format == "FEHM":
        self.print_log(f"--> Writing {filename}")
        with open(filename, 'w+') as fp:
            fp.write('permeability\n')
            for i, k in enumerate(self.perm):
                fp.write(f'-{i+7:d} 0 0 {k:0.5e} {k:0.5e} {k:0.5e}\n')
            fp.write("\n")


def dump_transmissivity(self, filename, format=None):
    """ Write transmissivity values to file.
    
    Parameters
    -----------
        self : DFN object

        filename : string
            name of file

        format : string
            format type with options None, fehm, FEHM. Default is None
    """
    if format is None:
        np.savetxt(filename, self.transmissivity)
    elif format == "fehm" or format == "FEHM":
        self.print_log(f"--> Writing {filename}")
        with open(filename, 'w+') as fp:
            fp.write('transmissivity\n')
            for i, trans in enumerate(self.transmissivity):
                fp.write(f'-{i:d} 0 0 {trans:0.5e}\n')


def dump_fracture_info(self, filename):
    """ Write fracture info (connections, perm, aperture) to file.
    
    Parameters
    -----------
        self : DFN object

        filename : string
            name of file
    """
    self.print_log(f"--> Writing {filename}")
    connections = np.genfromtxt("dfnGen_output/fracture_info.dat",
                                skip_header=1)[:, 0].astype(int)
    with open(filename, "w+") as fp:
        fp.write("num_connections perm aperture\n")
        for i in range(self.num_frac):
            fp.write(
                f"{connections[i]:d} {self.perm[i]:0.8e} {self.aperture[i]:0.8e}\n"
            )
    self.print_log("--> Complete")


def dump_hydraulic_values(self, prefix=None, format=None):
    """ Writes all hydraulic property values to files.
    
    Parameters
    -----------
        self : DFN object

        prefix : string
            prefix of aperture.dat and perm.dat file names
            prefix_aperture.dat and prefix_perm.dat 
        
        format : string
            format type. Default is None
    """
    self.print_log("--> Dumping values to files")
    if not prefix:
        self.print_log(f"--> Using prefix {prefix}")
    if not format:
        self.print_log(f"--> Using format : {format}")

    if prefix is not None:
        aper_filename = prefix + '_aperture.dat'
        perm_filename = prefix + '_perm.dat'
        trans_filename = prefix + '_transmissivity.dat'
        frac_info_filename = "dfnGen_output/" + prefix + '_fracture_info.dat'
    else:
        aper_filename = "aperture.dat"
        perm_filename = "perm.dat"
        trans_filename = "transmissivity.dat"
        frac_info_filename = "dfnGen_output/fracture_info.dat"

    self.dump_aperture(aper_filename, format)
    self.dump_perm(perm_filename, format)
    self.dump_transmissivity(trans_filename, format)
    self.dump_fracture_info(frac_info_filename)
