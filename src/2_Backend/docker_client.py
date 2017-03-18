import docker


class docker_client(object):
    def __init__(self):
        self.client = docker.from_env()
        self.containers = {}

    def _get_images(self):
        return self.client.list()

    def create_node(self, type=None):
        """
        Creates docker container. Returns container id
        """
        new_container = self.client.containers.run('test-ip', command='bin/sh', detach=True, tty=True)
        self.containers[new_container.id] = new_container
        return new_container.id
