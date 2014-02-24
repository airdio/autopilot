#! /usr/bin python

import os
import os.path
import sys
import yaml
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
from autopilot.workflows.workflowtype import WorkflowType
from autopilot.test.aptest import APtest
from autopilot.clientcontext.deploymentcontext import DeploymentContext
from autopilot.common.apenv import ApEnv


class DeploymentContextTest(APtest):
    """ Deployment context tests
    """
    def setUp(self):
        self.context_file = ""

    def test_parse_deployment(self):
        apenv = ApEnv()
        context = DeploymentContext(apenv, yaml.load(self.openf("deployment.yml")), yaml.load(self.openf("aws.yml")))
        self.ae(WorkflowType.Deployment,  context.workflow_type)
        self.ae("awstest1", context.stack.name)
        self.ae(3, len(context.stack.roles))
        self.ae("role1", context.stack.roles["role1"].name)
        self.ae(2, context.stack.roles["role1"].instances)
        self.ae("1.0", context.stack.roles["role1"].version)
        self.ae("git", context.stack.vcs.target)
        self.ae("http://www.github.com/stack1/", context.stack.vcs.url)

        # roles
        self.ae("role2", context.stack.roles["role2"].name)
        self.ae(1, context.stack.roles["role2"].instances, 1)
        self.ae("1.1", context.stack.roles["role2"].version, "1.1")

        self.ae("role3", context.stack.roles["role3"].name)
        self.ae(1, context.stack.roles["role3"].instances)
        self.ae("2.0", context.stack.roles["role3"].version)

        #provider
        self.ae("<class 'autopilot.cloud.aws.awscloud.AWScloud'>", str(type(context.cloud)))
        self.ae("987654321BA", context.cloud.aws_access_key_id)
        self.ae("123456789AB", context.cloud.aws_secret_access_key)

    def test_parse_min_deployment(self):
        apenv = ApEnv({"vcs_target": "git", "vcs_url": "http://www.github.com/"})
        context = DeploymentContext(apenv, yaml.load(self.openf("deployment_min.yml")))
        self.ae(WorkflowType.Deployment,  context.workflow_type)
        self.ae("awstest1", context.stack.name)
        self.ae(1, len(context.stack.roles))
        self.ae("role1", context.stack.roles["role1"].name)
        self.ae(1, context.stack.roles["role1"].instances)
        self.ae("1.0", context.stack.roles["role1"].version)
        self.ae("git", context.stack.vcs.target)
        self.ae("http://www.github.com/awstest1", context.stack.vcs.url)

        #provider
        #self.ae("<class 'autopilot.cloud.awscloud.AWScloud'>", str(type(context.cloud)))
        #self.ae("987654321BA", context.cloud.aws_access_key_id)
        #self.ae("123456789AB", context.cloud.aws_secret_access_key)