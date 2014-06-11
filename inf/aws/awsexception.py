#! /usr/bin python
from autopilot.common.exception import AutopilotException


class AWSError(AutopilotException):
    """Base exception for all AWS related errors"""

class RegionDoesNotExist(AWSError):
    def __init__(self, region_name):
        self.msg = "region %s does not exist" % region_name

class AMIDoesNotExist(AWSError):
    def __init__(self, image_id):
        self.msg = "AMI %s does not exist" % image_id

class InstanceDoesNotExist(AWSError):
    def __init__(self, instance_id, label='instance'):
        self.msg = "%s '%s' does not exist" % (label, instance_id)

class InstanceNotRunning(AWSError):
    def __init__(self, instance_id, state, label='instance'):
        self.msg = "%s %s is not running (%s)" % (label, instance_id, state)

class SecurityGroupDoesNotExist(AWSError):
    def __init__(self, sg_name):
        self.msg = "security group %s does not exist" % sg_name

class PlacementGroupDoesNotExist(AWSError):
    def __init__(self, pg_name):
        self.msg = "placement group %s does not exist" % pg_name

class KeyPairAlreadyExists(AWSError):
    def __init__(self, keyname):
        self.msg = "keypair %s already exists" % keyname

class KeyPairDoesNotExist(AWSError):
    def __init__(self, keyname):
        self.msg = "keypair %s does not exist" % keyname

class ZoneDoesNotExist(AWSError):
    def __init__(self, zone, region):
        self.msg = "zone %s does not exist in region %s" % (zone, region)

class VolumeDoesNotExist(AWSError):
    def __init__(self, vol_id):
        self.msg = "volume %s does not exist" % vol_id

class SnapshotDoesNotExist(AWSError):
    def __init__(self, snap_id):
        self.msg = "snapshot %s does not exist" % snap_id

class BucketAlreadyExists(AWSError):
    def __init__(self, bucket_name):
        self.msg = "bucket with name '%s' already exists on S3\n" % bucket_name
        self.msg += "(NOTE: S3's bucket namespace is shared by all AWS users)"

class BucketDoesNotExist(AWSError):
    def __init__(self, bucket_name):
        self.msg = "bucket '%s' does not exist" % bucket_name

class InvalidOperation(AWSError):
    pass

class InvalidBucketName(AWSError):
    def __init__(self, bucket_name):
        self.msg = "bucket name %s is not valid" % bucket_name

class InvalidImageName(AWSError):
    def __init__(self, image_name):
        self.msg = "image name %s is not valid" % image_name

class AWSUserIdRequired(AWSError):
    def __init__(self):
        self.msg = "No Amazon user id specified in config (AWS_USER_ID)"

class EC2CertRequired(AWSError):
    def __init__(self):
        self.msg = "No certificate file (pem) specified in config (EC2_CERT)"

class EC2PrivateKeyRequired(AWSError):
    def __init__(self):
        self.msg = "No private certificate file (pem) file specified in "
        self.msg += "config (EC2_PRIVATE_KEY)"

class EC2CertDoesNotExist(AWSError):
    def __init__(self, key):
        self.msg = "EC2 certificate file %s does not exist" % key

class EC2PrivateKeyDoesNotExist(AWSError):
    def __init__(self, key):
        self.msg = "EC2 private key file %s does not exist" % key

class SpotHistoryError(AWSError):
    def __init__(self, start, end):
        self.msg = "no spot price history for the dates specified: "
        self.msg += "%s - %s" % (start, end)

class VPCDoesNotExists(AWSError):
    def __init__(self):
        self.msg = "VPC does not exists or invalid "

class PropagationException(AWSError):
    pass
