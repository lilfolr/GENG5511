from docker_client import docker_client
import os, shutil


HOST_MNT_DIR = "/tmp/docker_mnt"
ACCEPT_LOG_FILE = "ulogd_accept.log"
DROP_LOG_FILE = "ulogd_drop_reject.log"
class backend(object):
    def __init__(self):
        self.current_nodes = []
        self.d_c = docker_client()
        self._clean()

    def _clean(self):
        # Clean file-shares
        try:
            shutil.rmtree(HOST_MNT_DIR)
        except Exception as e:
            os.makedirs(HOST_MNT_DIR)
        # Clean docker
        self.d_c.destroy_containers()

    def create_node(self, node_id, firewall_type):
        new_dir = os.path.join(HOST_MNT_DIR, str(node_id))
        os.makedirs(new_dir)
        print("Made dir "+new_dir)
        container_id = self.d_c.create_container(new_dir)
        self.current_nodes.append({
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

