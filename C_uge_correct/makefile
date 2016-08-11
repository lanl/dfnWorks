
CC=gcc -std=c99
CFLAGS= -O3 -lm -Wall -g 

OBJ = main.o 

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

correct_uge: $(OBJ)
	gcc -o $@ $^ $(CFLAGS)

