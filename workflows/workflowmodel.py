#! /usr/bin/python
import simplejson
from autopilot.common.utils import Dct


class WorkflowModel(object):
    """
    Object representation of a workflow
    """
    def __init__(self, wf_id, type, target, domain, inf, groupset):
        self.wf_id = wf_id
        self.type = type
        self.target = target
        self.inf = inf
        self.domain = domain
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
                             Dct.get(modeld, "domain"),
                             Dct.get(modeld, "inf"),
                             Dct.get(modeld, "taskgroups"))


