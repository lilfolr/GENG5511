import random
from database_client import DatabaseClient


class Application(object):
    def __init__(self):
        self.current_nodes = {}
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
            "firewall_type": firewall_type
        }

    def destroy_node(self, node_id):
        """Deletes Node"""
        self.current_nodes.pop(node_id)

    def cleanup(self):
        """
        Cleanup before removing application
        """
        pass


def _generate_mac_ip(node_id):
    mod = node_id % 255
    node_id -= mod * 255
    return ("%02x:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        mod,
        node_id
    ),
            "10.%02x.%02x.%02x" % (
                random.randint(0, 255),
                mod,
                node_id
            ))
