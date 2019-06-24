
CC=gcc -std=c99
CFLAGS= -O3 -lm -Wall -g 

OBJ = main.o 

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

correct_stor: $(OBJ)
	gcc -o $@ $^ $(CFLAGS)

clean:
	rm -f main.o 

