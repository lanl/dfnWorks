#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <cstdlib>
#include <cmath>
#include <cstring>

struct Params {
    std::string matID_file;
    std::string aper_file;
    std::string stor_in_file;
    std::string stor_out_file;
};

// Function to open a file for reading
std::ifstream openFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file) {
        std::cerr << "Can't open file: " << filename << "\n";
        exit(1);
    }
    std::cout << "Opening file " << filename << "\n";
    return file;
}

// Function to open a file for writing
std::ofstream openOutputFile(const std::string& filename) {
    std::ofstream file(filename);
    if (!file) {
        std::cerr << "Can't open file: " << filename << "\n";
        exit(1);
    }
    return file;
}

void parseCommandLineArgs(int countArgs, char* args[], std::string& paramsName) {
    paramsName = (countArgs > 1) ? args[1] : "convert_uge_params.txt";
}

void readInParams(std::ifstream& fparams, Params& params) {
    fparams >> params.matID_file >> params.stor_in_file >> params.stor_out_file >> params.aper_file;
}

void copyHeader(std::ifstream& f2d, std::ofstream& f3d) {
    std::cout << "Copying Header\n";
    std::string line;
    
    for (int i = 0; i < 2; i++) {
        std::getline(f2d, line);
        f3d << line << "\n";
    }
}

void copyMain(std::ifstream& f2d, std::ofstream& f3d, const Params& params) {
    std::ifstream fmz = openFile(params.matID_file);
    std::ifstream fad = openFile(params.aper_file);

    int nnodes, nedges, area_coef, max_neighb, snode_edge;
    f2d >> nedges >> nnodes >> snode_edge >> area_coef >> max_neighb;
    f3d << nedges << " " << nnodes << " " << snode_edge << " " << area_coef << " " << max_neighb << "\n";
    std::cout << "There are " << nnodes << " nodes and " << nedges << " edges \n";

    struct Material {
        unsigned int matnumber;
    };

    std::vector<Material> node(nnodes);

    // Read material file
    std::string junk;
    unsigned int mat_number, nnum, currentn;
    fmz >> junk;

    while (true) {
        fmz >> mat_number >> junk;
        if (junk == "nnum") {
            fmz >> nnum;
            for (unsigned int i = 0; i < nnum; i++) {
                fmz >> currentn;
                node[currentn - 1].matnumber = mat_number;
            }
        } else {
            break;
        }
    }
    std::cout << "\nThere are " << mat_number - 6 << " materials\n";

    // Read aperture file
    std::vector<double> aperturem(mat_number);
    int apmat, zn;
    double currentap;
    fad >> junk;

    for (int i = 0; i < mat_number; i++) {
        fad >> apmat >> zn >> zn >> currentap;
        apmat *= -1;
        aperturem[apmat - 1] = currentap;
    }

    std::cout << "Correcting Voronoi Volumes\n";
    f3d << " ";

    // Voronoi Volumes
    for (int i = 0; i < nnodes; i++) {
        double volume2d, volume3d;
        f2d >> volume2d;
        volume3d = volume2d * aperturem[node[i].matnumber - 1];

        f3d << volume3d << ((i + 1) % 5 == 0 || i == nnodes - 1 ? "\n" : " ");
    }

    // Count for Each Row
    int count, c = 0;
    for (int i = 0; i < nnodes + 1; i++) {
        f2d >> count;
        f3d << count << ((++c % 5 == 0 || i == nnodes) ? "\n" : " ");
    }

    // Row Entries
    std::vector<unsigned int> nodeind(nedges);
    c = 0;
    for (int i = 0; i < nedges; i++) {
        f2d >> count;
        nodeind[i] = count;
        f3d << count << ((++c % 5 == 0 || i == nedges - 1) ? "\n" : " ");
    }

    // Indices into Coefficient List
    c = 0;
    for (int i = 0; i < nedges * area_coef; i++) {
        f2d >> count;
        f3d << count << ((++c % 5 == 0 || i == nedges * area_coef - 1) ? "\n" : " ");
    }

    c = 0;
    for (int i = 0; i < nnodes + 1; i++) {
        f2d >> count;
        f3d << count << ((++c % 5 == 0 || i == nnodes) ? "\n" : " ");
    }

    c = 0;
    for (int i = 0; i < nnodes; i++) {
        f2d >> count;
        f3d << count << ((++c % 5 == 0 || i == nnodes - 1) ? "\n" : " ");
    }

    // Geometric Area Coefficient Values
    for (int i = 0; i < nedges * area_coef; i++) {
        double volume2d, volume3d;
        f2d >> volume2d;
        volume3d = volume2d * aperturem[node[nodeind[i] - 1].matnumber - 1];

        f3d << volume3d << (((i + 1) % 5 == 0 || i == nedges * area_coef - 1) ? "\n" : " ");
    }

    std::cout << "Conversion Complete\n";
}

int main(int argc, char* args[]) {
    std::cout << "--> DFN STOR file: recalculating length of area coefficients to 2D area.----- \n";
    std::cout << "--> Current version works for Uniform Fracture Aperture\n";

    std::string paramsName;
    parseCommandLineArgs(argc, args, paramsName);
    std::cout << "Params File Name: " << paramsName << "\n";

    std::ifstream fp = openFile(paramsName);
    Params params;
    readInParams(fp, params);

    std::cout << "-> Material File: " << params.matID_file << "\n";
    std::cout << "-> Aperture File: " << params.aper_file << "\n";
    std::cout << "-> stor input File: " << params.stor_in_file << "\n";
    std::cout << "-> stor output File: " << params.stor_out_file << "\n\n";

    std::ifstream f2d = openFile(params.stor_in_file);
    std::ofstream f3d = openOutputFile(params.stor_out_file);

    copyHeader(f2d, f3d);
    copyMain(f2d, f3d, params);

    std::cout << "Cleaning up\n";
    return 0;
}