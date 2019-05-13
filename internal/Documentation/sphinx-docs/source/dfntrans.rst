.. _dftrans-chapter:

dfnTrans
============

dfnTrans is a method for resolving solute transport using control volume flow
solutions obtained from dfnFlow on the unstructured mesh generated using dfnGen.
We adopt a Lagrangian approach and represent a non-reactive conservative solute
as a collection of indivisible passive tracer particles. Particle tracking
methods (a) provide a wealth of information about the local flow field, (b) do
not suffer from numerical dispersion, which is inherent in the discretizations
of advection–dispersion equations, and (c) allow for the computation of each
particle trajectory to be performed in an intrinsically parallel fashion if
particles are not allowed to interact with one another or the fracture network.
However, particle tracking on a DFN poses unique challenges that arise from (a)
the quality of the flow solution, (b) the unstructured mesh representation of
the DFN, and (c) the physical phenomena of interest. The flow solutions obtained
from dfnFlow are locally mass conserving, so the particle tracking method does
not suffer from the problems inherent in using Galerkin finite element codes. 

dfnTrans starts from  reconstruction of local velocity field: Darcy fluxes
obtained using dfnFlow are used to reconstruct the local velocity field, which
is used for particle tracking on the DFN. Then, Lagrangian transport simulation
is used to determine pathlines through the network and simulate transport. It is
important to note that dfnTrans itself only solves for advective transport, but
effects of longitudinal dispersion and matrix diffusion, sorption, and other
retention processes are easily incorporated by post-processing particle
trajectories. The detailed description of dfnTrans algorithm and implemented
methodology is in `Makedonska, N., Painter, S. L., Bui, Q. M., Gable, C. W., &
Karra, S. (2015). Particle tracking approach for transport in three-dimensional
discrete fracture networks. Computational Geosciences, 19(5), 1123-1137.
<http://link.springer.com/article/10.1007/s10596-015-9525-4>`_


All source files of C code of dfnTrans are in ``DFNTrans/`` directory of
dfnWorks 2.2. It compiles under linux/mac machines using ``makefile``.  In order
to run transport, first, all the parameters and paths should be set up in the
PTDFN Control file, PTDFN_control.dat. Then, the following command should be
run: 

``./dfnTrans PTDFN_control.dat``

The control  file sets all necessary parameters to run particle tracking in
dfnWorks.  Below is one control file example that includes a short
explanation of each parameter setting:

.. code-block:: c

    /***********************************************************************/
    /*   CONTROL FILE FOR PARTICLE TRACKING IN DISCRETE FRACTURE NETWORK   */
    /***********************************************************************/

    /**********************  INPUT FILES: grid *****************************/
    /**** input files with grid of DFN, mainly it's output of DFNGen ******/
    param: params.txt
    poly: poly_info.dat
    inp: full_mesh.inp
    stor: full_mesh.stor
    boundary: allboundaries.zone
    /* boundary conditions: reading the nodes that belong to in-flow and 
    out-flow boundaries. Should be consistent with those applied to obtain
    steady state pressure solution (PFLOTRAN)   */
    /*1 - top;  2 - bottom;  3 - left_w;  4 - front_s;  5 - right_e;  6 - back_n */
    in-flow-boundary: 3 
    out-flow-boundary: 5


    /**************** INPUT FILES: PFLOTRAN flow solution *******************/
    PFLOTRAN: yes
    PFLOTRAN_vel: darcyvel.dat 
    PFLOTRAN_cell: cellinfo.dat
    PFLOTRAN_uge: full_mesh_vol_area.uge

    /**************** INPUT FILES: FEHM flow solution ***********************/
    /*currently we are using PFLOTRAN , but the code would work with FEHM, too */ 
    FEHM: no
    FEHM_fin: dfn.fin

    /************************  OUTPUT FILES  ********************************/
    /* initial grid info structure output, usefull for debugging */
    out_grid: no
    /* flow field: 3D Darcy velocities: output file has an each nodes position 
    and its Darcy velocity, reconstructed from fluxes */ 
    out_3dflow: no
    /* out initial positions of particles into separate file */ 
    out_init: no 
    /* out particle trajectories tortuosity file, torts.dat */
    out_tort: no

    /*************** output options for particles trajectories ****************/
    /* output frequency is set according to trajectories curvature. We check the 
    curvature of particles trajectory each segment, from intersection to intersection.
    If it's like a straight line, then the output is less frequent (in case of 
    "out_curv:yes", if "no",  the output file will contain every time step) */
    out_curv: yes 
    /* output into avs file (GMV visualization, Paraview visualization) */
    out_avs: no 
    /* output into trajectories ascii files (veloc+posit+cell+fract+time) */
    out_traj: yes

    /* temporary outputs (every time step from intersection to intersection)*/
    /* use outputs to file or memory buffer. Memory buffer by default */
    out_filetemp: no

    /************* output directories *************************************/
    out_dir: traj_SR /* path and name of directory where all the particle 
                         tracking results will be written*/


    out_path: trajectories /*name of directory where all particle
                        trajectories will be saved, in out_dir path */ 

    /* name of resultant file (in out_dir path), which contains total travel time and 
                    final positions of particles */
    out_time: partime



    /**************** PARTICLES INITIAL POSITIONS ******************************/

    /*****  particles positions according to in-flow flux weight *********/
    init_fluxw: no //turn on this input option (don't forget to turn off rest of PARTICLES INITIAL POSITIONS options)
    init_totalnumber: 10000 // distance [m] between particles at inflow face for equal flux weight calculation


    /****init_nf: if yes - the same number of particles (init_partn) will be placed 
         on every boundary fracture edge on in-flow boundary, 
         equidistant from each other ****/
    init_nf: yes 
    init_partn: 10

    /****init_eqd: if yes - particles will be placed on the same distance from
         each other on all over in-flow boundary edges ***********************/  
    init_eqd: no  //maximum number of particles that user expects on one boundary edge
    init_npart: 100

    /*** all particles start from the same region at in-flow boundary, in a range  
        {in_xmin, in_xmax,in_ymin, in_ymax, in_zmin, in_zmax} **************/
    init_oneregion: no    
    in_partn: 100000
    in_xmin: -50.0 
    in_xmax: -50.0 
    in_ymin: -20.0 
    in_ymax:  20.0 
    in_zmin: -15.0 
    in_zmax:  0.0

    /**** all particles are placed randomly over all fracture surface 
         (not only on boundary edges!) ************************************/
    init_random: no 
    // total number of particles
    in_randpart: 100    

    /**** all particles are seed randomly over matrix, 
         they will start travel in DFN from the node/cell that is closest to
         their initial position in rock matrix ***************************/
          
    init_matrix: no
    // to obtain these files, run python script RandomPositGener.py
    inm_coord: ParticleInitCoordR.dat
    inm_nodeID: ClosestNodeR.inp
    inm_porosity: 0.02
    inm_diffcoeff: 1.0e-12

    /*************** Intersection Mixing Rule **********************************/
    /****streamline_routing: if yes - streamline routing is the selected subgrid process
         otherwise the complete mixing rule is selected ****/
    streamline_routing: no 


    /************* TIME DOMAIN RANDOM WALK ******************************/
    tdrw: no 
    tdrw_porosity: 0.02
    tdrw_diffcoeff: 1.0e-11

    /****************** FLOW AND FRACTURE PARAMETERS **********************/
    porosity: 1.0 // porosity 
    density: 997.73  //fluid density 
    satur: 1.0
    thickness: 1.0 //DFN aperture  (used in case of no aperture file provided)

    /************************ APERTURE *********************************/ 

    aperture: yes  //DFN aperture
    aperture_type: frac //aperture is giving per cell (type "cell") 
    //    or per fracture (type "frac")
    // for now we use an aperture giving per fracture
    aperture_file: aperture.dat


    /********************  TIME ********************************************/
    timesteps: 2000000
    //units of time (years, days, hours, minutes) 
    time_units: seconds

    /**** flux weighted particles*/
    /**** in case of random initial positions of particles - it's aperture weighted **/
    flux_weight: yes
    /* random generator seed */
    seed: 337799

    /*********************  Control Plane/Cylinder Output ********************/
    /*** virtual Control planes will be build in the direction of flow. 
    Once particle crosses the control plane, it's position, velocity, time 
    will output to an ascii file. ****/ 
    ControlPlane: yes 

    /* the path and directory name with all particles output files */
    control_out: outcontroldir

    /* Delta Control Plane - the distance between control planes */
    delta_Control: 1

    /* ControlPlane: direction of flow: x-0; y-1; z-2 */
    flowdir: 0 


    /**************************************************************************/
    /endendend/
    END


