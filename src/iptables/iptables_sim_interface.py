import iptables_sim

p=iptables_sim.in_packet()
r=iptables_sim.in_rule()

p.ttl = 10
p.src_addr = "192.168.1.3"
p.dst_addr = "192.168.1.2"

packet_match = iptables_sim.run_sim(p,r)