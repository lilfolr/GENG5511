IDIR=include
CC=gcc -fmax-errors=10 -w
CFLAGS=-c
LIBS=-lcheck -lm -lpthread -lrt

all: run

run: iptables.o
	$(CC) run.c ip_tables.o -o run

iptables.o:
	$(CC) $(CFLAGS) ip_tables.c -I$(IDIR)

test: build-test
	./test 

build-test: run
	checkmk test.check > test.tmp.c
	$(CC) -o test test.tmp.c $(LIBS)

clean:
	rm -f *.o run test test.tmp.c
