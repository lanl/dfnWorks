#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <cstdlib>
#include <cmath>
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
    std::string stor_in_file;
    std::string stor_out_file;
    int cell_flag;
};

// Find integers
int readInt(const std::string& buf) {
    std::istringstream iss(buf);
    std::string temp;
    int num;
    bool found = false;  // Track whether we have found a valid number

    // Read words until we find a valid integer
    while (iss >> temp) {
        std::istringstream tempStream(temp);
        char leftover;
        if (tempStream >> num && !(tempStream >> leftover)) { 
            found = true;
            break;
        }
    }

    // If no integer was found, print an error and exit
    if (!found) {
        std::cerr << "ERROR: parsing line: " << buf << std::endl;
        exit(1);
    }

    return num;
}

// Checks for null pointers
void check_null_pointer(void* temp) {
    if (!temp) {
        std::cerr << "Out of Memory\n";
        exit(1);
    }
}

// Open input File
std::ifstream open_file(const std::string& filename) {
    std::ifstream file(filename);
    if (!file) {
        std::cerr << "Error: Unable to open file: " << filename << std::endl;
        exit(1);
    }
    std::cout << "Opening input file " << filename << std::endl;
    return file;
}

// Open output file
std::ofstream open_output_file(const std::string& filename) {
    std::ofstream file(filename);
    if (!file) {
        std::cerr << "Can't open file: " << filename << "\n";
        exit(1);
    }
    std::cout << "Opening output file " << filename << std::endl;
    return file;
}

/*********************************************************\
* UGE Specific
\*********************************************************/

// Get node number
int get_number_of_nodes(const std::string& mesh_file) {
    std::ifstream fp = open_file(mesh_file);
    int numNodes, numElem, numNodeAtt, numElemAtt, tmp;
    
    if (!(fp >> numNodes >> numElem >> numNodeAtt >> numElemAtt >> tmp)) {
        std::cerr << "*** Error Reading number of nodes ***\n";
    }

    std::cout << "Number of Nodes: " << numNodes << "\n";
    return numNodes;
}

// Get material id
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

// Loading Aperture
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
}

// Loading Aperture cell
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
}

// Converting UGE file 
void convert_uge(const std::string& uge_in_file, const std::string& uge_out_file, std::vector<int>& matID, std::vector<int>& aper_index, std::vector<double>& aper_values)  {
    // Open input and output files
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
    
    // Reading in number of cells
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
    
    // Reading in number of connections
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

// Converting UGE cells 
void convert_uge_cell(const std::string& uge_in_file, const std::string& uge_out_file, std::vector<int>& matID, std::vector<int>& aper_index, std::vector<double>& aper_values){
    // Open input and output files
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
    
    // Reading in number of cells
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
    
    // Readin in number of connections
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
    
    // Closing files
    fin.close();
    fout.close();
    std::cout << "--> new UGE written in " << uge_out_file << "\n";
}

// UGE Specific parameters
void readInUGEParams(std::ifstream& fparams, Params& params) {
    fparams >> params.mesh_file >> params.matID_file >> params.uge_in_file >> params.uge_out_file >> params.aper_file >> params.cell_flag;
}

// Parse UGE Parameters
void parseCommandLineArgs(int countArgs, char* args[], std::string& paramsName) {
    paramsName = (countArgs > 1) ? args[1] : "convert_uge_params.txt";
}

// Stor Specific Parameters
void readInParams(std::ifstream& fparams, Params& params) {
    fparams >> params.matID_file >> params.stor_in_file >> params.stor_out_file >> params.aper_file;
}

/*********************************************************\
* STOR Specific
\*********************************************************/

// Copying header
void copyHeader(std::ifstream& f2d, std::ofstream& f3d) {
    std::cout << "Copying Header\n";
    std::string line;
    
    for (int i = 0; i < 2; i++) {
        std::getline(f2d, line);
        f3d << line << "\n";
    }
}

// Matrix Parameters
void copyMain(std::ifstream& f2d, std::ofstream& f3d, const Params& params) {
    // Read in file
    std::ifstream fmz(params.matID_file);
    if (!fmz) {
        std::cerr << "Error opening material file: " << params.matID_file << "\n";
        std::exit(1);
    }
    std::cout << params.matID_file << " opened.\n";
    // --- Read aperature file ---
    std::ifstream fad(params.aper_file);
    if (!fad) {
        std::cerr << "Error opening aperature file: " << params.aper_file << "\n";
        std::exit(1);
    }

    // Get Nodes and Edges
    int nnodes, nedges, area_coef, max_neighb, snode_edge;
    f2d >> nedges >> nnodes >> snode_edge >> area_coef >> max_neighb;
    f3d << nedges << " " << nnodes << " " << snode_edge << " " << area_coef << " " << max_neighb << "\n";
    std::cout << "There are " << nnodes << " nodes and " << nedges << " edges \n";

    unsigned int mat_number, nnum, currentn;
    std::string junk;

    struct Material {
        unsigned int matnumber;
    };

    // Allocate material vector (one per node)
    std::vector<Material> node(nnodes);

    // Read a header junk string before entering the loop.
    if (!(fmz >> junk)) {
        std::cerr << "Failed to read header from material file.\n";
        std::exit(1);
    }
    
    // Use a counter for the number of processed materials.
    unsigned int materialCount = 0;
    
    // Process material blocks
    do {
        if (!(fmz >> mat_number)) break;
        if (!(fmz >> junk)) break; 
        
        // If the command string starts with "nnum", process the following node indices.
        if (junk.compare(0, 4, "nnum") == 0) {
            if (!(fmz >> nnum)) break;
            
            for (unsigned int i = 0; i < nnum; i++) {
                if (!(fmz >> currentn)) break;
                // Check to ensure currentn > 0 to avoid underflow, then adjust for zero-based indexing.
                if (currentn > 0 && (currentn - 1) < node.size()) {
                    node[currentn - 1].matnumber = mat_number;
                } else {
                    std::cerr << "Index out of range: " << currentn << "\n";
                }
            }
            materialCount++; // Count this processed material block.
        } else {
            break;
        }
    } while (junk.compare(0, 4, "stop") != 0);
    std::cout << "\nThere are " << materialCount << " materials\n";
    std::vector<double> aperturem(materialCount);    
    std::cout << "Correcting Voronoi Volumes\n";
    f3d << " ";

    // Calculate voronoi volumes
    double volume2d, volume3d;
    int count = 0;
    int c = 0;

    for (int i = 0; i < nnodes; i++) {
        if (!(f2d >> volume2d)) {
            std::cerr << "Error reading volume for node " << i + 1 << "\n";
            break;
        }
        // Multiply volume2d by the appropriate aperture value
        volume3d = volume2d * aperturem[node[i].matnumber - 1];
        
        if (((i + 1) % 5 == 0) || (i == nnodes - 1)){
            f3d << std::setprecision(12) << volume3d << "\n";
        }
        else{
            f3d << std::setprecision(12) << volume3d << " ";
        }
    }
    
    // Count rows
    c = 0;
    for (int i = 0; i < nnodes + 1; i++) {
        //std::cout << "Calculating row count\n";
        f2d >> count;
        c++;
        if ((c % 5 == 0) || (i == nnodes))
            f3d << std::setw(10) << count << "\n";
        else
            f3d << std::setw(10) << count << " ";
    }
    
    // Row Entries
    std::vector<unsigned int> nodeind(nedges);
    c = 0;
    for (int i = 0; i < nedges; i++) {
        //std::cout << "Calculating row entries\n";
        f2d >> count;
        nodeind[i] = count;
        c++;
        if ((c % 5 == 0) || (i == nedges - 1))
            f3d << std::setw(10) << count << "\n";
        else
            f3d << std::setw(10) << count << " ";
    }
    
    // Indices into Coefficient List
    c = 0;
    for (int i = 0; i < nedges * area_coef; i++) {
        f2d >> count;
        c++;
        if ((c % 5 == 0) || (i == nedges * area_coef - 1))
            f3d << std::setw(10) << count << "\n";
        else
            f3d << std::setw(10) << count << " ";
    }
    
    c = 0;
    for (int i = 0; i < nnodes + 1; i++) {
        f2d >> count;
        c++;
        if ((c % 5 == 0) || (i == nnodes))
            f3d << std::setw(10) << count << "\n";
        else
            f3d << std::setw(10) << count << " ";
    }
    
    c = 0;
    for (int i = 0; i < nnodes; i++) {
        f2d >> count;
        c++;
        if ((c % 5 == 0) || (i == nnodes - 1))
            f3d << std::setw(10) << count << "\n";
        else
            f3d << std::setw(10) << count << " ";
    }
    
    // Geometric Area Coefficient Values
    for (int i = 0; i < nedges * area_coef; i++) {
        f2d >> volume2d;
        // Use the previously read node index (stored in nodeind) to retrieve the material
        int nodeIndex = static_cast<int>(nodeind[i]) - 1;
        volume3d = volume2d * aperturem[node[nodeIndex].matnumber - 1];
        if (((i + 1) % 5 == 0) || (i == nedges * area_coef - 1))
            f3d << std::setw(15) << std::scientific << std::setprecision(12) << volume3d << "\n";
        else
            f3d << std::setw(15) << std::scientific << std::setprecision(12) << volume3d << " ";
    }
    
    std::cout << "Conversion Complete\n";
}

int main(int argc, char* args[]) {
    std::string paramsName;

    if (argc > 1) {
        paramsName = args[1];
     
        if (paramsName == "convert_uge_params.txt") {
            std::cout << "Params File Name " << paramsName << "\n";
            std::ifstream fp = open_file(paramsName);
            Params params;
            readInUGEParams(fp, params);

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
            std::cout << "Cleaning up\n" ;

        }
        else if (paramsName == "convert_stor_params.txt") {
            std::cout << "--> DFN STOR file: recalculating length of area coefficients to 2D area.----- \n";
            std::cout << "--> Current version works for Uniform Fracture Aperture\n";

            std::string paramsName;
            parseCommandLineArgs(argc, args, paramsName);
            std::cout << "Params File Name: " << paramsName << "\n";

            std::ifstream fp = open_file(paramsName);
            Params params;
            readInParams(fp, params);

            std::cout << "-> Material File: " << params.matID_file << "\n";
            std::cout << "-> Aperture File: " << params.aper_file << "\n";
            std::cout << "-> stor input File: " << params.stor_in_file << "\n";
            std::cout << "-> stor output File: " << params.stor_out_file << "\n\n";

            std::ifstream f2d = open_file(params.stor_in_file);
            std::ofstream f3d = open_output_file(params.stor_out_file);

            copyHeader(f2d, f3d);
            copyMain(f2d, f3d, params);

            std::cout << "Cleaning up\n" ;
        }
        else{
            std::cout << "File name not set.";
        }

    } else {
        paramsName = "Error";  // Default value
    }
    return 0;
}