CC=gcc

CFLAGS =  -lm -Wall -g -O3

OBJECTS= main.o ReadGridInit.o  RotateFracture.o VelocityReconstruction.o TrackingPart.o InitialPartPositions.o output.o

DFNTrans : $(OBJECTS)
       
	$(CC)  $(OBJECTS) -o DFNTrans $(CFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $<
clean:
	rm -rf DFNTrans main.o ReadGridInit.o  RotateFracture.o VelocityReconstruction.o TrackingPart.o InitialPartPositions.o output.o

