#! /usr/bin python

import os
import os.path
import sys
sys.path.append(os.environ['AUTOPILOT_DEV'] + '/../')
from autopilot.test.aptest import APtest
from autopilot.workflows.workflowcontext import WorkflowContext

class DeploymentContextTest(APtest):
    """ Deployment context tests
    """
    def setUp(self):
        self.context_file = ""

    def test_parse(self):
        context = WorkflowContext("deployment.yml", "aws.yml")
        self.ae(WorkflowContext.Type.Deployment,  context.type)
        self.ae("awstest1", context.stack.name)
        self.ae(3, len(context.stack.roles))
        self.ae("role1", context.stack.roles["role1"].name)
        self.ae(2, context.stack.roles["role1"].instances)
        self.ae("1.0", context.stack.roles["role1"].version)
        self.ae("git", context.stack.vcs)
        self.ae("http://www.github.com/stack1/", context.stack.vcs_url)

        # roles
        self.ae("role2", context.stack.roles["role2"].name)
        self.ae(1, context.stack.roles["role2"].instances, 1)
        self.ae("1.1", context.stack.roles["role2"].version, "1.1")

        self.ae("role3", context.stack.roles["role3"].name)
        self.ae(1, context.stack.roles["role3"].instances)
        self.ae("2.0", context.stack.roles["role3"].version)

        #provider
        self.ae("<class 'autopilot.cloud.awscloud.AWScloud'>", str(type(context.cloud)))
        self.ae("987654321BA", context.cloud.aws_access_key_id)
        self.ae("123456789AB", context.cloud.aws_secret_access_key)