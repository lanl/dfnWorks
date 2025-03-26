#include <iostream>
#include <string>
#include <ctime>
#include <fstream>
#include <sstream>
#include <stdio.h>
#include <cstring>
#include "logFile.h"

Logger logger("correct_volumes_logfile.log");
// Bring in uge.cpp and stor.cpp
extern int uge_main(int argc, char* args[]);
extern int stor_main(int argc, char* args[]);

// Map the modes to an integer
int getModeCode(const std::string &mode) {
    if (mode == "convert_stor_params.txt") return 1;
    if (mode == "convert_uge_params.txt") return 2;
    return 0;  // unknown mode
}

int main(int argc, char* args[]) {
    std::string logString =  "Creating Volume file.\n";
    logger.writeLogFile(INFO,  logString);

    for (int i = 0; i < argc; ++i) {
        std::cout << args[i] << " ";
    }
    std::cout << "\n";

    if (argc < 2) {
        logString = "Error: <mode> [parameter file...]\nModes: convert_stor_params.txt, convert_uge_params.txt\n";
        logger.writeLogFile(ERROR,  logString);
        return 1;
    }

    // The mode is the second argument (args[1])
    std::string mode = args[1];

    // Map mode string to a code
    int modeCode = getModeCode(mode);
    std::cout << "-> Mode Code: " << modeCode << "\n";

    // Dispatch to the proper main function using original arguments
    switch (modeCode) {
        case 1:
            return stor_main(argc, args);
        case 2:
            return uge_main(argc, args);
        default:
            logString = "Error: Unknown Mode.\n";
            logger.writeLogFile(ERROR,  logString);
            return 1;
    }
}