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

typedef struct _params
{
    char matID_file[64];
    char aper_file[64];
    char stor_in_file[64];
    char stor_out_file[64];
}Params;


/*********************************************************\
 *Funciton:check_null_pointer
 Checks to see is a pointer is NULL
 \*********************************************************/
void checkNullPointer(char*temp)
{
    if(temp==NULL)
    {
        fprintf(stderr,"Out of Memory");
        exit(1);
    }
}
/*********************************************************\
 *Funciton:create_new_pointer
 Returns a New Pointer of size size.
 \*********************************************************/
char *createNewPointer(int size)
{
    char *temp;
    temp = malloc(size);
    checkNullPointer(temp);
    return temp;
}
/**************************************************************\
 * Function:open_file
 This Function Opens the Main Las File
 \**************************************************************/
FILE *openFile(char *base, char *name, char *fileMode)
{
    FILE *fp;
    char *new_name;

    new_name = createNewPointer(200);

    strcpy(new_name, base);
    strcat(new_name, name);

    if ((fp = fopen(new_name, fileMode)) == NULL)
    {
        fprintf(stderr,"Can't open \"%s\" file.\n", new_name);
        exit(1);
    }
    else{printf("Opening file %s\n",new_name);}

    free(new_name);
    return fp;
}
/*************************************************************\
 * Function:close_file
 Closes files, exits program if an error exists
 \*************************************************************/
void closeFile(FILE *fp)
{
    if(fclose(fp) != 0)
    {
        fprintf(stderr, "*** Error closing file ***\n");
        exit(1);
    }
}

void parseCommandLineArgs(int countArgs, char *args[], char *paramsName)
{
    if (countArgs > 1)
    {
        strcpy(paramsName, args[1]);
    }
    else {
        strcpy(paramsName, "convert_uge_params.txt");
    }
}


void readInParams(FILE *fparams, Params *params){
    // Read in Params File
    // line 2
    if(fscanf(fparams, "%s", &params->matID_file) != 1){printf("ERROR reading in material file name\n");}
    // line 3
    if(fscanf(fparams, "%s", &params->stor_in_file) != 1){printf("ERROR reading in stor_in_file name\n");}
    // line 4
    if(fscanf(fparams, "%s", &params->stor_out_file) != 1){printf("ERROR reading in stor_out_file name\n");}
    // line 5
    if(fscanf(fparams, "%s", &params->aper_file) != 1){printf("ERROR reading in aperture file name\n");}
}

/*****1. ASCII Header*******/
void copyHeader(FILE *f2d, FILE *f3d){
    printf("Copying Header\n");
    char cs;
    for (int i=0; i<2; i++) {
        do{
            cs=fgetc(f2d);
            fprintf(f3d,"%c", cs);
        }     
        while (cs!='\n');
    }
}

/****2. Matrix Parameters *******/
void copyMain(FILE *f2d, FILE *f3d, Params *params){

    FILE *fad, *fmz;
    int nnodes, nedges, area_coef, max_neighb, snode_edge, c;
    int res, count=0;
    char junk[128]={0};
    double volume2d=0.0, volume3d=0.0 ;
    unsigned int mat_number=0, nnum=0, currentn;
    fscanf (f2d," %d %d %d %d %d \n", &nedges, &nnodes, &snode_edge, &area_coef, &max_neighb );
    fprintf (f3d," %15d  %15d  %15d  %10d  %10d \n", nedges, nnodes, snode_edge, area_coef, max_neighb );       
    printf("There are %d nodes and %d edges \n", nnodes, nedges);
     
      /**** reading material and aperture files  *****/
    struct material {
        unsigned int matnumber;
        //double aperture[max_neighb]; 
    };
    
    struct material *node; 
    node=(struct material*) malloc (nnodes*sizeof(struct material));
    
    /**** reading tri_fracture_material.zone file *****/
    fmz = openFile(params->matID_file,"","r");
    fscanf(fmz,"%s \n", &junk);
    do{
        fscanf(fmz,"%d \n", &mat_number);
        fscanf(fmz,"%s \n", &junk);
        if ( (res=strncmp(junk, "nnum", 4)) == 0){
            fscanf(fmz,"%d \n",&nnum);
            for (int i=0; i<nnum; i++){
                fscanf(fmz,"%d ",&currentn);
                node[currentn-1].matnumber=mat_number;
            } 
        }
        else{
           break;
        }
    } while((res=strncmp(junk, "stop", 4)) != 0);
 
    closeFile(fmz);


    printf("\nThere are %d materials\n",mat_number-6);
    /*** reading aperture.dat file ****************/
    double currentap=0.0, aperturem[mat_number];
    int apmat=0, zn;
    fad = openFile(params->aper_file,"","r");
    fscanf(fad,"%s \n", &junk);
    for (int i=0; i<mat_number; i++){
        fscanf(fad,"%d %d %d %lf \n", &apmat, &zn, &zn, &currentap);
        apmat=apmat*(-1);
        aperturem[apmat-1]=currentap;
     }
    closeFile(fad);

    printf("Correcting Voronoi Volumes\n");
    fprintf(f3d," "); // File formating
    /*****3.Voronoi Volumes *****/
    for (int i=0; i < nnodes; i++){
        fscanf(f2d,"%lf", &volume2d);
        volume3d=volume2d*aperturem[node[i].matnumber-1];
        if ((((i+1) % 5)==0) || (i==nnodes-1)){
            fprintf(f3d," %15.12E \n", volume3d);
         }
        else{
            fprintf(f3d," %15.12E ", volume3d);
        }
    }
     
    /****4. Count for Each Row*******/
    c=0; 
    for (int i=0; i<nnodes+1; i++){
        fscanf(f2d,"%d", &count);
        c++;
        if (((c % 5)==0)|| (i==nnodes)){
            fprintf(f3d," %10d \n", count);
        }
        else{
            fprintf(f3d," %10d ", count);
        }
      }

    /***5. Row Entries***********/
    //unsigned int nodeind;
    unsigned int* nodeind=malloc (nedges*sizeof(unsigned int));
    c=0;  
    for (int i=0; i<nedges; i++){
        fscanf(f2d,"%d", &count);
        nodeind[i]=count;
        c++;
        if (((c % 5)==0)|| (i==nedges-1)){
            fprintf(f3d," %10d \n", count);
        }
        else{
            fprintf(f3d," %10d ", count);
        }
    }

    /*****6. Indices into Coefficient List*****/
    c=0; 
    for (int i=0; i<nedges*area_coef; i++){
        fscanf(f2d,"%d", &count);
        c++;
        if (((c % 5)==0)|| (i==nedges*area_coef-1)){
            fprintf(f3d," %10d \n", count);
        }
        else{
            fprintf(f3d," %10d ", count);
        }
    }

    c=0; 
    for (int i=0; i<nnodes+1; i++){
        fscanf(f2d,"%d", &count);
        c++;
        if (((c % 5)==0) || (i==nnodes)){
            fprintf(f3d," %10d \n", count);
        }
        else{
            fprintf(f3d," %10d ", count);
        }
    }

   c=0; 
    for (int i=0; i<nnodes; i++){
        fscanf(f2d,"%d", &count);
        c++;
        if (((c % 5)==0) || (i==nnodes-1)){
            fprintf(f3d," %10d \n", count);
        }
        else{
            fprintf(f3d," %10d ", count);
        }
    }
   
    /***7. Geometric Area Coefficient Values****/
    for (int i=0; i<nedges*area_coef; i++){
        fscanf(f2d,"%lf", &volume2d);
        volume3d=volume2d*aperturem[node[nodeind[i]-1].matnumber-1];
        if ((((i+1) % 5)==0)|| (i==nedges*area_coef-1)){
            fprintf(f3d," %15.12E \n", volume3d);
        }
        else{
            fprintf(f3d," %15.12E ", volume3d);
        }
    }

    free(node);
    free(nodeind);
    printf("Conversion Complete\n"); 
}


int main(int argc, char* args[]){

    printf("--> DFN STOR file: recalculating length of area coefficients to 2D area.----- \n"); 
    printf("--> Current version works for Uniform Fracture Aperature\n");
    FILE *fp,*f2d,*f3d;
    char *paramsName;
    Params *params;
    if (( params = (Params *) malloc( sizeof(Params) ) ) == NULL) {
        printf("ERROR ALLOCATING oneStepParams\n");}

    paramsName = createNewPointer(50);
    parseCommandLineArgs(argc, args, paramsName);
    printf("Params File Name %s\n",paramsName);
    fp = openFile(paramsName, "", "r");
    readInParams(fp, params);

    printf("-> Material File: %s\n", params->matID_file);
    printf("-> Aperture File: %s\n", params->aper_file);
    printf("-> stor input File: %s\n", params->stor_in_file);
    printf("-> stor output File: %s\n\n", params->stor_out_file);
    
    free(paramsName);

    f2d = openFile(params->stor_in_file,"","r");
    f3d = openFile(params->stor_out_file,"","w");
    copyHeader(f2d, f3d);    

    copyMain(f2d, f3d, params);
    printf("Cleaning up\n"); 
    closeFile(f2d);
    closeFile(f3d);

    return 0;
}
