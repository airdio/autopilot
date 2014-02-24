#! /usr/bin/env python
__author__ = 'sujeet'

import os
import os.path
import sys
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
from autopilot.common.apenv import ApEnv
from autopilot.test.common.tasks import TouchfileTask

from autopilot.workflows.tasks.task import Task
from autopilot.workflows.tasks.taskstack import Taskstack
from autopilot.test.aptest import APtest


class TaskstackTest(APtest):
    """ Tests test stack
    """
    def test_stack(self):
        apenv = ApEnv()
        task1 = TouchfileTask(apenv, "wf_1", "file1.log")
        task1.run(self._statusf)
        task2 = TouchfileTask(apenv, "wf_1", "file2.log")
        task2.run(self._statusf)
        self.at(os.path.isfile(task1.file_name))
        self.at(os.path.isfile(task2.file_name))
        ts = Taskstack()
        ts.push(task1)
        ts.push(task2)
        ts.rewind()
        self.af(os.path.isfile(task1.file_name))
        self.af(os.path.isfile(task2.file_name))

    def _statusf(self, t):
        pass