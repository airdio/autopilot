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
from autopilot.specifications.apspec import Apspec
from autopilot.agent.tasks.InstallRoleTask import InstallRoleTask
from autopilot.workflows.tasks.task import TaskState
from autopilot.protocol.message import Message
from autopilot.agent.handlers.stackdeployhandler import StackDeployHandler


class InstallRoleTest(APtest):
    """
    Install Role task tests
    """
    def test_install_role_task(self):
        stack = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf('stack_test_python.yml'))
        working_dir = '/tmp/test_install_role_task/'
        status_dir = '/tmp/test_install_role_task_status/hadoop-base/hdfs/'
        self.resetdir(working_dir)
        self.resetdir(status_dir)
        properties = {
            "stack": stack,
            "target_role_group": "hdfs",
            "target_role": stack.groups.get("hdfs").roles[0],
            "role_working_dir": working_dir,
            "role_status_dir": status_dir
        }

        wf_id = "InstallRole_test_wf_id"
        task = InstallRoleTask(self.get_default_apenv(wf_id), wf_id, None, properties, None)
        task.run()
        self.ae(TaskState.Done, task.result.state, "Task should be in done state")

        with open(os.path.join(working_dir, 'autopilot/hadoop-base/hdfs/dump_stack.out')) as f:
            o = json.load(f)
            self.at(o)
            self.at(o["role_groups"])

        current_file_path = os.path.join(status_dir, "current")
        with open(current_file_path) as f:
            stack_name = f.readline().strip()
            self.ae("hadoop-base", stack_name)

    def test_install_role_git_clone_error(self):
        stack = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf('stack_test_python.yml'))
        stack.deploy.git = "http://badurl"
        working_dir = '/tmp/test_install_role_task/'
        status_dir = '/tmp/test_install_role_task_status/hadoop-base/hdfs/'
        self.resetdir(working_dir)
        self.resetdir(status_dir)
        properties = {
            "stack": stack,
            "target_role_group": "hdfs",
            "target_role": stack.groups.get("hdfs").roles[0],
            "role_working_dir": working_dir,
            "role_status_dir": status_dir
        }

        wf_id = "InstallRole_test_wf_id"
        task = InstallRoleTask(self.get_default_apenv(wf_id), wf_id, None, properties, None)
        task.run()

        self.ae(TaskState.Error, task.result.state, "Task should be error")
        self.ae(exception.GitInstallProviderException, type(task.result.exceptions[0]))

    def test_stack_handler(self):
        stack = Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org",
                            self.openf('stack_test_python.yml'))
        working_dir = '/tmp/test_install_role_task/'
        status_dir = '/tmp/test_install_role_task_status/'

        apenv = ApEnv(dict(WORKING_DIR=working_dir, STATUS_DIR=status_dir))

        msg = Message(type="stack-deploy",
                      headers={"domain": "dev.contoso.org"},
                      data={"target_role_group": "hdfs", "stack": stack})

        handler = StackDeployHandler(apenv=apenv, message_type=msg.type)
        future = handler.process(message=msg)
        response_message = future.get(timeout=30)
        self.at(response_message, "Response message should not be None")

        current_file_path = os.path.join(status_dir, "hadoop-base/hdfs/current")
        with open(current_file_path) as f:
            stack_name = f.readline().strip()
            self.ae("hadoop-base", stack_name)