# Launching images via the JupyterHub API

This example creates a very basic Launcher service, presenting a choice of images to launch.
The service uses the JupyterHub API to launch 

Key points:

- launcher uses JupyterHub OAuth to retrieve API credentials, user info
- the Launcher service requests permissions to launch servers on behalf of the user (i.e. it does _not_ have permission to manage servers on its own, only granted on a per-user basis)
- the Spawner accepts an `image` argument via the `user_options`
- the spawner can validate which images are acceptable before launching
- the launcher service makes an API request to launch a _named_ server with the given image, so users can have multiple images at once
- after requesting the launch, the user is redirected to the spawn-pending page to await the launch, so the service doesn't need to implement progress, etc.

This is like a very lightweight BinderHub, with the following assumptions:

- starting from built images, rather than including a build step
- users are authenticated with jupyterhub, not anonymous 

Anonymous users and building images are the two main things that BinderHub implements. If you already have a build step, this example can be used as-is for the launch step, following the build.
