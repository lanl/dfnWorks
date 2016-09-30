CXX = g++

CXXFLAGS  = -std=c++11 -Wall -O3

main: main.o linkedList.o tri.o node.o  parseInputFunctions.o
	$(CXX) $(CXXFLAGS) -o GenIntElmntList main.o parseInputFunctions.o linkedList.o node.o tri.o

main.o:  main.cpp

linkedList.o: linkedList.cpp linkedList.h

node.o: node.cpp node.h

parseInputFunctions.o: parseInputFunctions.cpp parseInputFunctions.h

tri.o: tri.cpp tri.h

clean:
	rm -f main.o parseInputFunctions.o linkedList.o node.o tri.o

