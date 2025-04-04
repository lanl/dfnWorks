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
#include "logFile.h"

extern Logger logger;
 
struct Params {
    std::string matID_file;
    std::string aper_file;
    std::string stor_in_file;
    std::string stor_out_file;
}; 

// Open file to read
std::ifstream openFile(const std::string& filename) {
    std::ifstream file(filename);
    std::string logString;
    if (!file) {
        logString = "Can't open file: " + filename + "\n";
        logger.writeLogFile(ERROR,  logString);
        exit(1);
    }
    logString = "Opening input file " + filename + "\n";
    logger.writeLogFile(INFO,  logString);
    return file;
}

// Open file to write
std::ofstream openOutputFile(const std::string& filename) {
    std::ofstream file(filename);
    std::string logString;
    if (!file) {
        logString = "Can't open file: " + filename + "\n";
        logger.writeLogFile(ERROR,  logString);
        exit(1);
    }
    logString = "Opening output file " + filename + "\n";
    logger.writeLogFile(INFO,  logString);
    return file;
} 

// Parse line
void parseCommandLineArgs(int countArgs, char* args[], std::string& paramsName) {
    paramsName = (countArgs > 1) ? args[1] : "convert_uge_params.txt";
} 

// Create a namespace for stor parameters
namespace stor {
    void readInParams(std::ifstream& fparams, Params& params) {
        fparams >> params.matID_file >> params.stor_in_file >> params.stor_out_file >> params.aper_file;
    }
}

void copyHeader(std::ifstream& f2d, std::ofstream& f3d) {
    std::string logString;
    logString = "Copying Header\n";
    logger.writeLogFile(INFO,  logString);
    std::string line; 

    for (int i = 0; i < 2; i++) {
        std::getline(f2d, line);
        f3d << line << "\n";
    }
} 

void copyMain(std::ifstream& f2d, std::ofstream& f3d, const Params& params) {
    // Read in file
    std::ifstream fmz(params.matID_file);
    std::string logString;
    if (!fmz) {
        logString = "Error opening material file: " + params.matID_file + "\n";
        logger.writeLogFile(ERROR,  logString);
        std::exit(1);
    }
    logString = params.matID_file + " opened.\n";
    logger.writeLogFile(INFO,  logString);
    // --- Read aperature file ---
    std::ifstream fad(params.aper_file);
    if (!fad) {
        logString = "Error opening aperature file: " + params.aper_file + "\n";
        logger.writeLogFile(ERROR,  logString);
        std::exit(1);
    }
 
    // Get Nodes and Edges
    int nnodes, nedges, area_coef, max_neighb, snode_edge;
    f2d >> nedges >> nnodes >> snode_edge >> area_coef >> max_neighb;
    f3d << nedges << " " << nnodes << " " << snode_edge << " " << area_coef << " " << max_neighb << "\n";
    logString = "There are " + to_string(nnodes) + " nodes and " + to_string(nedges) + " edges \n";
    logger.writeLogFile(INFO,  logString);
 
    unsigned int mat_number, nnum, currentn;
    std::string junk;

    struct Material {
        unsigned int matnumber;
    };
    std::vector<Material> node(nnodes);
 
    // Read a header junk string before entering the loop.
    if (!(fmz >> junk)) {
        logString = "Failed to read header from material file.\n";
        logger.writeLogFile(ERROR,  logString);
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

                    logString = "Index out of range: " + to_string(currentn) + "\n";
                    logger.writeLogFile(ERROR,  logString);
                }
            }
            materialCount++; // Count this processed material block.
        } else {
            break; 
        }
    } while (junk.compare(0, 4, "stop") != 0);
    logString = "There are " + to_string(materialCount) + " materials\n";
    logger.writeLogFile(INFO,  logString);
    std::vector<double> aperturem(materialCount);  
    logString = "Correcting Voronoi Volumes\n";
    logger.writeLogFile(INFO,  logString);
    f3d << " ";
  
    // Calculate voronoi volumes
    double volume2d, volume3d;
    int count = 0;
    int c = 0;

    for (int i = 0; i < nnodes; i++) {
        if (!(f2d >> volume2d)) {
            logString = "Error reading volume for node " + to_string(i + 1) + "\n";
            logger.writeLogFile(ERROR,  logString);
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
 
    // Count for Each Row
    c = 0;

    for (int i = 0; i < nnodes + 1; i++) {
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
    logString = "Conversion Complete\n";
    logger.writeLogFile(INFO,  logString);
}

int stor_main(int argc, char* args[]) {
    std::string logString = "--> DFN STOR file: recalculating length of area coefficients to 2D area.----- \n";
    logger.writeLogFile(INFO,  logString);
    logString = "--> Current version works for Uniform Fracture Aperture\n";
    logger.writeLogFile(INFO,  logString);
    std::string paramsName;
    parseCommandLineArgs(argc, args, paramsName);
    logString = "Params File Name: " + paramsName + "\n";
    logger.writeLogFile(INFO,  logString);
 
    std::ifstream fp = openFile(paramsName);
    Params params;
    stor::readInParams(fp, params);
 
    logString = "-> Material File: " + params.matID_file + "\n";
    logger.writeLogFile(INFO,  logString);
    logString =  "-> Aperture File: " + params.aper_file + "\n";
    logger.writeLogFile(INFO,  logString);
    logString =  "-> stor input File: " + params.stor_in_file + "\n";
    logger.writeLogFile(INFO,  logString);
    logString =  "-> stor output File: " + params.stor_out_file + "\n";
    logger.writeLogFile(INFO,  logString);
    std::ifstream f2d = openFile(params.stor_in_file);
    std::ofstream f3d = openOutputFile(params.stor_out_file);
 
    copyHeader(f2d, f3d);
    copyMain(f2d, f3d, params);

    logString = "Cleaning up\n";
    logger.writeLogFile(INFO,  logString);
    return 0;
}