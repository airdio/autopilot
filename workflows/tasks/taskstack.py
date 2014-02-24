__author__ = 'sujeet'


class Taskstack(object):
    """ Holds a stack of tasks and rewinds in the opposite order added
    """
    def __init__(self,):
        self.tasks = []

    def push(self, task):
        """Adds a stack to the task stack
        """
        self.tasks.append(task)

    def rewind(self):
        """ Calls rollback on the tasks in the reverse order
        """
        for t in self.tasks[::-1]:
            t.rollback()
        self.tasks = []