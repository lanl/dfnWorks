import matplotlib.pyplot as plt
from vedo import Plotter, Volume

from pysimfrac.src.general.helper_functions import print_error


def Euclidean_distance(frac_3D):
    from scipy.ndimage import distance_transform_edt
    return distance_transform_edt(frac_3D == 0)

def plot_3D(self, edist=True):
    """ 
    

    Parameters
    ------------
        edist : booleam
            DESCRIPTION. The default is True.

    Returns
    -------
        None

    """

    vdp = Plotter(shape=(1, 1),
                  axes=9,
                  bg='peachpuff',
                  bg2='blue9',
                  screensize=(1200 * 4, 900 * 4),
                  offscreen=False)

    if edist:
        to_plot = Euclidean_distance(self.frac_3D)
    else:
        to_plot = (self.frac_3D == 0)

    lego = Volume(to_plot.T).legosurface(vmin=1, vmax=5).cmap('turbo',
                                                              vmin=-1,
                                                              vmax=5)

    lego += Volume(self.frac_3D.T == 0).legosurface(
        vmin=1, vmax=2).c('lightgray').opacity(0.05)

    cam = dict(
        pos=(235.8, -687.4, 266.2),
        focalPoint=(99.50, 99.50, 46.50),
        viewup=(-0.04663, 0.2611, 0.9642),
        distance=828.3,
        clippingRange=(578.0, 1145),
    )

    vdp.show(lego, camera=cam)


def plot_aperture_field(self, figname=None):
    """ Create a contour plot of the aperture field

    Parameters
    --------------------
        self : object
            simFrac Class
        figname : str
            Name of figure to be saved. If figname is None (default), then no figure is saved. 

    Returns
    --------------------
        fig : Figure

        ax : Axes

    Notes
    --------------------
        None
    
    """

    if self.lx >= self.ly:
        viz_scale_factor = 10 / self.lx
    else:
        viz_scale_factor = 10 / self.ly

    fig, ax = plt.subplots(figsize=(self.lx * viz_scale_factor,
                                    self.ly * viz_scale_factor))
    CS = ax.contourf(self.X, self.Y, self.aperture, cmap='bone')
    cbar = fig.colorbar(CS)
    cbar.ax.set_ylabel(f'Aperture values [{self.units}]',
                       fontsize=18,
                       rotation=90)
    plt.xlabel(f'X [{self.units}]', fontsize=18)
    plt.ylabel(f'Y [{self.units}]', fontsize=18)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    if figname:
        plt.savefig(figname, dpi=300)

    return fig, ax


def plot_surface(self, surface='both', figname=None):
    """ Create a 3D surface plot

    Parameters
    --------------------
        self : object
            simFrac Class
        surface : str
            Named of desired surface to plot. Options are 'top', 'bottom', and 'both'(default). 
        figname : str
            Name of figure to be saved. If figname is None (default), then no figure is saved. 

    Returns
    --------------------
        None

    Notes
    --------------------
        If surface name 'aperture' is provided, then plot_aperture_field is called.  
    
    """

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(10, 10))
    ax.set_box_aspect((self.lx, self.ly, 2))

    if surface == 'both':
        ax.plot_surface(self.X, self.Y, self.top, cmap='bone', linewidth=0)
        ax.plot_surface(self.X, self.Y, self.bottom, cmap='bone', linewidth=0)
    elif surface == 'top':
        ax.plot_surface(self.X, self.Y, self.top, cmap='bone', linewidth=0)
    elif surface == 'bottom':
        ax.plot_surface(self.X, self.Y, self.bottom, cmap='bone', linewidth=0)
    elif surface == "aperture":
        plt.close()
        fig, ax = self.plot_aperture_field(figname)
        return fig, ax
    else:
        print_error(
            f"Error. Unknown surface provided - {surface}. Acceptable surfaces are 'top', 'bottom', or 'both'"
        )

    plt.xlabel(f'X [{self.units}]', fontsize=18)
    plt.ylabel(f'Y [{self.units}]', fontsize=18)
    ax.zaxis.set_rotate_label(False)
    ax.set_zlabel(f'Surface Height [{self.units}]', fontsize=18, rotation=90)
    if figname:
        plt.savefig(figname, dpi=150)
    return fig, ax
