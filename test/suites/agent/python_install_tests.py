#! /usr/bin python
import sys
import os
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
import json
from autopilot.common.asyncpool import taskpool
from autopilot.common import exception
from autopilot.common import utils
from autopilot.common.apenv import ApEnv
from autopilot.test.common.aptest import APtest
from autopilot.specifications.apspec import Apspec
from autopilot.agent.installers.InstallProviders import GitInstallProvider


class PythonInstallProviderTest(APtest):
    """
    Role Spec tests
    """
    def test_python_clone_install(self):
        stack = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf('stack_test_python.yml'))

        repo_base_dir = '/tmp/ap_testrun1'
        self.resetdir(repo_base_dir)
        apenv = ApEnv()
        git = GitInstallProvider(apenv, "hdfs", "hadoop-base", stack, repo_base_dir)
        git.run(blocking=True, timeout=10)

        with open(os.path.join(repo_base_dir, 'autopilot/hadoop-base/hdfs/dump_stack.out')) as f:
            o = json.load(f)
            self.at(o)
            self.at(o["role_groups"])

    def test_python_clone_install_async(self):
        # verify that if git install does not block other async events
        # if functions are pumped through gevent
        stack = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf('stack_test_python.yml'))
        tc = PythonInstallProviderTest.TimeClass()

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

    def test_python_clone_fail(self):
        stack = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf('stack_test_python.yml'))

        working_dir = '/tmp/ap_testrun1'
        self.resetdir(working_dir)
        apenv = ApEnv()
        stack.deploy.git = "https//bad_url"
        git = GitInstallProvider(apenv, "hdfs", "hadoop-base", stack, working_dir)
        self.assertRaises(exception.GitInstallProviderException, git.run)

    def test_python_install_fail(self):
        stack = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf('stack_test_python.yml'))

        working_dir = '/tmp/ap_testrun1'
        self.resetdir(working_dir)
        apenv = ApEnv()
        stack.deploy.metafile = "meta_raise_error.yml"
        git = GitInstallProvider(apenv, "hdfs", "hadoop-base", stack, working_dir)
        self.assertRaises(exception.GitInstallProviderException, git.run)

    def test_python_install_no_install_function(self):
        stack = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf('stack_test_python.yml'))
        working_dir = '/tmp/ap_testrun1'
        self.resetdir(working_dir)
        apenv = ApEnv()
        stack.deploy.metafile = "meta_bad_module.yml"
        git = GitInstallProvider(apenv, "hdfs", "hadoop-base", stack, working_dir)
        self.assertRaises(exception.GitInstallProviderException, git.run)

    def test_python_install_no_metafile(self):
        stack = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf('stack_test_python.yml'))

        repo_base_dir = '/tmp/ap_testrun1'
        self.resetdir(repo_base_dir)
        apenv = ApEnv()
        stack.deploy.metafile = "meta_non_existent.yml"
        git = GitInstallProvider(apenv, "hdfs", "hadoop-base", stack, repo_base_dir)
        git.run(blocking=True, timeout=10)

        with open(os.path.join(repo_base_dir, 'autopilot/hadoop-base/hdfs/dump_stack.out')) as f:
            o = json.load(f)
            self.at(o)
            self.at(o["role_groups"])

    def test_python_install_default_metafile(self):
        stack = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf('stack_test_python.yml'))

        repo_base_dir = '/tmp/ap_testrun1'
        self.resetdir(repo_base_dir)
        apenv = ApEnv()
        stack.deploy.metafile = "meta_non_existent.yml"
        git = GitInstallProvider(apenv, "hdfs", "hadoop-base", stack, repo_base_dir)
        git.run(blocking=True, timeout=10)

        with open(os.path.join(repo_base_dir, 'autopilot/hadoop-base/hdfs/dump_stack.out')) as f:
            o = json.load(f)
            self.at(o)
            self.at(o["role_groups"])