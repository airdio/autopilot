#! /usr/bin/env python
__author__ = 'sujeet'

import os
import os.path
import sys
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')

from autopilot.workflows.tasks.task import Task
from autopilot.workflows.tasks.taskstack import Taskstack
from autopilot.test.aptest import APtest


class TaskstackTest(APtest):
    """ Tests test stack
    """
    verifyl = []

    def test_stack(self):
        TaskstackTest.verifyl = []
        task1 = TouchfileTask("file1.log")
        task1.run()
        task2 = TouchfileTask("file2.log")
        task2.run()
        self.at(os.path.isfile(task1.file_name))
        self.at(os.path.isfile(task2.file_name))
        ts = Taskstack(self._statusf)
        ts.push(task1)
        ts.push(task2)
        ts.rewind()
        self.af(os.path.isfile(task1.file_name))
        self.af(os.path.isfile(task2.file_name))
        self.ae(TaskstackTest.verifyl[0], task2.name)
        self.ae(TaskstackTest.verifyl[1], task1.name)

    def _statusf(self, t, s):
        if s == Task.StatusRollback:
            TaskstackTest.verifyl.append(t.name)


class TouchfileTask(Task):
    def __init__(self, file_name):
        Task.__init__(self, "Touchfile", None, None)
        self.file_name = file_name

    def run(self):
        f = open(self.file_name, 'w')
        f.close()

    def rollback(self):
        os.remove(self.file_name)