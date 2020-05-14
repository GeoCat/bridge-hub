import sys
from pathlib import Path

from lxml import objectify

# config file name
_CONFIG_XML = "bridgeapi.xml"


class ApiConfig:
    def __init__(self, config_file=_CONFIG_XML):
        cfg_path = Path(config_file)
        if not cfg_path.is_absolute():
            cfg_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
            cfg_path = cfg_dir / cfg_path
        uri = cfg_path.as_uri()
        self._root = objectify.parse(uri).getroot()

    @property
    def host(self):
        return (self._root.host.text or "").strip()

    @property
    def port(self):
        try:
            return int(self._root.port.text or "")
        except ValueError:
            return 0
