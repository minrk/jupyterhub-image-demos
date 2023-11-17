import sys

c = get_config()  # noqa

c.JupyterHub.services = [
    {
        'name': 'launcher',
        'url': 'http://127.0.0.1:10101',
        'command': [sys.executable, './launcher.py'],
        'oauth_client_allowed_scopes': ['admin:servers!user'],
    },
]

c.JupyterHub.load_roles = [
    {
        "name": "user",
        # grant all users access to all services
        "scopes": ["access:services", "self"],
    }
]

c.JupyterHub.allow_named_servers = True
c.JupyterHub.default_url = "/services/launcher/"

from dockerspawner import DockerSpawner
from tornado import web

class ImageSelectingDockerSpawner(DockerSpawner):
    
    async def check_allowed(self, image):
        """Check if an image is allowed
        
        e.g. restricting to private registry, list of allowed images, etc.
        """
        if not image.startswith(("quay.io/jupyter/", "quay.io/jupyterhub/")):
            raise web.HTTPError(400, reason=f"Image {image} not allowed.")
        # default behavior is to check against DockerSpawner.allowed_images
        return await super().check_allowed(image)
    
    async def progress(self):
        yield {
            "message": f"Launching image {self.image}...",
            "progress": 50,
        }


c.JupyterHub.spawner_class = ImageSelectingDockerSpawner
c.DockerSpawner.prefix = "jupyter-api"

# allow connect 
c.JupyterHub.hub_ip = "0.0.0.0" # needed for containers
# connect by ip instead of hostname, so container can connect to hub
import netifaces
c.JupyterHub.hub_connect_ip = netifaces.ifaddresses("en0")[netifaces.AF_INET][0]["addr"]

# test boilerplate
c.JupyterHub.bind_url = "http://127.0.0.1:9876"
c.JupyterHub.authenticator_class = "dummy"
c.JupyterHub.tornado_settings = {"slow_spawn_timeout": 0}
c.DockerSpawner.remove = True
