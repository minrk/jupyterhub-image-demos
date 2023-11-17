from pathlib import Path
import json
import os
from urllib.parse import quote, urlparse

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from jupyterhub.services.auth import HubOAuthCallbackHandler, HubOAuthenticated
from jupyterhub.utils import url_path_join

from tornado import web
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
import jinja2

here = Path(__file__).parent.resolve()
templates_dir = here / "templates"


async def api_request(hub_auth, path, method="GET", token=None, **kwargs):
    url = hub_auth.api_url + path

    headers = kwargs.setdefault("headers", {})
    if token is None:
        token = hub_auth.api_token
    headers.setdefault("Authorization", f"token {token}")
    req = HTTPRequest(
        url,
        method=method,
        **kwargs,
    )
    r = await AsyncHTTPClient().fetch(req)
    response_text = r.body.decode("utf8", "replace")
    if not response_text:
        return None
    else:
        return json.loads(response_text)


images = {
    "base": "quay.io/jupyter/base-notebook",
    "scipy": "quay.io/jupyter/scipy-notebook",
}


class MainPage(HubOAuthenticated, web.RequestHandler):
    @web.authenticated
    def get(self):
        tpl = self.settings["jinja_env"].get_template("launcher.html.j2")
        self.write(tpl.render(images=images.keys(), user=self.current_user))


class LaunchHandler(HubOAuthenticated, web.RequestHandler):
    @web.authenticated
    async def get(self, server_name):
        try:
            image = images[server_name]
        except KeyError:
            raise web.HTTPError(404, f"No such server: {server_name}")
        
        server_name_url = quote(server_name)

        user_name = self.current_user["name"]
        user_name_url = quote(user_name)
        token = self.hub_auth.get_token(self)
        user_model = await api_request(self.hub_auth, f"/users/{user_name_url}", token=token)
        user_servers = user_model["servers"]
        server_model = user_servers.get(server_name)
        if server_model is None or server_model["stopped"]:
            # not running, launch the named server with the requested image
            await api_request(
                self.hub_auth,
                f"/users/{user_name_url}/servers/{server_name_url}",
                method="POST",
                body=json.dumps({"image": image}),
                token=token,
            )
        else:
            # already running, will redirect to spawn-pending page
            pass
        self.redirect(f"/hub/spawn-pending/{user_name_url}/{server_name_url}")


def main():
    base_url = os.environ["JUPYTERHUB_SERVICE_PREFIX"]
    jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(searchpath=templates_dir),
        )
    jinja_env.globals["base_url"] = base_url
    app = web.Application(
        [
            (base_url, MainPage),
            (
                url_path_join(
                    base_url, "oauth_callback"
                ),
                HubOAuthCallbackHandler,
            ),
            (
                url_path_join(base_url, "/launch/(.*)"),
                LaunchHandler,
            ),
        ],
        cookie_secret=os.urandom(32),
        jinja_env=jinja_env,
    )

    http_server = HTTPServer(app)
    url = urlparse(os.environ["JUPYTERHUB_SERVICE_URL"])

    http_server.listen(url.port, url.hostname)

    IOLoop.current().start()


if __name__ == "__main__":
    main()
