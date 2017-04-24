
    std::ofstream bottomFile; 
    std::string bottomFileName = "bottom.txt"; 
    bottomFile.open(bottomFileName.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(bottomFile, bottomFileName);


