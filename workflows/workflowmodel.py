#! /usr/bin/python
import simplejson
from autopilot.common.utils import Dct


class WorkflowModel(object):
    """
    Object representation of a workflow
    """
    def __init__(self, wf_id, type, target, token, audit, inf, groupset):
        self.wf_id = wf_id
        self.type = type
        self.target = target
        self.account = token
        self.audit = audit
        self.inf = inf
        self.groupset = groupset
        self.parallel = True

    @staticmethod
    def load(mstream):
        """
        Loads a serialized workflow model
        """
        modeld = simplejson.load(mstream)
        return WorkflowModel(Dct.get(modeld, "wf_id"),
                             Dct.get(modeld, "type"),
                             Dct.get(modeld, "target"),
                             Dct.get(modeld, "token"),
                             Dct.get(modeld, "audit"),
                             Dct.get(modeld, "inf"),
                             Dct.get(modeld, "taskgroups"))


