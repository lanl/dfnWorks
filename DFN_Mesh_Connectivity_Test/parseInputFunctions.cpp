#include <algorithm>
#include <iostream>
#include "parseInputFunctions.h"

// Comment/Uncomment for debug prints
//#define DEBUG


/*************************************************************************************/
// Search file for a word/string
// arg 1: Input file stream (ifstream) object
// arg 2: String to search for in ifstream file object (arg 1)
// Return Val: 1 - Word ('search') was found, stream points to directly after the word
//             0 - Word ('search') was not found. Stream has eof flag set.
bool findWord(std::ifstream &stream, std::string search) {
    std::string word;
    
    while (stream >> word) {
        if (word == search) {
            break;
        }
    }
    
    if ((int) stream.tellg() == -1) {
        return false;
    }
    
    return true;
}


/*************************************************************************************/
// Reads in intersection line connectivity from .inp file into LineConnectin array
// Arg 1: Path to intersecion.inp file
// Arg 2: Variable to store/output the LineConnection[] size;
// Return: Array of struct LineConnection
LineConnection* readIntersectionConnectivity(const char *filePath, int &connSize_Out) {
    using namespace std;
    ifstream file;
    file.open(filePath, ifstream::in);
    
    if (!file.is_open()) {
        cout << "Unable to open file: " << filePath << endl;
        exit(1);
    }
    
    //second number tells us array size
    file >> connSize_Out >> connSize_Out;
#ifdef DEBUG
    std::cout << "intersection connection size = " << connSize_Out << "\n";
#endif
    LineConnection* connection = new LineConnection[connSize_Out];
    
    for (int i = 0; i < connSize_Out; i++) {
        findWord(file, "line");
        file >> connection[i].a;
        file >> connection[i].b;
#ifdef DEBUG
        std::cout << "con " << i << " : " << connection[i].a << ", " << connection[i].b << "\n";
#endif
    }
    
    file.close();
    return connection;
}


/*************************************************************************************/
// Skip n lines in a file (ifstream object)
// Arg 1: Number of lines to skip
// Arg 2: Input file stream object
void skipLines(int n, std::ifstream &file) {
    std::string line;
    
    for (int i = 0; i < n; i++) {
        std::getline(file, line);
    }
}


/*************************************************************************************/
// Returns number of lines from the current file ptr to the end of file
// Arg 1: Input file stream object
// Return: Number of lines from current file ptr location to eof
int countLines(std::ifstream &file) {
    std::streampos pos = file.tellg();
    std::string line;
    int count = 0;
    
    while (std::getline(file, line)) {
        count++;
    }
    
    //clear eof bit
    file.clear();
    file.seekg(pos);
    return count;
}


/*************************************************************************************/
// Updates LineConnection array which is populated in readIntersectionConnectivity()
// Replaces intersection node numbers with their corresponding global node numbers
// Arg 1: Path to intersectin node to global node file
// Arg 2: LineConnection array which will be updated with global node numbers
// Arg 3: LineConnection array size
void updateToGlobalNodeNums(const char *filePath, LineConnection* connection, int connSize) {
    std::ifstream file;
    file.open(filePath, std::ifstream::in);
    
    if (!file.is_open()) {
        std::cout << "Unable to open file: " << filePath << std::endl;
        exit(1);
    }
    
    // Skip first 3 lines of intersection node to global node file
    skipLines(3, file);
#ifdef DEBUG
    std::streampos pos = file.tellg();
    std::cout << "Node to Global File:\n";
    std::string word;
    
    while (file >> word) {
        std::cout << word << "\n";
    }
    
    file.clear();
    file.seekg(pos);
#endif
    // Go through all connections and update
    // the node ids to global node ids
    int intNode, globalNode;
    intNode = 1;
    file >> globalNode;
    
    for (int i = 0; i < connSize; i++) {
        if (intNode != connection[i].a) {
            intNode++;
            file >> globalNode;
        }
        
        if (connection[i].a == intNode) {
            connection[i].a = globalNode;
        }
        
        if (intNode != connection[i].b) {
            intNode++;
            file >> globalNode;
        }
        
        if (connection[i].b == intNode) {
            connection[i].b = globalNode;
        }
    }
    
    file.close();
}


/*************************************************************************************/
// Reads in tri elements from mesh.inp file into struct Tri array, keeping the
// Tri int triplets ordered least to greatest. This helps to easily populate
// the edge graph.
// Arg 1: Path to fractures mesh.inp file
// Arg 2: Output of the size of the Struct tri array generated in this function
// Arg 3: Output of the min node ID seen in the first or second element of the tri struct array
// Arg 4: Output of the max node ID seen in the first or second element of the tri struct array
// Note: The min and max variables are used later in allocating edgeGraph memory.
//       The min is also used as an array index offset
Tri* readTriElements(const char* filePath, int& numElmts_out, int& minId, int& maxId) {
    std::ifstream file;
    file.open(filePath, std::ifstream::in);
    
    if (!file.is_open()) {
        std::cout << "Unable to open file: " << filePath << std::endl;
        exit(1);
    }
    
    //seond number tells us # of tri elements
    file >> numElmts_out >> numElmts_out;
#ifdef DEBUG
    std::cout << "\nnumber of elmts = " << numElmts_out << "\n";
#endif
    Tri* triElmts = new Tri[numElmts_out];
    // init min and max
    maxId = 0;
    minId = 0x7FFFFFFF; //max int
    // Note: we only need the min and max of tri.a and tri.b
    // array access, and memory allocation,  will only ever
    // use a and b
#ifdef DEBUG
    std::cout << "min init = " << minId << std::endl;
#endif
    
    for (int i = 0; i < numElmts_out; i++) {
        bool found = findWord(file, "tri");
        
        if (!found) {
            std::cout << "ERROR while parsing mesh inp file\n";
            exit(1);
        }
        
        // keeping these triplets sorted helps
        // when building the edge graph
        int temp[3];
        file >> temp[0] >> temp[1] >> temp[2];
        std::sort(temp, temp + 3);
        triElmts[i].a = temp[0];
        triElmts[i].b = temp[1];
        triElmts[i].c = temp[2];
        
        if (triElmts[i].a > maxId) {
            maxId = triElmts[i].a;
        }
        
        if (triElmts[i].b > maxId) {
            maxId = triElmts[i].b;
        }
        
        if (triElmts[i].a < minId) {
            minId = triElmts[i].a;
        }
        
        if (triElmts[i].b < minId) {
            minId = triElmts[i].b;
        }
    }
    
    file.close();
    return triElmts;
}


