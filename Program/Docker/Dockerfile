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
