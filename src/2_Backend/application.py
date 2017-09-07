import os, io
import sys
import random
import logging
import csv
import json
from copy import deepcopy

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
logger.setLevel(logging.DEBUG)

class Application(object):
    def __init__(self):
        self.current_nodes = {}
        self.node_connections = []
        self.db = DatabaseClient()
        self.sim_packets = []  # [ip.in_packet]
        # 3 result files: Per packet; Per node per packet & per rule per node per packet
        self.sim_results = {'packet_results':[],'node_results':[],'rule_results':[]}  # 

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


    def simulate(self, packets=None):
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
        logger.debug("Starting Simulation")
        if not packets:
            packets = self.sim_packets
        logger.debug("Packets: "+str(packets))
        for packet in packets:
            logger.info("{} -> {}".format(packet.src_addr, packet.dst_addr))
            src_node_id = [x for x,v in self.current_nodes.items() if v['ip']==packet.src_addr][0]
            dst_node_id = [x for x,v in self.current_nodes.items() if v['ip']==packet.dst_addr][0]
            src_node_out_chain = self.current_nodes[src_node_id]["firewall"].chains["OUTPUT"]
            dst_node_in_chain = self.current_nodes[dst_node_id]["firewall"].chains["INPUT"]
            # Check output
            logger.info("Checking Server node")
            str_protocol = ip.reverse_lookup_protocol(packet.protocol)
            out_res = self._traverse_chain(src_node_id, src_node_out_chain, packet, 0, "OUTPUT")
            packet_result = {
                "Packet_ID":        "-1",
                "Source_IP":        packet.src_addr,
                "Destination_IP":   packet.dst_addr,
                "Protocol":         str_protocol,
                "Result":           out_res,
            }
            self.sim_results["node_results"].append({
                'Packet_ID':    '-1',
                'Hop_Number':   '1',
                'Node_IP':      packet.src_addr, 
                'Direction':    'Output', 
                'Protocol':     str_protocol, 
                'Result':       out_res
            })
            
            # TODO: check forward

            # check input
            if out_res == "ACCEPT":
                logger.info("Checking Client node")
                in_res = self._traverse_chain(dst_node_id, dst_node_in_chain, packet, 0, "INPUT")
                self.sim_results["node_results"].append({
                    'Packet_ID':    '-1',
                    'Hop_Number':   '2',
                    'Node_IP':      packet.dst_addr, 
                    'Direction':    'Input', 
                    'Protocol':     str_protocol, 
                    'Result':       in_res
                })
                packet_result["Result"] = in_res
            else:
                in_res = "None"
            self.sim_results["packet_results"].append(packet_result)
            yield (
                (src_node_id, (int(out_res=="ACCEPT"), int(out_res=="DROP"), int(out_res=="REJECT"))),
                (dst_node_id, (int(in_res=="ACCEPT"), int(in_res=="DROP"), int(in_res=="REJECT")))
            )  

    def set_sim_packets(self, packet_csv):
        next(packet_csv)  # Skip header row
        row_n = 0
        for row in packet_csv:      # ['1', 'icmp', '', '', '', '10.190.0.0', '', '2']
            if not self._valid_sim_packet_row(row):
                raise Exception("Row {} is invalid".format(str(row_n+1)))
            print (row)     
            packet = in_packet()
            packet.ttl      = int(row[7])
            packet.protocol = ip.lookup_protocol(row[1])
            packet.src_addr = row[5]
            packet.dst_addr = row[6]
            self.sim_packets.append(packet)
    def _valid_sim_packet_row(self,row):
        if len(row)!=8:
            return False
        for r in row:
            if not isinstance(r, str):
                return False
        if not ip.lookup_protocol(row[1]):
            return False
        return True

    def _traverse_chain(self, node, chain, packet, recursive_count, chain_name=""):
        """
        Returns "DROP"; "ACCEPT"; or "REJECT"
        """
        logger.info("Running for chain "+chain_name)
        # 'Packet_ID', 'Node_IP', 'Chain', 'Protocol', 'Rule', 'Result'
        rule_result = {"Packet_ID": "-1", "Chain": chain_name, "Node_IP": self.current_nodes[node]["ip"], 
                       "Protocol": ip.reverse_lookup_protocol(packet.protocol)}
        if recursive_count>500:
            logger.warning("Recursion loop detected - dropping")
            return "DROP"       # Prevent looped chains breaking the system
        for rule in chain:
            ip_rule = in_rule()
            prot_no = ip.lookup_protocol(rule.protocol)
            ip_rule.protocol = prot_no if prot_no else 1  #TODO: Allow for 'ANY' protocol
            ip_rule.src_addr = rule.src if rule.src else ""
            ip_rule.dst_addr = rule.dst if rule.dst else ""  # TODO: 'ANY' is probably a mask
            ip_rule.indev = rule.input_device if rule.input_device else ""
            ip_rule.outdev = rule.output_device if rule.output_device else ""
            ip_rule_str = "P:{} S:{} D:{} iD:{} oD:{}".format(ip.reverse_lookup_protocol(ip_rule.protocol), ip_rule.src_addr, ip_rule.dst_addr, ip_rule.indev, ip_rule.outdev)
            logger.debug("Checking Packet {} against Rule {}".format("S: "+packet.src_addr+" D:"+packet.dst_addr, ip_rule_str))
            if ip.check_rule_packet(ip_rule, packet):
                if rule.match in ip.BASE_RULES:
                    tmp_res = deepcopy(rule_result)
                    tmp_res["Rule"] = ip_rule_str
                    tmp_res["Result"] = "DROP"
                    self.sim_results["rule_results"].append(tmp_res)
                    return rule.match
                else:
                    try:
                        next_chain = self.current_nodes[node]["firewall"].chains[rule.match]
                        tmp_res = deepcopy(rule_result)
                        tmp_res["Rule"] = ip_rule_str
                        tmp_res["Result"] = next_chain
                        self.sim_results["rule_results"].append(tmp_res)
                        return self._traverse_chain(node, next_chain, packet, recursive_count+1, rule.match)
                    except KeyError:
                        logger.warning("Chain {} can't be found".format(rule.match))
                        tmp_res = deepcopy(rule_result)
                        tmp_res["Rule"] = "Chain not found"
                        tmp_res["Result"] = "DROP"
                        self.sim_results["rule_results"].append(tmp_res)
                        return "DROP"
            else:
                continue
        # Shouldn't happen as chains always end on a catch-all rule
        logger.warning("Shouldn't be here... defaulting to drop")
        tmp_res = deepcopy(rule_result)
        tmp_res["Rule"] = "Default chain policy"
        tmp_res["Result"] = "DROP"
        self.sim_results["rule_results"].append(tmp_res)
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
