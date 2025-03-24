#include <iostream>
#include <string>

// Bring in uge.cpp and stor.cpp
extern int stor_main(int argc, char* argv[]);
extern int uge_main(int argc, char* argv[]);

// Map the modes to a integer
int getModeCode(const std::string &mode) {
    if (mode == "convert_stor_params.txt") return 1;
    if (mode == "convert_uge_params.txt") return 2;
    return 0;  // unknown mode
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <mode> [additional parameters...]\n";
        std::cerr << "Modes: convert_stor_params.txt, convert_uge_params.txt\n";
        return 1;
    }

    // Find current mode
    std::string mode = argv[1];

    // Adjust the argument pointers
    int newArgc = argc - 1;
    char** newArgv = argv + 1;

    // Map the mode string
    int modeCode = getModeCode(mode);

    // Switch cases
    switch (modeCode) {
        case 1:
            return stor_main(newArgc, newArgv);
        case 2:
            return uge_main(newArgc, newArgv);
        default:
            std::cerr << "Unknown mode: " << mode << "\n";
            return 1;
    }
}