CC=gcc
CFLAGS=-c

all: run

run: iptables.o
	$(CC) run.c ip_tables.o -o run

iptables.o:
	$(CC) $(CFLAGS) ip_tables.c -Iinclude


clean:
	rm *.o run