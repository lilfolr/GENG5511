IDIR=include
CC=gcc
CFLAGS=-c

all: run

run: iptables.o
	$(CC) run.c ip_tables.o -o run

iptables.o:
	$(CC) $(CFLAGS) ip_tables.c -I$(IDIR)


clean:
	rm -f *.o run 
