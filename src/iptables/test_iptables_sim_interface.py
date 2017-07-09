import unittest
import ip


class TestRules(unittest.TestCase):
    def test_create_rule(self):
        ip.Rule()


class TestChains(unittest.TestCase):
    def setUp(self):
        self.chain = ip.IPTables()

    def test_default(self):
        self.assertCountEqual(["INPUT", "OUTPUT", "FORWARD"], list(self.chain.chains.keys()))

    def test_create_chain(self):
        chain_name = "New Chain"
        self.chain.create_chain(chain_name)
        self.assertCountEqual(["INPUT", "OUTPUT", "FORWARD", chain_name], list(self.chain.chains.keys()))

    def test_remove_chain(self):
        chain_name = "New Chain"
        self.chain.create_chain(chain_name)
        self.chain.remove_chain(chain_name)
        self.assertCountEqual(["INPUT", "OUTPUT", "FORWARD"], list(self.chain.chains.keys()))

    def test_remove_main_chain(self):
        for chain_name in ["INPUT", "OUTPUT", "FORWARD"]:
            with self.assertRaises(ValueError):
                self.chain.remove_chain(chain_name)

    def test_add_chain_rule(self):
        chain_name = "New Chain"
        new_rule = ip.Rule()
        new_rule.src = "1.1.1.1"
        new_rule.match_chain = ip.RuleResults.ACCEPT
        self.chain.create_chain(chain_name)
        self.chain.add_chain_rule("INPUT", new_rule)
        self.assertEqual(new_rule, self.chain.chains["INPUT"][0])
        self.assertNotEqual(new_rule, self.chain.chains["INPUT"][1])

    def test_remove_chain_rule(self):
        chain_name = "New Chain"
        new_rule = ip.Rule()
        new_rule.src = "1.1.1.1"
        new_rule.match_chain = ip.RuleResults.ACCEPT
        self.chain.create_chain(chain_name)
        self.chain.add_chain_rule("INPUT", new_rule)
        self.chain.remove_chain_rule("INPUT", 1)
        self.assertEqual(new_rule, self.chain.chains["INPUT"][0])


if __name__ == '__main__':
    unittest.main()
