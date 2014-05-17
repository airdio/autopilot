#! /user/bin python

from autopilot.common.utils import Dct
from autopilot.inf.inf import Inf, InfRequestContext
from autopilot.inf.aws import awsutils


class AWSInfRequestContext(InfRequestContext):
        def __init__(self, spec, callback=None):
            InfRequestContext.__init__(self, spec, callback)

class AWSInf(Inf):
    """ AWS Cloud specific implementation
    """

    def __init__(self, aws_access_key=None,
                 aws_secret_key=None, statusf=None):
        Inf.__init__(self, statusf)
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key

    def initialize_environment(self, spec={}, callback=None):
        """
        Create a deployment environment based on the spec.
        At minimum this will create:
        1. VPC and internet gateway attache to the VPC
        2. Security group with inbound traffic for 0.0.0.0/0 on port 22 and port 80
           attached to the VPC
        3. A subnet
        4. Create a new key_pair ???
        """
        vconn = self._get_vpc()

        # create a vpc
        vpc = vconn.create_vpc(Dct.get(spec, "cidr", "10.0.0.0/16"))
        spec["vpc_id"] = vpc.id

        # create a subnet within the vpc
        subnet = vconn.create_subnet(vpc.id, Dct.get(spec, "cidr", "10.0.0.0/24"))
        spec["subnet_id"] = subnet.id

        # create an internet gateway and attach to the vpc
        # create a route table and routes and attach it to the internet gateway
        # create a security group and attach it to the vpc
        ec2conn = self._get_ec2()
        sg = ec2conn.create_group(name="sg_{0}".format(spec["uname"]), description=None,
                                  auth_ssh=True, vpc_id=vpc.id, http=True)
        spec["security_group"].append(sg.id)

        # return updated spec
        return AWSInfRequestContext(spec, callback)

    def provision(self, spec={}, tags=[], callback=None):
        """
        Provision a set of machines asynchronously as per spec
        Returns a AWSInfRequestContext context
        """
        ec2 = self._get_ec2()
        sg = ec2.create_group("sg_{0}".format(Dct.get(spec, "uname")), description="ap security group",
                              vpc_id=Dct.get(spec, "vpc_id"))
        reservation = ec2.request_instances(image_id=spec["image_id"], instance_type=spec["instance_type"],
                                            count=spec["count"], security_group_ids=[sg.id],
                                            subnet_id=spec["subnet_id"])
        return AWSInfRequestContext(spec, ec2, reservation)

    def _get_ec2(self):
        return awsutils.EasyEC2(aws_access_key_id = self.aws_access_key,
                                aws_secret_access_key = self.aws_secret_key, aws_region_name="us-east-1")

    def _get_vpc(self):
        return awsutils.EasyVPC(aws_access_key_id = self.aws_access_key,
                                aws_secret_access_key = self.aws_secret_key, aws_region_name="us-east-1")

# import time
# import boto
# import boto.ec2.networkinterface
#
# from settings.settings import AWS_ACCESS_GENERIC
#
# ec2 = boto.connect_ec2(*AWS_ACCESS_GENERIC)
#
# interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(subnet_id='subnet-11d02d71',
#                                                                     groups=['sg-0365c56d'],
#                                                                     associate_public_ip_address=True)
# interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)
#
# reservation = ec2.run_instances(image_id='ami-a1074dc8',
#                                 instance_type='t1.micro',
#                                 #the following two arguments are provided in the network_interface
#                                 #instead at the global level !!
#                                 #'security_group_ids': ['sg-0365c56d'],
#                                 #'subnet_id': 'subnet-11d02d71',
#                                 network_interfaces=interfaces,
#                                 key_name='keyPairName')
#
# instance = reservation.instances[0]
# instance.update()
# while instance.state == "pending":
#     print instance, instance.state
#     time.sleep(5)
#     instance.update()
#
# instance.add_tag("Name", "some name")
#
# print "done", instance