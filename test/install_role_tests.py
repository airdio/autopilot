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
from autopilot.agent.tasks.InstallRole import InstallRole
from autopilot.common.asyncpool import taskpool
from autopilot.workflows.tasks.task import TaskState


class InstallRoleTest(APtest):
    """
    Install Role task tests
    """
    def test_install_role_task(self):
        stack = self.create_specs(rspec_file='role_test_python.yml',
                                   sspec_file='stack_test_python.yml')
        test_dir = '/tmp/test_install_role_task/'
        properties = {
            "target": "hdfs",
            "stack": stack,
            "install_dirs": {
                "root_dir": test_dir,
                "current_file": "current",
                "versions_dir": "versions"
            }
        }
        # print stack.groups.get('hdfs').roles
        wf_id = "InstallRole_test_wf_id"
        task = InstallRole(self.get_default_apenv(wf_id), wf_id, None, properties, None)
        task.run()
        self.ae(TaskState.Done, task.result.state, "Task should be in done state")
        working_dir = os.path.join(test_dir, stack.name, "hdfs", "hdfs", "versions", "2.4")
        with open(os.path.join(working_dir, 'dump_stack.out')) as f:
            o = json.load(f)
            self.at(o)
            # self.at(o["org"])
            # self.at(o["type"])