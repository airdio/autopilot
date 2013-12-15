__author__ = 'sujeet'


class Task(object):
    """Base class for Tasks
    """
    StatusAdded = 0
    StatusRollback = 1

    def __init__(self, name):
        self.name = name

    def run(self):
        pass

    def rollback(self):
        pass
