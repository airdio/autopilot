#! /usr/bin/python
from autopilot.agent.tasks.InstallRole import InstallRole

# {
# "type": "stack",
# "target": "role_group1",
# "stack": {
#   "name": "mystack",
#   "role_groups": {},
#   }
# }


class Handler(object):
    """
    Entry point into handling incoming requests.
    """
    def __init__(self, request):
        self.request = request

    def process(self):
        pass


class StackHandler(Handler):
    """
    Handle stack install
    """
    def __init__(self, request):
        Handler.__init__(self, request)

    def process(self):
        pass

Name = "InstallRole"
ROOT_DIR = "/var/lib/autopilot/"
CURRENT_FILE = "current"
VERSIONS_DIR = "versions"

