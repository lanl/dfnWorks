#ifndef _PARSEINPUTFUNCTIONS_H_
#define _PARSEINPUTFUNCTIONS_H_

#include <fstream>
#include <string>
#include "lineConnection.h"
#include "tri.h"

bool findWord(std::ifstream &stream, std::string search);
LineConnection* readIntersectionConnectivity(const char *filePath, int &connSize_Out);
void skipLines(int n, std::ifstream &file);
int countLines(std::ifstream &file);
void updateToGlobalNodeNums(const char *filePath, LineConnection* connection, int connSize);
Tri* readTriElements(const char* filePath, int& numElmts_out, int& minId, int& maxId);

#endif
