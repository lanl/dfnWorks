#include <stdio.h>
#include <search.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "FuncDef.h" 
#include <unistd.h>
#include <time.h>
#include<sys/stat.h>
#include <stdio.h>

struct inpfile {
  char filename[120];
  long int flag;
  double param;
}; 
///////////////////////////////////////////////////////////////////////////////
void OutputMarPlumDisp (int currentnum, char path[125])
/****** function reads trajectory files and forms output fro MARFA, PLUMECALC, ********************/
{
  struct inpfile inputfile;
  char filename[125], cs;
  unsigned int marfa=0, plumec=0,  i, j; 
  double time_days=0.0;
  double time_years=0.0;
  int res=0;
  FILE *plum;
  FILE *mar;
  
  
  
  time_years=(365.0*24.0*60.0*60.0)/timeunit;// units for marfa
  time_days=(24.0*60.0*60.0)/timeunit; //units for plumecalc
  
  inputfile=Control_File("out_marfa:",10);
  res=strncmp(inputfile.filename,"yes",3);
  if (res==0)
    {
      marfa=1;
      sprintf(filename,"%s/trajectories.dat",maindir);
      mar = OpenFile(filename,"w");   
      fprintf(mar,"! The file produced for MARFA and contains rajectories of particle, simulated using \n");
      fprintf(mar,"! DFNTrans code: particle tracking code in discrete fracture network.\n");  
      //      fprintf(mar,"../../../  PUT A RIGHT PATH TO THE DATA!! \n");
      fprintf(mar,"/scratch/er/dharp/source/MARFA3.2.3/data/ \n"); 
      fprintf(mar,"%05d \n", currentnum);
    }
  inputfile=Control_File("out_plumecalc:",14);
  res=strncmp(inputfile.filename,"yes",3);
  if (res==0)
    {
      plumec=1;
      sprintf(filename,"%s/trajout",maindir);
      plum = OpenFile(filename,"w");  
      fprintf(plum,"! The file produced for PLUMECALC and contains rajectories of particle, simulated using \n");
      fprintf(plum,"! DFNTrans code: particle tracking code in discrete fracture network.\n");  
      fprintf(plum,"%d \n", currentnum);  
    } 
    
  int status, traj_o=0;  
  inputfile=Control_File("out_traj:",9);
  res=strncmp(inputfile.filename,"yes",3);
  if (res==0)
    traj_o=1;
    
    
  double posx=0.0, posy=0.0, posz=0.0, vx=0.0, vy=0.0, vz=0.0, ttime=0.0, apert=0.0, beta=0.0, ntime, bbet=0.0; 
   
  unsigned int cell, fr, ts, numtimes, inters; 
  // lopp on particles trajectories files
  for (i=1; i<=currentnum; i++)
    {
    
    
      sprintf(filename,"%s/traject_%d",path,i);
      FILE *tr = OpenFile(filename,"r");
      if (fscanf(tr,"%d \n", &numtimes)!=1)
	printf("Error");
      if (plumec==1)
	fprintf(plum,"%d \n",numtimes);
      do 
	cs=fgetc(tr); 
      while (cs!='\n');
      
  
      //   current time step, x-, y-, z- pos., Vx, Vy, Vz at ths positions, # of cell, #of fracture, travel time, aperture , beta  
  
      for (j=1; j<=numtimes; j++)
	{
	  if (fscanf(tr,"%d %lf %lf %lf %lf %lf %lf %d %d %lf %lf %lf %d \n",&ts, &posx, &posy, &posz, &vx, &vy, &vz, &cell, &fr, &ttime, &apert, &beta, &inters )!=13)
	    printf("ErrorTr");
    
	  // MARFA output
	  if (marfa == 1)
	    {
	      if (j==1)
		fprintf(mar,"Part%05d    %4.4f   %4.4f   %4.4f \n", i, posx, posy, posz);
	      else
		{
		  ntime=ttime/time_years;
		  bbet=ntime/(ttime/beta);
		  fprintf(mar,"%7.4f   %7.4f   %7.4f    rtID   %3.8E  %3.8E   %3.8E \n", posx, posy, posz, ntime, bbet, 0.00); 
		}
	    }
    
	  //PLUMECALC output
	  if (plumec==1)
	    {
	      ntime=ttime/time_days;
	      fprintf(plum,"%f   %f   %f   %f \n", ntime, posx, posy, posz); 
	    }
    
  
    
    
	} 
      fclose(tr);
      if (traj_o==0)
	{
	  status = remove(filename);
 
	  if( status != 0 )
     
	    {
	      printf("Unable to delete the file %s\n", filename);
	      perror("Error");
	    }    
	}
    
      if (marfa ==1)
	fprintf(mar," END \n");
    
  
    } //end loop on particles trajectories files    
    	
  if (marfa ==1)
    fclose(mar);
  if (plumec == 1)
    fclose(plum);  
   
  return;
}
//////////////////////////////////////////////////////////////////////////////	
