c = get_config()  # noqa

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

    async def start(self):
        handler = self.handler
        image_param = handler.get_argument("image", None)
        self.log.info(f"Selecting image={image_param}")
        if image_param:
            self.image = await self.check_allowed(image_param)
        return await super().start()


c.JupyterHub.spawner_class = ImageSelectingDockerSpawner
c.DockerSpawner.image = "quay.io/jupyterhub/singleuser:4.0"
c.DockerSpawner.prefix = "jupyter-url"

# allow connect 
c.JupyterHub.hub_ip = "0.0.0.0" # needed for containers
# connect by ip instead of hostname, so container can connect to hub
import netifaces
c.JupyterHub.hub_connect_ip = netifaces.ifaddresses("en0")[netifaces.AF_INET][0]["addr"]

# test boilerplate
c.JupyterHub.bind_url = "http://127.0.0.1:9999"
c.JupyterHub.authenticator_class = "dummy"
c.JupyterHub.tornado_settings = {"slow_spawn_timeout": 0}
c.DockerSpawner.remove = True
