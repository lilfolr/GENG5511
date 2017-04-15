
from pypacker import psocket
from pypacker.layer3.ip import IP
from pypacker.layer3.icmp import ICMP
from pypacker.layer4.tcp import TCP
from pypacker.layer4.udp import UDP

IN_FIFO = "/mnt/vol1/IN"

# Example input to fifo: 
# "ip;tcp;;10.1.1.1;10.1.1.2;12;80;"
psock = psocket.SocketHndl(mode=psocket.SocketHndl.MODE_LAYER_3, timeout=10)


def read_in():
    while True:
        with open(IN_FIFO) as fifo:
            yield fifo.read()


def send_packet(network, packet_type, application_type, src_ip, dst_ip, sport, dport, data, ttl=5):
    """

    :param network:             Layer 3: IP | ICMP
    :param packet_type:         Layer 4: TCP| UDP
    :param application_type:    Layer 5: DHCP| DNS| HTTP|
    :param src_ip:
    :param dst_ip:
    :param sport:
    :param dport:
    :param data:
    :param ttl:
    :return:
    """
    packet = None
    sport = int(sport)
    dport = int(dport)
    ttl = int(ttl)
    if network.lower() == "ip":
        if packet_type.lower() == "tcp":
            print("Sending tcp")
            packet = IP(src_s=src_ip, dst_s=dst_ip, ttl=ttl, p=6) + TCP(sport=sport, dport=dport)
        if packet_type.lower() == "udp":
            print("Sending udp")
            packet = IP(src_s=src_ip, dst_s=dst_ip, ttl=ttl, p=17) + UDP(sport=sport, dport=dport)
    elif network.lower() == "icmp":
        packet = IP(src_s=src_ip, dst_s=dst_ip, ttl=ttl, p=1) + ICMP(type=8) + ICMP.Echo(id=123, seq=1, body_bytes=b"ping")

    if packet:
        psock.send(packet.bin(), dst=packet.dst_s)
    else:
        raise Exception("Not implemented")


for x in read_in():
    a=x.split(";")[0:8]
    try:
        send_packet(*a)
    except:
        print ("Error sending")
