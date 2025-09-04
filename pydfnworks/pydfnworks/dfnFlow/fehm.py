import os
import subprocess
import sys
import glob
import shutil
from time import time
import numpy as np
"""
Functions for using FEHM in dfnWorks
"""

import os
from time import time

def parse_stor_file(filepath):
    """
    Parse a LaGriT-formatted ASCII STOR file into its structured data blocks.

    This function reads a `.stor` file, extracts header metadata and all subsequent
    numerical data blocks (volumes, connectivity, pointers, and coefficients), and
    returns them as a list of NumPy arrays.

    The expected structure of the file is:
        - 3 header lines (text)
        - Line 3 contains: [nedges, nnodes, ptr_size, num_area_coef, ...]
        - 7 numerical blocks follow:
            1. Voronoi volumes (nnodes)
            2. Row counts (nnodes + 1)
            3. Connectivity list (nedges)
            4. Pointers into coefficient list (nedges * num_area_coef)
            5. Diagonal pointer padding (nnodes + 1)
            6. Diagonal matrix indices (nnodes)
            7. Area coefficients (nedges * num_area_coef)

    Parameters
    ----------
    filepath : str
        Path to the STOR file (ASCII format) to parse.

    Returns
    -------
    List[np.ndarray]
        A list of 7 NumPy arrays corresponding to:
            [volumes, row_counts, conn_list, pointer_block,
             diag_pointers, row_diagonals, area_coefficients]

    Raises
    ------
    ValueError
        If the number of parsed float entries is insufficient based on header metadata.

    Notes
    -----
    This function assumes:
        - The file uses whitespace-separated float values for all numerical blocks.
        - Area coefficients are stored as scalars (`num_area_coef = 1`) or higher.
        - The function does not preserve file pointer for later parsing.

    Examples
    --------
    >>> blocks = parse_stor_file("mesh.stor")
    >>> volumes = blocks[0]
    >>> conn_list = blocks[2]
    """

    with open(filepath, 'r') as file:
        lines = file.readlines()

    # Extract dimension info from line 3
    header_vals = list(map(int, lines[2].split()))
    nedges = header_vals[0]
    nnodes = header_vals[1]
    num_area_coef = header_vals[3]  # assumed position

    # Calculate block lengths
    block_sizes = [
        nnodes,
        nnodes + 1,
        nedges,
        nedges * num_area_coef,
        nnodes + 1,
        nnodes,
        nedges * num_area_coef
    ]

    # Read all remaining float values
    data = []
    for line in lines[3:]:  # Skip header
        data.extend(map(float, line.strip().split()))

    # Sanity check
    expected_total = sum(block_sizes)
    if len(data) < expected_total:
        raise ValueError(f"Not enough data: expected {expected_total}, got {len(data)}")

    # Slice data into blocks
    blocks = []
    start = 0
    for size in block_sizes:
        blocks.append(np.array(data[start:start + size]))
        start += size

    return blocks  # list of 7 arrays


def write_stor_file(filepath_out, header_lines, blocks):
    """
     Write numerical data blocks to a LaGriT-formatted ASCII STOR file.

    This function outputs a `.stor` file that conforms to the LaGriT STOR format,
    using fixed-width formatting and 5 values per line, matching Fortran-style
    output conventions.

    The function assumes that `blocks` is a list of 7 NumPy arrays corresponding to
    parsed data from a STOR file. Each block is written in the correct order and format:
        1. Voronoi volumes (floats)
        2. Row counts (integers)
        3. Connectivity list (integers)
        4. Pointer indices into coefficient list (integers)
        5. Diagonal pointer padding (integers)
        6. Diagonal indices (integers)
        7. Area coefficients (floats)

    Parameters
    ----------
    filepath_out : str
        The path to the output `.stor` file to be written.

    header_lines : List[str]
        The first three lines of the original STOR file header, including:
            - Line 1: Title line
            - Line 2: Date or model info line
            - Line 3: Matrix dimension parameters

    blocks : List[np.ndarray]
        A list of 7 NumPy arrays, each containing one of the STOR file's
        numerical blocks, in the following order:
            [volumes, row_counts, conn_list, pointer_block,
             diag_pointers, row_diagonals, area_coefficients]

    Notes
    -----
    - Floats are written with 12-digit precision and scientific notation (width 20).
    - Integers are written right-aligned with 10-character width.
    - All values are formatted 5 per line for strict format compliance.
    - The function overwrites `filepath_out` if it already exists.

    Examples
    --------
    >>> header_lines = ["Title\n", "Date Line\n", "3603 537 4141 1 13\n"]
    >>> write_stor_file("corrected.stor", header_lines, blocks)
    """    
    def format_floats(arr):
        lines = []
        for i, val in enumerate(arr):
            lines.append(f"{val:20.12E}")
            if (i + 1) % 5 == 0 or i == len(arr) - 1:
                lines.append('\n')
            else:
                lines.append(' ')
        return lines

    def format_integers(arr):
        lines = []
        for i, val in enumerate(arr):
            lines.append(f"{int(val):10d}")
            if (i + 1) % 5 == 0 or i == len(arr) - 1:
                lines.append('\n')
            else:
                lines.append(' ')
        return lines

    with open(filepath_out, 'w') as fout:
        # Header (first 3 lines)
        for line in header_lines:
            fout.write(line)

        # Write each block in the correct format
        fout.writelines(format_floats(blocks[0]))  # volumes
        fout.writelines(format_integers(blocks[1]))  # row_counts
        fout.writelines(format_integers(blocks[2]))  # conn_list
        fout.writelines(format_integers(blocks[3]))  # pointer block
        fout.writelines(format_integers(blocks[4]))  # diag pointers
        fout.writelines(format_integers(blocks[5]))  # row diags
        fout.writelines(format_floats(blocks[6]))    # area coefficients


def correct_stor_file(self):
    """
    Corrects the Voronoi volumes and area coefficients in a STOR file
    by applying aperture adjustments.

    This method reads an ASCII-formatted STOR file used in FEHMN simulations,
    adjusts the volume and area values based on the aperture data, and writes
    a new corrected version of the file.

    Assumptions:
        - Only ASCII STOR format is supported.
        - Area coefficients are in scalar format (NUM_AREA_COEF = 1).
        - Instance attributes include:
            self.stor_file: Path to the input STOR file.
            self.material_ids: List of material IDs for each cell.
            self.aperture: List of aperture values (by cell or material).
            self.cell_based_aperture: Boolean flag.
            self.print_log: Logging function.
    """

    self.stor_file = "full_mesh.stor"
    if not os.path.isfile(self.stor_file):
        self.print_log("Error. Cannot find STOR file.\nExiting\n", 'error')

    blocks = parse_stor_file(self.stor_file)

    volumes = blocks[0]
    for i in range(self.num_nodes):
        volumes[i] *= self.aperture[self.material_ids[i] - 1]
    blocks[0] = volumes

    conn_list = blocks[2].astype(int)
    areas = blocks[6]
    for i in conn_list:
        areas[i] *= self.aperture[self.material_ids[i-1] - 1]
    blocks[6] = areas 

    # Also grab the first 3 header lines
    with open(self.stor_file, 'r') as f:
        header_lines = [next(f) for _ in range(3)]
    stor_out_file = self.stor_file.replace('.stor', '_vol_area.stor')
    write_stor_file(stor_out_file, header_lines, blocks)

    self.print_log("correcting stor file complete")


def correct_perm_for_fehm():
    """ FEHM wants an empty line at the end of the perm file
    This functions adds that line return
    
    Parameters
    ----------
        None

    Returns
    ---------
        None

    Notes
    ------------
        Only adds a new line if the last line is not empty
    """
    # self.print_log("Modifing perm.dat for FEHM")
    fp = open("perm.dat")
    lines = fp.readlines()
    fp.close()
    # Check if the last line of file is just a new line
    # If it is not, then add a new line at the end of the file
    if len(lines[-1].split()) != 0:
        print("--> Adding line to perm.dat")
        fp = open("perm.dat", "a")
        fp.write("\n")
        fp.close()


def fehm(self):
    """Run FEHM 

    Parameters
    ----------
        self : object 
            DFN Class
   
    Returns
    -------
        None

    Notes
    -----
    See https://fehm.lanl.gov/ for details about FEHM

    """
    self.print_log("--> Running FEHM")
    if self.flow_solver != "FEHM":
        error = "Error. Incorrect flow solver requested\n"
        self.print_log(error, 'error')
        sys.exit(1)

    try:
        shutil.copy(self.dfnFlow_file, self.jobname)
    except:
        error = f"--> Error copying FEHM run file: {self.dfnFlow_file}"
        self.print_log(error, 'error')
        sys.exit(1)

    path = self.dfnFlow_file.strip(self.local_dfnFlow_file)
    with open(self.local_dfnFlow_file) as fp:
        line = fp.readline()
    fehm_input = line.split()[-1]
    try:
        shutil.copy(path + fehm_input, os.getcwd())
    except:
        error = f"--> Error copying FEHM input file: {fehm_input}"
        self.print_log(error, 'error')
        sys.exit(1)


    self.correct_stor_file() 
    self.dump_hydraulic_values(format = "FEHM")
    correct_perm_for_fehm()
    tic = time()
    cmd = os.environ["FEHM_EXE"] + " " + self.local_dfnFlow_file
    # self.call_executable(cmd)
    subprocess.call(cmd, shell = True)
    self.print_log('=' * 80)
    self.print_log("FEHM Complete")
    elapsed = time() - tic
    self.print_log(f"Time Required {elapsed} Seconds")
    self.print_log('=' * 80)
    correct_volume_file = os.path.join(self.jobname, "correct_volumes_logfile.log")
    if os.path.exists(correct_volume_file):
        self.print_log(f"--> Printing correct volumes output file:")
        self.print_log(f"filename: {correct_volume_file}")
        try:
            with open(correct_volume_file, 'r') as file:
                for line in file:
                    self.print_log(line.strip())
        except FileNotFoundError:
            self.print_log(f"File not found: {correct_volume_file}")
        except Exception as e:
            self.print_log(f"An error occurred: {e}")
