.. _output-chapter_

Output files
=============

dfnWorks outputs about a hundred different output files. This section describes the contents and purpose of each file.


File locations
----------------

Here is a list of file locations after dfnWorks has finished running:

dfnworks-main
^^^^^^^^^^^^^^

- allboundaries.zone_
- aperture.dat_
- cell_info.dat_
- darcyvel.dat_
- dfnTrans_output_dir_
- params.txt_
- PTDFN_control.dat_
- tri_fracture.stor_
- boundary_back_n.zone_
- pboundary_bottom.zone_
- pboundary_front_s.zone_
- pboundary_left_w.zone_
- pboundary_right_e.zone_
- pboundary_top.zone_


dfnGen
^^^^^^^

- connectivity.dat_
- DFN_output.txt_
- families.dat_
- input_generator.dat_
- input_generator_clean.dat_
- normal_vectors.dat_
- radii_
- radii.dat_
- radii_Final.dat_
- rejections.dat_
- rejectsPerAttempt.dat_
- translations.dat_
- triple_points.dat_
- user_rects.dat_
- warningFileDFNGen.dat_

LaGriT
^^^^^^^^

- bound_zones.lgi_
- boundary_output.txt_
- finalmesh.txt_
- full_mesh.inp_
- full_mesh.gmv_
- full_mesh.lg_
- intersections_
- lagrit_logs_
- logx3dgen_
- outx3dgen_
- parameters_
- polys_
- tri_fracture.stor_
- user_function.lgi_
- user_function2.lgi_

PFLOTRAN
^^^^^^^^^

- aperture.dat_
- cellinfo.dat_
- dfn_explicit-000.vtk_
- dfn_explicit-001.vtk_
- dfn_explicit-mas.dat_
- dfn_explicit.in_
- dfn_explicit.out_
- dfn_properties.h5_
- full_mesh.uge_
- full_mesh_viz.inp_
- full_mesh_vol_area.uge_
- materialid.dat_
- parsed_vtk_
- perm.dat_
- pboundary_back_n.ex_
- pboundary_bottom.ex_
- pboundary_front_s.ex_
- pboundary_left_w.ex_
- pboundary_right_e.ex_
- pboundary_top.ex_


dfnGen 
--------

connectivity.dat:

**connectivity.dat:**

.. _connectivity.dat:

Fracture connection list. Each row corresponds to a single fracture. The integers in that row are the fractures that fracture intersects with. These are the non-zero elements of the adjacency matrix. Located in generator directory.  

convert_uge_params.txt:

**convert_uge_params.txt:**

.. _convert_uge_params.txt:

Input file do conver_uge executable. Located in pflotran directory. 


**DFN_output.txt:**

.. _DFN_output.txt:

Detailed information about fracture network. Output by DFNGen.  Located in generatory directory once network is complete. 

**families.dat:**

.. _families.dat:
Information about fracture families. Produced by DFNGen. Located in generator directory. 

**input_generator.dat:**

.. _input_generator.dat:
Input file for DFN generator. Located in generator.

**input_generator_clean.dat:**

.. _input_generator_clean.dat:
Abbreviated input file for DFN generator. Located in main directory.

**normal_vectors.dat:**

.. _normal_vectors.dat:
Normal vector of each fracture in the network. Located in generator. 

**poly_info.dat:**

.. _poly_info.dat:
Fracture information output by DFNGen. Format: Fracture Number, Family number, rotation angle for rotateln in LaGriT, x0, y0, z0, x1, y1, z1 (end points of line of rotation). Located in LaGriT. 

**user_rects.dat:**

.. _user_rects.dat:
User defined rectangle file. Located in generator directory once network is complete. 


**radii:**

.. _radii:
Subdirectory containing fracture radii information. Located in generator.


**radii.dat:**

.. _radii.dat:
Concatentate file of fracture radii. Contains fractures that are removed due to isolation.  Located in generator.


**radii_Final.dat:**

.. _radii_Final.dat:
Concatentated file of final radii in the DFN. Located in generator.


**rejections.dat:**

.. _rejections.dat:
Summary of rejection reasons. Located in generator.


**rejectsPerAttempt.dat:**

.. _rejectsPerAttempt.dat:
Number of rejections per attempted fracture. Located in generator.


**translations.dat:**

.. _translations.dat:
Fracture centriods. Located in generator.


**triple_points.dat:**

.. _triple_points.dat:
x,y,z location of triple intersection points. Located in main directory.


**warningFileDFNGen.txt:**

.. _warningFileDFNGen.txt:
Warning file output by DFNGen. Located in generator. 

LaGrit 
---------

**bound_zones.lgi:**

.. _bound_zones.lgi:
LaGriT run file to identify boundary nodes. Dumps zone files. Located in LaGriT directory.

**boundary_output.txt:**

.. _boundary_output.txt:
Output file from bound_zones.lgi. Located in LaGriT directory. 

**finalmesh.txt:**

.. _finalmesh.txt:
Brief summary of final mesh. Located in LaGriT directory. 

**full_mesh.inp:**

.. _full_mesh.inp:
Full DFN mesh in AVS format. Located in main directory.

**full_mesh.gmv:**

.. _full_mesh.gmv:
Full DFN mesh in GMV (general mesh viewer) format. Located in LaGriT directory.

**full_mesh.lg:**

.. _full_mesh.lg:
Information: Full DFN mesh in LaGriT binary format. Located in LaGriT directory. 

**intersections:**

.. _intersections:
Directory containing intersection avs files output by the generator and used by LaGrit. Located in LaGriT. 

**lagrit_logs:**

.. _lagrit_logs:
Directory of output files from individual meshing. Located in LaGriT

**logx3dgen:**

.. _logx3dgen:
LaGriT output. Located in LaGriT. 

**outx3dgen:**

.. _outx3dgen:
LaGriT output. Located in LaGriT.

**parameters:**

.. _parameters:
Directory of parameter*.mgli files used for fracture meshing. Located in LaGriT. 

**params.txt:**

.. _params.txt:
Parameter information about the fracture network used for meshing. Includes number of fractures, h, visualmode, expected number of dudded points, and x,y,z dimensions of the domain. Located in main directory.

**polys:**

.. _polys:
Subdirectory contiaining AVS file for polygon boundaries. Located in LaGriT.

**tri_fracture.stor:**

.. _tri_fracture.stor:
FEHM stor file. Information about cell volume and area. Located in LaGriT.

.. _user_function.lgi
Function used by LaGriT for meshing. Defines coarsening gradient. Located in LaGriT.

.. _user_function2.lgi
Function used by LaGriT for meshing. Defines coarsening gradient. Located in LaGriT.


PFLOTRAN 
----------

.. target_notes::
    
    .. _aperture.dat:
    Fracture based aperture value for the DFN. Used to rescale volumes in full_mesh_vol_area.uge. Located in main directory.

    .. _cellinfo.dat:
    Mesh information output by PFLOTRAN. Used by DFNTrans. Located in main directory. 

    .. _dfn_explicit-000.vtk
    VTK file of initial conditions of PFLOTRAN. Mesh is not included in this file. Located in pflotran directory.

    .. _dfn_explicit-001.vtk
    VTK file of steady-state solution of PFLOTRAN. Mesh is not included in this file. Located in pflotran directory.

    .. _dfn_explicit-mas.dat:
    pflotran information file. Located in pflotran directory. 

    .. _dfn_explicit.in:
    pflotran input file. Located in pflotran directory. 

    .. _dfn_explicit.out:
    pflotran output file. Located in pflotran directory. 

    .. _dfn_properties.h5:
    h5 file of fracture network properties, permeability, used by pflotran. Located in pflotran directory.

    .. _full_mesh.uge:
    Full DFN mesh in UGE format. NOTE volumes are not correct in this file. This file is processed by convert_uge to create full_mesh_vol_area.uge, which has the correct volumes. Located in PFLOTRAN directory. 


    .. _full_mesh_viz.inp:
    Full DFN mesh with limited attributes in AVS format. Located in LaGriT directory.  

    .. _full_mesh_vol_area.uge:
    Full DFN in uge format. Volumes and areas have been corrected. Used by PFLOTRAN. Located in main directory. 

    .. _materialid.dat:
    Material ID (Fracture Number) for every node in the mesh. Used by lagrit2pflotran. Located in main directory.

    .. _parsed_vtk:
    Directory of pflotran results. Located in main directory.

    .. _perm.dat:
    Fracture permeabilities in FEHM format. Each fracture is listed as a zone, starting index at 7. Located in main directory.

    .. _pboundary_back_n.ex:
    Boundary file for back of the domain used by PFLOTRAN. Located in pflotran directory. 

    .. _pboundary_bottom.ex:
    Boundary file for bottom of the domain used by PFLOTRAN. Located in pflotran directory. 

    .. _pboundary_front_s.ex:
    Boundary file for front of the domain used by PFLOTRAN. Located in pflotran directory. 

    .. _pboundary_left_w.ex:
    Boundary file for left side of the domain used by PFLOTRAN. Located in pflotran directory. 

    .. _pboundary_right_e.ex:
    Boundary file for right of the domain used by PFLOTRAN. Located in pflotran directory. 

    .. _pboundary_top.ex:
    Boundary file for top of the domain used by PFLOTRAN. Located in pflotran directory.  

dfnTrans 
-------------

**allboundaries.zone:**

.. _allboundaries.zone:
Concatenated file of all zone files. Used by DFNTrans. Located in main directory 

**darcyvel.dat:**

.. _darcyvel.dat:
Concatenated file of darcy velocities output by PFLOTRAN. Used by DFNTrans. Located in main directory.

**dfnTrans_output_dir:**

.. _dfnTrans_output_dir:
Outpur directory from DFNTrans. Particle travel times, trajectories, and reconstructed Velocities are in this directory. Located in main directory.

**PTDFN_control.dat:**

.. _PTDFN_control.dat:
Input file for DFNTrans. Located in main directory. 

**tri_fracture.stor:**

.. _tri_fracture.stor:
FEHM stor file. Information about cell volume and area. Used by DFNTrans. Located in main directory.

**pboundary_back_n.zone:**

.. _pboundary_back_n.zone:
Boundary zone file for the back of the domain. Used by DFNTrans. Located in the main diretory.


**pboundary_bottom.zone:**

.. _pboundary_bottom.zone:
Boundary zone file for the bottom of the domain. Used by DFNTrans. Located in the main diretory.

**pboundary_front_s.zone:**

.. _pboundary_front_s.zone:
Boundary zone file for the front of the domain. Used by DFNTrans. Located in the main diretory.


**pboundary_left_w.zone:**

.. _pboundary_left_w.zone:
Boundary zone file for the left side of the domain. Used by DFNTrans. Located in the main diretory.


**pboundary_right_e.zone:**

.. _pboundary_right_e.zone:
Boundary zone file for the bottom of the domain. Used by DFNTrans. Located in the main diretory.

**pboundary_top.zone:**

.. _pboundary_top.zone:
Boundary zone file for the top of the domain. Used by DFNTrans. Located in the main diretory.

