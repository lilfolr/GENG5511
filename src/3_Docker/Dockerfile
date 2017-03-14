FROM alpine:3.4
RUN apk add --update \
    -U iptables \
    -U ulogd \
    python \
    python-dev \
    py-pip \
    build-base \
  && pip install virtualenv scapy \
  && rm -rf /var/cache/apk/*

COPY ulogd.conf /etc/ulogd.conf
COPY iptables-save iptables-save
# Once the container is made, the following needs to be run:
# su root -c 'iptables-restore iptables-save'
# This cant be in the dockerfile - https://github.com/docker/docker/issues/1916