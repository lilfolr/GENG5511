Files
=====

**interface.i** -  Interface file allowing `swig` to facilitate calling `c` with `python`  
**iptables_sim_interface.py** - The python file other files should call to invoke iptables stuff  
**makefile** - makefile to compile iptables & swig's conversions  
**run.c** - root `c` file. Calls iptables functions 

Compilation
===========

Pre-requisits
-------------
You will need the following installed:  
`python2.7`  
`python2.7-dev` - Headers located in `/usr/include/python2.7` [if not, change the makefile]  

Compiling
---------
Compile by running  
`make`

