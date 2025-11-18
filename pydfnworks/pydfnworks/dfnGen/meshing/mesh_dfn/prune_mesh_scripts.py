"""
.. module:: prune_mesh_scripts.py
   :synopsis: create lagrit scripts for meshing dfn using LaGriT 
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""
import os, sys
from shutil import copy, move
import subprocess
import numpy as np
from pathlib import Path

from pydfnworks.dfnGen.meshing.mesh_dfn import mesh_dfn_helper as mh


def load_connectivity_file(path):
    """ Load file
 
    Parameters
    ---------
        path : path to file

    Returns
    -------
        connectivity : list

    Notes
    -----

   """
    connectivity = []
    with open(path + "/dfnGen_output/connectivity.dat", "r") as fp:
        for line in fp.readlines():
            tmp = []
            line = line.split()
            for frac in line:
                tmp.append(int(frac))
            connectivity.append(tmp)
    return connectivity


def edit_intersection_files(self):
    """ If pruning a DFN, this function walks through the intersection files
    and removes references to files that are not included in the 
    fractures that will remain in the network.
 
    Parameters
    ---------
        self.num_frac : int 
            Number of Fractures in the original DFN
        
        fracture_list :list of int
            List of fractures to keep in the DFN

    Returns
    -------
        None

    Notes
    -----
    1. Currently running in serial, but it could be parallelized
    2. Assumes the pruning directory is not the original directory

   """
    # Make list of connectivity.dat

    fractures_to_remove = list(
        set(range(1, self.num_frac + 1)) - set(self.fracture_list))

    # remove symbolic link and setup local intersection directory
    if os.path.isdir(self.jobname + '/intersections'):
        os.unlink(self.jobname + '/intersections')
        os.mkdir(self.jobname + '/intersections')
    else:
        os.mkdir(self.jobname + '/intersections')
    os.chdir(self.jobname + '/intersections')

    ## DEBUGGING ##
    # clean up directory
    #fl_list = glob.glob("*prune.inp")
    #for fl in fl_list:
    #   os.remove(fl)
    ## DEBUGGING ##

    self.print_log("--> Editing Intersection Files")
    connectivity = load_connectivity_file(self.path)
    ## Note this could be easily changed to run in parallel if needed. Just use cf
    for ifrac in self.fracture_list:
        filename = f'intersections_{ifrac}.inp'
        self.print_log(f'--> Working on: {filename}')
        intersecting_fractures = connectivity[ifrac - 1]
        pull_list = list(
            set(intersecting_fractures).intersection(set(fractures_to_remove)))
        if len(pull_list) > 0:
            # Create Symlink to original intersection file
            os.symlink(self.path + 'intersections/' + filename, filename)
            # Create LaGriT script to remove intersections with fractures not in prune_file
            lagrit_script = f"""
read / {filename} / mo1 
pset / pset2remove / attribute / b_a / 1,0,0 / eq / {pull_list[0]}
"""
            for jfrac in pull_list[1:]:
                lagrit_script += f'''
pset / prune / attribute / b_a / 1,0,0 / eq / {jfrac}
pset / pset2remove / union / pset2remove, prune
rmpoint / pset, get, prune
pset / prune / delete
     '''
            lagrit_script += f'''
rmpoint / pset, get, pset2remove 
rmpoint / compress
    
cmo / modatt / mo1 / imt / ioflag / l
cmo / modatt / mo1 / itp / ioflag / l
cmo / modatt / mo1 / isn / ioflag / l
cmo / modatt / mo1 / icr / ioflag / l
    
cmo / status / brief
dump / intersections_{ifrac}_prune.inp / mo1
finish
'''

            lagrit_filename = 'prune_intersection.lgi'
            with open(lagrit_filename, 'w') as f:
                f.write(lagrit_script)
                f.flush()
            mh.run_lagrit_script("prune_intersection.lgi",
                                 f"pruning_{ifrac}.txt",
                                 quiet=True)
            os.remove(filename)
            if os.path.isfile(f"intersections_{ifrac}_prune.inp"):
                move(f"intersections_{ifrac}_prune.inp",
                     f"intersections_{ifrac}.inp")
            else:
                error = f"Error. intersections_{ifrac}_prune.inp file not found.\nExitting Program"
                self.print_log(error, 'error')
        else:
            try:
                copy(self.path + 'intersections/' + filename, filename)
            except:
                pass

    os.chdir(self.jobname)
    self.num_frac = len(self.fracture_list)
    self.print_log("--> Done editting intersection files")



def edit_params(self):
    """
    Edit and rewrite the ``params.txt`` file with updated fracture information.

    This method reads the existing ``params.txt`` file from the directory specified by
    ``self.path`` and writes a new version to a path derived from ``self.jobname``.
    The first line of the file is replaced with the number of fractures defined by
    ``self.num_frac``. The following seven lines are copied directly from the input file.

    The method logs progress messages before and after the operation, and safely removes
    any existing output file before writing the new one.

    Steps performed:
        1. Deletes an existing output file if present.
        2. Opens the input ``params.txt`` for reading.
        3. Writes ``self.num_frac`` as the first line of the new file.
        4. Skips the first line of the input and copies the next seven lines.
        5. Logs completion of the process.

    Raises
    ------
    FileNotFoundError
        If the input ``params.txt`` file does not exist in ``self.path``.

    Side Effects
    ------------
    Creates or overwrites ``<jobname>params.txt`` in the working directory.

    See Also
    --------
    edit_radii_final : Edits and rewrites the radii data file.
    write_poly_info : Writes updated fracture polygon information.
    """

    self.print_log("--> Editing params.txt file")
    params_path = Path(self.path) / "params.txt"
    output_path = Path(f"{self.jobname}params.txt")
    # Remove old file if it exists
    try:
        output_path.unlink()
    except FileNotFoundError:
        pass

    # Read and write files safely
    with params_path.open("r") as fin, output_path.open("w") as fout:
        fout.write(f"{self.num_frac}\n")
        # Skip the first line and copy the next 7
        fin.readline()
        for _ in range(7):
            fout.write(fin.readline())
    self.print_log("--> Complete")


def write_poly_info(self):
    """
    Write fracture polygon data to the ``poly_info.dat`` file.

    This method generates a new ``poly_info.dat`` file containing information for each
    fracture polygon based on the data stored in ``self.poly_info``. Each line of the file
    represents one fracture and includes both integer and floating-point values describing
    its geometric and topological properties.

    The method logs progress messages, deletes any existing file with the same name, and
    writes the new data sequentially for all fractures.

    File Format
    ------------
    Each line of ``poly_info.dat`` is formatted as:
        ``index poly_id x y z region property1 property2 flag``

    Where:
        * ``index`` – fracture index (1-based)
        * ``poly_id`` – integer polygon ID
        * ``x, y, z`` – floating-point coordinates
        * ``region`` – integer region identifier
        * ``property1, property2`` – floating-point properties
        * ``flag`` – integer indicator (e.g., fracture type)

    Raises
    ------
    FileNotFoundError
        If the output path is invalid or cannot be created.

    Side Effects
    ------------
    Creates or overwrites the file ``<jobname>poly_info.dat`` in the working directory.

    See Also
    --------
    edit_params : Edits and rewrites the parameters file.
    edit_radii_final : Writes fracture radii data.
    """

    self.print_log("--> Editing poly_info.dat file")
    output_path = Path(f"{self.jobname}poly_info.dat")
    # Remove old file if it exists
    try:
        output_path.unlink()
    except FileNotFoundError:
        pass
    # Write new data
    with output_path.open("w") as fp:
        for i in range(self.num_frac):
            info = self.poly_info[i]
            fp.write(
                f"{i + 1} {int(info[1])} {info[2]:.6f} {info[3]:.6f} {info[4]:.6f} "
                f"{int(info[5])} {info[6]:.6f} {info[7]:.6f} {int(info[8])}\n"
            )

    self.print_log("--> Complete")

def edit_radii_final(self):
    """
    Edit and rewrite the ``radii_Final.dat`` file with updated fracture radius data.

    This method reads the existing ``radii_Final.dat`` file from the ``dfnGen_output`` 
    directory located at ``self.path`` and writes a new version to a corresponding 
    directory derived from ``self.jobname``. The first two header lines are copied 
    directly, while subsequent lines are replaced with the radius values stored in 
    ``self.radii``.

    Each output line contains two floating-point radius values and one integer, 
    representing the geometric properties of individual fractures.

    Steps performed
    ---------------
    1. Ensures the output directory exists.
    2. Copies the two header lines from the input file.
    3. Writes updated radius data for each fracture.
    4. Logs progress before and after completion.

    File Format
    ------------
    Each data line of ``radii_Final.dat`` is formatted as:
        ``radius_min radius_max fracture_id``

    Where:
        * ``radius_min`` – minimum radius (float)
        * ``radius_max`` – maximum radius (float)
        * ``fracture_id`` – integer index of the fracture

    Raises
    ------
    FileNotFoundError
        If the input ``radii_Final.dat`` file does not exist at ``self.path``.

    Side Effects
    ------------
    Creates or overwrites ``<jobname>dfnGen_output/radii_Final.dat``.

    See Also
    --------
    write_poly_info : Writes fracture polygon information.
    edit_params : Updates the parameters file.
    """
    self.print_log("--> Editing radii_Final.dat file")

    input_path = Path(self.path) / "dfnGen_output" / "radii_Final.dat"
    output_path = Path(f"{self.jobname}dfnGen_output") / "radii_Final.dat"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Copy header and write new radii data
    with input_path.open("r") as fin, output_path.open("w") as fout:
        # Copy the first two header lines directly
        fout.write(fin.readline())
        fout.write(fin.readline())

        # Write radii values for remaining fractures
        for i in range(self.num_frac):
            fout.write(f"{self.radii[i, 0]:.6f} {self.radii[i, 1]:.6f} {int(self.radii[i, 2])}\n")

    self.print_log("--> Complete")

def edit_normal_vectors(self):
    """
    Edit and rewrite the ``normal_vectors.dat`` file with updated fracture orientation data.

    This method generates a new ``normal_vectors.dat`` file containing the normal vector
    components for each fracture in the discrete fracture network. It reads from the
    original file located in ``self.path/dfnGen_output`` and writes the updated data to
    the corresponding path derived from ``self.jobname``.

    The method ensures the output directory exists, logs progress, and writes each
    fracture’s normal vector as a line of three floating-point values with 12 digits of
    precision.

    Steps performed
    ---------------
    1. Ensures the output directory exists.
    2. Opens the existing ``normal_vectors.dat`` file for reading.
    3. Writes one line per fracture containing its normal vector components.
    4. Logs completion of the process.

    File Format
    ------------
    Each line of ``normal_vectors.dat`` is formatted as:
        ``nx ny nz``

    Where:
        * ``nx`` – x-component of the fracture’s unit normal vector
        * ``ny`` – y-component of the fracture’s unit normal vector
        * ``nz`` – z-component of the fracture’s unit normal vector

    Raises
    ------
    FileNotFoundError
        If the input ``normal_vectors.dat`` file does not exist at ``self.path``.

    Side Effects
    ------------
    Creates or overwrites ``<jobname>dfnGen_output/normal_vectors.dat``.

    See Also
    --------
    edit_radii_final : Writes updated fracture radius information.
    write_poly_info : Writes fracture polygon data.
    """
    self.print_log("--> Editing normal_vectors.dat file")

    input_path = Path(self.path) / "dfnGen_output" / "normal_vectors.dat"
    output_path = Path(f"{self.jobname}dfnGen_output") / "normal_vectors.dat"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Read and write normal vectors
    with input_path.open("r") as fin, output_path.open("w") as fout:
        for i in range(self.num_frac):
            fout.write(
                f"{self.normal_vectors[i, 0]:.12f} "
                f"{self.normal_vectors[i, 1]:.12f} "
                f"{self.normal_vectors[i, 2]:.12f}\n"
            )

    self.print_log("--> Complete")


def edit_translations(self, keep_list=None, precision=12):
    """
    Edit and rewrite the ``translations.dat`` file with filtered and formatted translation data.

    This method processes the existing ``translations.dat`` file in the 
    ``dfnGen_output`` directory under ``self.path`` and writes an updated version 
    to a path derived from ``self.jobname``. Each line of the file represents 
    a translation vector for a fracture, consisting of three floating-point values 
    (x, y, z). Lines marked with the letter ``R`` are excluded from the output.

    Optionally, a list of indices can be supplied through ``keep_list`` to filter 
    which translation vectors are written to the output. The precision of the 
    output floating-point numbers can also be configured.

    Parameters
    ----------
    keep_list : array_like of int, optional
        List of one-based indices specifying which fractures to retain. 
        If ``None``, all valid translation vectors are written.
    precision : int, default=6
        Number of decimal places to use when formatting floating-point values.

    Steps performed
    ---------------
    1. Ensures the output directory exists.
    2. Copies the header line from the input file.
    3. Skips lines ending with ``R`` (representing removed fractures).
    4. Optionally filters translation vectors by ``keep_list``.
    5. Writes filtered and formatted data for up to ``self.num_frac`` fractures.
    6. Logs completion of the process.

    File Format
    ------------
    The file ``translations.dat`` contains one translation vector per line:
        ``x y z``

    Where:
        * ``x`` – x-coordinate of the translation vector (float)
        * ``y`` – y-coordinate of the translation vector (float)
        * ``z`` – z-coordinate of the translation vector (float)

    Raises
    ------
    FileNotFoundError
        If the input ``translations.dat`` file is missing from ``self.path``.
    ValueError
        If a line cannot be parsed into three numeric values.

    Side Effects
    ------------
    Creates or overwrites the file ``<jobname>dfnGen_output/translations.dat``.

    See Also
    --------
    edit_normal_vectors : Writes fracture orientation data.
    edit_radii_final : Updates fracture radius information.
    write_poly_info : Writes polygonal fracture data.
    """
    self.print_log("--> Editing translations.dat file")

    input_path = Path(self.path) / "dfnGen_output" / "translations.dat"
    output_path = Path(f"{self.jobname}dfnGen_output") / "translations.dat"

    # Make sure the output folder is present
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r") as fin, output_path.open("w") as fout:
        # copy header line exactly
        fout.write(fin.readline())

        # parse remaining lines, skipping those that end with 'R'
        pts = []
        for line in fin:
            parts = line.strip().split()
            if not parts:
                continue
            if parts[-1] == "R":
                continue
            try:
                x, y, z = map(float, parts[:3])
            except ValueError:
                # ignore malformed rows
                continue
            pts.append((x, y, z))

        points = np.asarray(pts, dtype=float)

        # optional filtering by keep_list (one based indices)
        if keep_list is not None:
            idx = np.asarray(keep_list, dtype=int) - 1
            points = points[idx, :]

        # write up to self.num_frac rows
        n = min(self.num_frac, len(points))
        fmt = f"{{:.{precision}f}} {{:.{precision}f}} {{:.{precision}f}}\n"
        for i in range(n):
            fout.write(fmt.format(points[i, 0], points[i, 1], points[i, 2]))

    self.print_log("--> Complete")


def write_surface_area(self):
    """
    Write the ``surface_area_Final.dat`` file containing the surface area of retained fractures.

    This method generates a new ``surface_area_Final.dat`` file that records the 
    surface areas of all remaining fractures after isolated and clustered fractures 
    have been removed. The data are written with 12 decimal places of precision, 
    one value per line, preceded by a descriptive header.

    The output file is written to the ``dfnGen_output`` directory corresponding to 
    ``self.jobname``. The method ensures the output directory exists and logs the 
    progress of the operation.

    Steps performed
    ---------------
    1. Ensures the output directory exists.
    2. Writes a descriptive header line to the output file.
    3. Writes the surface area value for each remaining fracture.
    4. Logs completion of the process.

    File Format
    ------------
    The file ``surface_area_Final.dat`` is structured as follows:

    .. code-block:: text

        Fracture Surface Area After Isolated Fracture and Cluster Removal
        A_1
        A_2
        A_3
        ...
        A_n

    Where:
        * ``A_i`` – surface area of the *i*-th retained fracture (float, 12 decimal precision)

    Raises
    ------
    OSError
        If the output file cannot be written due to permission or path issues.

    Side Effects
    ------------
    Creates or overwrites ``<jobname>dfnGen_output/surface_area_Final.dat``.

    See Also
    --------
    edit_radii_final : Writes updated fracture radii data.
    edit_normal_vectors : Writes fracture normal vector information.
    write_poly_info : Writes fracture polygon geometry data.
    """

    self.print_log("--> Editing surface_area_Final.dat file")

    output_path = Path(f"{self.jobname}dfnGen_output") / "surface_area_Final.dat"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write surface area data
    with output_path.open("w") as fout:
        fout.write(
            "Fracture Surface Area After Isolated Fracture and Cluster Removal\n"
        )
        for i in range(self.num_frac):
            fout.write(f"{self.surface_area[i]:.12f}\n")

    self.print_log("--> Complete")

def edit_polygons(self):
    """
    Edit and rewrite the ``polygons.dat`` file with the updated set of retained fractures.

    This method reads the existing ``polygons.dat`` file from the 
    ``dfnGen_output`` directory under ``self.path`` and writes a filtered version 
    to the corresponding directory derived from ``self.jobname``. The output file 
    includes only the fracture polygons specified in ``self.keep_list`` and updates 
    the header to reflect the new number of retained polygons.

    The purpose of this operation is to synchronize the polygon dataset with the 
    reduced fracture set after isolated and unwanted fractures are removed.

    Steps performed
    ---------------
    1. Ensures the output directory exists.
    2. Reads the input ``polygons.dat`` file and extracts its contents.
    3. Writes a new header with the current value of ``self.num_frac``.
    4. Filters and writes only the polygons corresponding to indices in ``self.keep_list``.
    5. Logs the total number of retained fractures.

    File Format
    ------------
    The file ``polygons.dat`` begins with a header line specifying the number of 
    polygons, followed by one line per retained fracture polygon:

    .. code-block:: text

        nPolygons: N
        <polygon_data_line_1>
        <polygon_data_line_2>
        ...
        <polygon_data_line_N>

    Where:
        * ``N`` – number of retained polygons
        * ``<polygon_data_line_i>`` – data describing the *i*-th fracture polygon

    Raises
    ------
    FileNotFoundError
        If the input ``polygons.dat`` file does not exist at ``self.path``.
    OSError
        If the output file cannot be written due to permission or path issues.

    Side Effects
    ------------
    Creates or overwrites ``<jobname>dfnGen_output/polygons.dat``.

    See Also
    --------
    write_poly_info : Writes fracture polygon property data.
    edit_radii_final : Writes updated fracture radii.
    write_surface_area : Outputs surface area data for retained fractures.
    """
    self.print_log("--> Editing polygons.dat file")

    input_path = Path(self.path) / "dfnGen_output" / "polygons.dat"
    output_path = Path(f"{self.jobname}dfnGen_output") / "polygons.dat"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    retained_fractures = []

    with input_path.open("r") as fin:
        header = fin.readline()  # Original header, likely "nPolygons: ..."
        data_lines = fin.read().strip().splitlines()

    with output_path.open("w") as fout:
        # Write updated header
        fout.write(f"nPolygons: {self.num_frac}\n")

        for idx, line in enumerate(data_lines, start=1):
            if idx in self.keep_list:
                retained_fractures.append(idx)
                fout.write(f"{line}\n")

    self.print_log(f"--> Retained {len(retained_fractures)} polygons")

def clean_up_files_after_prune(self):
    """
    Clean and regenerate all DFN output files after fracture pruning.

    This method updates all relevant Discrete Fracture Network (DFN) data files
    after the network has been pruned to include only the fractures listed in the 
    prune file. It removes references to discarded fractures and regenerates 
    all dependent data files required for subsequent flow or transport simulations.

    Specifically, this method updates:
        * ``params.txt`` – fracture count and configuration parameters
        * ``poly_info.dat`` – polygonal fracture information
        * ``radii_Final.dat`` – fracture radius data
        * ``normal_vectors.dat`` – fracture orientation vectors
        * ``translations.dat`` – fracture translation vectors
        * ``surface_area_Final.dat`` – fracture surface area data
        * ``polygons.dat`` – retained fracture polygons

    The function logs progress before and after processing, ensuring all DFN data
    are synchronized following pruning operations.

    Parameters
    ----------
    self : DFN object
        Instance of the DFN class containing fracture data, pruning state, and paths.

    Returns
    -------
    None

    Notes
    -----
    This function **must** be executed after any pruning operation if a flow or 
    transport simulation is to be performed. It ensures that all geometry and 
    metadata files are consistent with the updated fracture set.

    See Also
    --------
    edit_params : Updates the fracture count in the parameters file.
    write_poly_info : Writes fracture polygon properties.
    edit_radii_final : Writes updated fracture radius data.
    edit_normal_vectors : Updates fracture orientation vectors.
    edit_translations : Filters and writes translation vectors.
    write_surface_area : Writes retained fracture surface areas.
    edit_polygons : Updates the retained polygon list.
    """
 
    self.print_log("\n--> Editing Fracture Files: Starting")
    self.edit_params()
    self.write_poly_info() 
    self.edit_radii_final()  
    self.edit_normal_vectors() 
    self.edit_translations() 
    self.write_surface_area() 
    self.edit_polygons() 
    self.print_log("--> Editing Fracture Files: Complete\n")

def clean_up_after_prune(self, dump_files=False):
    """
    Update the DFN object after pruning and optionally regenerate associated data files.

    This method updates all internal fracture-related attributes of the DFN object 
    to include only those fractures specified in ``self.prune_file``. It adjusts 
    arrays such as fracture radii, normal vectors, centers, permeability, aperture, 
    and polygonal information to reflect the reduced set of fractures.  

    Optionally, if ``dump_files`` is set to ``True``, this method also calls 
    :meth:`clean_up_files_after_prune` to regenerate all corresponding output files 
    (e.g., ``params.txt``, ``poly_info.dat``, ``radii_Final.dat``, etc.) to ensure 
    consistency between in-memory data and on-disk DFN representations.

    Parameters
    ----------
    self : DFN object
        Instance of the DFN class containing fracture data, metadata, and paths.
    dump_files : bool, optional
        Whether to rewrite all fracture-related output files after pruning. 
        Defaults to ``False``.

    Attributes Updated
    ------------------
    keep_list : ndarray of int
        Sorted list of retained fracture indices read from ``self.prune_file``.
    fracture_list : ndarray of int
        Alias for ``keep_list``; maintained for compatibility.
    num_frac : int
        Updated number of fractures remaining after pruning.
    poly_info : ndarray
        Filtered polygonal fracture data corresponding to retained fractures.
    families : ndarray
        Family identifiers for retained fractures.
    perm : ndarray
        Permeability values for retained fractures.
    aperture : ndarray
        Aperture values for retained fractures.
    radii : ndarray
        Radii data for retained fractures.
    normal_vectors : ndarray
        Normal vector components for retained fractures.
    centers : ndarray
        Center coordinates for retained fractures.
    surface_area : ndarray
        Surface area values for retained fractures.

    Notes
    -----
    This method must be executed immediately after pruning to ensure the DFN 
    object reflects the correct subset of fractures. If a flow or transport 
    solution is to be run, ``dump_files`` should be set to ``True`` to update 
    all relevant output files accordingly.

    See Also
    --------
    clean_up_files_after_prune : Regenerates all DFN output files after pruning.
    """

    self.print_log(f"--> Editing DFN file based on fractures in {self.prune_file}")
    self.keep_list = np.sort(np.genfromtxt(self.prune_file).astype(int))
    self.fracture_list = self.keep_list
    self.num_frac = len(self.keep_list)
    self.poly_info = self.poly_info[self.keep_list - 1, :]
    self.families = self.families[self.keep_list - 1]
    self.perm = self.perm[self.keep_list - 1]
    self.aperture = self.aperture[self.keep_list - 1]
    # self.material_ids = self.material_ids[keep_list - 1]
    self.radii = self.radii[self.keep_list - 1, :]
    self.normal_vectors= self.normal_vectors[self.keep_list - 1, :]
    self.centers = self.centers[self.keep_list - 1, :]
    self.surface_area = self.surface_area[self.keep_list - 1]
    print(f"--> Modifying DFN properties based on fractures in {self.prune_file}: Complete")

    if dump_files:
        self.clean_up_files_after_prune()
