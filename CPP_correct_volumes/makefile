CC = g++ -std=c++17
CFLAGS = -O3 -Wall -g

# Target executable name
TARGET = correct_volume

# List of source files
SRCS = main.cpp stor.cpp uge.cpp

# Default target: build the unified driver
all: $(TARGET)

$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRCS)

# Clean up compiled files
clean:
	rm -f $(TARGET)