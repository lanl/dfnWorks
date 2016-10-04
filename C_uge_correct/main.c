/*
 *  connected.c
 *
 *
 *  Created by Jeffrey Hyman on 10/28/13.
 *  Copyright 2013 University of Arizona. All rights reserved.
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>


int readInt(char* buf);

int readInt(char* buf) {
    int i = 0;
    //find start of numbers
    while (buf[i] > 0x39 || buf[i] < 0x30 ) {
        if (buf[i] == '\0') {
            printf("ERROR parsing line\n");
            exit(1);
        }
        i++;
    }
    return atoi(&buf[i]);
}

/*********************************************************\
 *Funciton:check_null_pointer
 Checks to see is a pointer is NULL
 \*********************************************************/
void check_null_pointer(char*temp)
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
char *create_new_pointer(int size)
{
    char *temp;
    temp = malloc(size);
    check_null_pointer(temp);
    return temp;
}
/**************************************************************\
 * Function:open_file
 This Function Opens the Main Las File
 \**************************************************************/
FILE *open_file(char *base, char *name, char *fileMode)
{
    FILE *fp;
    char *new_name;
    
    new_name = create_new_pointer(200);
    
    strcpy(new_name, base);
    strcat(new_name, name);
    
    if ((fp = fopen(new_name, fileMode)) == NULL)
    {
        fprintf(stderr,"Can't open \"%s\" file.\n", new_name);
        exit(1);
    }
    free(new_name);
    return fp;
}

/*************************************************************\
 * Function:close_file
 Closes files, exits program if an error exists
 \*************************************************************/
void close_file(FILE *fp)
{
    if(fclose(fp) != 0)
    {
        fprintf(stderr, "*** Error closing file ***\n");
        exit(1);
    }
}
int get_number_of_nodes(char *mesh_file){
	
	FILE *fp;
	int numNodes, numElem, numNodeAtt, numElemAtt, tmp;	
	printf("Opening %s\n", mesh_file);
	// Get number of Nodes
	fp = open_file(mesh_file,"", "r");
	if (fscanf(fp, "\t%d\t%d\t%d\t%d\t%d\n", &numNodes, &numElem, &numNodeAtt, &numElemAtt, &tmp) != 5){
		fprintf(stderr, "*** Error Reading in number of nodes ***\n");
	}
	printf("Number of Nodes: %d\n", numNodes);
	close_file(fp);   

	return numNodes;
}

int load_mat_id(char *matID_file, int numNodes, int *matID){

	FILE *fp;
	char *line = NULL;
	size_t len = 0;
	int num_mat;
	int matid; 
	// Load in Material ID  
	printf("Reading in Material ID: %s\n", matID_file); 
	// Open Material ID file
	fp = open_file(matID_file, "", "r");
	// Jump Over Header
	for (int i = 0; i < 3; i++){
		getline(&line, &len, fp);
	}	
	num_mat = 0;
	for (int i = 0; i < numNodes; i++){
		if( fscanf(fp, "%d", &matid) != 1){
			printf("Error Reading in Mat ID\n");
		} 
		matID[i] = matid;
		if(matid > num_mat){ num_mat = matid;}
	}
	printf("There are %d Materials\n", matid);
	close_file(fp);
	return num_mat;
} 

void load_aperture(char *aper_file, int num_mat, int *aper_index, double *aper_values){
	FILE *fp;
	int aper_id;
	int tmp, tmp2;
	double aper; 
	
	char *line = NULL;
	size_t len = 0;
	printf("Reading in Apertures\n"); 
	fp = open_file(aper_file, "", "r");
	// Skip Header
	getline(&line, &len, fp);
	for (int i = 0; i < num_mat; i++){
		if (fscanf(fp, "%d %d %d %lf\n", &aper_id, &tmp, &tmp2, &aper) != 4){
			printf("Error loading apertures\n");
	}
		aper_index[i] = aper_id;
		aper_values[i] = aper;
	}
	close_file(fp);
}

void convert_uge(char *uge_in_file, char *uge_out_file, int *matID, int *aper_index, double *aper_values){

	// Read in UGE file
	FILE *fin, *fout;
	char *buf;
	size_t bufsize = 256;
	int cell_index, index_1, index_2;
	double x, y, z;
	double volume;
	int conn_index_1;
	int conn_index_2;
	
	printf("Reading in UGE: %s \n", uge_in_file);
	fin = open_file(uge_in_file, "", "r");
	fout  = open_file(uge_out_file, "", "w");
	
	buf = (char *)malloc(bufsize * sizeof(char));
	//read line
	getline(&buf, &bufsize,  fin);
	int NumCells = readInt(buf);
	
	printf("Number of Cells: %i\n", NumCells);
	
	fprintf(fout, "CELLS\t%i\n", NumCells);
	for (int i = 0; i < NumCells; i++){
		 if(fscanf(fin, "\t%d %lf %lf %lf %lf\n", &cell_index, &x, &y, &z, &volume) != 5){
			printf("*** Error loading Cells in the UGE file ***\n");
		} 
		 index_1 = matID[cell_index - 1] - 1;	
		 if (aper_index[index_1] == -1*matID[cell_index - 1] - 6){
			volume *= aper_values[index_1]; 
		}
		else { 
			printf("*** Error Indexing Aperture List ***\n");
			printf("Index from aperture: %d\n", aper_index[index_1] );
			printf("Index from matid: %d\n", -1*matID[cell_index-1] -6);
		}	
		//fprintf(fid,"%i\t%0.12E\t%0.12E\t%0.12E\t%0.12E\n", cell_index, x, y, z, volume);
		fprintf(fout,"%i\t%0.12E\t%0.12E\t%0.12E\t%0.12E\n", cell_index, x, y, z, volume);
	}
	// Read in Number of Connections
	getline(&buf, &bufsize,  fin);
	int NumConns = readInt(buf);
	printf("--> Number of Connections: %i\n", NumConns);
	free(buf);

	fprintf(fout, "CONNECTIONS\t%i\n", NumConns);
	for (int i = 0; i < NumConns; i++){
		if(fscanf(fin, "\t%d %d %lf %lf %lf %lf\n", &conn_index_1, &conn_index_2, &x, &y, &z, &volume) != 6){
			printf("*** Error loading connections in the UGE file *** \n");
		} 
	        index_1 = matID[conn_index_1 - 1] - 1;	
	        index_2 = matID[conn_index_2 - 1] - 1;	
		volume *= 0.5*(aper_values[index_1] + aper_values[index_2]);	
		//fprintf(fid,"%d\t%d\t%0.12E\t%0.12E\t%0.12E\t%0.12E\n", conn_index_1, conn_index_2, x, y, z, volume);	
		fprintf(fout,"%d\t%d\t%0.12E\t%0.12E\t%0.12E\t%0.12E\n", conn_index_1, conn_index_2, x, y, z, volume);	
	}
	close_file(fin);
	close_file(fout);
	printf("--> new UGE written in %s\n", uge_out_file);
}

int main(int argc, char *argv[]){

	char *mesh_file;
	char *matID_file;
	char *aper_file;
	char *uge_in_file;
	char *uge_out_file;
	
	mesh_file = create_new_pointer(256);
	matID_file = create_new_pointer(256);
	aper_file = create_new_pointer(256);
	uge_in_file = create_new_pointer(256);
	uge_out_file = create_new_pointer(256);
	
	mesh_file = argv[1];
	matID_file = argv[2];
	aper_file = argv[3];
	uge_in_file = argv[4];
	uge_out_file = argv[5];

	printf("\nCorrecting UGE Volumes and Areas for dfnWorks\n");
	printf("--> Current version works for Uniform Fracture Aperature\n");
	printf("-> Mesh File: %s\n", mesh_file);
	printf("-> MatID File: %s\n", matID_file);
	printf("-> Aperture File: %s\n", aper_file);
	printf("-> UGE input File: %s\n", uge_in_file);
	printf("-> UGE output File: %s\n\n", uge_out_file);

	int numNodes = get_number_of_nodes(mesh_file);
	int *matID = malloc(numNodes* sizeof(int *));
	int num_mat = load_mat_id(matID_file, numNodes, matID);

	// load in Apertures
	double *aper_values = malloc(numNodes *sizeof(double *));
	int *aper_index = malloc(numNodes *sizeof(int* ));
	load_aperture(aper_file, num_mat, aper_index, aper_values);
	convert_uge(uge_in_file, uge_out_file, matID, aper_index, aper_values);
	
	free(matID);
	free(aper_values);
	free(aper_index);
	return 0;
}
