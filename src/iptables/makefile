IDIR=include
CC=gcc
CFLAGS=-c
LIBS=-lcheck -lm -lpthread -lrt

travis: run.o
	swig -py3 -python interface.i
	$(CC) $(CFLAGS) -fPIC -I/usr/include/python3.4 interface_wrap.c 
	gcc -shared run.o interface_wrap.o -o _iptables_sim.so

all: run.o
	swig -py3 -python interface.i
	$(CC) $(CFLAGS) -fPIC -I/usr/include/python3.5 interface_wrap.c 
	gcc -shared run.o interface_wrap.o -o _iptables_sim.so

run.o: iptables.o
	$(CC) -fPIC -c run.c ip_tables.o -o run.o

iptables.o:
	$(CC) $(CFLAGS) ip_tables.c -I$(IDIR)

clean:
	rm -f *.o *.so *.pyc 
	rm -f test test.tmp.c 
	rm -f interface_wrap.c iptables_sim.py
