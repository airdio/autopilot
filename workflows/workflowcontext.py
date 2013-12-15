#! /usr/bin python

import yaml
from autopilot.workflows.Stack import Stack, Role
from autopilot.cloud.cloud import Cloud
from autopilot.cloud.awscloud import AWScloud


class WorkflowContext(object):
    """ Represents a deployment context
    """

    class Type(object):
        Deployment = 1

    def __init__(self, context_file, cloud_config=None):
        self.stack = None
        if cloud_config is None:
            self.cloud = WorkflowContext._get_default_cloud()
        else:
            self.cloud = WorkflowContext._resolve_cloud(cloud_config)

        self.type = WorkflowContext.Type.Deployment
        self._resolve_context_file(context_file)

    def _resolve_context_file(self, context_file):
        wd = yaml.load(open(context_file)).get("workflow")
        self.type = wd["workflow_type"]
        stackd = wd["stack"]
        #print stackd
        self.stack = Stack(stackd["name"], stackd["version"],
                           WorkflowContext._resolve_roles(stackd.get("roles", {})),
                           stackd["vcs"], stackd["vcs_url"])

    @staticmethod
    def _resolve_roles(role_list=[]):
        roles = {}
        for r in role_list:
            roles[r["name"]] = Role(r["name"], r["version"], r.get("instances", 1))
        return roles

    @staticmethod
    def _resolve_cloud(cloud_config):
        #for now return aws always
        return AWScloud.resolve_cloud(cloud_config)

    @staticmethod
    def _get_default_cloud():
        # todo
        # for now no-op. need to implement correctly
        return AWScloud("", "")



