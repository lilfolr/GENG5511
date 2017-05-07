CC=gcc
CFLAGS=-c

all: run

run: iptables.o
	$(CC) run.c ip_tables.o -liptc -lip4tc -lip6tc -ldl -lnfnetlink -o run

iptables.o:
	$(CC) $(CFLAGS) ip_tables.c -Iinclude


clean:
	rm -f *.o run 