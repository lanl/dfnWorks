#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <cstdlib>
#include <cstring>
#include <string>
#include <limits>
#include <iomanip>


struct Params {
    std::string mesh_file;
    std::string matID_file;
    std::string aper_file;
    std::string uge_in_file;
    std::string uge_out_file;
    int cell_flag;
};

int readInt(const std::string& buf) {
    std::cout << "The buf is?: " << buf << std::endl;
    std::istringstream iss(buf);
    std::string temp;
    int num;
    bool found = false;  // Track whether we have found a valid number

    // Read words until we find a valid integer
    while (iss >> temp) {
        std::istringstream tempStream(temp);
        char leftover;
        if (tempStream >> num && !(tempStream >> leftover)) { 
            std::cout << "Number found: " << num << std::endl;
            found = true;
            break;  // Stop as soon as we find the first valid integer
        }
    }

    std::cout << "What is found?: " << found << std::endl;

    // If no integer was found, print an error and exit
    if (!found) {
        std::cerr << "ERROR: parsing line: " << buf << std::endl;
        exit(1);
    }

    return num;
}

void check_null_pointer(void* temp) {
    if (!temp) {
        std::cerr << "Out of Memory\n";
        exit(1);
    }
}

std::ifstream open_file(const std::string& filename) {
    std::ifstream file(filename);
    if (!file) {
        std::cerr << "Error: Unable to open file: " << filename << std::endl;
        exit(1);
    }
    std::cout << "Opening input file " << filename << std::endl;
    return file;
}

std::ofstream open_output_file(const std::string& filename) {
    std::ofstream file(filename);
    if (!file) {
        std::cerr << "Can't open file: " << filename << "\n";
        exit(1);
    }
    std::cout << "Opening output file " << filename << std::endl;
    return file;
}

int get_number_of_nodes(const std::string& mesh_file) {
    std::ifstream fp = open_file(mesh_file);
    int numNodes, numElem, numNodeAtt, numElemAtt, tmp;
    
    if (!(fp >> numNodes >> numElem >> numNodeAtt >> numElemAtt >> tmp)) {
        std::cerr << "*** Error Reading number of nodes ***\n";
    }

    std::cout << "Number of Nodes: " << numNodes << "\n";
    return numNodes;
}

int load_mat_id(const std::string& matID_file, int numNodes, std::vector<int>& matID) {
    std::ifstream fp = open_file(matID_file);
    std::string line;
    
    for (int i = 0; i < 3; i++) std::getline(fp, line); // Skip header

    int num_mat = 0, matid;
    for (int i = 0; i < numNodes; i++) {
        if (!(fp >> matid)) {
            std::cerr << "Error Reading in Mat ID\n";
        }
        matID[i] = matid;
        if (matid > num_mat) num_mat = matid;
    }

    std::cout << "There are " << num_mat << " Materials\n";
    return num_mat;
}

void load_aperture(const std::string& aper_file, int num_mat, std::vector<int>& aper_index, std::vector<double>& aper_values) {
    std::ifstream fp = open_file(aper_file);
    std::string line;
    std::getline(fp, line); // Skip header

    int aper_id, tmp, tmp2;
    double aper;
    for (int i = 0; i < num_mat; i++) {
        if (!(fp >> aper_id >> tmp >> tmp2 >> aper)) {
            std::cerr << "Error loading apertures\n";
        }
        aper_index[i] = aper_id;
        aper_values[i] = aper;
    }
    std::cout << "Aperture loaded\n";
}

void load_aperture_cell(const std::string& aper_file, int numNodes, std::vector<int>& aper_index, std::vector<double>& aper_values) {
    std::ifstream fp = open_file(aper_file);
    std::string line;
    std::getline(fp, line); // Skip header

    int aper_id, tmp, tmp2;
    double aper;
    for (int i = 0; i < numNodes; i++) {
        if (!(fp >> aper_id >> tmp >> tmp2 >> aper)) {
            std::cerr << "Error loading apertures\n";
        }
        aper_index[i] = aper_id;
        aper_values[i] = aper;
    }
    std::cout << "Aperture loaded\n";
}


void convert_uge(const std::string& uge_in_file, const std::string& uge_out_file, std::vector<int>& matID, std::vector<int>& aper_index, std::vector<double>& aper_values)  {
    // Open input and output files using C++ streams
    std::ifstream fin(uge_in_file);
    if (!fin) {
        std::cerr << "Error opening input file: " << uge_in_file << "\n";
        return;
    }
    std::ofstream fout(uge_out_file);
    if (!fout) {
        std::cerr << "Error opening output file: " << uge_out_file << "\n";
        return;
    }

    std::string buf;
    std::cout << "Reading in UGE: " << uge_in_file << "\n";
    
    // Read the first line from the input file
    std::getline(fin, buf);
    int NumCells = readInt(buf);
    std::cout << "Number of Cells: " << NumCells << "\n";
    fout << "CELLS\t" << NumCells << "\n";
    
    int cell_index, index_1, index_2;
    double x, y, z, volume;
    for (int i = 0; i < NumCells; i++) {
        // Read the cell data; using >> extraction to mimic fscanf
        fin >> cell_index >> x >> y >> z >> volume;
        if (fin.fail()) {
            std::cout << "*** Error loading Cells in the UGE file ***\n";
        }
        
        index_1 = matID[cell_index - 1] - 1;
        if (aper_index[index_1] == -1 * matID[cell_index - 1] - 6) {
            volume *= aper_values[index_1];
        } else {
            std::cout << "*** Error Indexing Aperture List ***\n";
            std::cout << "Index from aperture: " << aper_index[index_1] << "\n";
            std::cout << "Index from matid: " << -1 * matID[cell_index - 1] - 6 << "\n";
        }
        
        fout << cell_index << "\t"
             << std::scientific << std::setprecision(12) << x << "\t"
             << y << "\t" << z << "\t" << volume << "\n";
    }
    
    // Remove any leftover newline character after formatted input
    fin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    
    // Read the next line which contains the number of connections
    std::getline(fin, buf);
    int NumConns = readInt(buf);
    std::cout << "--> Number of Connections: " << NumConns << "\n";
    fout << "CONNECTIONS\t" << NumConns << "\n";
    
    int conn_index_1, conn_index_2;
    for (int i = 0; i < NumConns; i++) {
        fin >> conn_index_1 >> conn_index_2 >> x >> y >> z >> volume;
        if (fin.fail()) {
            std::cout << "*** Error loading connections in the UGE file ***\n";
        }
        
        index_1 = matID[conn_index_1 - 1] - 1;
        index_2 = matID[conn_index_2 - 1] - 1;
        volume *= 0.5 * (aper_values[index_1] + aper_values[index_2]);
        
        fout << conn_index_1 << "\t" << conn_index_2 << "\t"
             << std::scientific << std::setprecision(12) << x << "\t"
             << y << "\t" << z << "\t" << volume << "\n";
    }
    
    fin.close();
    fout.close();
    std::cout << "--> new UGE written in " << uge_out_file << "\n";
}
 
void convert_uge_cell(const std::string& uge_in_file, const std::string& uge_out_file, std::vector<int>& matID, std::vector<int>& aper_index, std::vector<double>& aper_values){
    // Open input and output files using C++ streams
    std::ifstream fin(uge_in_file);
    if (!fin) {
        std::cerr << "Error opening input file: " << uge_in_file << "\n";
        return;
    }
    std::ofstream fout(uge_out_file);
    if (!fout) {
        std::cerr << "Error opening output file: " << uge_out_file << "\n";
        return;
    }

    std::string buf;
    std::cout << "Reading in UGE: " << uge_in_file << "\n";
    
    // Read the first line from the input file
    std::getline(fin, buf);
    int NumCells = readInt(buf);
    std::cout << "Number of Cells: " << NumCells << "\n";
    fout << "CELLS\t" << NumCells << "\n";
    
    int cell_index;
    double x, y, z, volume;
    for (int i = 0; i < NumCells; i++) {
        fin >> cell_index >> x >> y >> z >> volume;
        if (fin.fail()) {
            std::cout << "*** Error loading Cells in the UGE file ***\n";
        }
        
        volume *= aper_values[cell_index - 1];
        fout << cell_index << "\t"
             << std::scientific << std::setprecision(12) << x << "\t"
             << y << "\t" << z << "\t" << volume << "\n";
    }
    
    // Remove any leftover newline character after formatted input
    fin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    
    // Read the next line which contains the number of connections
    std::getline(fin, buf);
    int NumConns = readInt(buf);
    std::cout << "--> Number of Connections: " << NumConns << "\n";
    fout << "CONNECTIONS\t" << NumConns << "\n";
    
    int conn_index_1, conn_index_2;
    for (int i = 0; i < NumConns; i++) {
        fin >> conn_index_1 >> conn_index_2 >> x >> y >> z >> volume;
        if (fin.fail()) {
            std::cout << "*** Error loading connections in the UGE file ***\n";
        }
        
        volume *= 0.5 * (aper_values[conn_index_1 - 1] + aper_values[conn_index_2 - 1]);
        fout << conn_index_1 << "\t" << conn_index_2 << "\t"
             << std::scientific << std::setprecision(12) << x << "\t"
             << y << "\t" << z << "\t" << volume << "\n";
    }
    
    fin.close();
    fout.close();
    std::cout << "--> new UGE written in " << uge_out_file << "\n";
}


// void convert_uge(const std::string& uge_in_file, const std::string& uge_out_file, std::vector<int>& matID, std::vector<int>& aper_index, std::vector<double>& aper_values) {
//     std::ifstream fin = open_file(uge_in_file);
//     std::cout << "Opening input file: " << uge_in_file << "\n";
//     std::ofstream fout = open_output_file(uge_out_file);
//     std::cout << "Opening output file: " << uge_out_file << "\n";
    
//     std::string buf;

//     std::getline(fin, buf);
//     std::cout << "What is buf from the convert before cell?: " << buf << std::endl;
//     int NumCells = readInt(buf);
//     std::cout << "numcells?: " << NumCells << std::endl;

//     std::cout << "CELLS\t" << NumCells << "\n";

//     int cell_index;
//     double x, y, z, volume;
//     for (int i = 0; i < NumCells; i++) {
//         if (!(fin >> cell_index >> x >> y >> z >> volume)) {
//             std::cerr << "*** Error loading Cells in the UGE file ***\n";
//         }

//         int index_1 = matID[cell_index - 1] - 1;
//         if (aper_index[index_1] == -1 * matID[cell_index - 1] - 6) {
//             volume *= aper_values[index_1];
//         } else {
//             std::cerr << "*** Error Indexing Aperture List ***\n";
//         }

//         fout << cell_index << "\t" << x << "\t" << y << "\t" << z << "\t" << volume << "\n";
//     }

//     fin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

//     std::getline(fin, buf);
//     std::cout << "What is buf from the convert before connection?: " << buf << std::endl;
//     int NumConns = readInt(buf);

//     std::cout << "numconns?: " << NumConns << std::endl;

//     std::cout << "CONNECTIONS\t" << NumConns << std::endl;

//     int conn_index_1, conn_index_2;
//     for (int i = 0; i < NumConns; i++) {
//         if (!(fin >> conn_index_1 >> conn_index_2 >> x >> y >> z >> volume)) {
//             std::cerr << "*** Error loading connections in the UGE file ***\n";
//         }

//         int index_1 = matID[conn_index_1 - 1] - 1;
//         int index_2 = matID[conn_index_2 - 1] - 1;
//         volume *= 0.5 * (aper_values[index_1] + aper_values[index_2]);

//         fout << conn_index_1 << "\t" << conn_index_2 << "\t" << x << "\t" << y << "\t" << z << "\t" << volume << "\n";
//     }

//     std::cout << "--> new UGE written in " << uge_out_file << "\n";
// }


void readInParams(std::ifstream& fparams, Params& params) {
    fparams >> params.mesh_file >> params.matID_file >> params.uge_in_file >> params.uge_out_file >> params.aper_file >> params.cell_flag;
}

int main(int argc, char* args[]) {
    std::string paramsName = (argc > 1) ? args[1] : "convert_uge_params.txt";

    std::cout << "Params File Name " << paramsName << "\n";
    std::ifstream fp = open_file(paramsName);
    Params params;
    readInParams(fp, params);

    std::cout << "\nCorrecting UGE Volumes and Areas for dfnWorks\n";
    std::cout << "-> Mesh File: " << params.mesh_file << "\n";
    std::cout << "-> MatID File: " << params.matID_file << "\n";
    std::cout << "-> Aperture File: " << params.aper_file << "\n";
    std::cout << "-> UGE input File: " << params.uge_in_file << "\n";
    std::cout << "-> UGE output File: " << params.uge_out_file << "\n\n";

    int numNodes = get_number_of_nodes(params.mesh_file);
    std::vector<int> matID(numNodes);
    int num_mat = load_mat_id(params.matID_file, numNodes, matID);

    std::vector<double> aper_values(numNodes);
    std::vector<int> aper_index(numNodes);

    if (params.cell_flag < 0) {
        load_aperture(params.aper_file, num_mat, aper_index, aper_values);
        convert_uge(params.uge_in_file, params.uge_out_file, matID, aper_index, aper_values);
    }
    if (params.cell_flag > 0) {
        load_aperture_cell(params.aper_file, numNodes, aper_index, aper_values);
        convert_uge_cell(params.uge_in_file, params.uge_out_file, matID, aper_index, aper_values);
    }

    return 0;
}