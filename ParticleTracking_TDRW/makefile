
CC=gcc 


CFLAGS =  -lm   -Wall -g -O3


OBJECTS= main.o ReadGridInit.o  RotateFracture.o VelocityReconstruction.o TrackingPart.o InitialPartPositions.o output.o

DFNTrans_TDRW: $(OBJECTS)
       
	$(CC)  $(OBJECTS) -o DFNTrans_TDRW $(CFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $<
clean:
	rm -rf DFNTrans_TDRW main.o ReadGridInit.o  RotateFracture.o VelocityReconstruction.o TrackingPart.o InitialPartPositions.o output.o

