import requests
import json

class ServerBase:
    def __init__(self):
        self._warnings = []
        self._errors = []
        self.username = None
        self.password = None

    def log_info(self, text):
        pass

    def log_warning(self, text):
        self._warnings.append(text)

    def log_error(self, text):        
        self._errors.append(text)

    def reset_log(self):
        self._warnings = []
        self._errors = []

    def logged_info(self):
        return self._warnings, self._errors

    def set_credentials(self, username, password):
        self.username = username
        self.password = password

    def get_credentials(self):
        return self.username, self.password

    def request(self, url, data=None, method="get", headers=None, files=None):
        headers = headers or {}
        files = files or {}
        username, password = self.get_credentials()
        req_method = getattr(requests, method.lower())
        if isinstance(data, dict):
            data = json.dumps(data)
            headers["content-type"] = "application/json"
        self.log_info("Making %s request to '%s'" % (method, url))
        r = req_method(
            url, headers=headers, files=files, data=data, auth=(username, password)
        )
        r.raise_for_status()
        return r

    def validateGeodataBeforePublication(self, errors, toPublish):
        pass

    def validateMetadataBeforePublication(self, errors):
        pass
