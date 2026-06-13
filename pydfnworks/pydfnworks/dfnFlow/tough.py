#!/usr/bin/env python3
"""Convert a DFNWorks UGE file to a TOUGH MESH file.

1. The code reads `full_mesh_vol_area.uge` and writes the `MESH` file for TOUGH.

2. The permeability of all connections is set by default to the first permeability value specified in the TOUGH input file.

3. Boundary and well information should be added manually, for example, by changing the volume to 1.0e50.

4. The magnitude of gravity in the TOUGH input file should be a positive number.

5. The default media name is DFNMM

"""

import math
from pathlib import Path
from typing import Iterable
from time import time
import shutil
import os 
import subprocess
import numpy as np 


def load_zone_file_nodes(self, zone_file):
    self.print_log(f'--> Gather nodes from zone file: {zone_file}')
    with open(zone_file, 'r') as fzone:
        self.print_log('--> Reading boundary node ids')
        node_array = fzone.read().split()
        # num_nodes = int(node_array[4])
        node_array = [int(n) for n in node_array[5:-1]]
    self.print_log('--> Finished reading zone file')
    return node_array

# ---------------------------------------------------------------------------
# Low-level parsing helpers
# ---------------------------------------------------------------------------

def parse_numbers(line: str) -> list[float]:
    """Parse a whitespace-delimited numeric line."""
    return [float(value) for value in line.split()]


def read_section_header(line: str, expected_name: str) -> int:
    """Validate and parse a UGE section header line, returning the element count.

    UGE section headers have the form ``<NAME> <count>``, e.g. ``CELLS 1024``
    or ``CONNECTIONS 2048``.  The name check is case-insensitive.

    Parameters
    ----------
    line:
        The raw text line read from the UGE file.
    expected_name:
        The section keyword that must appear in the first field (e.g.
        ``"CELLS"`` or ``"CONNECTIONS"``).

    Returns
    -------
    int
        The integer count declared in the header.

    Raises
    ------
    ValueError
        If the line does not match the ``<NAME> <count>`` pattern or the
        keyword does not match *expected_name*.
    """
    fields = line.split()
    if len(fields) != 2 or fields[0].upper() != expected_name:
        raise ValueError(f"Expected '{expected_name} <count>' header, got: {line.rstrip()}")
    return int(fields[1])


# ---------------------------------------------------------------------------
# TOUGH naming convention
# ---------------------------------------------------------------------------

def tough_element_name(index: int) -> str:
    """Return a 5-character TOUGH element name, such as AAA01 or AAB01.

    TOUGH element names are composed of a 3-letter group prefix followed by a
    2-digit local index (01–99).  The prefix cycles through all combinations of
    uppercase ASCII letters (AAA, AAB, …, ZZZ), giving a maximum capacity of
    26³ × 99 = 1,756,776 unique names.

    The mapping is:
      * ``index`` 1–99   → ``AAA01``–``AAA99``
      * ``index`` 100–198 → ``AAB01``–``AAB99``
      * …and so on through ``ZZZ99``.

    Parameters
    ----------
    index:
        1-based element index from the UGE ``CELLS`` section.

    Returns
    -------
    str
        A zero-padded 5-character name string.

    Raises
    ------
    ValueError
        If *index* is less than 1 or exceeds the naming capacity.
    """
    if index < 1:
        raise ValueError(f"Element index must be positive, got {index}")

    # Determine which letter-group (prefix) this index falls in and the
    # 1-based position within that group (1–99).
    group_index = (index - 1) // 99
    local_index = (index - 1) % 99 + 1

    if group_index >= 26**3:
        raise ValueError(f"Element index {index} is too large for AAA01-ZZZ99 naming")

    # Decompose group_index into three base-26 digits to obtain the prefix letters.
    first = chr(ord("A") + group_index // (26**2))
    second = chr(ord("A") + (group_index // 26) % 26)
    third = chr(ord("A") + group_index % 26)
    return f"{first}{second}{third}{local_index:02d}"


# ---------------------------------------------------------------------------
# Geometry helper
# ---------------------------------------------------------------------------

def euclidean_distance(point_a: Iterable[float], point_b: Iterable[float]) -> float:
    """Return the Euclidean (straight-line) distance between two points.

    Works for any number of dimensions as long as both iterables have the same
    length.  Used here to compute the distance from each element centroid to
    the shared face centroid when writing TOUGH ``CONNE`` records.

    Parameters
    ----------
    point_a, point_b:
        Coordinate sequences (e.g. ``(x, y, z)`` tuples).

    Returns
    -------
    float
        The Euclidean distance ‖point_a − point_b‖₂.
    """
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(point_a, point_b)))


# ---------------------------------------------------------------------------
# Main conversion routine
# ---------------------------------------------------------------------------

def convert_uge_to_tough(self,
    input_filename,  
    output_filename,
    boundary_filenames=None,
    boundary_nodes=None,  
) -> None:

# def convert_uge_to_tough(self,
#     input_filename,  
#     output_filename,
#     boundary_filenames = None,
#     boundary_nodes = np.array([]),  
# ) -> None:
    """Convert a DFNWorks UGE mesh file to a TOUGH2/TOUGH+ MESH file.

    Reads the binary ``CELLS`` and ``CONNECTIONS`` sections from a
    ``full_mesh_vol_area.uge`` file produced by DFNWorks/LaGriT and writes the
    corresponding ``ELEME`` and ``CONNE`` blocks required by the TOUGH simulator.

    ELEME block
    -----------
    Each line encodes one grid element with its rock-type label, volume,
    and centroid coordinates.  All elements are assigned the default rock-type
    ``"DFNMM"``.  Boundary elements (e.g. injection/production wells) must be
    set to a large volume (1 × 10⁵⁰) manually after this routine completes.

    CONNE block
    -----------
    Each line encodes one connection between two adjacent elements.  The
    permeability index (``conx_ki``) is fixed at 1 so that TOUGH uses the
    first permeability value defined in its input file for every connection.
    The gravitational cosine ``beta`` is the cosine of the angle between the
    vertical (−z) direction and the vector joining the two element centroids.

    Parameters
    ----------
    self:
        The parent DFNWorks object, used only for ``self.print_log``.
    input_filename:
        Path to the source UGE file (typically ``full_mesh_vol_area.uge``).
    output_filename:
        Destination path for the TOUGH ``MESH`` file.

    Notes
    -----
    * Gravity magnitude in the TOUGH input deck must be a **positive** number.
    * The UGE ``CELLS`` section is 1-indexed; the first numeric field on each
      cell line is the cell index and is skipped during parsing.
    * Element coordinates are cached in memory to compute connection distances
      and the gravitational cosine, so peak memory scales with ``num_ele``.
    """
    self.print_log("--> Starting: Converting UGE mesh file format to TOUGH mesh")

    t = time()  # start timer

    input_path = Path(input_filename)
    if not input_path.is_file():
        self.print_log(f'Error. Cannot find {input_path} file\nExiting\n', 'error')

    output_path = Path(output_filename)

    # boundary_nodes = np.array([]) if boundary_nodes is None else boundary_nodes
    # if boundary_filenames is not None:
    #     boundary_nodes = np.concatenate([boundary_nodes] + [self.load_zone_file_nodes(f) for f in boundary_filenames])
    # if boundary_nodes.size > 0:
    #     print("--> Boundary nodes")
    #     print(boundary_nodes)

    boundary_nodes = [] if boundary_nodes is None else list(boundary_nodes)
    if boundary_filenames is not None:
        for f in boundary_filenames:
            boundary_nodes.extend(self.load_zone_file_nodes(f))
    if boundary_nodes:
        print("--> Boundary nodes")
        print(boundary_nodes)

    # Placeholder for any unused floating-point field in the ELEME record.
    unknown = 0.0
    # Default rock-type label written into every ELEME record.
    rock_type = "DFNMM"
    # Permeability index: TOUGH uses the ki-th permeability value from the
    # input file for this connection.  Set to 1 so all connections share the
    # first (and typically only) permeability entry.
    conx_ki = 1
    # Accumulated (x, y, z) centroids; indexed by 0-based element number so
    # that connection lookup is element_coordinates[conxname - 1].
    element_coordinates: list[tuple[float, float, float]] = []

    with input_path.open("r", encoding="utf-8") as fin, output_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as fout:
        # ------------------------------------------------------------------ #
        # ELEME block – one record per grid element
        # ------------------------------------------------------------------ #
        fout.write(f"{'ELEME':>5}\n")

        num_ele = read_section_header(fin.readline(), "CELLS")
        for i in range(1, num_ele + 1):
            line = fin.readline()
            if not line:
                raise ValueError(f"Unexpected end of file while reading element {i}")

            nums = parse_numbers(line)
            if len(nums) < 5:
                raise ValueError(f"Element line {i} has fewer than 5 numeric fields")

            # UGE CELLS columns: [cell_id, x, y, z, volume, ...]
            # cell_id (nums[0]) is the 1-based index and is not used directly
            # here because the loop counter i already tracks it.
            x, y, z = nums[1], nums[2], nums[3]
            volume = nums[4]
            # Fix boundary node volume to large number, then they are held constant. 
            # Probably need something different for more complex BC
            if i in boundary_nodes:
                volume = 1e51

            element_coordinates.append((x, y, z))

            element_name = tough_element_name(i)

            # TOUGH ELEME record layout (fixed-width columns):
            #   cols  1– 5  element name
            #   cols  6–20  rock-type label (right-aligned in a 15-char field)
            #   cols 21–30  element volume [m³]
            #   cols 31–39  unused float (set to 0.0)
            #   cols 40–49  unused/blank field
            #   cols 50–58  x-coordinate [m]
            #   cols 59–67  y-coordinate [m]
            #   cols 68–76  z-coordinate [m]
            fout.write(
                f"{element_name:5s}{rock_type:>15s}"
                f"{volume:10.4E}{unknown:+9.3E}{'':10s}"
                f"{x:+9.3E}{y:+9.3E}{z:+9.3E}\n"
            )

        # ------------------------------------------------------------------ #
        # CONNE block – one record per element–element connection
        # ------------------------------------------------------------------ #
        num_con = read_section_header(fin.readline(), "CONNECTIONS")
        fout.write(f"\n{'CONNE':>5}\n")

        for i in range(1, num_con + 1):
            line = fin.readline()
            if not line:
                raise ValueError(f"Unexpected end of file while reading connection {i}")

            nums = parse_numbers(line)
            if len(nums) < 6:
                raise ValueError(f"Connection line {i} has fewer than 6 numeric fields")

            # UGE CONNECTIONS columns:
            #   [elem1_id, elem2_id, face_cx, face_cy, face_cz, face_area, ...]
            conxname1 = int(nums[0])
            conxname2 = int(nums[1])
            face_centroid = (nums[2], nums[3], nums[4])
            area = nums[5]

            # Retrieve the cached centroids for both elements (convert from
            # 1-based UGE indices to 0-based list indices).
            point1 = element_coordinates[conxname1 - 1]
            point2 = element_coordinates[conxname2 - 1]

            element_name1 = tough_element_name(conxname1)
            element_name2 = tough_element_name(conxname2)

            # Distances from each element centroid to the shared face centroid.
            # TOUGH uses these to compute transmissivities via the two-point
            # flux approximation: T = A·k / (d1 + d2).
            conx_d1 = euclidean_distance(point1, face_centroid)
            conx_d2 = euclidean_distance(point2, face_centroid)
            # Cosine between gravity and the line connecting the two elements.
            # beta = cos(θ) where θ is the angle between the −z axis (gravity)
            # and the vector from element 1 to element 2.  TOUGH uses this for
            # the gravitational head term in Darcy's law.
            # A negative sign is applied because the z-component of the unit
            # vector pointing from element 1 to element 2 is negated to align
            # with the downward gravity convention.
            point2_to_1 = tuple(p2 - p1 for p1, p2 in zip(point1, point2))
            norm = math.sqrt(sum(value**2 for value in point2_to_1))
            beta = 0.0 if norm == 0.0 else -point2_to_1[2] / norm
            # Treat near-zero cosines as exactly zero to avoid spurious
            # gravitational contributions for nearly horizontal connections.
            if abs(beta) < 1.0e-5:
                beta = 0.0

            # TOUGH CONNE record layout (fixed-width columns):
            #   cols  1– 5  element name 1
            #   cols  6–10  element name 2
            #   cols 11–30  permeability index (integer, right-aligned)
            #   cols 31–40  distance d1: centroid 1 → face [m]
            #   cols 41–50  distance d2: centroid 2 → face [m]
            #   cols 51–60  interface area [m²]
            #   cols 61–69  gravitational cosine beta (signed)
            fout.write(
                f"{element_name1:5s}{element_name2:5s}"
                f"{conx_ki:20d}{conx_d1:10.4e}{conx_d2:10.4e}"
                f"{area:10.4e}{beta:+9.3e}\n"
            )

        # Blank line signals the end of the CONNE block to TOUGH.
        fout.write("\n")
    self.print_log("--> Complete: Converting UGE mesh file format to TOUGH mesh")

    elapsed = time() - t
    self.print_log(
        f'--> Time elapsed for file conversion: {elapsed:0.3f} seconds\n'
    )


# ---------------------------------------------------------------------------
# High-level entry point
# ---------------------------------------------------------------------------

def lagrit_to_tough(self, tough_mesh_filename = "MESH", boundary_filenames = None, boundary_nodes = None):
    """Convert a LaGriT-generated DFN mesh to a TOUGH MESH file.

    This is the primary public entry point for the TOUGH mesh conversion
    workflow.  It chains two steps:

    1. ``correct_uge_file()`` – runs the existing LaGriT-to-PFLOTRAN pipeline,
       which produces ``full_mesh_vol_area.uge`` as a side effect.
    2. ``convert_uge_to_tough()`` – translates that UGE file into the TOUGH
       ``MESH`` format at *tough_mesh_filename*.

    Parameters
    ----------
    self:
        The parent DFNWorks object.  Must expose ``print_log``,
        ``lagrit2pflotran``, and ``convert_uge_to_tough`` methods.
    tough_mesh_filename:
        Destination path for the output TOUGH ``MESH`` file.
    """
    self.print_log("\n--> Converting mesh file format to TOUGH mesh: Starting\n")
    # Step 1: Run the LaGriT pipeline; produces full_mesh_vol_area.uge.
    self.correct_uge_file()
    # Step 2: Translate the UGE output to the TOUGH MESH format.
    self.convert_uge_to_tough('full_mesh_vol_area.uge', tough_mesh_filename, boundary_filenames, boundary_nodes) 
    self.print_log("--> Converting mesh file format to TOUGH mesh: Complete\n")



def tough(self):
    """ Run TOUGH. Copy TOUGH run file into working directory and run with ncpus

    Parameters
    ----------
        self : object
            DFN Class

    Returns
    ----------
        None

    Notes
    ----------
    """
    self.print_log('=' * 80)
    self.print_log("--> Running TOUGH Starting")
    self.print_log('=' * 80)


    if self.flow_solver != "TOUGH":
        error = "Error. Wrong flow solver requested\n"
        self.print_log(error, 'error')

    try:
        shutil.copy(os.path.abspath(self.dfnFlow_file),
                    os.path.abspath(os.getcwd()))
    except Exception as e:
        error = f"--> Error. Unable to copy TOUGH input file\nError: {e}"
        self.print_log(error, 'error')

    # mpirun = os.environ['PETSC_DIR'] + '/' + os.environ[
    #     'PETSC_ARCH'] + '/bin/mpiexec'

    # if not (os.path.isfile(mpirun) and os.access(mpirun, os.X_OK)):
    #     # PETSc did not install MPI. Hopefully, the user has their own MPI.
    # mpirun = 'mpiexec'

    # cmd = 'time mpiexec -n ' + str(self.ncpu) + \
    #       ' ' + os.environ['TOUGH_EXE'] + self.local_dfnFlow_file

    cmd = 'time ' + os.environ['TOUGH_EXE'] + ' ' + self.local_dfnFlow_file

    self.print_log(f"--> Running: {cmd}")
    subprocess.call(cmd, shell=True)

    self.print_log('=' * 80)
    self.print_log("--> Running TOUGH Complete")
    self.print_log('=' * 80)
    self.print_log("\n")
