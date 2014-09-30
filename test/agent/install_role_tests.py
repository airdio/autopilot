#! /usr/bin python

import os
import os.path
import sys
import json

import os
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
from autopilot.test.common.aptest import APtest
from autopilot.common import exception
from autopilot.common import utils
from autopilot.common.apenv import ApEnv
from autopilot.agent.tasks.InstallRoleTask import InstallRoleTask
from autopilot.common.asyncpool import taskpool
from autopilot.workflows.tasks.task import TaskState
from autopilot.protocol.message import Message
from autopilot.agent.handlers.stacks import StackDeployHandler


class InstallRoleTest(APtest):
    """
    Install Role task tests
    """
    def test_install_role_task(self):
        rspec, stack = self.create_specs(rspec_file='role_test_python.yml',
                                         sspec_file='stack_test_python.yml')
        test_dir = '/tmp/test_install_role_task/'
        self.rmdir(os.path.join(test_dir, stack.name))
        properties = {
            "stack": stack,
            "target_role_group": "hdfs",
            "target_role": stack.groups.get("hdfs").roles[0],
            "install_dirs": {
                "root_dir": test_dir,
                "current_file": "current",
                "versions_dir": "versions"
            }
        }
        # print stack.groups.get('hdfs').roles
        wf_id = "InstallRole_test_wf_id"
        task = InstallRoleTask(self.get_default_apenv(wf_id), wf_id, None, properties, None)
        task.run()

        self.ae(TaskState.Done, task.result.state, "Task should be in done state")
        working_dir = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "versions", "2.4")
        with open(os.path.join(working_dir, 'dump_stack.out')) as f:
            o = json.load(f)
            self.at(o)
            self.at(o["role_groups"])
            self.at(o["target"])

        current_file_path = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "current")
        with open(current_file_path) as f:
            curr_ver = f.readline()
            self.ae("2.4", curr_ver, "new current version is 2.4")

    def test_install_role_task_async(self):
        rspec, stack = self.create_specs(rspec_file='role_test_python.yml',
                                         sspec_file='stack_test_python.yml')
        test_dir = '/tmp/test_install_role_task/'
        self.rmdir(os.path.join(test_dir, stack.name))
        properties = {
            "stack": stack,
            "target_role_group": "hdfs",
            "target_role": stack.groups.get("hdfs").roles[0],
            "install_dirs": {
                "root_dir": test_dir,
                "current_file": "current",
                "versions_dir": "versions"
            }
        }

        tc = InstallRoleTest.TimeClass()
        # pump run through gevent
        wf_id = "InstallRole_test_wf_id"
        task = InstallRoleTask(self.get_default_apenv(wf_id), wf_id, None, properties, None)
        taskpool.spawn(task.run)
        taskpool.spawn(tc.update_time)
        taskpool.join(timeout=10)
        self.at(tc.func_time < utils.get_utc_now_seconds())

        self.ae(TaskState.Done, task.result.state, "Task should be in done state")
        working_dir = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "versions", "2.4")
        with open(os.path.join(working_dir, 'dump_stack.out')) as f:
            o = json.load(f)
            self.at(o)
            self.at(o["role_groups"])
            self.at(o["target"])

        current_file_path = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "current")
        with open(current_file_path) as f:
            curr_ver = f.readline()
            self.ae("2.4", curr_ver, "new current version is 2.4")

    def test_install_role_git_clone_error(self):
        rspec, stack = self.create_specs(rspec_file='role_test_python.yml',
                                         sspec_file='stack_test_python.yml')
        test_dir = '/tmp/test_install_role_task/'
        self.rmdir(os.path.join(test_dir, stack.name))

        properties = {
            "stack": stack,
            "target_role_group": "hdfs",
            "target_role": stack.groups.get("hdfs").roles[0],
            "install_dirs": {
                "root_dir": test_dir,
                "current_file": "current",
                "versions_dir": "versions"
            }
        }

        stack.groups.get("hdfs").roles[0].deploy["git"] = "https://badurl"
        wf_id = "InstallRole_test_wf_id"
        task = InstallRoleTask(self.get_default_apenv(wf_id), wf_id, None, properties, None)
        task.run()
        self.ae(TaskState.Error, task.result.state, "Task should be error")
        self.ae(exception.GitInstallProviderException, type(task.result.exceptions[0]))
        current_file_path = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "current")
        self.af(os.path.exists(current_file_path))

    def test_install_role_update(self):
        rspec, stack = self.create_specs(rspec_file='role_test_python.yml',
                                         sspec_file='stack_test_python.yml')
        test_dir = '/tmp/test_install_role_task/'
        self.rmdir(os.path.join(test_dir, stack.name))
        properties = {
            "stack": stack,
            "target_role_group": "hdfs",
            "target_role": stack.groups.get("hdfs").roles[0],
            "install_dirs": {
                "root_dir": test_dir,
                "current_file": "current",
                "versions_dir": "versions"
            }
        }
        # Install version 2.4 first
        wf_id = "InstallRole_test_wf_id"
        task = InstallRoleTask(self.get_default_apenv(wf_id), wf_id, None, properties, None)
        task.run()
        self.ae(TaskState.Done, task.result.state, "Task should be in done state")
        working_dir = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "versions", "2.4")
        current_file_path = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "current")
        self.at(len(self.listfiles(working_dir)) > 0)
        with open(current_file_path) as f:
            curr_ver = f.readline()
            self.ae("2.4", curr_ver, "First current version should be 2.4")

        #update to version 2.5 and install again
        stack.groups.get("hdfs").roles[0].version = "2.5"
        task = InstallRoleTask(self.get_default_apenv(wf_id), wf_id, None, properties, None)
        task.run()

        # verify if new version is installed
        self.ae(TaskState.Done, task.result.state, "Task should be in done state")
        working_dir = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "versions", "2.5")
        self.at(len(self.listfiles(working_dir)) > 0, "new version 2.5 files are installed")

        with open(current_file_path) as f:
            curr_ver = f.readline()
            self.ae("2.5", curr_ver, "new current version is 2.5")

        # verify if original version is still there
        self.ae(TaskState.Done, task.result.state, "Task should be in done state")
        working_dir = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "versions", "2.4")
        self.at(len(self.listfiles(working_dir)) > 0, "new version 2.4 files are still there")

    def test_install_role_update_error(self):
        rspec, stack = self.create_specs(rspec_file='role_test_python.yml',
                                         sspec_file='stack_test_python.yml')
        test_dir = '/tmp/test_install_role_task/'
        self.rmdir(os.path.join(test_dir, stack.name))
        properties = {
            "stack": stack,
            "target_role_group": "hdfs",
            "target_role": stack.groups.get("hdfs").roles[0],
            "install_dirs": {
                "root_dir": test_dir,
                "current_file": "current",
                "versions_dir": "versions"
            }
        }
        # Install version 2.4 first
        wf_id = "InstallRole_test_wf_id"
        task = InstallRoleTask(self.get_default_apenv(wf_id), wf_id, None, properties, None)
        task.run()
        self.ae(TaskState.Done, task.result.state, "Task should be in done state")
        working_dir = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "versions", "2.4")
        current_file_path = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "current")
        self.at(len(self.listfiles(working_dir)) > 0)
        with open(current_file_path) as f:
            curr_ver = f.readline()
            self.ae("2.4", curr_ver, "First current version should be 2.4")

        #update to version 2.5 and bad url and install again
        stack.groups.get("hdfs").roles[0].version = "2.5"
        stack.groups.get("hdfs").roles[0].deploy["git"] = "https://badurl"
        task = InstallRoleTask(self.get_default_apenv(wf_id), wf_id, None, properties, None)
        task.run()

        # verify that the task fails and the old version is still the current
        self.ae(TaskState.Error, task.result.state, "Task should be error state")
        working_dir = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "versions", "2.4")
        current_file_path = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "current")
        self.at(len(self.listfiles(working_dir)) > 0, "old version 2.4 files are not removed")

        with open(current_file_path) as f:
            curr_ver = f.readline()
            self.ae("2.4", curr_ver, "current version is 2.4")

    def test_stack_handler(self):
        rspec, stack = self.create_specs(rspec_file='role_test_python.yml',
                                         sspec_file='stack_test_python.yml')
        test_dir = '/tmp/test_install_role_task/'
        self.rmdir(os.path.join(test_dir, stack.name))

        apenv = ApEnv({
                "root_dir": test_dir,
                "current_file": "current",
                "versions_dir": "versions"
        })

        msg = Message(type="stack-deploy",
                      headers={"domain": "dev.contoso.org"},
                      data={"target_role_group": "hdfs",
                            "stack": stack})

        handler = StackDeployHandler(apenv=apenv, message_type=msg.type)
        future = handler.process(message=msg)
        response_message = future.get(timeout=30)
        current_file_path = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "current")
        self.at(response_message, "Response messae should not be None")
        with open(current_file_path) as f:
            curr_ver = f.readline()
            self.ae("2.4", curr_ver, "new current version is 2.4")