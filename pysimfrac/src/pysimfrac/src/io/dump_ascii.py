import numpy as np

def dump_surface_ascii(self, field, filename, coordinates, indices):
    """  Writes a single field to ascii file. 

    Parameters
    --------------------
        self : object
            simFrac Class
        field : 2D Numpy array
            Array of surface values
        filename_prefix : str
            Prefix for filename
        coordinates : bool
            True / False to write x/y coordinates to file
        indices : bool
            True / False to write i/j indices to file

    Returns
    --------------------
        None

    Notes
    --------------------
        None

    """

    output = np.reshape(field, self.nx*self.ny)   
    header = "value"
    if coordinates:
        x = np.reshape(self.X, self.nx*self.ny)
        y = np.reshape(self.Y, self.nx*self.ny)
        output = np.c_[output,x,y]
        header += ",x,y"
    if indices:
        nx = np.linspace(0, self.nx - 1, self.nx)
        ny = np.linspace(0, self.ny - 1, self.ny)
        n, m = np.meshgrid(nx, ny)
        n = np.reshape(n, self.nx*self.ny)
        m = np.reshape(m, self.nx*self.ny)
        output = np.c_[output, n, m]
        header += ",i,j"
    print(f"--> writting to file {filename}")
    np.savetxt(filename, output, delimiter=",", header = header)


def dump_ascii(self, surface = "all", filename_prefix = None, coordinates = False, indices = False):
    """  Writes a surface fields to ascii files. 

    Parameters
    --------------------
        self : object
            simFrac Class
        surface : str
            Named of desired surface to write to file. Options are 'aperture', 'top', 'bottom', and 'all'(default). 
        filename_prefix : str
            Prefix for filename
        coordinates : bool
            True / False to write x/y coordinates to file
        indices : bool
            True / False to write i/j indices to file

    Returns
    --------------------
        None

    Notes
    --------------------
        Files written out are aperture.dat, top.dat, and bottom.dat

    """

    print(f"--> Writting surfaces to file")
    # Write surfaces to file
    if surface == "all":
        surfaces = ["aperture", "top", "bottom"]
        for sf in surfaces:
            if sf == "aperture":
                field = self.aperture
                filename = filename_prefix + ""
            elif sf == "top":
                field = self.top
            elif sf == "bottom":
                field = self.bottom
            
            if filename_prefix:
                filename = filename_prefix + "_" + sf + ".dat"
            else:
                filename = sf + ".dat"

            self.dump_surface_ascii(field, filename, coordinates, indices)
    
    else:
        if surface == "aperture":
            field = self.aperture
        elif surface == "top":
            field = self.top
        elif surface == "bottom":
            field = self.bottom
        
        if filename_prefix:
            filename = filename_prefix + "_" + surface + ".dat"
        else:
            filename = surface + ".dat"
 
        self.dump_surface_ascii(field, filename, coordinates, indices)


    print(f"--> Writting surfaces to file complete\n")
