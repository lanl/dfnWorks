#include <iostream>
#include <string>

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
    std::cout << "Argc: " << argc << "\nArgs: ";
    for (int i = 0; i < argc; ++i) {
        std::cout << args[i] << " ";
    }
    std::cout << "\n";

    if (argc < 2) {
        std::cerr << "Usage: " << args[0] << " <mode> [parameter file...]\n";
        std::cerr << "Modes: convert_stor_params.txt, convert_uge_params.txt\n";
        return 1;
    }

    // The mode is the second argument (args[1])
    std::string mode = args[1];
    std::cout << "Mode: " << mode << "\n";

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
            std::cerr << "Unknown mode: " << mode << "\n";
            return 1;
    }
}