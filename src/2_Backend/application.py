import os, sys
import random
import logging
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
            returns 
            ( 
                (src: blocked_out?), //add forward at some stage
                (dst: blocked_in?)
            )
        """
        import random
        for k,v in packets.items():
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
    node_id = int((node_id-mod) / 256)

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
