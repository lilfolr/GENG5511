# Support protocols:
# 'HTTP',
# 'HTTPS',
# 'FTP',
# 'SMTP',
# 'DNS',
# 'DHCP'
import os, time
from pypacker.layer3.ip import IP
from pypacker.layer3.icmp import ICMP

IN_FIFO = "/mnt/vol1/IN"

def read_in():
	while True:
        with open(IN_FIFO) as fifo:
            yield fifo.read()


def send_packet(network, packet_type, src_ip, dst_ip, sport, dport, data):
	# network: tcp/udp/icmp
	if network.lower()=="icmp":
		 # Type 8 = Echo
		ip = IP(src_s=src_ip, dst_s=dst_ip, p=1) + \
		ICMP(type=8) + \
		ICMP.Echo(id=1, seq=1, body_bytes=b"Echo")
	else:
		raise Exception("Not implemented")

print(read_in())

