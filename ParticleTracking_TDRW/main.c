#include <stdio.h>
#include <search.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "FuncDef.h" 
#include <unistd.h>
#include <time.h>


 
/********* Global variables: *******************************/
/* nnodes - number of nodes     */
/* ncells - number of triangles */     
/* nfract - number of fractures */    
/* max_neighb - maximum number of edges in Voronoi polygon */    
/* npart - initial number of particles */
/* np - current particle index */
/* nzone_in - number of nodes in flow-in zone */
/* nodezonein - dynamic array with node's ID in flow-in zone */
/* node - node's data structure */
/* fracture - fracture's data structure */
/* particle - particle's data structure */
/* cell - cell's data structure */
/* pflotran and fehm are flags on which flow solver is used*/

unsigned int pflotran;
unsigned int fehm;
unsigned int nnodes;
unsigned int ncells;
unsigned int nfract; 
unsigned int max_neighb;
unsigned int npart;
unsigned int np;
unsigned int nzone_in;
unsigned int *nodezonein; 
unsigned int *nodezoneout; 
unsigned int flag_w;
struct material *fracture;
struct vertex *node;
struct contam *particle;
struct element *cell;
char maindir[125]; 
char controlfile[120]; 

double porosity;
double density;
unsigned long int timesteps;
double thickness;   
double saturation;
double timeunit;
double totalFluxIn;


struct inpfile {
  char filename[120];
  long int flag;
  double param;
}; 

int main (int argc, char* controlf[]) {

      
  if (argc==2)
    {
      strcpy(controlfile, controlf[1]); 
      printf("The input parameters are read from %s control file. \n", controlf[1]);
         
    }
  else if (argc>2)
    {
      printf("Too many arguments \n");  
      exit (1);
    }
  else
    {
      printf("Provide the name of Input Control File \n");
      exit(1);
    }

  printf("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
  printf("~~~ Program: DFNWorks / DFNTrans V1.0, C code, Linux ~~~~~~~~~~~~~\n");
  printf("~~~~~~~~~~~~ April 1st, 2015.  LA-CC-14-091 ~~~~~~~~~~~~~~~~~~~~~~~~~\n");
  printf("\n This program was prepared at Los Alamos National Laboratory (LANL),\n");
  printf(" Earth and Environmental Sciences Division, Computational Earth \n");
  printf(" Science Group (EES-16), Subsurface Flow and Transport Team.\n");
  printf(" All rights in the program are reserved by the DOE and LANL.\n");
  printf(" Permission is granted to the public to copy and use this software \n");
  printf(" without charge, provided that this Notice and any statement of \n");
  printf(" authorship are reproduced on all copies. Neither the U.S. Government \n");
  printf(" nor LANS makes any warranty, express or implied, or assumes \n");    
  printf(" any liability or responsibility for the use of this software.\n");
  printf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
  printf("~~~Developers: Nataliia Makedonska, Scott L. Painter, Carl W. Gable\n");
  printf(" Last update Apr. 1st, 2015, by N. Makedonska (nataliia@lanl.gov)\n");
  printf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
  
  /** define time at which program run starts ****/ 
  time_t current_time;
  char* c_time_string;
  current_time=time(NULL);
  c_time_string=ctime(&current_time);
  printf("\n PROGRAM STARTS. current time: %s\n",c_time_string);
       
     
  /**** open control file to read main parameters **************************/   
  int res;    
  struct inpfile inputfile;
    
  inputfile = Control_Data("seed:\0",5 );
  srand48(inputfile.flag);
     
  inputfile=Control_Param("density:",8);
  density=inputfile.param;
   
  inputfile=Control_Param("porosity:",9);
  porosity=inputfile.param;
   
  inputfile=Control_Param("satur:",6);
  saturation=inputfile.param;
   
  inputfile=Control_Param("thickness:",10);
  thickness=inputfile.param;
   
  inputfile = Control_Param("timesteps:",10 );
  timesteps=(int)inputfile.param;

  
  inputfile=Control_File("time_units:",11);
  res=String_Compare(inputfile.filename,"years");
  if (res==0)
    timeunit=365.0*24.0*60.0*60.0;
 
  else
    {
      res=String_Compare(inputfile.filename,"days");
      if (res==0)
	timeunit=24.0*60.0*60.0;
      else
	{ 
	  res=String_Compare(inputfile.filename,"hours");
	  if (res==0)
	    timeunit=60.0*60.0;
	  else
	    {
	      res=String_Compare(inputfile.filename,"minutes");
	      if (res==0)
		timeunit=60.0;
	      else
		{
		  res=String_Compare(inputfile.filename,"seconds");
		  if (res==0)
		    timeunit=1.0; 
		  else
		    timeunit=1.0;   
		} } } } 
  printf(" \n Particles velocities are calculated in [m/%s]. \n", inputfile.filename); 
   
     
      
  inputfile = Control_File("out_dir:",8 );
  strcpy(maindir,inputfile.filename);
  mkdir(maindir, 0777);
  printf("\n All output files will be written in %s/ \n", maindir);
      

  /***** open files and read values of global variables, such as total number of 
	 nodes, cells, fractures. Memory allocation.******/  
  printf("---------------------GRID DATA READING--------------------------\n"); 
  ReadInit();

     
  /**** open files and read GRID data FLOW SOLUTION data into structures ****/

  ReadDataFiles ();
    

  printf("\n Data Reading is Done\n");

  /*** Read nodes with Dirichlet BC **********************/
  printf("\n---------------------BOUNDARY CONDITIONS----------------------\n"); 
  ReadBoundaryNodes();
   
    

  CheckGrid();
    
  /*** rotates fractures into xy plane ******/
  Convertto2d();
     
        
  printf("\n----------------VELOCITY RECONSTRUCTION-----------------------\n"); 
  /*** Darcy's velocities reconstraction *******/
  DarcyVelocity();

  /*** define time step as function of polygon volume and velocity ******/
  DefineTimeStep();

  Convertto3d();
  /*** Velocity3D creates a file where all velocities are in 3D ******/
  /* good for visualization of velocity field in 3D domain */    
   
   
  inputfile = Control_File("out_3dflow:",11 );
  res=String_Compare(inputfile.filename,"yes");
  if(res==0)
    Velocity3D();
       
  inputfile = Control_File("out_grid:",9 );
  res=String_Compare(inputfile.filename,"yes");
  if(res==0)
    WritingInit();

  printf("\n------------------PARTICLE TRACKING---------------------------\n"); 
 
  ParticleTrack ();

  /****   free memomry that was allocated for data structures *****/
 

  free(fracture);
 
  free(node); 
  
  free(cell);
  
  free(nodezonein);

  free(nodezoneout);
  
  free(particle);
   

  /**** define time at program end ******/
   
  current_time=time(NULL);
  c_time_string=ctime(&current_time);
  printf("\n PROGRAM ENDS. current time: %s\n",c_time_string);
       
  return 0;
}

////////////////////////////////////////////////////////////////////////////////////
 
