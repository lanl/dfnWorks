CC = g++ -std=c++17
CFLAGS = -O3 -Wall -g

# Define the targets
TARGETS = correct_stor correct_uge

# Default target: build both executables
all: $(TARGETS)

# Build correct_stor with BUILD_STOR defined
correct_stor: main.cpp
	$(CC) -o $@ main.cpp $(CFLAGS) -DBUILD_STOR

# Build correct_uge with BUILD_UGE defined
correct_uge: main.cpp
	$(CC) -o $@ main.cpp $(CFLAGS) -DBUILD_UGE

# Clean up compiled files
clean:
	rm -f $(TARGETS)