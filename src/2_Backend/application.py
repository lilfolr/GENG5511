import os
import sys
import random
import logging
import random

from database_client import DatabaseClient

if os.name == 'nt':
    base_index = '..\\1_GUI\\'
    sys.path.append(os.path.abspath(os.path.join(sys.path[0], "..\\iptables\\")))
else:
    base_index = '../1_GUI/'
    sys.path.append(os.path.abspath(os.path.join(sys.path[0], "../iptables/")))
import iptables_sim_interface as ip

logger = logging.getLogger(__name__)


class Application(object):
    def __init__(self):
        self.current_nodes = {}
        self.node_connections = []
        self.db = DatabaseClient()

    def create_node(self, node_id, firewall_type="IPTables"):
        """
        Creates new node.
        Returns node id
        """
        if node_id in self.current_nodes:
            raise ValueError("Node ID taken")
        mac_ad, ip_ad = _generate_mac_ip(node_id)
        self.current_nodes[node_id] = {
            "mac": mac_ad,
            "ip": ip_ad,
            "firewall_type": firewall_type,
            "firewall": ip.IPTables()
        }

    def destroy_node(self, node_id):
        """Deletes Node"""
        self.current_nodes.pop(node_id)

    def connect_nodes(self, node_1, node_2):
        if node_1 not in self.current_nodes or node_2 not in self.current_nodes:
            raise ValueError("Invalid Node IDs")
        if (node_1, node_2) in self.node_connections or (node_2, node_1) in self.node_connections:
            logger.warning("Nodes already connected")
        else:
            self.node_connections.append((node_1, node_2))

    def get_node_firewall(self, node_id):
        return self.current_nodes[node_id]["firewall"]

    def simulate(self, packets):
        """
            packets: [{
                    "NL": "TCP",
                    "AL": "",
                    "SP": 22,
                    "DP": 22, 
                    "SN": 0,
                    "DN": 1,
                    "TTL": 33,
                }]
            returns 
            ( 
                (src: blocked_out?), //add forward at some stage
                (dst: blocked_in?)
            )
        """
        for k, v in packets.items():
            # packet = ip.in_packet()
            # packet.ttl = v['TTL']
            # packet.protocol = 1  # icmp
            # packet.dst_addr = self.current_nodes[v['DN']]["ip"]
            # packet.src_addr = self.current_nodes[v['SN']]["ip"]
            src_node_out_chain = self.current_nodes[v['SN']]["firewall"].chains["OUTPUT"]
            dst_node_in_chain = self.current_nodes[v['DN']]["firewall"].chains["INPUT"]

            # Check output
            for rule in src_node_out_chain:
                ip_rule = ip.in_rule()
                ip_rule.protocol = 1 # icmp
                ip_rule.src_addr = if rule['src']
                ip_rule.dst_addr = 
                ip_rule.indev = 
                ip_rule.outdev = 
                if rule_match


# typedef struct in_rules{
#     int protocol;
#     char* src_addr;
#     char* dst_addr;
#     char* indev;
#     char* outdev;
# } in_rule;



            # forward_rule

            # check forward
            # check input
            yield (
                (v['DN'], bool(random.getrandbits(1))),
                (v['SN'], bool(random.getrandbits(1)))
            )

    def cleanup(self):
        """
        Cleanup before removing application
        """
        pass


def _generate_mac_ip(node_id):
    mod = node_id % 256
    node_id = int((node_id - mod) / 256)

    return ("%02x:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        node_id,
        mod,
    ),
            "10.{}.{}.{}".format(
                random.randint(0, 255),
                node_id,
                mod
            ))
