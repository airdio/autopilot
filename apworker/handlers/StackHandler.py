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
    def __init__(self, request):
        self.request = request

    def process(self):
        pass


class StackHandler(Handler):
    def __init__(self, request):
        Handler.__init__(self, request)

    def process(self):

