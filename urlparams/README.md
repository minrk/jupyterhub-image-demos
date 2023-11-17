# Launching images by url parameter

Key points:

- JupyterHub passes the tornado RequestHandler that initiated a spawn to the Spawner prior to Spawner.start
- Spawner.start may use `handler.get_argument` to check if an image
- Spawner can limit what images are allowed as appropriate, to avoid launching arbitrary images

As a result, the following links can be used to launch specific images:

- http://localhost:9999/hub/spawn?image=quay.io/jupyterhub/singleuser:4
- http://localhost:9999/hub/spawn?image=quay.io/jupyter/scipy-notebook
- http://localhost:9999/hub/spawn?image=notallowed

Caveats:

- if a server is already running, the request will be redirected to a running server, even if the image doesn't match

Named servers can be used to mitigate this, but requires some API calls to work properly.
