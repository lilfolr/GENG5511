FROM alpine:3.4

MAINTAINER Leighton Lilford<lrlilford@gmail.com>

RUN apk add --update \
    -U iptables \
    -U ulogd \
    python3 \
    python-dev \
    py-pip \
    build-base \
  && pip install virtualenv \
  && rm -rf /var/cache/apk/*

COPY ulogd.conf /etc/ulogd.conf
COPY iptables-save iptables-save

RUN virtualenv env -p python3 && source env/bin/activate && pip install pypacker
# Once the container is made, the following needs to be run:
# su root -c 'iptables-restore iptables-save'
# This cant be in the dockerfile - https://github.com/docker/docker/issues/1916
