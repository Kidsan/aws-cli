import aws.ec2 as ec2
import aws.ebs as ebs
import aws.s3 as s3
import aws.cloudwatch as cloudwatch
import aws.sns as sns
import aws.autoscaling as autoscaling


class AWS:
    """Class for managing all AWS interactions
    - boto3 and the configuration are dependency injected to allow for unit testing
    - we could mock boto3 and pass it in here to test behaviour in different scenarios
    - We could alternatively injected the boto resources we are using instead.
    """
    def __init__(self, boto3, boto_config):
        self.boto3 = boto3
        self.key_id = boto_config["key_id"]
        self.secret_key = boto_config["secret_key"]
        self.region = boto_config["region"]
        ec2_resource = self.boto3.resource(
            'ec2',
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
        ec2_client = self.boto3.client(
            'ec2',
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
        self.ec2 = ec2.EC2Controller(ec2_resource, ec2_client)
        self.ebs = ebs.EBSController(ec2_resource)
        self.s3 = s3.S3Controller(self.boto3.resource(
            's3',
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        ))
        self.cloudwatch = cloudwatch.CloudWatchController(self.boto3.client(
            'cloudwatch',
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        ))
        self.sns = sns.SNSController(self.boto3.resource(
            'sns',
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        ))
        self.autoscaling = autoscaling.AutoscalingController(self.boto3.client(
            'autoscaling',
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        ))
    
    def list_ec2s(self, filter=""):
        return self.ec2.list_instances(filter)

    def start_ec2(self, instance_id):
        try:
            self.ec2.start_instance(instance_id)
            print("Starting instance", instance_id, "please wait...")
            self.ec2.wait_for_instances_running([instance_id])
            print("Instance", instance_id, "is now running")
        except Exception as e:
            print(e)
            print("Please ensure you entered a valid, non-running AWS EC2 instance id")
        

    def stop_ec2(self, instance_id):
        try:
            print("Stopping instance", instance_id)
            return self.ec2.stop_instance(instance_id)
        except Exception as e:
            print(e)
            print("Please ensure you entered a valid, running AWS EC2 instance id")


    def create_instance_ami(self, instance_id, name):
        try:
            return self.ec2.create_ami(name,instance_id)
        except Exception as e:
            print(e)


    def create_instance(self, ami_id):
        try:
            instance = self.ec2.create_instance(ami_id,1,1)
            instance_id = instance[0].id
            print("Starting instance", instance_id, "please wait...")
            self.ec2.wait_for_instances_running([instance_id])
        except Exception as e:
            print(e)

    def list_volumes(self):
        try:
            return self.ebs.list_volumes()
        except Exception as e:
            print(e)
    
    def attach_volumes(self, volume_id, instance_id, mount_path):
        try:
            return self.ebs.attach_volume(volume_id, instance_id, mount_path)
        except Exception as e:
            print(e)

    def detach_volumes(self, volume_id, instance_id):
        try:
            return self.ebs.detach_volume(volume_id,instance_id)
        except Exception as e:
            print(e)

    def create_snapshot(self, volume_id, description):
        try:
            return self.ebs.create_snapshot(volume_id, description)
        except Exception as e:
            print(e)

    def list_snapshots(self):
        try:
            return self.ebs.list_snapshots()
        except Exception as e:
            print(e)
    
    def create_volume(self, snapshot_id):
        try:
            return self.ebs.create_volume(snapshot_id)
        except Exception as e:
            print(e)

    def list_buckets(self):
        try:
            return self.s3.list_buckets()
        except Exception as e:
            print(e)

    def get_objects(self,bucket_name):
        try:
            return self.s3.list_objects(bucket_name)
        except Exception as e:
            print(e)
    
    def download_object(self,bucket_name, object_name, target_path):
        try:
            return self.s3.download_object(bucket_name,object_name,target_path)
        except Exception as e:
            print(e)

    def upload_object(self, bucket_name, file_path, key):
        try:
            self.s3.upload_object(bucket_name, file_path, key)
            print("upload successful")
        except Exception as e:
            print(e)

    def delete_object(self, bucket_name, key):
        try:
            return self.s3.delete_object(bucket_name, key)
        except Exception as e:
            print(e)

    def get_metrics(self, instance_id):
        try:
            return self.cloudwatch.get_metrics(instance_id)
        except Exception as e:
            print(e)
    
    def create_alarm(self, instance_id, email):
        """Here we must create multiple resources:
        1. An SNS topic to publish the alarm to
        2. A subscription for the given email address to that SNS topic
        3. The alarm that fires when CPU usage is below 28%
        """
        try:
            topic_arn = self.sns.create_topic(str(instance_id) + '-low-cpu-usage').arn
            self.sns.create_email_subscription(topic_arn, email)
            self.cloudwatch.create_cpu_alarm(instance_id,topic_arn)
            print("Alarm created. Please check your email to confirm the sns subscription.")
        except Exception as e:
            print(e)

    def create_asg_group(self, name, instance_id, required, minimum, maximum):
        try:
            self.autoscaling.create(name, instance_id, required, minimum, maximum)
            print("Created ASG.")
        except Exception as e:
            print(e)

    def attach_instances(self, asg_name, instances):
        try:
            return self.autoscaling.attach_instances(asg_name, instances)
        except Exception as e:
            print(e)
    
    def detach_instances(self, asg_name, instances):
        try:
            return self.autoscaling.detach_instances(asg_name, instances)
        except Exception as e:
            print(e)
    
    def refresh_instances(self, asg_name):
        try:
            return self.autoscaling.refresh_instances(asg_name)
        except Exception as e:
            print(e)

    def list_asgs(self):
        try:
            return self.autoscaling.get_asgs()
        except Exception as e:
            print(e)
