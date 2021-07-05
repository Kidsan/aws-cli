class AutoscalingController:
    def __init__(self, autoscaling_client):   
        self.autoscaling = autoscaling_client
    """
    AWS Auto Scaling is a grouping of EC2 instances that AWS treats as a unit.
    We can add instances to Auto Scaling groups, and configure parameters which allow
    management over the number of instances in the group. This is useful if we have a service
    that can see spikes in demand. We can configure the AWS Auto Scaling group with a minumum and maximum
    number of instances, as well as scale-up and scale-down policies indicating how and when AWS should increase 
    or decrease the number of instances in the group.
    The ASG can also monitor instance health, and terminate and replace instances it determines unhealthy. By dynamically
    scaling the number of instances we have deployed, and by letting the ASG deploy instances in multiple availability zones
    we see improved availability, scalability, and a reduction in cost (vs having a high number deployed all the time to 
    handle spikes in traffic)
    """
    
    def create(self, name, instance_id, required_instances, min_instances, max_instances):
        """Creates a new ASG and new instances in the ASG copied from the instance id provided

        Args:
            name (string): the name to assign the ASG
            instance_id (string): the instance id to base the ASG off
            required_instances (int): the required number of instances to run in the ASG
            min_instances (int): the minimum number of instances to run in the ASG
            max_instances (int): the maximum number of instances to run in the ASG
        """

        return self.autoscaling.create_auto_scaling_group(
            AutoScalingGroupName=name,
            InstanceId=instance_id,
            MinSize=min_instances,
            MaxSize=max_instances,
        )

    def attach_instances(self, asg_name, instance_ids):
        """Attaches instances to the ASG, up to the maximum configured value for the ASG.

        Args:
            asg_name (string): the name of the ASG to attach instances to
            instance_ids (:list: `string`): list of instance ids to attach
        """
        return self.autoscaling.attach_instances(InstanceIds=instance_ids, AutoScalingGroupName=asg_name)

    def detach_instances(self, asg_name, instance_ids, decrement_desired=True):
        """Attaches instances to the ASG, up to the maximum configured value for the ASG.

        Args:
            asg_name (string): the name of the ASG to detach instances from
            instance_ids (:list: `string`): list of instance ids to detach
            decrement_desired (bool): reduce the desired capacity of the ASG correspondingly (default: true)
        """
        return self.autoscaling.detach_instances(InstanceIds=instance_ids, AutoScalingGroupName=asg_name, ShouldDecrementDesiredCapacity=decrement_desired)

    def refresh_instances(self, asg_name):
        """Triggers a rolling refresh of instances in the ASG group, replacing each instance with a new one

        Args:
            asg_name (string): the name of the ASG to refresh
        """
        return self.autoscaling.start_instance_refresh(AutoScalingGroupName=asg_name, Strategy='Rolling')

    def get_asgs(self):
        """Lists auto scaling groups
        """
        asgs =  self.autoscaling.describe_auto_scaling_groups()['AutoScalingGroups']
        for index, asg in enumerate(asgs):
            print("\t",index,": ID:",asg["AutoScalingGroupName"])
