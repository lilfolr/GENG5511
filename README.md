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

### Installations
// as sudo
`apt-get update`
`apt-get upgrade -y`

`apt-get install build-essential libpcre3-dev -y`
`apt-get install python3-dev python-pip -y`
`apt install swig -y`
`pip install virtualenv`

`git clone https://github.com/lilfolr/geng5511.git`

### Compile iptables
`cd geng5511/src/iptables`  
`make`

### Install webserver
`cd ../2_backend/`
`virtualenv env -p python3`
`. ./env/bin/activate`
`pip install -r requirements.txt`

### Running webserver:
`python webserver.py`

### Docker container [if used]

build with `docker build -t alpine_ipt .`
