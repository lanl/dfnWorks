CXX = g++

CXXFLAGS  = -std=c++11 -Wall -O3

main: main.o parseInputFunctions.o linkedList.o node.o
	$(CXX) $(CXXFLAGS) -o ConnectivityTest main.o parseInputFunctions.o linkedList.o node.o

main.o:  main.cpp

linkedList.o: linkedList.cpp linkedList.h

node.o: node.cpp node.h

parseInputFunctions.o: parseInputFunctions.cpp parseInputFunctions.h

clean:
	rm -f main.o parseInputFunctions.o linkedList.o node.o

