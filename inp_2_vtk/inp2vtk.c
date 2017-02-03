    def inp2vtk(self, inp_file=''):
            import pyvtk as pv

            with open(inp_file, 'r') as f:
                line = f.readline()
                num_nodes = int(line.strip(' ').split()[0])
                num_elems = int(line.strip(' ').split()[1])

                coord = np.zeros((num_nodes, 3), 'float')
                elem_list_tri = []
                elem_list_tetra = []

                for i in range(num_nodes):
                    line = f.readline()
                    coord[i, 0] = float(line.strip(' ').split()[1])
                    coord[i, 1] = float(line.strip(' ').split()[2])
                    coord[i, 2] = float(line.strip(' ').split()[3])

                for i in range(num_elems):
                    line = f.readline().strip(' ').split()
                    line.pop(0)
                    line.pop(0)
                    elem_type = line.pop(0)
                    if elem_type == 'tri':
                        elem_list_tri.append([int(i) - 1 for i in line])
                    if elem_type == 'tet':
                        elem_list_tetra.append([int(i) - 1 for i in line])

            print('--> Writing inp data to vtk format')

            vtk = pv.VtkData(pv.UnstructuredGrid(coord, tetra=elem_list_tetra, triangle=elem_list_tri),
                             'Unstructured pflotran grid')
            vtk.tofile(vtk_file)

#include <stdio.h>
#include <string.h>

// get the number of nodes and the number of elements from the first line of the VTK file
int* getNumbers(char* firstLine) {

    int numbers[2];

    char* num_nodes = strsep(&firstLine, " ");
    numbers[0] = atoi(numNodes);

    char* num_elems = strsep(&firstLine, " ");
    numbers[1] = atoi(numElems);

    return &numbers;
}

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

int main(int argc, char* argv[])
{
    char const* const inp_file_ame = argv[1];
    FILE* inp_file = fopen(inp_file_name, "r"); 
    char line[100];
    int* numbers;
    fgets(line, sizeof(line), inp_file);

    // get the number of nodes and the number of elements from the first line of the VTK file
    numbers = getNumbers(line);
    int num_nodes = numbers[0];
    int num_elems = numbers[1];

    // Allocate the coordinate array
    float** coordinate_list = malloc(num_nodes*sizeof(float*));
    for (int i=0; i<num_nodes; i++) {
        coordinate_list[i] = malloc(3*sizeof(float));
    }

    // Populate the coordinate array from the .inp file
    for (int i=0; i<num_nodes; i++) {
        fgets(line, sizeof(line), inp_file);
        coordinate_list[i] = getCoordinates(line);
    }

    int* element_list = malloc(num_elems, sizeof(int));

    // Populate the element array from the inp file
    for (int i=0; i<num_elems; i++) {
        fgets(line, sizeof(line), inp_file);
        element_list[i] = getCoordinates(line);
    }



    fclose(inp_file);
    return 0;
}