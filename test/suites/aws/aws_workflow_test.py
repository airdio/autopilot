#! /usr/bin/python
#! /usr/bin/python

import unittest
import json
import os
import os.path
import sys
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
import gevent
import gevent.monkey
from autopilot.specifications.apspec import Apspec
from autopilot.specifications.wfmapper import StackMapper
from autopilot.workflows.workflowexecutor import WorkflowExecutor
from autopilot.workflows.tasks.task import TaskState
from autopilot.specifications.tasks.deployrole import DeployRole, DomainInit, StackInit
from autopilot.test.suites.aws.awstest import AWStest
# monkey patch
gevent.monkey.patch_all()


class AwsWorkflowTest(AWStest):
    """
    AWS Workflow Tests
    """
    def test_deploy_from_spec_roles_only(self):
        wf_id = self.get_unique_wf_id()
        apenv = self.get_aws_default_apenv(wf_id=wf_id)
        sspec = Apspec.load(apenv, "contoso.org",
                            "dev.marketing.contoso.org", self.openf('stack_spec2.yml'))
        workflow_state = self.get_aws_default_workflow_state()
        mapper = StackMapper(apenv=apenv, wf_id=wf_id, org="contoso.org", domain="dev.marketing.contoso.org",
                             owner="apuser", stack_spec=sspec, stack_state=workflow_state)
        ex = WorkflowExecutor(apenv=apenv, model=mapper.build_workflow())
        all_instances_ids = []
        all_sgids = []
        try:
            self.execute_workflow(ex, timeout=300)
            role_groups = workflow_state.get("stack_spec").get("materialized").get("role_groups")
            for (key, role_group) in role_groups.items():
                all_instances_ids.extend([instanced.get('instance_id') for instanced in role_group.get('instances')])
                all_sgids.extend(role_group.get("security_group_ids"))
            self.ae(3, len(all_instances_ids))
            self.ae(3, len(all_sgids))
        finally:
            json.dump(workflow_state, open('/tmp/wf_state.sz', 'w'))
            if all_instances_ids:
                self.terminate_instances_by_ids(all_instances_ids, all_sgids)

    def get_DeployRole(self, apenv, inf, wf_id, properties, workflow_state):
        return DeployRole(apenv, wf_id, inf, properties, workflow_state)

    def get_DomainInit(self, apenv, inf, wf_id, properties, workflow_state):
        return DomainInit(apenv, wf_id, inf, properties, workflow_state)

    def get_StackInit(self, apenv, inf, wf_id, properties, workflow_state):
        return StackInit(apenv, wf_id, inf, properties, workflow_state)