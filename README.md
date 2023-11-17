# JupyterHub image-selecting demos

Demos of selecting images

The gist:

- Spawner can receive launch parameters in two ways:
  - `user_options`, specified via the REST API or a spawn form, or
  - query parameters, via the request handler
- Spawners can decide what to do based on this information in their `.start()` method

Two examples:

1. `urlparams` allows launching a selected image purely via a URL parameter.
  Doesn't 
2. `launch-api` uses an API request to launch named servers, like a binder-lite where it assumes 'real' users and that images already exist. Could be extended to include building images, a la BinderHub itself
