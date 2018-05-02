.. _output-chapter:

Output files
=============

dfnWorks outputs about a hundred different output files. This section describes the contents and purpose of each file.


File locations
----------------

Here is a list of file locations after dfnWorks has finished running:

dfnWorks-main
^^^^^^^^^^^^^^

- allboundaries.zone_
- aperture.dat_
- cellinfo.dat_
- darcyvel.dat_
- dfnTrans_output_dir_
- params.txt_
- PTDFN_control.dat_
- pboundary_back_n.zone_
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
- warningFileDFNGen.txt_

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

**connectivity.dat:**

.. _connectivity.dat:

Fracture connection list. Each row corresponds to a single fracture. The integers in that row are the fractures that fracture intersects with. These are the non-zero elements of the adjacency matrix. 

**convert_uge_params.txt:**

.. _convert_uge_params.txt:

Input file do conver_uge executable. 

**DFN_output.txt:**

.. _DFN_output.txt:

Detailed information about fracture network. Output by DFNGen.  

**families.dat:**

.. _families.dat: 

Information about fracture families. Produced by DFNGen. 

**input_generator.dat:**

.. _input_generator.dat:

Input file for DFN generator. 

**input_generator_clean.dat:**

.. _input_generator_clean.dat:

Abbreviated input file for DFN generator. 

**normal_vectors.dat:**

.. _normal_vectors.dat:

Normal vector of each fracture in the network. 

**poly_info.dat:**

.. _poly_info.dat:

Fracture information output by DFNGen. Format: Fracture Number, Family number, rotation angle for rotateln in LaGriT, x0, y0, z0, x1, y1, z1 (end points of line of rotation). 

**user_rects.dat:**

.. _user_rects.dat:

User defined rectangle file. 


**radii:**

.. _radii:

Subdirectory containing fracture radii information. 

**radii.dat:**

.. _radii.dat:

Concatentate file of fracture radii. Contains fractures that are removed due to isolation.  


**radii_Final.dat:**

.. _radii_Final.dat:

Concatentated file of final radii in the DFN. 


**rejections.dat:**

.. _rejections.dat:

Summary of rejection reasons. 


**rejectsPerAttempt.dat:**

.. _rejectsPerAttempt.dat:

Number of rejections per attempted fracture. 


**translations.dat:**

.. _translations.dat:

Fracture centriods. 


**triple_points.dat:**

.. _triple_points.dat:

x,y,z location of triple intersection points. 


**warningFileDFNGen.txt:**

.. _warningFileDFNGen.txt:

Warning file output by DFNGen. 

LaGrit 
---------

**bound_zones.lgi:**

.. _bound_zones.lgi:

LaGriT run file to identify boundary nodes. Dumps zone files. 

**boundary_output.txt:**

.. _boundary_output.txt:

Output file from bound_zones.lgi. 

**finalmesh.txt:**

.. _finalmesh.txt:

Brief summary of final mesh. 

**full_mesh.inp:**

.. _full_mesh.inp:

Full DFN mesh in AVS format. 

**full_mesh.gmv:**

.. _full_mesh.gmv:

Full DFN mesh in GMV (general mesh viewer) format. 

**full_mesh.lg:**

.. _full_mesh.lg:

Full DFN mesh in LaGriT binary format. 

**intersections:**

.. _intersections:

Directory containing intersection avs files output by the generator and used by LaGrit. 

**lagrit_logs:**

.. _lagrit_logs:

Directory of output files from individual meshing. 

**logx3dgen:**

.. _logx3dgen:

LaGriT output. 

**outx3dgen:**

.. _outx3dgen:

LaGriT output. 

**parameters:**

.. _parameters:

Directory of parameter*.mgli files used for fracture meshing. 

**params.txt:**

.. _params.txt:

Parameter information about the fracture network used for meshing. Includes number of fractures, h, visualmode, expected number of dudded points, and x,y,z dimensions of the domain. 

**polys:**

.. _polys:

Subdirectory contiaining AVS file for polygon boundaries. 

**tri_fracture.stor:**

.. _tri_fracture.stor:

FEHM stor file. Information about cell volume and area. 

**user_function.lgi:**

.. _user_function.lgi:

Function used by LaGriT for meshing. Defines coarsening gradient. 


PFLOTRAN 
----------

**aperture.dat:**

.. _aperture.dat:

Fracture based aperture value for the DFN. Used to rescale volumes in full_mesh_vol_area.uge. 

**cellinfo.dat:**

.. _cellinfo.dat:

Mesh information output by PFLOTRAN. 

**dfn_explicit-000.vtk:**

.. _dfn_explicit-000.vtk:

VTK file of initial conditions of PFLOTRAN. Mesh is not included in this file. 

**dfn_explicit-001.vtk:**

.. _dfn_explicit-001.vtk:

VTK file of steady-state solution of PFLOTRAN. Mesh is not included in this file. 

**dfn_explicit-mas.dat:**

.. _dfn_explicit-mas.dat:

pflotran information file. 

**dfn_explicit.in:**

.. _dfn_explicit.in:

pflotran input file. 

**_dfn_explicit.out:**

.. _dfn_explicit.out:

pflotran output file. 

**dfn_properties.h5:**

.. _dfn_properties.h5:

h5 file of fracture network properties, permeability, used by pflotran. 

**full_mesh.uge:**

.. _full_mesh.uge:

Full DFN mesh in UGE format. NOTE volumes are not correct in this file. This file is processed by convert_uge to create full_mesh_vol_area.uge, which has the correct volumes. 


**full_mesh_viz.inp:**

.. _full_mesh_viz.inp:

Full DFN mesh with limited attributes in AVS format. 

**full_mesh_vol_area.uge:**

.. _full_mesh_vol_area.uge:

Full DFN in uge format. Volumes and areas have been corrected. 

**materialid.dat:**

.. _materialid.dat:

Material ID (Fracture Number) for every node in the mesh. 

**parsed_vtk:**

.. _parsed_vtk:

Directory of pflotran results. 

**perm.dat:**

.. _perm.dat:

Fracture permeabilities in FEHM format. Each fracture is listed as a zone, starting index at 7. 

**pboundary_back_n.ex:**

.. _pboundary_back_n.ex:

Boundary file for back of the domain used by PFLOTRAN. 

**pboundary_bottom.ex:**

.. _pboundary_bottom.ex:

Boundary file for bottom of the domain used by PFLOTRAN. 

**pboundary_front_s.ex:**

.. _pboundary_front_s.ex:

Boundary file for front of the domain used by PFLOTRAN. 

**pboundary_left_w.ex:**

.. _pboundary_left_w.ex:

Boundary file for left side of the domain used by PFLOTRAN. 

**pboundary_right_e.ex:**

.. _pboundary_right_e.ex:

Boundary file for right of the domain used by PFLOTRAN. 

**pboundary_top.ex:**

.. _pboundary_top.ex:

Boundary file for top of the domain used by PFLOTRAN. 

dfnTrans 
-------------

**allboundaries.zone:**

.. _allboundaries.zone:

Concatenated file of all zone files. 

**darcyvel.dat:**

.. _darcyvel.dat:

Concatenated file of darcy velocities output by PFLOTRAN. 

**dfnTrans_output_dir:**

.. _dfnTrans_output_dir:

Outpur directory from DFNTrans. Particle travel times, trajectories, and reconstructed Velocities are in this directory. 

**PTDFN_control.dat:**

.. _PTDFN_control.dat:

Input file for DFNTrans. 

**pboundary_back_n.zone:**

.. _pboundary_back_s.zone:

Boundary zone file for the back of the domain. Normal vector (0,1,0) +- pi/2 

**pboundary_bottom.zone:**

.. _pboundary_bottom.zone:

Boundary zone file for the bottom of the domain. Normal vector (0,0,-1) +- pi/2 

**pboundary_front_s.zone:**

.. _pboundary_front_n.zone:

Boundary zone file for the front of the domain. Normal vector (0,-1,0) +- pi/2 


**pboundary_left_w.zone:**

.. _pboundary_left_w.zone:

Boundary zone file for the left side of the domain. Normal vector (-1,0,0) +- pi/2 


**pboundary_right_e.zone:**

.. _pboundary_right_e.zone:


Boundary zone file for the bottom of the domain. Normal  vector (1,0,0) +- pi/2 

**pboundary_top.zone:**

.. _pboundary_top.zone:

Boundary zone file for the top of the domain. Normal vector (0,0,1) +- pi/2 

