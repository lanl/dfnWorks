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


def load_material_ids(self, material_id_file, skip_header_lines=0):
    """Load one material id per element from a whitespace-delimited file.

    Generic loader: skips ``skip_header_lines`` lines, then reads every
    remaining whitespace-separated token as an integer, one per element, in
    the same order as the UGE ``CELLS`` section.

    This has not been validated against a real dfnWorks ``materialid.dat``
    file, if your header doesn't match a simple fixed number of lines to
    skip, adjust ``skip_header_lines`` accordingly or parse the file
    yourself and pass the resulting list straight to ``material_ids=`` on
    ``convert_uge_to_tough``/``lagrit_to_tough`` instead of using this
    loader.

    Parameters
    ----------
    self:
        The parent DFNWorks object, used only for ``self.print_log``.
    material_id_file:
        Path to the material-id file.
    skip_header_lines:
        Number of leading lines to discard before parsing integers.
        Default ``0``.

    Returns
    -------
    list[int]
        One material id per element, in CELLS order.
    """
    self.print_log(f"--> Gather material ids from file: {material_id_file}")
    with open(material_id_file, "r") as f:
        lines = f.readlines()[skip_header_lines:]
    material_ids = [int(float(tok)) for line in lines for tok in line.split()]
    self.print_log(f"--> Loaded {len(material_ids)} material ids")
    return material_ids


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
    # return f"{first}{second}{third}{local_index:02d}"
    return f"{first}{second}{third}{local_index:2d}"

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
    material_ids=None,
    material_names=None,
    default_rock_type="DFNMM",
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
    and centroid coordinates.  By default every element is assigned the
    rock-type given by ``default_rock_type`` (``"DFNMM"`` unless
    overridden).  Pass ``material_ids``/``material_names`` to assign
    different rock types to different elements instead, see below.
    Boundary elements (e.g. injection/production wells) are set to a large
    volume (1 × 10⁵¹) automatically when listed in ``boundary_nodes``/
    ``boundary_filenames``.

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
    material_ids:
        Optional per-element material id, used to look up each element's
        rock-type name in ``material_names``. If omitted (left as
        ``None``), falls back to ``self.material_ids`` when the DFN object
        has that attribute set, that's the normal way this gets supplied,
        pass it explicitly here only to override that for one call.
        Two forms are accepted:

        * A dense list/array with exactly ``num_ele`` entries (one per
          element, in the same order as the UGE ``CELLS`` section, i.e.
          ``material_ids[i-1]`` is the id for 1-based element ``i``).
          Every distinct id that appears must have an entry in
          ``material_names``, there is no silent fallback to
          ``default_rock_type`` for a dense list, an unmapped id raises.
        * A sparse ``dict`` keyed by 1-based element index. Elements not
          present in the dict use ``default_rock_type``, this form is for
          when you only want to override a subset of elements.

        If omitted entirely, every element gets ``default_rock_type``
        (the original single-rock-type behavior).
    material_names:
        Mapping of material id -> rock-type name string. Required when
        ``material_ids`` is given. Each name must be at most 5 characters
        (the width of the ELEME rock-type field, and the name TOUGH will
        look for in your input file's ``ROCKS`` block), a longer name
        silently corrupts the column layout rather than erroring inside
        TOUGH, so this is validated upfront here instead.
    default_rock_type:
        Rock-type name used for any element not otherwise assigned by
        ``material_ids``/``material_names`` (or for every element, if
        ``material_ids`` is omitted). Default ``"DFNMM"``. Must also be at
        most 5 characters.

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

    def _validate_rock_name(name):
        if not isinstance(name, str) or len(name) < 1 or len(name) > 5:
            raise ValueError(
                f"Rock-type name {name!r} is invalid: TOUGH ELEME/ROCKS "
                f"names must be a string of 1-5 characters."
            )

    # If not passed explicitly, fall back to DFN.material_ids, since that's
    # where this is generally set for a given DFN.
    if material_ids is None:
        material_ids = getattr(self, "material_ids", None)

    _validate_rock_name(default_rock_type)
    material_ids_is_dict = isinstance(material_ids, dict)
    if material_ids is not None:
        if material_names is None:
            raise ValueError("material_names must be provided when material_ids is given")
        for name in material_names.values():
            _validate_rock_name(name)
        if not material_ids_is_dict:
            # Dense form: require full coverage of every id actually used,
            # checked once num_ele is known, below.
            distinct_ids = set(material_ids)
        else:
            distinct_ids = set(material_ids.values())
        missing = sorted(mid for mid in distinct_ids if mid not in material_names)
        if missing:
            raise ValueError(
                f"material_names is missing entries for material id(s): {missing}. "
                f"Every distinct id used in material_ids must have a corresponding "
                f"rock-type name, there is no silent fallback for unmapped ids."
            )

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

        if material_ids is not None and not material_ids_is_dict and len(material_ids) != num_ele:
            raise ValueError(
                f"material_ids has {len(material_ids)} entries, but the mesh has "
                f"{num_ele} elements (from the UGE CELLS header); a dense "
                f"material_ids list must have exactly one entry per element, in "
                f"the same order as the UGE file. Use a dict keyed by element "
                f"index instead if you only want to specify a subset."
            )

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

            # Resolve this element's rock type: dense list (indexed by
            # position), sparse dict (indexed by 1-based element id), or
            # just the default if material_ids wasn't given / doesn't cover
            # this element.
            if material_ids is None:
                rock_type = default_rock_type
            elif material_ids_is_dict:
                mid = material_ids.get(i)
                rock_type = material_names[mid] if mid is not None else default_rock_type
            else:
                rock_type = material_names[material_ids[i - 1]]

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
# INCON (fixed boundary condition) writer
# ---------------------------------------------------------------------------

def write_tough_incon(self, boundary_conditions, output_filename="INCON", porosity=0.3):
    """Write a TOUGH INCON file fixing primary variables at boundary nodes.

    This is the INCON-side counterpart to the ``boundary_nodes`` volume
    override in ``convert_uge_to_tough``. Setting a node's volume to 1e50/1e51
    stops its state from changing; this function is what actually assigns the
    state to hold it at. Nodes must get *both* treatments to behave as a true
    Dirichlet boundary condition -- this function alone does not fix the
    volume, and ``boundary_nodes=`` alone does not fix the state.

    Unlike the single flat ``boundary_nodes`` list used for the volume
    override, this function keeps each zone file as its own group so
    different faces can be pinned to different states, e.g. a high pressure
    on the right face and a low pressure on the left.

    Parameters
    ----------
    self:
        The parent DFNWorks object, used only for ``self.print_log``.
    boundary_conditions:
        Mapping of zone-file path -> primary variable tuple, e.g.::

            {
                "boundary_right_w.ex": (2.0e6, 1.0e-10, 25.0),
                "boundary_left_e.ex":  (1.0e5, 1.0e-10, 25.0),
            }

        Each tuple must contain exactly NEQ values, in the order and units
        of the EOS's primary variables (e.g. for REAL_GAS+H2O without salt,
        single-phase aqueous state: pressure [Pa], dissolved-gas mass
        fraction [-], temperature [C] -- see the RealGasBrine manual's
        Table 3.1 for other phase states).
    output_filename:
        Destination path for the TOUGH INCON file. Default ``"INCON"``.
    porosity:
        Porosity value written into every entry's header record. This must
        be a real number, not blank -- confirmed against a real TOUGH+ SAVE
        file, a blank porosity field causes the whole entry to be ignored
        and the element falls back to the PARAM.4 defaults instead of the
        primary variables given here. Default ``0.3``, matching the DFNMM
        rock type's default porosity; pass the actual value for your rock
        type if it differs.

    Notes
    -----
    * If the same node id appears in more than one zone file, whichever
      entry is written last (dict iteration order) wins; overlapping
      boundary groups are not merged or averaged, so keep zone files
      non-overlapping.
    * To also fix the volumes for these same nodes, pass the union of all
      zone-file node ids as ``boundary_nodes`` to ``convert_uge_to_tough``
      (or ``lagrit_to_tough``) -- see ``load_boundary_nodes`` below.
    """
    self.print_log("--> Starting: Writing TOUGH INCON boundary conditions")

    with open(output_filename, "w", encoding="utf-8", newline="\n") as fout:
        fout.write(f"{'INCON':<83}\n")
        for zone_file, primary_vars in boundary_conditions.items():
            node_ids = self.load_zone_file_nodes(zone_file)
            self.print_log(
                f"--> {zone_file}: {len(node_ids)} boundary nodes, "
                f"primary variables = {primary_vars}"
            )
            for node_id in node_ids:
                element_name = tough_element_name(node_id)
                # INCON.1  Format(A5,I5,5X,E15.9): name, NSEQ (blank = 0),
                # blank spacer, PORX. PORX must be a real value, not blank --
                # a blank porosity field causes TOUGH+ to fall back to the
                # PARAM.4 defaults for the WHOLE entry (confirmed against a
                # real SAVE file), so this is not optional like the classic
                # TOUGH2 docs suggest.
                fout.write(f"{element_name:5s}{'':5s}{'':5s}{porosity:15.8E}\n")
                # INCON.2  Format(4E20.13): up to 4 primary variables per
                # line; continue on additional lines if NEQ > 4.
                remaining = list(primary_vars)
                while remaining:
                    chunk, remaining = remaining[:4], remaining[4:]
                    fout.write("".join(f"{v:20.13E}" for v in chunk) + "\n")
        # Blank line signals the end of the INCON block to TOUGH.
        fout.write("\n")

    self.print_log("--> Complete: Writing TOUGH INCON boundary conditions")


def load_boundary_nodes(self, boundary_filenames):
    """Return the union of node ids from one or more dfnWorks zone files.

    Convenience helper for building the ``boundary_nodes`` argument to
    ``convert_uge_to_tough``/``lagrit_to_tough`` from the same zone files
    passed to ``write_tough_incon``, so the volume override and the fixed
    INCON state always land on the same set of nodes.

    Parameters
    ----------
    self:
        The parent DFNWorks object, used only for ``self.print_log``.
    boundary_filenames:
        Iterable of zone-file paths (e.g. dfnWorks ``.ex`` boundary files).

    Returns
    -------
    set[int]
        The union of 1-based node ids across all supplied zone files.
    """
    node_ids: set[int] = set()
    for zone_file in boundary_filenames:
        node_ids.update(self.load_zone_file_nodes(zone_file))
    return node_ids


# ---------------------------------------------------------------------------
# Embed boundary conditions directly in the INFILE (avoids the INCON
# overwrite problem below)
# ---------------------------------------------------------------------------

def write_infile_incon_block(self, infile_path, boundary_conditions, output_path=None, porosity=0.3):
    """Embed boundary-condition INCON entries directly into an INFILE.

    IMPORTANT: TOUGH+ regenerates the standalone INCON disk file from
    whatever is in the INFILE's own INCON block during startup, even if
    that block is blank. So a separate INCON file built by
    ``write_tough_incon`` gets silently overwritten the moment ``tough()``
    actually runs the executable, before it's ever used. The fix is to put
    the entries directly in the INFILE's INCON block instead of relying on
    a standalone file at all, this function does that splice.

    Parameters
    ----------
    self:
        The parent DFNWorks object, used only for ``self.print_log``.
    infile_path:
        Path to the existing INFILE (must contain a line starting with
        ``INCON`` in columns 1-5, immediately followed on the next line by
        the blank record that currently closes the empty block).
    boundary_conditions:
        Same mapping as ``write_tough_incon``: zone-file path -> primary
        variable tuple, e.g. ``{"boundary_right_e.zone": (2.0e6, 1.0e-10, 25.0)}``.
    output_path:
        Where to write the resulting INFILE. Defaults to overwriting
        *infile_path* in place.
    porosity:
        Porosity value written into every entry's header record; see
        ``write_tough_incon`` for why this must be a real number, not blank.

    Notes
    -----
    * This does not touch the separate INCON file at all, and after using
      this, you should delete any leftover standalone INCON file so there's
      no ambiguity about which one TOUGH+ is reading (it will read the one
      embedded in INFILE either way, since that's what gets regenerated to
      disk at startup, but a stale separate file lying around is a
      confusing thing to leave behind).
    * As with ``write_tough_incon``, this only writes the *state*. The
      volume override (``boundary_nodes=`` on ``convert_uge_to_tough`` /
      ``lagrit_to_tough``) is a separate, still-required step to actually
      hold these nodes at a fixed value.
    """
    self.print_log(f"--> Starting: Embedding INCON boundary conditions into {infile_path}")

    with open(infile_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    incon_idx = None
    for i, line in enumerate(lines):
        if line[:5] == "INCON":
            incon_idx = i
            break
    if incon_idx is None:
        raise ValueError(f"No INCON block header found in {infile_path}")

    # The existing block is assumed empty: the very next line is the blank
    # record that closes it. Build the new entries and insert them between
    # the header and that blank line.
    entry_lines = []
    for zone_file, primary_vars in boundary_conditions.items():
        node_ids = self.load_zone_file_nodes(zone_file)
        self.print_log(
            f"--> {zone_file}: {len(node_ids)} boundary nodes, "
            f"primary variables = {primary_vars}"
        )
        for node_id in node_ids:
            element_name = tough_element_name(node_id)
            entry_lines.append(f"{element_name:5s}{'':5s}{'':5s}{porosity:15.8E}\n")
            remaining = list(primary_vars)
            while remaining:
                chunk, remaining = remaining[:4], remaining[4:]
                entry_lines.append("".join(f"{v:20.13E}" for v in chunk) + "\n")

    new_lines = lines[: incon_idx + 1] + entry_lines + lines[incon_idx + 1 :]

    dest = output_path if output_path is not None else infile_path
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(new_lines)

    self.print_log(f"--> Complete: Embedding INCON boundary conditions into {dest}")


# ---------------------------------------------------------------------------
# Remove the empty INCON block from an INFILE
# ---------------------------------------------------------------------------

def remove_incon_block(self, infile_path, output_path=None):
    """Delete an empty INCON block from an INFILE so a standalone file wins.

    A bare ``INCON`` keyword followed by a blank line is TOUGH+'s
    documented way of explicitly forcing PARAM.4 defaults and ignoring any
    standalone INCON file on disk, that's the behavior you were hitting.
    Omitting the block entirely (the same way ELEME/CONNE are omitted when
    a separate MESH file is used) should let TOUGH+ fall through to reading
    the standalone INCON file undisturbed, instead of regenerating it from
    the (empty) block content.

    Parameters
    ----------
    self:
        The parent DFNWorks object, used only for ``self.print_log``.
    infile_path:
        Path to the existing INFILE. Must contain a line starting with
        ``INCON`` in columns 1-5, immediately followed by the blank record
        that closes the (empty) block.
    output_path:
        Where to write the resulting INFILE. Defaults to overwriting
        *infile_path* in place.

    Notes
    -----
    * This is the alternative to ``write_infile_incon_block``: keep your
      boundary conditions in a standalone file written by
      ``write_tough_incon``, and use this function once on your INFILE
      template so that file is actually respected instead of clobbered.
    * If TOUGH+ still overwrites the INCON file after this change, the
      escape-hatch behavior described above isn't the whole story, and it's
      worth checking the next .out log for the exact wording around
      "Write file <INCON>" to see what triggered it that time.
    """
    self.print_log(f"--> Starting: Removing empty INCON block from {infile_path}")

    with open(infile_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    incon_idx = None
    for i, line in enumerate(lines):
        if line[:5] == "INCON":
            incon_idx = i
            break
    if incon_idx is None:
        raise ValueError(f"No INCON block header found in {infile_path}")

    # Expect the block to be empty: header line immediately followed by the
    # blank record that closes it. Remove both.
    if lines[incon_idx + 1].strip() != "":
        raise ValueError(
            f"INCON block at line {incon_idx + 1} is not empty -- "
            f"refusing to remove it automatically, check {infile_path} by hand"
        )
    new_lines = lines[:incon_idx] + lines[incon_idx + 2 :]

    dest = output_path if output_path is not None else infile_path
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(new_lines)

    self.print_log(f"--> Complete: Removing empty INCON block from {dest}")


# ---------------------------------------------------------------------------
# High-level entry point
# ---------------------------------------------------------------------------

def lagrit_to_tough(self, tough_mesh_filename = "MESH", boundary_filenames = None, boundary_nodes = None,
                     material_ids = None, material_names = None, default_rock_type = "DFNMM"):
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
    boundary_filenames, boundary_nodes, material_ids, material_names, default_rock_type:
        Passed straight through to ``convert_uge_to_tough``, see there for
        details, in particular for how to assign different rock types to
        different elements via ``material_ids``/``material_names``.
    """
    self.print_log("\n--> Converting mesh file format to TOUGH mesh: Starting\n")
    # Step 1: Run the LaGriT pipeline; produces full_mesh_vol_area.uge.
    self.correct_uge_file()
    # Step 2: Translate the UGE output to the TOUGH MESH format.
    self.convert_uge_to_tough('full_mesh_vol_area.uge', tough_mesh_filename, boundary_filenames, boundary_nodes,
                               material_ids, material_names, default_rock_type)
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

    # cmd = 'time ' + os.environ['TOUGH_EXE'] + ' ' + self.local_dfnFlow_file
    # cmd = 'time ' + os.environ['TOUGH_EXE'] + ' <' + self.local_dfnFlow_file + '>' + self.local_dfnFlow_file + '.out'

    # self.print_log(f"--> Running: {cmd}")
    # subprocess.call(cmd, shell=True)

    cmd = 'time ( ' + os.environ['TOUGH_EXE'] + ' <' + self.local_dfnFlow_file + ' | tee ' + self.local_dfnFlow_file + '.out )'

    self.print_log(f"--> Running: {cmd}")
    subprocess.call(cmd, shell=True)

    self.print_log('=' * 80)
    self.print_log("--> Running TOUGH Complete")
    self.print_log('=' * 80)
    self.print_log("\n")
