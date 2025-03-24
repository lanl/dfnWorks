#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <cstdlib>
#include <cstring>
#include <string>
#include <limits>
#include <iomanip> 
#include "logFile.h"

extern Logger logger;

struct Params {
    std::string mesh_file;
    std::string matID_file;
    std::string aper_file;
    std::string uge_in_file;
    std::string uge_out_file;
    int cell_flag;
};

// Find valis integer 
int readInt(const std::string& buf) {
    std::string logString;
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
            break;  // Stop as soon as we find the first valid integer
        }
    } 
    // If no integer was found, print an error and exit
    if (!found) {
        logString = "ERROR: parsing line: " + buf+ "\n";
        logger.writeLogFile(ERROR,  logString);
        exit(1);
    }
    return num;
}

// Checks for null pointers
void check_null_pointer(void* temp) {
<<<<<<< HEAD
    std::string logString;
    if (!temp) {
        logString = "Out of Memory\n";
        logger.writeLogFile(ERROR,  logString);
=======
    if (!temp) {
        std::cerr << "Out of Memory\n";
>>>>>>> 4421e8f0 (Updates to add a main driver and single executable)
        exit(1);
    }
}

// Opens file to read
std::ifstream open_file(const std::string& filename) {
    std::string logString;
    std::ifstream file(filename);
    if (!file) {
        logString = "Error: Unable to open file: " + filename + "\n";
        logger.writeLogFile(ERROR,  logString);
        exit(1);
    }
    logString =  "Opening input file " + filename + "\n";
    logger.writeLogFile(INFO,  logString);
    return file;
}

// Opens file to write
std::ofstream open_output_file(const std::string& filename) {
    std::string logString;
    std::ofstream file(filename);
    if (!file) {
        logString = "Can't open file: " + filename + "\n";
        logger.writeLogFile(ERROR,  logString);
        exit(1);
    }
    logString =  "Opening output file " + filename+ "\n";
    logger.writeLogFile(INFO,  logString);
    return file;
}

int get_number_of_nodes(const std::string& mesh_file) {
    std::string logString;
    std::ifstream fp = open_file(mesh_file);
    int numNodes, numElem, numNodeAtt, numElemAtt, tmp;
    if (!(fp >> numNodes >> numElem >> numNodeAtt >> numElemAtt >> tmp)) {
        logString = "*** Error Reading number of nodes ***\n";
        logger.writeLogFile(ERROR,  logString);
    }
    logString =  "Number of Nodes: " + to_string(numNodes) + "\n";
    logger.writeLogFile(INFO,  logString);
    return numNodes;
}

int load_mat_id(const std::string& matID_file, int numNodes, std::vector<int>& matID) {
    std::string logString;
    std::ifstream fp = open_file(matID_file);
    std::string line;
    for (int i = 0; i < 3; i++) std::getline(fp, line); // Skip header
    int num_mat = 0, matid;
    for (int i = 0; i < numNodes; i++) {
        if (!(fp >> matid)) {
            logString = "Error Reading in Mat ID\n";
            logger.writeLogFile(ERROR,  logString);
        }
        matID[i] = matid;
        if (matid > num_mat) num_mat = matid;
    }
    logString =  "There are " + to_string(num_mat) + " Materials\n";
    logger.writeLogFile(INFO,  logString);
    return num_mat;
} 

void load_aperture(const std::string& aper_file, int num_mat, std::vector<int>& aper_index, std::vector<double>& aper_values) {
    std::string logString;
    std::ifstream fp = open_file(aper_file);
    std::string line;
    std::getline(fp, line); // Skip header
    int aper_id, tmp, tmp2;
    double aper;
 
    for (int i = 0; i < num_mat; i++) {
        if (!(fp >> aper_id >> tmp >> tmp2 >> aper)) {
            logString = "Error loading apertures\n";
            logger.writeLogFile(ERROR,  logString);
        }
        aper_index[i] = aper_id;
        aper_values[i] = aper;
    }
    logString =  "Aperture loaded\n";
    logger.writeLogFile(INFO,  logString);
}
 
void load_aperture_cell(const std::string& aper_file, int numNodes, std::vector<int>& aper_index, std::vector<double>& aper_values) {
    std::string logString;
    std::ifstream fp = open_file(aper_file);
    std::string line;
    std::getline(fp, line); // Skip header
    int aper_id, tmp, tmp2;
    double aper;
    for (int i = 0; i < numNodes; i++) {
        if (!(fp >> aper_id >> tmp >> tmp2 >> aper)) {
            logString = "Error loading apertures\n";
            logger.writeLogFile(ERROR,  logString);
        }
        aper_index[i] = aper_id;
        aper_values[i] = aper;
    }
    logString =  "Aperture loaded\n";
    logger.writeLogFile(INFO,  logString);
}

void convert_uge(const std::string& uge_in_file, const std::string& uge_out_file, std::vector<int>& matID, std::vector<int>& aper_index, std::vector<double>& aper_values)  {
    // Open input and output files using C++ streams
    std::string logString;
    std::ifstream fin(uge_in_file);
    if (!fin) {
        logString = "Error opening input file: " + uge_in_file + "\n";
        logger.writeLogFile(ERROR,  logString);
        return;
    }
    std::ofstream fout(uge_out_file);
    if (!fout) {
        logString = "Error opening output file: " + uge_out_file + "\n";
        logger.writeLogFile(ERROR,  logString);
        return;
    }
    std::string buf;
    logString =  "Reading in UGE: " + uge_in_file + "\n";
    logger.writeLogFile(INFO,  logString);
    
    // Read the first line from the input file
    std::getline(fin, buf);
    int NumCells = readInt(buf);
    logString =  "Number of Cells: " + to_string(NumCells) + "\n";
    logger.writeLogFile(INFO,  logString);
    fout << "CELLS\t" << NumCells << "\n";
    int cell_index, index_1, index_2;
    double x, y, z, volume;
    for (int i = 0; i < NumCells; i++) {
        // Read the cell data; using >> extraction to mimic fscanf
        fin >> cell_index >> x >> y >> z >> volume;
        if (fin.fail()) {
            logString =  "*** Error loading Cells in the UGE file ***\n";
            logger.writeLogFile(ERROR,  logString);
        }
        index_1 = matID[cell_index - 1] - 1;
        if (aper_index[index_1] == -1 * matID[cell_index - 1] - 6) {
            volume *= aper_values[index_1];
        } else {
            logString =  "*** Error Indexing Aperture List ***\nIndex from aperture: " + to_string(aper_index[index_1]) + "\nIndex from matid: " + to_string(-1 * matID[cell_index - 1] - 6) + "\n";
            logger.writeLogFile(ERROR,  logString);
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
    logString =  "--> Number of Connections: " + to_string(NumConns) + "\n";
    logger.writeLogFile(INFO,  logString);
    fout << "CONNECTIONS\t" << NumConns << "\n";
    int conn_index_1, conn_index_2;
    for (int i = 0; i < NumConns; i++) {
        fin >> conn_index_1 >> conn_index_2 >> x >> y >> z >> volume;
        if (fin.fail()) {
            logString =  "*** Error loading connections in the UGE file ***\n";
            logger.writeLogFile(ERROR,  logString);
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
    logString =  "--> new UGE written in " + uge_out_file + "\n";
    logger.writeLogFile(INFO,  logString);
}

void convert_uge_cell(const std::string& uge_in_file, const std::string& uge_out_file, std::vector<int>& matID, std::vector<int>& aper_index, std::vector<double>& aper_values){
    // Open input and output files using C++ streams
    std::string logString;
    std::ifstream fin(uge_in_file);
    if (!fin) {
        logString = "Error opening input file: " + uge_in_file + "\n";
        logger.writeLogFile(ERROR,  logString);
        return;
    }
    std::ofstream fout(uge_out_file);
 
    if (!fout) {
        logString = "Error opening output file: " + uge_out_file + "\n";
        logger.writeLogFile(ERROR,  logString);
        return;
    }
    std::string buf;
    logString =  "Reading in UGE: " + uge_in_file + "\n";
    logger.writeLogFile(INFO,  logString);

    // Read the first line from the input file
    std::getline(fin, buf);
    int NumCells = readInt(buf);
    logString =  "Number of Cells: " + to_string(NumCells) + "\n";
    logger.writeLogFile(INFO,  logString);
    fout << "CELLS\t" << NumCells << "\n";
    int cell_index; 
    double x, y, z, volume;
    for (int i = 0; i < NumCells; i++) {
        fin >> cell_index >> x >> y >> z >> volume;
        if (fin.fail()) {
            logString =  "*** Error loading Cells in the UGE file ***\n";
            logger.writeLogFile(ERROR,  logString);
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
    logString =  "--> Number of Connections: " + to_string(NumConns) + "\n";
    logger.writeLogFile(INFO,  logString);
    fout << "CONNECTIONS\t" << NumConns << "\n";
    int conn_index_1, conn_index_2;
    for (int i = 0; i < NumConns; i++) {
        fin >> conn_index_1 >> conn_index_2 >> x >> y >> z >> volume;
        if (fin.fail()) {
            logString =  "*** Error loading connections in the UGE file ***\n";
            logger.writeLogFile(ERROR,  logString);
        }
        volume *= 0.5 * (aper_values[conn_index_1 - 1] + aper_values[conn_index_2 - 1]);
        fout << conn_index_1 << "\t" << conn_index_2 << "\t"
             << std::scientific << std::setprecision(12) << x << "\t"
             << y << "\t" << z << "\t" << volume << "\n";
    }
    fin.close();
    fout.close();
    logString =  "--> new UGE written in " + uge_out_file + "\n";
    logger.writeLogFile(INFO,  logString);
}

void readInParams(std::ifstream& fparams, Params& params) {
    fparams >> params.mesh_file >> params.matID_file >> params.uge_in_file >> params.uge_out_file >> params.aper_file >> params.cell_flag;
}

int uge_main(int argc, char* args[]) {
    std::string logString;
    std::string paramsName = (argc > 1) ? args[1] : "convert_uge_params.txt";
    logString =  "Params File Name " + paramsName + "\n";
    logger.writeLogFile(INFO,  logString);
    std::ifstream fp = open_file(paramsName);
    Params params;
 
    readInParams(fp, params);
    logString =  "Correcting UGE Volumes and Areas for dfnWorks\n";
    logger.writeLogFile(INFO,  logString);
    logString =  "-> Mesh File: " + params.mesh_file + "\n";
    logger.writeLogFile(INFO,  logString);
    logString =  "-> MatID File: " + params.matID_file + "\n";
    logger.writeLogFile(INFO,  logString);
    logString =  "-> Aperture File: " + params.aper_file + "\n";
    logger.writeLogFile(INFO,  logString);
    logString =  "-> UGE input File: " + params.uge_in_file + "\n";
    logger.writeLogFile(INFO,  logString);
    logString =  "-> UGE output File: " + params.uge_out_file + "\n";
    logger.writeLogFile(INFO,  logString);
 
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