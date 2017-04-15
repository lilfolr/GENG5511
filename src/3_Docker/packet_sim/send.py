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

psock = psocket.SocketHndl(mode=psocket.SocketHndl.MODE_LAYER_3, timeout=10)

def read_in():
	while True:
        with open(IN_FIFO) as fifo:
            yield fifo.read()


def send_packet(network, packet_type, src_ip, dst_ip, sport, dport, data):
	# network: tcp/udp/icmp
	if network.lower()=="ip":
		if packet_type=="tcp":	
			print ("Sending")
			ip.IP(src_s="127.0.0.1", dst_s="127.0.0.1") + tcp.TCP(dport=80)
			psock.send(ip.bin(), dst=ip.dst_s)
	else:
		raise Exception("Not implemented")

for x in read_in():
	send_packet("ip", "tcp", "10.1.1.1", "10.1.1.2", None, None, None)
