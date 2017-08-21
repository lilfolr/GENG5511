import os, io
import sys
import random
import logging
import csv

from database_client import DatabaseClient

if os.name == 'nt':
    base_index = '..\\1_GUI\\'
    sys.path.append(os.path.abspath(os.path.join(sys.path[0], "..\\iptables\\")))
else:
    base_index = '../1_GUI/'
    sys.path.append(os.path.abspath(os.path.join(sys.path[0], "../iptables/")))
import iptables_sim_interface as ip
from iptables_sim import in_packet, in_rule
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

    def get_sim_template(self):
        """returns string template for packet simulation"""
        output = io.StringIO()
        csvWriter = csv.writer(output)
        csvWriter.writerow(['packet_id', 'network_layer', 'application_layer', 'source_port', 
                            'destination_port', 'source_ip', 'destination_ip', 'ttl'])
        i=1
        for node in self.current_nodes:
            csvWriter.writerow([str(i), 'icmp', '', '', '', self.current_nodes[node]['ip'], '', '2'])
            i += 1
        str_out = output.getvalue()
        output.close()
        return str_out


    def simulate(self, packets):
        """
            packets: [{
                    "NL": "ICMP",
                    "AL": "",
                    "SP": 22,
                    "DP": 22, 
                    "SN": 0,
                    "DN": 1,
                    "TTL": 33,
                }]
            returns 
            ( 
                (src: (A, B, R)), //add forward at some stage
                (dst: (A, B, R))
            )
        """
        for k, v in packets.items():
            packet = in_packet()
            packet.ttl = v['TTL']
            packet.protocol = 1  # icmp
            packet.dst_addr = self.current_nodes[v['DN']]["ip"]
            packet.src_addr = self.current_nodes[v['SN']]["ip"]
            src_node_out_chain = self.current_nodes[v['SN']]["firewall"].chains["OUTPUT"]
            dst_node_in_chain = self.current_nodes[v['DN']]["firewall"].chains["INPUT"]

            # Check output
            logger.info("Checking Server node")
            out_res = self._traverse_chain(v['SN'], src_node_out_chain, packet, 0)
            # TODO: check forward

            # check input                        
            if out_res == "ACCEPT":
                in_res = self._traverse_chain(v['DN'], dts_node_out_chain, packet, 0)
            else:
                in_res = "None"
            yield (
                (v['SN'], (int(out_res=="ACCEPT"), int(out_res=="DROP"), int(out_res=="REJECT"))),
                (v['DN'], (int(in_res=="ACCEPT"), int(in_res=="DROP"), int(in_res=="REJECT")))
            )  

    def _traverse_chain(self, node, chain, packet, recursive_count):
        """
        Returns "DROP"; "ACCEPT"; or "REJECT"
        """
        if recursive_count>500:
            logger.warning("Recursion detected - dropping")
            return "DROP"       # Prevent looped chains breaking the system
        for rule in chain:
            ip_rule = in_rule()
            ip_rule.protocol = 1 # icmp
            ip_rule.src_addr = rule.src if rule.src else ""
            ip_rule.dst_addr = rule.dst if rule.dst else ""  # TODO: 'ANY' is probably a mask
            ip_rule.indev = rule.input_device if rule.input_device else ""
            ip_rule.outdev = rule.output_device if rule.output_device else ""
            if ip.check_rule_packet(ip_rule, packet):
                if rule.match in ip.BASE_RULES:
                    return rule.match
                else:
                    try:
                        next_chain = self.current_nodes[v['SN']]["firewall"].chains[rule.match]
                        return self._traverse_chain(node, next_chain, packet, recursive_count+1)
                    except KeyError:
                        logger.warning("Chain {} can't be found".format(rule.match))
                        return "DROP"
            else:
                continue
        # Shouldn't happen as chains always end on a catch-all rule
        logger.warning("Shouldn't be here... defaulting to drop")
        return "DROP"


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
