import os
import zipfile
import webbrowser
import requests
from requests.auth import HTTPBasicAuth

from .serverbase import ServerBase


class TokenNetworkAccessManager:
    def __init__(self, url, username, password):
        self.url = url.strip("/")
        self.token = None
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(username, password)

    def set_token_in_header(self):
        if self.token is None:
            self.get_token()
        self.session.headers.update({"X-XSRF-TOKEN": self.token})

    def request(self, url, data=None, method="get", headers={}):
        self.set_token_in_header()
        method = getattr(self.session, method.lower())
        resp = method(url, headers=headers, data=data)
        resp.raise_for_status()
        return resp

    def get_token(self):
        signinUrl = self.url + "/eng/catalog.signin"
        self.session.post(signinUrl)
        self.token = self.session.cookies.get("XSRF-TOKEN")
        self.session.headers.update({"X-XSRF-TOKEN": self.token})


class GeonetworkServer(ServerBase):

    def __init__(self, url="", node="srv"):
        super().__init__()
        self.url = url
        self.node = node
        self._nam = TokenNetworkAccessManager(self.url, "", "")

    @staticmethod
    def servertype():
        return "geonetwork"

    def set_credentials(self, username, password):
        super().set_credentials(username, password)      
        self._nam = TokenNetworkAccessManager(self.url, username, password)

    def request(self, url, data=None, method="get", headers={}):
        return self._nam.request(url, data, method, headers)

    def publish_layer_metadata(self, meffile):
        self._nam.set_token_in_header()
        url = self.api_url() + "/records"
        headers = {"Accept": "application/json"}
        params = {"uuidProcessing", "OVERWRITE"}

        print(meffile, url)
        with open(meffile, "rb") as f:
            files = {"file": f}
            r = self._nam.session.post(url, files=files, headers=headers)
            r.raise_for_status()

    def api_url(self):
        return self.url + "/%s/api" % self.node

    def delete_metadata(self, uuid):
        url = self.api_url() + "/records/" + uuid
        self.request(url, method="delete")


