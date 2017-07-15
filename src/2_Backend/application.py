from database_client import database_client
import os, shutil, random


class Application(object):
    def __init__(self):
        self.current_nodes = []
        self.db = database_client()

    def create_node(self, node_id, firewall_type):
        node_mac, node_ip = _generate_mac_ip(node_id)       # Stored here - wont 'really' be used (we will fake it)
        new_dir = os.path.join(HOST_MNT_DIR, str(node_id))
        os.makedirs(new_dir)
        print("Made dir "+new_dir)
        container_id = self.d_c.create_container(new_dir)
        self.current_nodes.append({
            "mac": node_mac,
            "ip": node_id,
        	"node_id": node_id,
        	"container_id": "container_id",
        	"firewall_type": firewall_type
    	})

    def destroy_node(self, node_id):
    	container_ids = [x['container_id'] for x in self.current_nodes if x['node_id']==node_id]
    	if len(container_ids) !=1 :
    		raise EnvironmentError("Number of nodes matching id not 1. "+str(len(container_ids)))
    	else:
    		container_id = container_ids[0]
    		self.d_c.destroy_container(container_id)

    def cleanup(self):
        """
        Cleanup before removing application
        """
        pass

