import docker
"""
containers will talk through ports - Host:Client 
"""


class docker_client(object):
    def __init__(self):
        self.client = docker.from_env()
        self.containers = {}

    def _get_images(self):
        return self.client.list()

    def create_container(self, mnt_dir, type=None):
        """
        Creates docker container. Returns container id
        """
        #TODO: check mnt_dir exists
        volume_key = {mnt_dir:{'bind': '/mnt/vol1', 'mode': 'rw'}}
        new_container = self.client.containers.run('test-ip', command='bin/sh', detach=True, tty=True, volumes=volume_key, privileged=True)
        print("Running install commands")
        new_container.exec_run("sh -c 'iptables-restore<iptables-save' -s /bin/sh", tty=True, privileged=True,) # Setup initial iptables rules
        new_container.exec_run("sh -c 'ulogd' -s /bin/sh", tty=True, detach=True, privileged=True,)             # Setup iptables logging
        self.containers[new_container.id] = new_container
        return new_container.id

    def destroy_container(self, container_id):
        self.client.containers.get(container_id).remove(force=True)

    def destroy_containers(self):
        for container in self.client.containers.list():
            self.destroy_container(container.id)