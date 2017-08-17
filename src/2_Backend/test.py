import unittest
from application import Application

class applicationTest(unittest.TestCase):

    def test_create_rule(self):
        a = Application()
        a.create_node(1)

        for chain, rules in a.get_node_firewall(1).chains.items():
            chain = {
                "id" : chain,
                "label": chain,
                "children": []
            }
            i = 0
            for rule in rules:
                child = {
                    "id": i,
                    "label": "-i {} -o {} -p {} -s {} -d {} -j {}".format(rule.input_device, rule.output_device, 
                                                                        rule.protocol, rule.src, rule.dst, rule.match_chain)
                }
                chain["children"].append(child)
                i +=1