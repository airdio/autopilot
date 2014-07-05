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
        return WorkflowModel(modeld.get("wf_id"),
                             modeld.get("type"),
                             modeld.get("target"),
                             modeld.get("domain", None),
                             modeld.get("inf", None),
                             modeld.get("taskgroups"))


