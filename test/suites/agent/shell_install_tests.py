#! /usr/bin python

import os
import os.path
import sys
import json

import os
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
from autopilot.common import exception
from autopilot.common import utils
from autopilot.common.apenv import ApEnv
from autopilot.test.common.aptest import APtest
from autopilot.specifications.apspec import Apspec
from autopilot.agent.installers.InstallProviders import GitInstallProvider
from autopilot.common.asyncpool import taskpool


class ShellInstallProviderTest(APtest):
    """
    Role Spec tests
    """
    def test_shell_clone_install(self):
        stack = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf('stack_test_shell.yml'))

        repo_base_dir = '/tmp/ap_testrun1'
        self.resetdir(repo_base_dir)
        apenv = ApEnv()
        git = GitInstallProvider(apenv, "hdfs", "hadoop-base", stack, repo_base_dir)
        git.run(blocking=True, timeout=10)

        with open(os.path.join(repo_base_dir, 'autopilot/hadoop-base/hdfs/dump_stack.out')) as f:
            o = json.load(f)
            self.at(o)
            self.at(o["role_groups"])
            self.at(o["target"])

    def test_shell_clone_install_async(self):
        stack = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf('stack_test_shell.yml'))
        tc = ShellInstallProviderTest.TimeClass()

        repo_base_dir = '/tmp/ap_testrun1'
        self.resetdir(repo_base_dir)
        apenv = ApEnv()
        git = GitInstallProvider(apenv, "hdfs", "hadoop-base", stack, repo_base_dir)

        # pump run through gevent
        taskpool.spawn(git.run, args=dict(blocking=False, timeout=10))
        taskpool.spawn(tc.update_time)
        taskpool.join(timeout=10)

        self.at(tc.func_time < utils.get_utc_now_seconds())
        with open(os.path.join(repo_base_dir, 'autopilot/hadoop-base/hdfs/dump_stack.out')) as f:
            o = json.load(f)
            self.at(o)
            self.at(o["role_groups"])
            self.at(o["target"])

    def test_shell_install_fail(self):
        stack = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf('stack_test_shell.yml'))
        repo_base_dir = '/tmp/ap_testrun1'
        self.resetdir(repo_base_dir)
        apenv = ApEnv()
        stack.deploy.metafile = "meta_sh_raise_error.yml"
        git = GitInstallProvider(apenv, "hdfs", "hadoop-base", stack, repo_base_dir)
        self.assertRaises(exception.GitInstallProviderException, git.run)

    def test_install_no_such_file(self):
        stack = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf('stack_test_shell.yml'))
        repo_base_dir = '/tmp/ap_testrun1'
        self.resetdir(repo_base_dir)
        apenv = ApEnv()
        stack.deploy.metafile = "meta_sh_no_file.yml"
        git = GitInstallProvider(apenv, "hdfs", "hadoop-base", stack, repo_base_dir)
        self.assertRaises(exception.GitInstallProviderException, git.run)