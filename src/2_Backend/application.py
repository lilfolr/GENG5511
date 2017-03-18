from docker_client import docker_client

class backend(object):
    def __init__(self):
        self.current_nodes = []
        self.d_c = docker_client()

    def create_node(self, node_id, firewall_type):
        self.d_c.create_node()
