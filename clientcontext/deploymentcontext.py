#! /usr/bin python

from autopilot.workflows.workflowtype import WorkflowType
from autopilot.clientcontext.stack import Stack
from autopilot.clientcontext.role import Role
from autopilot.cloud.aws.awscloud import AWScloud
from autopilot.vcs.vcs import Vcs


class DeploymentContext(object):
    """ Represents a deployment context
    """
    def __init__(self, apenv, contextd, cloud_configd=None):
        """
        contextd -> context dictionary
        cloud_configd -> cloud config dictionary
        """
        self.apenv = apenv
        if cloud_configd is None:
            self.cloud = DeploymentContext._get_default_cloud()
        else:
            self.cloud = DeploymentContext._resolve_cloud(cloud_configd)

        self.workflow_type = WorkflowType.Deployment
        self.stack = self._get_stack(contextd)

    def _get_stack(self, contextd):
        stackd = contextd["stack"]
        #print stackd
        vcsd = stackd.get("vcs")
        if vcsd is None:
            vcs = Vcs(self.apenv.get("vcs_target"),
                      "{0}{1}".format(self.apenv.get("vcs_url"), stackd["name"]))
        else:
            vcs = Vcs(vcsd.get("target"), vcsd.get("url"))
        return Stack(stackd["name"], stackd["version"],
                           DeploymentContext._resolve_roles(stackd.get("roles", {})),
                           vcs)

    @staticmethod
    def _resolve_roles(role_list=[]):
        roles = {}
        for r in role_list:
            roles[r["name"]] = Role(r["name"], r["version"], r.get("instances", 1))
        return roles

    @staticmethod
    def _resolve_cloud(configd):
        #for now return aws always
        return AWScloud.resolve_cloud(configd)

    @staticmethod
    def _get_default_cloud():
        # todo
        # for now no-op. need to implement correctly
        return AWScloud("", "")



