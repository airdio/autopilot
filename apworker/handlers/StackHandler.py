#! /usr/bin/python
from autopilot.apworker.tasks.InstallRole import InstallRole

# {
# "type": "stack",
# "target": "role_group1"
# "stack": {
# "stack_spec": {},
# "materialized": {"domain":{}, "stack":{}, "role_groups": {}},
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

