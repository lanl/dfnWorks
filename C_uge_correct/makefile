CC = g++ -std=c++17  # Use g++ for C++ and set standard to C++17
CFLAGS = -O3 -Wall -g 

OBJ = main.o 

%.o: %.cpp $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

correct_uge: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)

clean:
	rm -f main.o


