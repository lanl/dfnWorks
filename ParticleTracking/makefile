
CC=gcc

CFLAGS = -O3 -lm -g -Wall

OBJECTS= main.o ReadGridInit.o  RotateFracture.o VelocityReconstruction.o TrackingPart1.o InitialPartPositions.o



DFNTrans: $(OBJECTS)
       
	$(CC)  $(OBJECTS) -o DFNTrans $(CFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $<


