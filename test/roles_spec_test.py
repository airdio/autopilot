#! /usr/bin python

import os
import os.path
import sys
import yaml
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
from autopilot.test.common.aptest import APtest
from autopilot.specifications.apspec import Apspec
from autopilot.common.apenv import ApEnv
from autopilot.specifications.wfmapper import StackMapper
from autopilot.specifications.tasks.deployrole import DeployRole, DomainInit, StackInit


class RoleSpecTest(APtest):
    """
    Role Spec tests
    """
    def test_parse_role_spec(self):
        rspec = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org", self.openf('role_spec1.yml'))
        # print rspec.todict()
        self.ae(3, len(rspec.roles))

    def test_parse_min_role_spec(self):
        rspec = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org", self.openf('role_spec_min.yml'))
        # print rspec.todict()
        self.ae(3, len(rspec.roles))
        self.ae(2.0, rspec.roles["yarn"].version)

    def test_parse_stack_spec(self):
        sspec = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org", self.openf('stack_spec1.yml'))
        # print rspec.todict()
        self.ae(2, len(sspec.groups))
        self.ae(2, len(sspec.groups["hdfs"].rolerefs))
        self.at(sspec.groups["hdfs"].rolerefs == ["hdfs", "yarn"])
        self.ae(1, sspec.groups["hdfs"].order)
        self.ae(5, sspec.groups["hdfs"].instanced['count'])
        self.ae(None, sspec.groups["zk"].order)

    def test_stack_mapper(self):
        rspec = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org", self.openf('role_spec2.yml'))
        sspec = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org", self.openf('stack_spec2.yml'))
        wf_id = self.get_unique_wf_id()
        properties = dict(properties=dict(aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
                                          aws_secret_access_key=os.environ["AWS_SECRET_KEY"]))
        infd = {'aws': properties}
        apenv = self.get_default_apenv(wf_id=wf_id, infd=infd)
        workflow_state = self.get_default_workflow_state()
        mapper = StackMapper(apenv=apenv, wf_id=wf_id, org="contoso.org", domain="dev.marketing.contoso.org",
                             owner="apuser", stack_spec=sspec, roles_spec=rspec,
                             stack_state=workflow_state)
        workflow = mapper.build_workflow()
        self.ae(4, len(workflow.groupset.groups))
        gp = filter(lambda g: g.groupid=="parallel_deploy_roles", workflow.groupset.groups).pop()
        self.ae(2, len(gp.tasks))

    def get_DeployRole(self, apenv, inf, wf_id, properties, workflow_state):
        return DeployRole(apenv, wf_id, inf, properties, workflow_state)

    def get_DomainInit(self, apenv, inf, wf_id, properties, workflow_state):
        return DomainInit(apenv, wf_id, inf, properties, workflow_state)

    def get_StackInit(self, apenv, inf, wf_id, properties, workflow_state):
        return StackInit(apenv, wf_id, inf, properties, workflow_state)


