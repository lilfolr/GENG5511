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
        volume_key = {mnt_dir:{'bind': '/mnt/vol1', 'mode': 'rw'}}
        new_container = self.client.containers.run('test-ip', command='bin/sh', detach=True, tty=True, volumes=volume_key, privileged=True)
        self.containers[new_container.id] = new_container
        return new_container.id

    def destroy_container(self, container_id):
        self.client.containers.get(container_id).kill()

    def destroy_containers(self):
        for container in self.client.containers.list():
            self.destroy_container(container.id)