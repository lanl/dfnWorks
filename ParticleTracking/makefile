
CC=gcc

CFLAGS =  -lm -O6 -Wall 

OBJECTS= main.o ReadGridInit.o  RotateFracture.o VelocityReconstruction.o TrackingPart1.o InitialPartPositions.o output.o



DFNTrans: $(OBJECTS)
       
	$(CC)  $(OBJECTS) -o DFNTrans $(CFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $<


