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

Running the application:

* `cd src/2_Backend`<br/>
* `source env/bin/activate` - Assuming you've got a virtualenv setup, with requirements installed </br>
* `python webserver.py`

* build container with `docker build -t alpine_ipt .`
