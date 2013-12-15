__author__ = 'sujeet'
from autopilot.workflows.tasks.task import Task


class Taskstack(object):
    """ Manages tasks and rewinds in the opposite order added
    """
    def __init__(self, statusf = None):
        self.status_function = statusf
        self.tasks = []

    def push(self, task):
        """Adds a stack to the task stack
        """
        self.tasks.append(task)
        if self.status_function is not None:
            self.status_function(task, Task.StatusAdded)

    def rewind(self):
        """ Calls rollback on the tasks in the reverse order
        """
        for t in self.tasks[::-1]:
            t.rollback()
            if self.status_function is not None:
                self.status_function(t, Task.StatusRollback)
        self.tasks = []