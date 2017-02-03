#include <stdio.h>
#include <string.h>
#include <stdlib.h>


// get the coordinates x, y, z from a line of a C file
float* getCoordinates(char* line) {

    float coordinates[3];

    char* x = strsep(&line, " ");
    char* y = strsep(&line, " ");
    char* z = strsep(&line, " ");

    coordinates[0] = atoi(x);
    coordinates[1] = atoi(y);
    coordinates[2] = atoi(z);
}

float** getCoordinateList(FILE* inp_file, int num_nodes) {


    char line[100];
    int i = 0;

    // Allocate the coordinate array
    float** coordinate_list = malloc(num_nodes*sizeof(float*));
    for (i=0; i<num_nodes; i++) {
        coordinate_list[i] = malloc(3*sizeof(float));
    }

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
    for (i=0; i < num_in_elem_list; i++) {
        elem_info[i] = line[j];
        j += 2;
    }

    return elem_info;
}

int** getElementList(FILE* inp_file, int num_elems, const char* type) {

    char line[100];
    int** element_list = malloc(num_elems*sizeof(int*));
    int i = 0;
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

int getNumElems(FILE* inp_file, const char* type) {

    int num = 0;
    // Populate the element array from the inp file
    int i = 0;
    char line[100];
    while(fgets(line, sizeof(line), inp_file)) { 
        if (strncmp(line, type, 3) == 0) 
            num += 1; 
    }
    return num;
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

    int num_nodes = atoi(strsep(&line, " "));
    int num_elems = atoi(strsep(&line, " "));
    
    float** coordinate_list = getCoordinateList(inp_file, num_nodes);
    int num_tet_elems = getNumElems(inp_file, "tet");
    int num_tri_elems = getNumElems(inp_file, "tri");

    rewind(inp_file);
    int** tet_element_list = getElementList(inp_file, num_tet_elems, "tet");
    rewind(inp_file);
    int** tri_element_list = getElementList(inp_file, num_tri_elems, "tri");

    fclose(inp_file);

    // WRITE VTK FILE
    char const* const vtk_file_name = argv[2];
    write_vtk_file(vtk_file_name, coordinate_list, tri_element_list, tet_element_list, num_nodes, num_tet_elems, num_tri_elems);
    return 0;
}



























































