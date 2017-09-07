import unittest
from application import Application
import logging, sys
from iptables_sim import in_packet, in_rule
import iptables_sim_interface as ip

class ApplicationTest(unittest.TestCase):
    def setUp(self):
        self.a = Application()
        self.a.create_node(1)

    def test_basic_run(self):
        log = logging.getLogger("simulator.test")
        self._add_rule()
        packet = self._set_packet()
        list(self.a.simulate())

    def _add_rule(self):
        node_id = 1
        firewall = self.a.get_node_firewall(node_id)
        ip_rule = ip.Rule()
        ip_rule.input_device = None
        ip_rule.output_device = None
        ip_rule.protocol = "ICMP"
        ip_rule.src =  self.a.current_nodes[1]["ip"]
        ip_rule.dst =  self.a.current_nodes[1]["ip"]
        ip_rule.match_chain = "ACCEPT"
        firewall.add_chain_rule("OUTPUT", ip_rule, 0)
        return

    def _set_packet(self):
        packet = in_packet()
        packet.ttl = 1
        packet.protocol = ip.lookup_protocol("icmp")
        packet.src_addr = self.a.current_nodes[1]["ip"]
        packet.dst_addr = self.a.current_nodes[1]["ip"]
        self.a.sim_packets.append(packet)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger( "simulator.test").setLevel( logging.DEBUG )
    unittest.main()


