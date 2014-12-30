#! /usr/bin python

class AutopilotException(Exception):
    def __init__(self, *args, **kwargs):
        self.message = args[0]
        self.inner_exception = kwargs.get('inner_exception', None)
        self.kwargs = kwargs

    def __str__(self):
        d = dict(message=self.message)
        d.update(self.kwargs)
        return str(d)


class AgentException(AutopilotException):
    def __init__(self, msg, *args, **kwargs):
        AutopilotException.__init__(self, msg, *args, **kwargs)


class GitInstallProviderException(AgentException):
    def __init__(self, msg, inner_exception=None):
        AgentException.__init__(self, msg, inner_exception=inner_exception)


class InvalidTargetRoleGroup(AgentException):
    def __init__(self, msg, inner_exception=None):
        AgentException.__init__(self, msg, inner_exception=inner_exception)


class WorkflowException(AutopilotException):
    """
    Base class for workflow related exceptions
    """
    def __init__(self, msg, wf_id, *args, **kwargs):
        AutopilotException.__init__(self, msg, args, kwargs)
        self.wf_id = wf_id


class AgentWorkflowException(WorkflowException):
    """
    Base class for workflow related exceptions
    """
    def __init__(self, msg, wf_id, *args, **kwargs):
        AutopilotException.__init__(self, msg, wf_id, args, kwargs)


class CommandNotFound(AutopilotException):
    """Raised when command is not found on the system's PATH """
    def __init__(self, cmd):
        self.message = "command not found: '%s'" % cmd


class RemoteCommandNotFound(CommandNotFound):
    """Raised when command is not found on a *remote* system's PATH """
    def __init__(self, cmd):
        self.message = "command not found on remote system: '%s'" % cmd


class AWSOperationException(AutopilotException):
    def __init__(self, msg, inner_exception=None, instances=None):
        AutopilotException.__init__(self, msg, inner_exception=inner_exception)
        self.instances = instances


class AWSInstanceProvisionTimeout(AWSOperationException):
    def __init__(self, msg, inner_exception=None, instances=None):
        AWSOperationException.__init__(self, msg, inner_exception=inner_exception, instances=instances)


class AWSPropogationException(AWSOperationException):
    def __init__(self, msg, inner_exception=None, instances=None):
        AWSOperationException.__init__(self, msg, inner_exception=inner_exception, instances=instances)

class SSHError(AutopilotException):
    """Base class for all SSH related errors"""


class SSHConnectionError(SSHError):
    """Raised when ssh fails to to connect to a host (socket error)"""
    def __init__(self, host, port):
        self.message = "failed to connect to host %s on port %s" % (host, port)


class SSHAuthException(SSHError):
    """Raised when an ssh connection fails to authenticate"""
    def __init__(self, user, host):
        self.message = "failed to authenticate to host %s as user %s" % (host,
                                                                     user)


class SSHNoCredentialsError(SSHError):
    def __init__(self):
        self.message = "No password or key specified"


class RemoteCommandFailed(SSHError):
    def __init__(self, msg, command, exit_status, output):
        self.message = msg
        self.command = command
        self.exit_status = exit_status
        self.output = output


class SSHAccessDeniedViaAuthKeys(AutopilotException):
    """
    Raised when SSH access for a given user has been restricted via
    authorized_keys (common approach on UEC AMIs to allow root SSH access to be
    'toggled' via cloud-init)
    """
    def __init__(self, user):
        self.message = "Access denied via AuthKeys for: {0}".format(user)


class SCPException(AutopilotException):
    """SCP exception class"""
    pass


class SecurityGroupDoesNotExist(AutopilotException):
    """
    Raised when aws security group is not found
    """
    def __init__(self, security_group_name=None, security_group_id=None):
        if security_group_name:
            self.message = "Security group not found: {0}".format(security_group_name)
        else:
            self.message = "Security group not found: {0}".format(security_group_id)

class InvalidIsoDate(AutopilotException):
    def __init__(self, date):
        self.message = "Invalid date specified: %s" % date


class InvalidHostname(AutopilotException):
    pass


class InvalidDevice(AutopilotException):
    def __init__(self, device):
        self.message = "invalid device specified: %s" % device


class InvalidPartition(AutopilotException):
    def __init__(self, part):
        self.message = "invalid partition specified: %s" % part


class PluginError(AutopilotException):
    """Base class for plugin errors"""


class PluginLoadError(PluginError):
    """Raised when an error is encountered while loading a plugin"""


class PluginSyntaxError(PluginError):
    """Raised when plugin contains syntax errors"""


class ValidationError(AutopilotException):
    """Base class for validation related errors"""


class ClusterReceiptError(AutopilotException):
    """Raised when creating/loading a cluster receipt fails"""


class ClusterValidationError(ValidationError):
    """Cluster validation related errors"""


class NoClusterNodesFound(ValidationError):
    """Raised if no cluster nodes are found"""
    def __init__(self, terminated=None):
        self.message = "No active cluster nodes found!"
        if not terminated:
            return
        self.message += "\n\nBelow is a list of terminated instances:\n"
        for tnode in terminated:
            id = tnode.id
            reason = 'N/A'
            if tnode.state_reason:
                reason = tnode.state_reason['message']
            state = tnode.state
            self.message += "\n%s (%s) %s" % (id, state, reason)


class NoClusterSpotRequests(ValidationError):
    """Raised if no spot requests belonging to a cluster are found"""
    def __init__(self):
        self.message = "No cluster spot requests found!"


class MasterDoesNotExist(ClusterValidationError):
    """Raised when no master node is available"""
    def __init__(self):
        self.message = "No master node found!"


class IncompatibleSettings(ClusterValidationError):
    """Raised when two or more settings conflict with each other"""


class InvalidProtocol(ClusterValidationError):
    """Raised when user specifies an invalid IP protocol for permission"""
    def __init__(self, protocol):
        self.message = "protocol %s is not a valid ip protocol. options: %s"
        self.message %= (protocol, ', '.join(static.PROTOCOLS))


class InvalidPortRange(ClusterValidationError):
    """Raised when user specifies an invalid port range for permission"""
    def __init__(self, from_port, to_port, reason=None):
        self.message = ''
        if reason:
            self.message += "%s\n" % reason
        self.message += "port range is invalid: from %s to %s" % (from_port,
                                                              to_port)


class InvalidCIDRSpecified(ClusterValidationError):
    """Raised when user specifies an invalid CIDR ip for permission"""
    def __init__(self, cidr):
        self.message = "cidr_ip is invalid: %s" % cidr


class InvalidZone(ClusterValidationError):
    """
    Raised when a zone has been specified that does not match the common
    zone of the volumes being attached
    """
    def __init__(self, zone, common_vol_zone):
        cvz = common_vol_zone
        self.message = ("availability_zone setting '%s' does not "
                    "match the common volume zone '%s'") % (zone, cvz)


class VolumesZoneError(ClusterValidationError):
    def __init__(self, volumes):
        vlist = ', '.join(volumes)
        self.message = 'Volumes %s are not in the same availability zone' % vlist


class ClusterTemplateDoesNotExist(AutopilotException):
    """
    Exception raised when user requests a cluster template that does not exist
    """
    def __init__(self, cluster_name):
        self.message = "cluster template %s does not exist" % cluster_name


class ClusterNotRunning(AutopilotException):
    """
    Exception raised when user requests a running cluster that does not exist
    """
    def __init__(self, cluster_name):
        self.message = "cluster %s is not running" % cluster_name


class ClusterDoesNotExist(AutopilotException):
    """
    Exception raised when user requests a running cluster that does not exist
    """
    def __init__(self, cluster_name):
        self.message = "cluster '%s' does not exist" % cluster_name


class ClusterExists(AutopilotException):
    def __init__(self, cluster_name, is_ebs=False, stopped_ebs=False):
        ctx = dict(cluster_name=cluster_name)
        if stopped_ebs:
            self.message = user_msgs.stopped_ebs_cluster % ctx
        elif is_ebs:
            self.message = user_msgs.active_ebs_cluster % ctx
        else:
            self.message = user_msgs.cluster_exists % ctx


class CancelledStartRequest(AutopilotException):
    def __init__(self, tag):
        self.message = "Request to start cluster '%s' was cancelled!!!" % tag
        self.message += "\n\nPlease be aware that instances may still be running."
        self.message += "\nYou can check this from the output of:"
        self.message += "\n\n   $ starcluster listclusters"
        self.message += "\n\nIf you wish to destroy these instances please run:"
        self.message += "\n\n   $ starcluster terminate %s" % tag
        self.message += "\n\nYou can then use:\n\n   $ starcluster listclusters"
        self.message += "\n\nto verify that the cluster has been terminated."
        self.message += "\n\nIf you would like to re-use these instances, rerun"
        self.message += "\nthe same start command with the -x (--no-create) option"


class CancelledCreateVolume(AutopilotException):
    def __init__(self):
        self.message = "Request to create a new volume was cancelled!!!"
        self.message += "\n\nPlease be aware that volume host instances"
        self.message += " may still be running. "
        self.message += "\n\nTo destroy these instances:"
        self.message += "\n\n   $ starcluster terminate %s"
        self.message += "\n\nYou can then use\n\n   $ starcluster listinstances"
        self.message += "\n\nto verify that the volume hosts have been terminated."
        self.message %= static.VOLUME_GROUP_NAME


class CancelledCreateImage(AutopilotException):
    def __init__(self, bucket, image_name):
        self.message = "Request to create an S3 AMI was cancelled"
        self.message += "\n\nDepending on how far along the process was before it "
        self.message += "was cancelled, \nsome intermediate files might still be "
        self.message += "around in /mnt on the instance."
        self.message += "\n\nAlso, some of these intermediate files might "
        self.message += "have been uploaded to \nS3 in the '%(bucket)s' bucket "
        self.message += "you specified. You can check this using:"
        self.message += "\n\n   $ starcluster showbucket %(bucket)s\n\n"
        self.message += "Look for files like: "
        self.message += "'%(iname)s.manifest.xml' or '%(iname)s.part.*'"
        self.message += "\nRe-executing the same s3image command "
        self.message += "should clean up these \nintermediate files and "
        self.message += "also automatically override any\npartially uploaded "
        self.message += "files in S3."
        self.message = self.message % {'bucket': bucket, 'iname': image_name}


CancelledS3ImageCreation = CancelledCreateImage


class CancelledEBSImageCreation(AutopilotException):
    def __init__(self, is_ebs_backed, image_name):
        self.message = "Request to create EBS image %s was cancelled" % image_name
        if is_ebs_backed:
            self.message += "\n\nDepending on how far along the process was "
            self.message += "before it was cancelled, \na snapshot of the image "
            self.message += "host's root volume may have been created.\nPlease "
            self.message += "inspect the output of:\n\n"
            self.message += "   $ starcluster listsnapshots\n\n"
            self.message += "and clean up any unwanted snapshots"
        else:
            self.message += "\n\nDepending on how far along the process was "
            self.message += "before it was cancelled, \na new volume and a "
            self.message += "snapshot of that new volume may have been created.\n"
            self.message += "Please inspect the output of:\n\n"
            self.message += "   $ starcluster listvolumes\n\n"
            self.message += "   and\n\n"
            self.message += "   $ starcluster listsnapshots\n\n"
            self.message += "and clean up any unwanted volumes or snapshots"


class ExperimentalFeature(AutopilotException):
    def __init__(self, feature_name):
        self.message = "%s is an experimental feature for this " % feature_name
        self.message += "release. If you wish to test this feature, please set "
        self.message += "ENABLE_EXPERIMENTAL=True in the [global] section of the"
        self.message += " config. \n\nYou've officially been warned :D"


class ThreadPoolException(AutopilotException):
    def __init__(self, msg, exceptions):
        self.message = msg
        self.exceptions = exceptions

    def print_excs(self):
        print self.format_excs()

    def format_excs(self):
        excs = []
        for exception in self.exceptions:
            e, tb_msg, jobid = exception
            excs.append('error occurred in job (id=%s): %s' % (jobid, str(e)))
            excs.append(tb_msg)
        return '\n'.join(excs)


class IncompatibleCluster(AutopilotException):
    default_msg = """\
INCOMPATIBLE CLUSTER: %(tag)s

The cluster '%(tag)s' is not compatible with StarCluster %(version)s. \
Possible reasons are:

1. The '%(group)s' group was created using an incompatible version of \
StarCluster (stable or development).

2. The '%(group)s' group was manually created outside of StarCluster.

3. One of the nodes belonging to '%(group)s' was manually created outside of \
StarCluster.

4. StarCluster was interrupted very early on when first creating the \
cluster's security group.

In any case '%(tag)s' and its nodes cannot be used with this version of \
StarCluster (%(version)s).

The cluster '%(tag)s' currently has %(num_nodes)d active nodes.

Please terminate the cluster using:

    $ starcluster terminate --force %(tag)s
"""

    def __init__(self, group):
        tag = group.name.replace(static.SECURITY_GROUP_PREFIX, '')
        states = ['pending', 'running', 'stopping', 'stopped']
        insts = group.connection.get_all_instances(
            filters={'instance-state-name': states,
                     'instance.group-name': group.name})
        ctx = dict(group=group.name, tag=tag, num_nodes=len(insts),
                   version=static.VERSION)
        self.message = self.default_msg % ctx

