#include <stdio.h>
#include <search.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
/**** the code reads a stor file of DFN (tri_fracture.stor)*****/
/**** the aperture values are in aperture.dat file****/
/**** then new stor file is created  ******/ 
/**** THIS VERSION OF CODE  CHANGES CELL'S VOLUME
      AND AREA COEFFICIENTS ACCORDING TO APERTURE ***********/
/****  ONLY FOR CONSTANT APERTURE ALONG EACH FRACTURE *******/       

int main(void)
{
//printf("----- DFN STOR file: recalculating length of area coefficients to 2D area.----- \n"); 
char file2d[128]={0}, file3d[128]={0}, file2dnew[128]={0};
int res;


      sprintf(file3d,"tri_fracture_apert_per_fract.stor");
      sprintf(file2d,"tri_fracture.stor");
      strcpy(file2dnew, file2d);
      
 if (res=strncmp(file2d, file3d, 128)==0)
 {

strcat(file2dnew,"2d");
  if ( 0 == rename(file2d, file2dnew) )
    {
    	printf ("\n Previous stor file %s was renamed to %s.\n", file2d, file2dnew );
    }

   else
     {
     printf ("\n File %s is not found\n", file2d);
      exit(1);
     }
 }
 FILE *f2d;
  if ((f2d = fopen (file2dnew,"r")) == NULL)
{
      printf ("\n File %s could not be opened\n", file2dnew);
      exit(1);
}
 FILE *f3d;
 
  if ((f3d = fopen (file3d,"w")) == NULL)
{
      printf ("\n File %s could not be opened\n", file3d);
     exit(1);
}
 double thickness=1.0;
 

 
int i,j=0,count=0;
char cs;
/*****1. ASCII Header*******/
   for (i=0; i<2; i++)
  {
    do 
{
      cs=fgetc(f2d);
     fprintf(f3d,"%c", cs);
     
 }     
    while (cs!='\n');

    }
/****2. Matrix Parameters *******/
   int nnodes, nedges, node_edge, area_coef, max_neighb,snode_edge, c=0;
   fscanf (f2d," %d %d %d %d %d \n", &nedges, &nnodes, &snode_edge, &area_coef, &max_neighb );
   fprintf (f3d," %15d  %15d  %15d  %10d  %10d \n", nedges, nnodes,snode_edge, area_coef, max_neighb );       
 double volume2d=0.0, volume3d=0.0 ;
 /**** reading material and aperture files  *****/
struct material {
unsigned int matnumber; };
//double aperture[max_neighb]; };

struct material *node; 
node=(struct material*) malloc (nnodes*sizeof(struct material));

unsigned int mat_number=0, nnum=0, currentn;
/**** reading tri_fracture_material.zone file *****/
FILE *mz;
if ((mz = fopen ("tri_fracture_material.zone","r")) == NULL)
{
      printf ("\n File tri_fracture_material.zone  could not be opened\n");
      exit(1);
}
 fscanf(mz,"%s \n", &file2d);
 do
 {

 fscanf(mz,"%d \n", &mat_number);
 fscanf(mz,"%s \n", &file2d);
 if (res=strncmp(file2d, "nnum", 4)==0)
     {
     fscanf(mz,"%d \n",&nnum);
     for (i=0; i<nnum; i++)
       {
       fscanf(mz,"%d ",&currentn);
       node[currentn-1].matnumber=mat_number;
       } 
     }
  else
    break;
 }
  while(res=strncmp(file2d, "stop", 4)!=0);
 fclose(mz);
  printf(" \n  %d material numbers",mat_number);
/*** reading aperture.dat file ****************/
double currentap=0.0, aperturem[mat_number];
int apmat=0, zn;
FILE *ad;
if ((ad = fopen ("aperture.dat","r")) == NULL)
{
      printf ("\n File aperture.dat  could not be opened\n");
      exit(1);
}

 fscanf(ad,"%s \n", &file2d);
 for (i=0; i<mat_number; i++)
 {
 fscanf(ad,"%d %d %d %lf \n", &apmat, &zn, &zn, &currentap);
  apmat=apmat*(-1)-6;
  aperturem[apmat-1]=currentap;
 }
 
fclose(ad);

/*****3.Voronoi Volumes *****/
for (i=0; i<nnodes; i++)
     {
     fscanf(f2d,"%lf", &volume2d);
      volume3d=volume2d*aperturem[node[i].matnumber-1];
      
      if ((((i+1) % 5)==0) || (i==nnodes-1))
     fprintf(f3d," %15.12E \n", volume3d);
     
     else
      {
      fprintf(f3d," %15.12E ", volume3d);
      }
      }
 
/****4. Count for Each Row*******/
    c=0; 
for (i=0; i<nnodes+1; i++)
     {
     fscanf(f2d,"%d", &count);
     c++;
     if (((c % 5)==0)|| (i==nnodes))
     fprintf(f3d," %10d \n", count);
     else
      {
      
      fprintf(f3d," %10d ", count);
      }
      
      
      }

/***5. Row Entries***********/
//unsigned int nodeind;


unsigned int* nodeind=malloc (nedges*sizeof(unsigned int));

    c=0;  
for (i=0; i<nedges; i++)
     {
     fscanf(f2d,"%d", &count);
     
     nodeind[i]=count;
      c++;
     if (((c % 5)==0)|| (i==nedges-1))
     fprintf(f3d," %10d \n", count);
     else
      {
     
      fprintf(f3d," %10d ", count);
      }
      }
/*****6. Indices into Coefficient List*****/
   c=0; 
for (i=0; i<nedges*area_coef; i++)
     {
     fscanf(f2d,"%d", &count);
      c++;
     if (((c % 5)==0)|| (i==nedges*area_coef-1))
     fprintf(f3d," %10d \n", count);
     else
      {
      
      fprintf(f3d," %10d ", count);
      }
      }

    c=0; 
for (i=0; i<nnodes+1; i++)
     {
     fscanf(f2d,"%d", &count);
      c++;
     if (((c % 5)==0)|| (i==nnodes))
     fprintf(f3d," %10d \n", count);
     else
      {
     
      fprintf(f3d," %10d ", count);
      }
      }

   c=0; 
for (i=0; i<nnodes; i++)
     {
     fscanf(f2d,"%d", &count);
      c++;
       if (((c % 5)==0) || (i==nnodes-1))
     fprintf(f3d," %10d \n", count);
     else
      {
     
      fprintf(f3d," %10d ", count);
      }
      }
   
/***7. Geometric Area Coefficient Values****/
   
for (i=0; i<nedges*area_coef; i++)
     {
     fscanf(f2d,"%lf", &volume2d);
      volume3d=volume2d*aperturem[node[nodeind[i]-1].matnumber-1];
     
     if ((((i+1) % 5)==0)|| (i==nedges*area_coef-1))
     fprintf(f3d," %15.12E \n", volume3d);
     else
      {
      
      fprintf(f3d," %15.12E ", volume3d);
      }
      }

   fclose(f2d);
   fclose(f3d);
   free(node);
   free(nodeind);
   printf("\n ----- DONE-------\n");   
return 0;
}
