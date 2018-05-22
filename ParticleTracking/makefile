
CC=gcc

CFLAGS =  -g -lm -O6 -Wall 



OBJECTS= main.o ReadGridInit.o  RotateFracture.o VelocityReconstruction.o TrackingPart1_test.o InitialPartPositions.o output.o


DFNTrans: $(OBJECTS)
       
	$(CC)  $(OBJECTS) -o DFNTrans $(CFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $<

clean: 
	 rm -f DFNTrans main.o ReadGridInit.o  RotateFracture.o VelocityReconstruction.o TrackingPart1_test.o InitialPartPositions.o output.o
