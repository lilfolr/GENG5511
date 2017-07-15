import iptables_sim

p=iptables_sim.in_packet()
r=iptables_sim.in_rule()

p.ttl = 10
p.src_addr = "192.168.1.3"
p.dst_addr = "192.168.1.2"
debug = 1

packet_match = iptables_sim.run_sim(p,r, debug)

from enum import Enum
from copy import deepcopy


class RuleResults(Enum):
    ACCEPT = 0
    DROP = 1
    REJECT = 2


class Rule(object):
    # Convention - None = Any value allowed
    input_device = None
    output_device = None
    protocol = None
    src = None
    dst = None
    match_chain = RuleResults.DROP  # Can either be a chain, or a final rule

    def __str__(self):
        return "{} {} {} {} {} {}".format(self.input_device,
                                          self.output_device,
                                          self.protocol,
                                          self.src,
                                          self.dst,
                                          str(self.match_chain))


class IPTables(object):
    """
    iptables instance. 
    Contains a collection of chains, each with a collection of rules.
    A list of packets can be inputted, with a list of responses
    """

    def __init__(self):
        # Start with 3 chains; INPUT FORWARD OUTPUT
        self.chains = {}
        self.base_chains = ["INPUT", "FORWARD", "OUTPUT"]
        for chain in self.base_chains:
            self.create_chain(chain)

    def create_chain(self, chain_name, default_policy=RuleResults.DROP):
        default_rule = Rule()
        default_rule.match_chain = default_policy
        self.chains[chain_name] = [deepcopy(default_rule)]  # List of rules

    def remove_chain(self, chain_name):
        if chain_name in self.base_chains:
            raise ValueError("Can not remove base chain")
        try:
            self.chains.pop(chain_name)
        except KeyError:
            print("Chain {} does not exist".format(chain_name))

    def add_chain_rule(self, chain_name, ip_rule, index_location=0):
        chain = self.chains.get(chain_name, None)
        if chain:
            chain.insert(index_location, ip_rule)
        else:
            print("Chain {} does not exist".format(chain_name))

    def remove_chain_rule(self, chain_name, index_location):
        chain = self.chains.get(chain_name, None)
        if chain:
            del chain[index_location]
        else:
            print("Chain {} does not exist".format(chain_name))

    def __str__(self):
        to_return = ""
        for chain, rules in self.chains.items():
            to_return += "CHAIN: {}\n".format(chain)
            i = 0
            for rule in rules:
                to_return += " >Rule {} {}\n".format(str(i), str(rule))
                i += 1
        return to_return