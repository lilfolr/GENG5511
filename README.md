[![Build Status](https://travis-ci.com/lilfolr/GENG5511.svg?token=Ysa8e5rvdwixpp3ztsqW&branch=master)](https://travis-ci.com/lilfolr/GENG5511)
GENG5511
========

Program parts:

GUI
---
- Provides a UI

Backend
-------
- All the functionality of the application
- Responds to reqs from the GUI
- Manages the containers

Containers
----------
- Docker containers
- 1 container per node
- Respond to backend reqs.

iptables
--------
- Contains modified iptables source
- Used for simulating firewall configs

Requirements
------------
* Python 3.5 [python3.5]
* Python 3.5 headers [python3.5-dev]

Install & Run:
--------------

### Compile iptables
`cd src/iptables`  
`make`

### Run webserver
`cd src/2_Backend`  
`source env/bin/activate` - Assuming you've got a virtualenv setup, with requirements installed  
`python webserver.py`

### Docker container [if used]

build with `docker build -t alpine_ipt .`
