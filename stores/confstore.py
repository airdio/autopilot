

import os
import importlib


class ConfStore(object):

    def __init__(self):
        self.conf_file = os.environ.get("AUTOPILOT_CONF_FILE", "settings.py")
        self.settings = self._load()

    def _load(self):
        return importlib.import_module(self.conf_file)

