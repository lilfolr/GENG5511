import iptables_sim
from collections import OrderedDict
# p=iptables_sim.in_packet()
# r=iptables_sim.in_rule()

# p.ttl = 10
# p.src_addr = "192.168.1.3"
# p.dst_addr = "192.168.1.2"
debug = 1

# packet_match = iptables_sim.run_sim(p,r, debug)

from enum import Enum
from copy import deepcopy


class Rule(object):
    # Convention - None = Any value allowed
    input_device = None
    output_device = None
    protocol = None
    src = None
    dst = None
    match_chain = "DROP"  # Can either be a chain, or a final rule

    def __str__(self):
        return "{} {} {} {} {} {}".format(self.input_device,
                                          self.output_device,
                                          self.protocol,
                                          self.src,
                                          self.dst,
                                          str(self.match_chain))

BASE_RULES = ["ACCEPT", "REJECT", "DROP"]
BASE_CHAINS = ["INPUT", "FORWARD", "OUTPUT"]
class IPTables(object):
    """
    iptables instance. 
    Contains a collection of chains, each with a collection of rules.
    A list of packets can be inputted, with a list of responses
    """

    def __init__(self):
        # Start with 3 chains; INPUT FORWARD OUTPUT
        self.chains = OrderedDict()
        self.base_chains = BASE_CHAINS
        self.base_rules  = BASE_RULES
        for chain in self.base_chains:
            self.create_chain(chain)
        for chain in self.base_rules:
            self.create_chain(chain, chain)

    def create_chain(self, chain_name, default_policy="DROP"):
        default_rule = Rule()
        default_rule.match_chain = default_policy
        self.chains[chain_name] = [deepcopy(default_rule)]  # List of rules

    def remove_chain(self, chain_name):
        if chain_name in self.base_chains + self.base_rules:
            raise ValueError("Can not remove base chain/rule")
        try:
            self.chains.pop(chain_name)
        except KeyError:
            print("Chain {} does not exist".format(chain_name))

    def add_chain_rule(self, chain_name, ip_rule, index_location=0):
        if chain_name in self.base_rules:
            raise ValueError("Can not add rules to a base rule")
        chain = self.chains[chain_name]
        if chain:
            chain.insert(index_location, ip_rule)
        else:
            raise ValueError("Chain {} does not exist".format(chain_name))

    def remove_chain_rule(self, chain_name, index_location):
        if chain_name in self.base_rules:
            raise ValueError("Can not remove rules from a base rule")
        chain = self.chains.get(chain_name, None)
        if chain:
            if index_location==len(chain)-1:
                raise ValueError("Can not remove the default rule")
            del chain[index_location]
        else:
            raise ValueError("Chain {} does not exist".format(chain_name))
        if len(chain)==0:
            self.create_chain(chain_name)
        

    def __str__(self):
        to_return = ""
        for chain, rules in self.chains.items():
            to_return += "CHAIN: {}\n".format(chain)
            i = 0
            for rule in rules:
                to_return += " >Rule {} {}\n".format(str(i), str(rule))
                i += 1
        return to_return

def check_rule_packet(rule, packet):
    return iptables_sim.run_sim(packet, rule, debug)

def lookup_protocol(protocol_name):
    # See botton of run.c
    if protocol_name.lower() == 'icmp':
        return 1
    return None
