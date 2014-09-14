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
from autopilot.agent.installers.InstallProviders import GitInstallProvider
from autopilot.common.asyncpool import taskpool


class ShellInstallProviderTest(APtest):
    """
    Role Spec tests
    """
    def test_shell_clone_install(self):
        (rspec, stack) = self.create_specs(rspec_file='role_test_shell.yml',
                                           sspec_file='stack_test_shell.yml')

        working_dir = '/tmp/ap_testrun1'
        self.resetdir(working_dir)
        apenv = ApEnv()
        apenv.add("target_role_group", "hdfs")
        apenv.add("target_role", "hdfs")
        apenv.add("stack", stack)
        git = GitInstallProvider(apenv, rspec.roles['hdfs'],
                                 "hdfs", stack, working_dir)
        git.run(blocking=True, timeout=10)

        with open(os.path.join(working_dir, 'dump_stack.out')) as f:
            o = json.load(f)
            self.at(o)
            self.at(o["role_groups"])
            self.at(o["target"])

    def test_shell_clone_install_async(self):
        (rspec, stack) = self.create_specs(rspec_file='role_test_shell.yml',
                                           sspec_file='stack_test_shell.yml')
        tc = ShellInstallProviderTest.TimeClass()

        working_dir = '/tmp/ap_testrun1'
        self.resetdir(working_dir)
        apenv = ApEnv()
        apenv.add("target_role_group", "hdfs")
        apenv.add("target_role", "hdfs")
        apenv.add("stack", stack)
        git = GitInstallProvider(apenv, rspec.roles['hdfs'],
                                 "hdfs", stack, working_dir)

        # pump run through gevent
        taskpool.spawn(git.run, args=dict(blocking=False, timeout=10))
        taskpool.spawn(tc.update_time)
        taskpool.join(timeout=10)

        self.at(tc.func_time < utils.get_utc_now_seconds())
        with open(os.path.join(working_dir, 'dump_stack.out')) as f:
            o = json.load(f)
            self.at(o)
            self.at(o["role_groups"])
            self.at(o["target"])

    def test_shell_install_fail(self):
        (rspec, stack) = self.create_specs(rspec_file='role_test_shell.yml',
                                           sspec_file='stack_test_shell.yml')
        working_dir = '/tmp/ap_testrun1'
        self.resetdir(working_dir)
        apenv = ApEnv()
        apenv.add("target_role_group", "hdfs")
        apenv.add("target_role", "hdfs")
        apenv.add("stack", stack)
        rspec.roles['hdfs'].deploy['script'] = "raise_error.sh"
        git = GitInstallProvider(apenv, rspec.roles['hdfs'],
                                 "hdfs", stack, working_dir)
        self.assertRaises(exception.GitInstallProviderException, git.run)

    def test_install_bad_module_async(self):
        (rspec, stack) = self.create_specs(rspec_file='role_test_shell.yml',
                                            sspec_file='stack_test_shell.yml')
        working_dir = '/tmp/ap_testrun1'
        self.resetdir(working_dir)
        apenv = ApEnv()
        apenv.add("target_role_group", "hdfs")
        apenv.add("target_role", "hdfs")
        apenv.add("stack", stack)
        rspec.roles['hdfs'].deploy['script'] = "does_not_exist.sh"
        git = GitInstallProvider(apenv, rspec.roles['hdfs'],
                                 "hdfs", stack, working_dir)

        tc = ShellInstallProviderTest.TimeClass()
        taskpool.spawn(self.assertRaises, args=dict(excClass=exception.GitInstallProviderException,
                                                    callableObj=git.run))
        taskpool.spawn(tc.update_time)
        taskpool.join(timeout=5)
        self.at(tc.func_time < utils.get_utc_now_seconds())