import sys
from integrated import *

def add_to_gen_input(num_shape, shape, in_var, obj_var):
    '''add parameter obj_var into generation input'''
    line='%s : { '%in_var
    for i in range(num_shape):
        if type(shape[obj_var][i])==int:
            line+='%d,'%shape[obj_var][i]
        if type(shape[obj_var][i])==float:
            line+='%f,'%shape[obj_var][i]
    #Remove comma
    line=line[:-1]
    line+='}\n'
    return line 

def dump_fracture_type(obj, num_obj, prefix):
    '''dump fracture information into generation input'''
    line='\n'
    line+=add_to_gen_input(num_obj, obj, prefix+'_p32Targets', 'p32')
    line+=add_to_gen_input(num_obj, obj, prefix+'aspect', 'aspect')
    line+=add_to_gen_input(num_obj, obj, prefix+'betaDistribution', 'beta')
    line+=add_to_gen_input(num_obj, obj, prefix+'kappa', 'kappa')
    line+=add_to_gen_input(num_obj, obj, prefix+'theta', 'theta')
    line+=add_to_gen_input(num_obj, obj, prefix+'phi', 'phi')
    line+=add_to_gen_input(num_obj, obj, prefix+'beta', 'beta')
    line+=add_to_gen_input(num_obj, obj, prefix+'Layer', 'layer')
    line+=add_to_gen_input(num_obj, obj, prefix+'distr', 'dist')
   
    line+=add_to_gen_input(len(obj['log_mean']), obj, prefix+'LogMean', 'log_mean')
    line+=add_to_gen_input(len(obj['sd']), obj, prefix+'sd', 'sd')
    line+=add_to_gen_input(len(obj['log_max']), obj, prefix+'LogMax', 'log_max')
    line+=add_to_gen_input(len(obj['log_min']), obj, prefix+'LogMin', 'log_min')
    line+=add_to_gen_input(len(obj['alpha']), obj, prefix+'alpha', 'alpha')
    line+=add_to_gen_input(len(obj['max']), obj, prefix+'min', 'min')
    line+=add_to_gen_input(len(obj['min']), obj, prefix+'max', 'max')
    line+=add_to_gen_input(len(obj['exp_mean']), obj, prefix+'ExpMean', 'exp_mean')
    line+=add_to_gen_input(len(obj['exp_min']), obj, prefix+'ExpMin', 'exp_min')
    line+=add_to_gen_input(len(obj['exp_max']), obj, prefix+'ExpMax', 'exp_max')
    line+=add_to_gen_input(len(obj['constant']), obj, prefix+'const', 'constant')
    #rphi: {0.0, 0.0}
    return line

def dump_user_fractures(uf, domain):
    '''write user fracture information into input file'''
    # User Defined Fratures
    

    num_uf=len(uf)

    print("Number of user defined fractures: %d\n"%num_uf)
    flags={'rect_by_coord':False, 'ell_by_coord':False, 'rect_by_input':False, 'ell_by_input':False}
    paths={'rect_by_coord': '~/', 'ell_by_coord':'~/', 'rect_by_input':'~/', 'ell_by_input':'~/'}
    for i in range(num_uf):
        if uf[i]['type']['rect_by_coord']:
            flags['rect_by_coord']=True 
            paths['rect_by_coord']=uf[i]['path']
        elif uf[i]['type']['ell_by_coord']:
            flags['ell_by_coord']=True 
            paths['ell_by_coord']=uf[i]['path']
        elif uf[i]['type']['rect_by_input']:
            flags['rect_by_input']=True 
            paths['rect_by_input']=uf[i]['path']
        elif uf[i]['type']['ell_by_input']:
            flags['ell_by_input']=True 
            paths['ell_by_input']=uf[i]['path']
    
    line='userRectanglesOnOff: %d\n'%int(flags['rect_by_input'])
    line+='UserRect_Input_File_Path: %s\n'%paths['rect_by_input'] 

    line+='userEllipsesOnOff: %d\n'%int(flags['ell_by_input'])
    line+='UserEll_Input_File_Path: %s\n'%paths['ell_by_input'] 

    line+='userRecByCoord: %d\n'%int(flags['rect_by_coord'])
    line+='RectByCoord_Input_File_Path: %s\n'%paths['rect_by_coord'] 

    line+='userEllByCoord: %d\n'%int(flags['ell_by_coord'])
    line+='EllByCoord_Input_File_Path: %s\n'%paths['ell_by_coord'] 

    return line 


def create_dfnGen_input(domain, path, fractures=[], uf=[], gen_input_name='default'):
    ''' convert fracture and domain dictionaries into dfnGen input'''
    
    boundary_list=['left_w', 'right_e', 'front_s', 'back_n', 'top', 'bottom']
    domain['number_of_families']=len(uf)

    # Dump Domain information
    gen_input='domainSize: {%f, %f, %f}\n'%(domain['x_length'],domain['y_length'],domain['z_length'])
    gen_input+='domainSizeIncrease: {%f, %f, %f}\n'%(domain['x_increase'],domain['y_increase'],domain['z_increase'])
    gen_input+='h: %f\n'%(domain['h']) 
    boundary=6*[0]
    inflow_index=boundary_list.index(domain['inflow_boundary'])
    outflow_index=boundary_list.index(domain['outflow_boundary'])
    boundary[inflow_index]=1
    boundary[outflow_index]=1
    gen_input+='boundaryFaces: {'
    for i in boundary:
        gen_input+='%d,'%i
    gen_input=gen_input[:-1]
    gen_input+='}\n'
    gen_input+='ignoreBoundaryFaces: %d\n'%int(domain['ignore_boundary_faces'])
    gen_input+='numOfLayers: %d\n'%domain['number_of_layers'] 
    if domain['number_of_layers'] > 0:
        gen_input+='layers: '
        for i in range(domain['number_of_layers']):
            gen_input+='{%f,%f} '%(domain['layer'][i][0],domain['layer'][i][1])
        gen_input+='\n'
    else:
        gen_input+='layers: {0,0}\n'

    # Dump Stop condition 
    if domain['stop_condition']['number']:
        gen_input+='stopCondition: 0\n'
        gen_input+='nPoly: %d\n'%domain['number_of_fractures']
    elif domain['stop_condition']['p32']:
        gen_input+='stopCondition: 1\n'
        gen_input+='nPoly: 0\n'
    else:
        sys.exit("ERROR: stop_condition not specified")

    # Dump degree
    if domain['angle']['degrees']: 
        gen_input+='eAngleOption: 0\n'
        gen_input+='rAngleOption: 0\n'
    elif domain['angle']['radians']: 
        gen_input+='eAngleOption: 1\n'
        gen_input+='rAngleOption: 1\n'

    
    gen_input+='seed: %d\n'%domain['seed']
    gen_input+='visualizationMode: %d\n'%int(domain['visualization_mode']) 
    gen_input+='forceLargeFractures: %d\n'%int(domain['force_large_fractures']) 
    gen_input+='removeFracturesLessThan: %d\n'%int(domain['remove_fractures_less_than']) 
    gen_input+='printRejectReasons: %d\n'%int(domain['print_rejection_reasons']) 
    gen_input+='outputAllRadii: %d\n'%int(domain['output_all_radii']) 
    gen_input+='outputAcceptedRadiiPerFamily: %d\n' %int(domain['output_accepted_radii_per_family']) 
    gen_input+='outputFinalRadiiPerFamily: %d\n' %int(domain['output_final_radii_per_family']) 
    gen_input+='keepOnlyLargestCluster: %d\n'%int(domain['keep_only_largest_cluster']) 
    gen_input+='tripleIntersections: %d\n'%int(domain['triple_intersections']) 
    gen_input+='disableFram: %d\n'%int(domain['fram_off'])
    gen_input+='insertUserRectanglesFirst: %d\n'%int(domain['insert_user_rectangles_first'])
    
    gen_input+='radiiListIncrease: %0.2f\n'%domain['radii_list_increase']
    gen_input+='rejectsPerFracture: %d\n'%domain['rejects_per_fracture']
    
    # Fracture Families
    num_ell=0
    num_rects=0 
    gen_input+='\nfamProb: {' 
    for i in range(domain['number_of_families']):
        gen_input+='%f,'%fractures[i]['probability']
        if fractures[i]['type']['ellipse']:
            num_ell+=1
        elif fractures[i]['type']['rect']:
            num_rects+=1
    #Remove comma
    if (gen_input[-1] == ','): 
        gen_input=gen_input[:-1]
    gen_input+='}\n'

    gen_input+="nFamEll: %d\n"%num_ell
    gen_input+="nFamRect: %d\n"%num_rects

    rects=group_family(fractures, domain['number_of_families'], 'rect')
    gen_input+=dump_fracture_type(rects, num_rects, 'r')

    ell=group_family(fractures, domain['number_of_families'], 'ellipse')
    gen_input+=dump_fracture_type(ell, num_ell, 'e')
    gen_input+=add_to_gen_input(num_ell, ell, 'enumPoints', 'number_of_points')
 
    gen_input+=dump_user_fractures(uf, domain)

    if domain['aperture']['log_normal']:
        gen_input+='aperture: 1\n'
    elif domain['aperture']['from_trans']:
        gen_input+='aperture: 2\n'
    elif domain['aperture']['constant']:
        gen_input+='aperture: 3\n'
    elif domain['aperture']['form_size']:
        gen_input+='aperture: 4\n'
    else:
        sys.exit("ERROR: Aperture not specified")

    gen_input+='apertureFromTransmissivity: {%f, %f}\n'%(domain['aperture']['F_T'],domain['aperture']['B_T'])
    gen_input+='constantAperture: %f\n'%domain['aperture']['value']
    gen_input+='lengthCorrelatedAperture: {%f, %f}\n'%(domain['aperture']['F_r'],domain['aperture']['B_r'])
    gen_input+='meanAperture: %f\n'%domain['aperture']['log_mean']
    gen_input+='stdAperture: %f\n'%domain['aperture']['std']
    
    if domain['permeability']['constant']: 
        gen_input+='permOption: 1\n'
    elif domain['permeability']['cubic']: 
        gen_input+='permOption: 0\n'
    else:
        sys.exit("ERROR: Permeability not specified")
   
    gen_input+='constantPermeability: %f\n'%domain['permeability']['value']
    gen_input+='\n\n'
    if (gen_input_name == 'default'):
        gen_input_name = 'dfn_gen_input.dat'
    
    print 'GEN INPUT NAME', gen_input_name
    print 'PATH ', path
    f=open(path + gen_input_name,'w')
    f.write(gen_input)
    f.close()
    print("Generator input complete")

def create_pflotran_input(domain, path):
    """Create pflotran input file"""
    pflotran_input="""
# Jan 13, 2014
# Nataliia Makedonska, Satish Karra, LANL
#================================================

SIMULATION
  SIMULATION_TYPE SUBSURFACE
  PROCESS_MODELS
    SUBSURFACE_FLOW flow
      MODE RICHARDS
    /
  /
END
SUBSURFACE

DFN

#=========================== discretization ===================================
GRID
  TYPE unstructured_explicit full_mesh_vol_area.uge 
  GRAVITY 0.d0 0.d0 0.d0
END


#=========================== fluid properties =================================
FLUID_PROPERTY
  DIFFUSION_COEFFICIENT 1.d-9
END

DATASET Permeability
  FILENAME dfn_properties.h5
END

#=========================== material properties ==============================
MATERIAL_PROPERTY soil1
  ID 1
  POROSITY 0.25d0
  TORTUOSITY 0.5d0
  CHARACTERISTIC_CURVES default
  PERMEABILITY
    DATASET Permeability
  /
END


#=========================== characteristic curves ============================
CHARACTERISTIC_CURVES default
  SATURATION_FUNCTION VAN_GENUCHTEN
    M 0.5d0
    ALPHA  1.d-4
    LIQUID_RESIDUAL_SATURATION 0.1d0
    MAX_CAPILLARY_PRESSURE 1.d8
  /
  PERMEABILITY_FUNCTION MUALEM_VG_LIQ
    M 0.5d0
    LIQUID_RESIDUAL_SATURATION 0.1d0
  /
END

#=========================== output options ===================================
OUTPUT
  TIMES s 0.01 0.05 0.1 0.2 0.5 1
#  FORMAT TECPLOT BLOCK
  PRINT_PRIMAL_GRID
  FORMAT VTK
  MASS_FLOWRATE
  MASS_BALANCE
  VARIABLES
    LIQUID_PRESSURE
    PERMEABILITY
  /
END

#=========================== times ============================================
TIME
  INITIAL_TIMESTEP_SIZE  1.d-8 s
  FINAL_TIME 1.d0 d
  MAXIMUM_TIMESTEP_SIZE 10.d0 d
  STEADY_STATE
END

# REFERENCE_PRESSURE 1500000.

#=========================== regions ==========================================
REGION All
  COORDINATES
    -1.d20 -1.d20 -1.d20
    1.d20 1.d20 1.d20
  /
END 

REGION inflow
  FILE %s 
END

REGION outflow
  FILE %s 
END

#=========================== flow conditions ==================================
FLOW_CONDITION initial
  TYPE
     PRESSURE dirichlet 
  /
  PRESSURE %0.2f 
END


FLOW_CONDITION inflow
  TYPE
    PRESSURE dirichlet
  /
  PRESSURE %0.2f 
END

FLOW_CONDITION outflow 
  TYPE 
     PRESSURE dirichlet
  /
  PRESSURE %0.2f 
END

#=========================== condition couplers ===============================
# initial condition
INITIAL_CONDITION
  FLOW_CONDITION initial
  REGION All
END


BOUNDARY_CONDITION INFLOW 
  FLOW_CONDITION inflow
  REGION inflow
END

BOUNDARY_CONDITION OUTFLOW
  FLOW_CONDITION outflow 
  REGION outflow
END

#=========================== stratigraphy couplers ============================
STRATA
  REGION All 
  MATERIAL soil1
END

END_SUBSURFACE
"""
    inflow_ex='pboundary_'+domain['inflow_boundary']+'.ex' 
    outflow_ex='pboundary_'+domain['outflow_boundary']+'.ex' 
    initial=0.5*(domain['inflow_pressure'] + domain['outflow_pressure'])
    pflotran_input=pflotran_input%(inflow_ex, outflow_ex, initial, domain['inflow_pressure'], domain['outflow_pressure'])

    f=open(path + 'dfn_explicit.in','w')
    f.write(pflotran_input)
    f.close()
    print("PFLOTRAN input finished")

def create_dfntrans_input(domain, path):
    '''Create DFNTrans input file'''

    dfntrans_input="""
/***********************************************************************/
/*   CONTROL FILE FOR PARTICLE TRACKING IN DISCRETE FRACTURE NETWORK   */
/***********************************************************************/

/**********************  INPUT FILES: grid *****************************/
/**** input files with grid of DFN, mainly it's output of DFNGen ******/
param: params.txt
poly: poly_info.dat
inp: full_mesh.inp
stor: tri_fracture.stor
boundary: allboundaries.zone
/* boundary conditions: reading the nodes that belong to in-flow and 
out-flow boundaries. Should be consistent with those applied to obtain
steady state pressure solution (PFLOTRAN)   */
/*1 - top;  2 - bottom;  3 - left_w;  4 - front_s;  5 - right_e;  6 - back_n */
in-flow-boundary: %d 
out-flow-boundary: %d 


/**************** INPUT FILES: PFLOTRAN flow solution *******************/
PFLOTRAN: yes 
PFLOTRAN_vel: darcyvel.dat 
PFLOTRAN_cell: cellinfo.dat
PFLOTRAN_uge: full_mesh_vol_area.uge

/**************** INPUT FILES: FEHM flow solution ***********************/
/*currently we are using PFLOTRAN , but the code would work with FEHM, too */ 
FEHM: no
FEHM_fin:  tri_frac.fin

/************************  OUTPUT FILES  ********************************/
/* initial grid info structure output, usefull for debugging */
out_grid: no
/* flow field: 3D Darcy velocities: output file has an each nodes position 
and its Darcy velocity, reconstructed from fluxes */ 
out_3dflow: no
/* out initial positions of particles into separate file */ 
out_init: no


/*************** output options for particles trajectories ****************/
/* output frequency is set according to trajectories curvature. We check the 
curvature of particles trajectory each segment, from intersection to intersection.
If it's like a straight line, then the output is less frequent (in case of 
"out_curv:yes", if "no",  the output file will contain every time step) */
out_curv: no 
/* output into avs file (GMV visualization, Paraview visualization) */
out_avs: no 
/* output into trajectories ascii files (veloc+posit+cell+fract+time) */
out_traj: no 
out_frac: no

/************* output directories *************************************/
out_dir: traj /* path and name of directory where all the particle 
                     tracking results will be written*/


out_path: trajectories /*name of directory where all particle
                    trajectories will be saved, in out_dir path */ 

/* name of resultant file (in out_dir path), which contains total travel time and 
				final positions of particles */
out_time: partime

/**************** PARTICLES INITIAL POSITIONS ******************************/
/****init_nf: if yes - the same number of particles (init_partn) will be placed 
     on every boundary fracture edge on in-flow boundary, 
     equidistant from each other ****/
init_nf: no
init_partn: 10

/****init_eqd: if yes - particles will be placed on the same distance from
     each other on all over in-flow boundary edges ***********************/  
init_eqd: yes
//maximum number of particles that user expects on one boundary edge
init_npart: %d 

/*** all particles start from the same region at in-flow boundary, in a range  
    {in_xmin, in_xmax,in_ymin, in_ymax, in_zmin, in_zmax} **************/
init_oneregion: no    
in_partn: 10
in_xmin: -20.0 
in_xmax: 20.0 
in_ymin: -20.0 
in_ymax: 20.0 
in_zmin: 499.0 
in_zmax: 501.0

/**** all particles are placed randomly over all fracture surface 
     (not only on boundary edges!) ************************************/
init_random: no
// total number of particles
in_randpart: 110000    

/**** all particles are seed randomly over matrix, 
     they will start travel in DFN from the node/cell that is closest to
     their initial position in rock matrix ***************************/
      
init_matrix: no
// to obtain these files, run python script RandomPositGener.py
inm_coord: ParticleInitCoordR.dat
inm_nodeID: ClosestNodeR.inp
inm_porosity: 0.02
inm_diffcoeff: 1.0e-12

/****************** FLOW AND FRACTURE PARAMETERS **********************/
porosity: 1.0 // porosity 
density: 997.73  //fluid density 
satur: 1.0
thickness: 1.0 //DFN aperture  (used in case of no aperture file provided)

aperture: yes  //DFN aperture
aperture_type: frac //aperture is giving per cell (type "cell") 
//    or per fracture (type "frac")
// for now we use an aperture giving per fracture
aperture_file: aperture.dat

/********************  TIME ********************************************/
timesteps: 200000000
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
ControlPlane: no 

/* the path and directory name with all particles output files */
control_out: outcontroldir

/* Delta Control Plane - the distance between control planes */
delta_Control: 1.0

/* ControlPlane: direction of flow: x-0; y-1; z-2 */
flowdir: 0

/**************************************************************************/
END

"""
    boundaries=['top', 'bottom', 'left_w', 'front_s', 'right_e', 'back_n']
    inflow_index=boundaries.index(domain['inflow_boundary'])+1
    outflow_index=boundaries.index(domain['outflow_boundary'])+1
    
    dfntrans_input=dfntrans_input%(inflow_index, outflow_index, domain['number_of_particles'])

    f=open(path + 'PTDFN_Control.dat','w')
    f.write(dfntrans_input)
    f.close()

    print("DFNTran input finished")

def create_txt_input_file(path):
    dfnGen = 'dfnGen ' + path + 'dfn_gen_input.dat \n'  
    pflotran = 'dfnFlow ' + path + 'dfn_explicit.in \n'
    dfntrans = 'dfnTrans ' + path + 'PTDFN_Control.dat \n'
    txt_file_name = 'integrated.txt'
    print 'writing ', path + txt_file_name
    f = open(path + txt_file_name, 'w')
    f.write(dfnGen) 
    f.write(pflotran)
    f.write(dfntrans)
    f.close()
