class EC2Controller:
    def __init__(self, ec2_resource, ec2_client):   
        self.ec2 = ec2_resource
        self.client = ec2_client

    def start_instance(self, instance_id):
        """Starts a currently non-running EC2

        Args:
            instance_id (string): the instance id to start
        """
        return self.ec2.Instance(instance_id).start()

    def stop_instance(self, instance_id ):
        """Stops a currently running EC2

        Args:
            instance_id (string): the instance id to stop
        """
        return self.ec2.Instance(instance_id).stop()

    def print_instance(self, index, instance):
        print("\t",index,": AMI:",instance.image_id, "- Instance:",  instance.id, "- State:", instance.state["Name"], "- Type:",  instance.instance_type, "- AZ:", instance.placement["AvailabilityZone"], "- Launch Time:", instance.launch_time)

    def list_instances(self, filter=""):
        """Lists instances. Running and non running are displayed separately. Can filter to only display running or non running

        Args:
            filter (string, [running, non_running], optional): The instances to display
        """
        running = []
        non_running = []
        # sort the instances by running or any other state
        for instance in self.ec2.instances.all():
            state = instance.state["Name"]
            if state == "running":
                running.append(instance)
            else:
                non_running.append(instance)
        if(filter == "running" or filter == ""):        
            print( "Running AWS EC2 instances: ")
            for index, instance in enumerate(running):
                self.print_instance(index, instance)            
        if(filter == "non_running" or filter == ""):      
            print( "Non Running AWS EC2 instances: ")
            for index, instance in enumerate(non_running):
                self.print_instance(index, instance)

    def create_ami(self, name, instance_id, no_reboot=True):
        """create an AMI of an instance. Instance rebooting suppresed by default.

        Args:
            name (string): name to attach to the AMI
            no_reboot (bool, default=false): reboot the instance during AMI creation
            instance_id (string): the instance id to create an AMI of
        """
        return self.ec2.Instance(instance_id).create_image(Name=name, NoReboot=no_reboot)

    def create_instance(self, image_id, min, max):
        """create instances based on the given AMI. Only creates t2.micros.

        Args:
            image_id (string): AMI to use when creating an image
            min (int): the minimum number of instances to create
            max (int): the maximum number of instances to create
        """
        return self.ec2.create_instances(ImageId=image_id, MinCount=min, MaxCount=max, InstanceType='t2.micro')

    def wait_for_instances_running(self, instances):
        """Polls AWS to wait for instances to be in a running state

        Args:
            instances (:list: `string`): list of instance ids to wait for
        """
        return self.client.get_waiter('instance_running').wait(InstanceIds=instances)