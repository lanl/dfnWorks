CC=gcc

CFLAGS =  -lm -Wall -g -O3 -std=gnu17 -Wno-error=implicit-function-declaration 

OBJECTS= main.o ReadGridInit.o  RotateFracture.o VelocityReconstruction.o TrackingPart.o InitialPartPositions.o output.o

DFNTrans : $(OBJECTS)
       
	$(CC)  $(OBJECTS) -o DFNTrans $(CFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $<
clean:
	rm -rf DFNTrans main.o ReadGridInit.o  RotateFracture.o VelocityReconstruction.o TrackingPart.o InitialPartPositions.o output.o

