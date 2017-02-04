#include <stdio.h>
#include <string.h>
#include <stdlib.h>


// get the coordinates x, y, z from a line of a C file
float* getCoordinates(const char* line) {

    float coordinates[3];
    float ignore; 
    sscanf(line, "%f %f %f %f", &ignore, &coordinates[0], &coordinates[1], &coordinates[2]);
    //printf("%f %f %f \n", coordinates[0], coordinates[1], coordinates[2]);
}

float** getCoordinateList(FILE* inp_file, int num_nodes) {


    char line[100];
    int i = 0;

    // Allocate the coordinate array
    float** coordinate_list = malloc(num_nodes*sizeof(float*));
    for (i=0; i<num_nodes; i++) {
        coordinate_list[i] = malloc(3*sizeof(float));
    }

    fgets(line, sizeof(line), inp_file);

    // Populate the coordinate array from the .inp file
    for (i=0; i<num_nodes; i++) {
        fgets(line, sizeof(line), inp_file);
        coordinate_list[i] = getCoordinates(line);
    }

    return coordinate_list;
}

int* getListForElement(char* line, int num_in_elem_list) {

    int j = 3;
    int i = 0;
    int* elem_info = NULL;
    elem_info = malloc(num_in_elem_list*sizeof(int));
    if (num_in_elem_list == 3)
        sscanf(line, "%d %d %d", &elem_info[0], &elem_info[1], &elem_info[2]);
    if (num_in_elem_list == 4)
        sscanf(line, "%d %d %d %d", &elem_info[0], &elem_info[1], &elem_info[2], &elem_info[3]);
    
    printf("read in element with num %d, parts %d %d %d\n", num_in_elem_list, elem_info[0], elem_info[1], elem_info[2]);  
    return elem_info;
}

int** getElementList(FILE* inp_file, int num_elems, const char* type) {

    char line[100];
    int** element_list = malloc(num_elems*sizeof(int*));
    int i = 0;
    printf("Trying to read element list for %d %s elems \n", num_elems, type); 
    // Populate the element array from the inp file
    for (i=0; i<num_elems; i++) {
        fgets(line, sizeof(line), inp_file);
        if (strncmp(line, type, 3) == 0) {
            int num_elems_in_list = 0;
            if (strncmp(line, "tet", 3) == 0)
                num_elems_in_list = 4;
            if (strncmp(line, "tri", 3) == 0)
                num_elems_in_list = 3;
            element_list[i] = getListForElement(line, num_elems_in_list);
        }
    }
    return element_list;
}

void getNumElems(FILE* inp_file, const char* type, int* counter) {

    // Populate the element array from the inp file
    int i = 0;
    char line[10000];
    char line_type[3];;
    char ign_1[10];
    char ign_2[10];;

    while(fgets(line, sizeof(line), inp_file)) { 
        sscanf(line, "%s %s %s", ign_1, ign_2, line_type);   
        if (strncmp(line_type, type, 3) == 0) 
             *counter += 1; 
    }
}

void write_vtk_header(FILE* vtk_file) {

    fprintf(vtk_file, "vtk DataFile Version 2.0\n");
    fprintf(vtk_file, "Unstructured pflotran grid\n");
    fprintf(vtk_file, "ASCII\n");
    fprintf(vtk_file, "DATASET UNSTRUCTURED GRID\n");
}


void write_vtk_coordinates(FILE* vtk_file, float** coordinate_list, int num_nodes) {

    fprintf(vtk_file, "POINTS %d double\n", num_nodes);
    int i = 0; 
    int j = 0;
    for (i=0; i<num_nodes; i++) {
        for (j=0; j<3; j++) {
            fprintf(vtk_file, "%f ", coordinate_list[i][j]);
        }
        fprintf(vtk_file, "\n");
    }
}

void write_vtk_element(FILE* vtk_file, int* element, int num_in_elem) {

    fprintf(vtk_file, "%d ", num_in_elem);
    int i = 0;
    for (i=0; i<num_in_elem; i++) {
        fprintf(vtk_file, "%d ", element[i]);
    }
    fprintf(vtk_file, "\n");
}

void write_vtk_elements(FILE* vtk_file, int** tri_element_list, int num_tri_elems, int** tet_element_list, int num_tet_elems) {

    int x = 42; // WHAT IS SECOND NUMBER?
    fprintf(vtk_file, "CELLS %d %d\n", num_tri_elems + num_tet_elems, x);

    int i = 0;
    for (i=0; i<num_tri_elems; i++) {
        write_vtk_element(vtk_file, tri_element_list[i], 3);
    }

    for (i=0; i<num_tet_elems; i++) {
        write_vtk_element(vtk_file, tet_element_list[i], 4);
    }

}

void write_vtk_element_types(FILE* vtk_file, int type, int num_elems) {

    fprintf(vtk_file, "CELL_TYPES %d\n", num_elems);
    int i = 0;
    for (i=0; i<num_elems; i++)
        fprintf(vtk_file,"%d ", type);
}

void write_vtk_file(char const* const vtk_file_name, float** coordinate_list, int** tri_element_list, int** tet_element_list, int num_nodes, int num_tet_elems, int num_tri_elems) {

    FILE* vtk_file = fopen(vtk_file_name, "w"); 
    int type = 5;
    write_vtk_header(vtk_file);
    write_vtk_coordinates(vtk_file, coordinate_list, num_nodes);
    write_vtk_elements(vtk_file, tri_element_list, num_tri_elems, tet_element_list, num_tet_elems);
    write_vtk_element_types(vtk_file, type, num_tet_elems + num_tri_elems);
    fclose(vtk_file);
}

int main(int argc, char* argv[]) {

    if (argc < 3) {
        printf("ERROR: need two filename arguments");
        return 0;
    }

    printf("Converting the .inp file %s \n", argv[1]);
    printf("Writing the .vtk file %s \n", argv[2]);
    
    // READ INP FILE
    char const* const inp_file_name = argv[1];
    FILE* inp_file = fopen(inp_file_name, "r"); 
    // get the number of nodes and the number of elements from the first line of the VTK file
    int* numbers;
    char* line = malloc(100);
    fgets(line, sizeof(line), inp_file);

    int num_nodes = 0; 
    int num_elems = 0;
    fscanf(inp_file, "%d %d", &num_nodes, &num_elems);

    printf("%d nodes read from inp file \n", num_nodes);
    printf("%d elements read from inp file \n", num_elems);    
    
    if (num_nodes < 0) 
        printf("ERROR: negative or nonzero number of nodes read from .inp file \n");

    if (num_elems < 0) 
        printf("ERROR: negative or nonzero number of elements read from .inp filei \n");

    float** coordinate_list = getCoordinateList(inp_file, num_nodes);
    printf("before getting number of elements \n");

    int num_tet_elems = 0;
    int num_tri_elems = 0;
    rewind(inp_file);
    getNumElems(inp_file, "tet", &num_tet_elems);
    if (num_tet_elems > 2000) {
        printf("catastrophic failure %d \n", num_tet_elems);
        exit(0);   
    } 
    rewind(inp_file); 
    getNumElems(inp_file, "tri", &num_tri_elems);
    if (num_tri_elems > 2000) {
       printf("ugggfgdsfadsfdsfa %d \n", num_tri_elems);
       exit(0);   
    }
    printf("before getting inp element lists \n");

    rewind(inp_file);
    int** tet_element_list = getElementList(inp_file, num_tet_elems, "tet");
    rewind(inp_file);
    int** tri_element_list = getElementList(inp_file, num_tri_elems, "tri");
    
    fclose(inp_file);

    printf("writing vtk file \n");

    // WRITE VTK FILE
    char const* const vtk_file_name = argv[2];
    write_vtk_file(vtk_file_name, coordinate_list, tri_element_list, tet_element_list, num_nodes, num_tet_elems, num_tri_elems);
    return 0;
}



























































