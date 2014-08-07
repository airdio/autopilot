#! /usr/bin python

import os
import os.path
import sys
import json

import os
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
from autopilot.common import exception
from autopilot.common.apenv import ApEnv
from autopilot.test.common.aptest import APtest
from autopilot.specifications.apspec import Apspec
from autopilot.apworker.installers.InstallProviders import GitInstallProvider


class InstallProviderTest(APtest):
    """
    Role Spec tests
    """
    def test_clone(self):
        (rspec, stack) = self._create_specs(rspec_file='role_testrun1.yml',
                                            sspec_file='stack_testrun1.yml')

        working_dir = '/tmp/ap_testrun1'
        self.resetdir(working_dir)
        apenv = ApEnv()
        apenv.add("target", "unittest1_role")
        apenv.add("stack", stack)
        git = GitInstallProvider(apenv, rspec.roles['hdfs'],
                                 "hdfs", "stack1", working_dir)
        git.run()

    def test_clone_fail(self):
        (rspec, stack) = self._create_specs(rspec_file='role_testrun1.yml',
                                            sspec_file='stack_testrun1.yml')

        working_dir = '/tmp/ap_testrun1'
        self.resetdir(working_dir)
        apenv = ApEnv()
        apenv.add("target", "unittest1_role")
        apenv.add("stack", stack)
        rspec.roles['hdfs'].deploy['git'] = "https//bad_url"
        git = GitInstallProvider(apenv, rspec.roles['hdfs'],
                                 "hdfs", "stack1", working_dir)
        self.assertRaises(exception.GitInstallProviderException, git.run)

    def _create_specs(self, rspec_file, sspec_file):
        rspec = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf(rspec_file))
        sspec = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf(sspec_file))
        return (rspec, {
                 "stack_spec": sspec,
                 "materialized": {"domain": {}, "stack": {}, "role_groups": {}},
                })