import auth
import aws
import boto3
import os
import getpass
import sys
import signal
import sys

def signal_handler(sig, frame):
    print('\nGoodbye!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

from cmd import Cmd

authenticator = auth.Auth()

free_tier_amis = {
    "windows": "ami-065a15cef040336bf",
    "linux": "ami-0dc8d444ee2a42d8a"
}

def gather_instance_id():
    print("Enter the id of an EC2:")
    return input("instance id: ")

def exit():
    print("bye!")
    sys.exit()


class EC2Manager(Cmd):
    intro = "Welcome to the EC2 Manager, type ? to list available commands."
    prompt = ("(ec2) ")
    def do_back(self, inp):
        AWSManager().cmdloop()

    def do_list(self, inp):
        return cloud.list_ec2s(inp)

    def do_start(self, inp):
        self.do_list("non_running")
        instance_id = gather_instance_id()
        if instance_id == "":
            return
        else:
            cloud.start_ec2(instance_id)

    def do_stop(self, inp):
        self.do_list("running")
        instance_id = gather_instance_id()
        if instance_id == "":
            return
        else:
            cloud.stop_ec2(instance_id)
    
    def do_create_ami(self, inp):
        self.do_list("")
        instance_id = gather_instance_id()
        if instance_id == "":
            return
        print("Enter the name to assign the AMI, leave blank to cancel:")
        ami_name = input("ami_name: ")
        if ami_name == "":
            return
        else:
            ami = cloud.create_instance_ami(instance_id,ami_name)
            if hasattr(ami, 'id'):
                print("Created AMI: ", ami.id)
    
    def do_launch(self, inp):
        print("Would you like to create a Windows or Linux instance?")
        instance_type = input("please enter an OS: ")
        instance_type_lowercase = instance_type.lower()

        # checks if chosen OS is one of our two free tier AMIs using a tuple
        if instance_type_lowercase not in ("windows", "linux"): 
            print("unable to create an instance of type", instance_type)
        else:
            ami = free_tier_amis[instance_type_lowercase] # a dict containing hardcoded free tier AMIs
            return cloud.create_instance(ami)

    def do_exit(self, inp):
        exit()

    def help_exit(self):
        print("\t - Exit the Application")
    
    def help_stop(self, inp):
        print("\t - Stop a non running AWS EC2 by instance_id.")
    
    def help_start(self, inp):
        print("\t - Start a non running AWS EC2 by instance_id.")

    def help_back(self):
        print("\t - return to the main menu")

    def help_list(self):
        print("\t - lists all AWS EC2 instances.")
        print("\t - Accepts optional parameters \"running\" or \"non_running\" and displays only those")
        print("\t\t - Example: list running")

    def help_create_ami(self):
        print("\t - Create an AMI based on an existing EC2")
    
    def help_launch(self):
        print("\t - Launch either a windows or linux EC2")

class EBSManager(Cmd):
    intro = "Welcome to the EBS Manager, type ? to list available commands"
    prompt = ("(ebs) ")

    def do_exit(self, inp):
        exit()

    def help_exit(self):
        print("\t - Exit the Application")

    def do_list(self, inp):
        return cloud.list_volumes()

    def do_attach(self, inp):
        self.do_list("")
        print("Enter a volume id to attach, leave blank to cancel:")
        volume_id = input("volume_id: ")
        if volume_id == "":
            return
        cloud.list_ec2s("")
        instance_id = gather_instance_id()
        if instance_id == "":
            return
        print("Enter the mountpath, e.g. /dev/sdh, leave blank  to cancel:")
        mount_path = input("mount path: ")
        if mount_path == "":
            return
        return cloud.attach_volumes(volume_id,instance_id, mount_path)
    
    def do_detach(self, inp):
        self.do_list("")
        print("Enter a volume id to detach, leave blank to cancel:")
        volume_id = input("volume_id: ")
        if volume_id == "":
            return
        cloud.list_ec2s("")
        instance_id = gather_instance_id()
        if instance_id == "":
            return
        return cloud.detach_volumes(volume_id,instance_id)

    def do_snapshot(self, inp):
        self.do_list("")
        print("Enter a volume id to snapshot, leave blank to cancel:")
        volume_id = input("volume_id: ")
        if volume_id == "":
            return
        print("Enter a description for the snapshot:")
        description = input("description: ")
        snapshot = cloud.create_snapshot(volume_id, description)
        if hasattr(snapshot, 'id'):
            print("Created snapshot:", snapshot.id)

    def do_create(self, inp):
        cloud.list_snapshots()
        print("Enter the snapshot id to create an EBS volume of, leave blank to cancel:")
        snapshot_id = input("snapshot_id: ")
        if snapshot_id == "":
            return
        volume = cloud.create_volume(snapshot_id)
        if hasattr(volume, 'id'):
            print("Created volume:", volume.id)

    def do_back(self, inp):
        AWSManager().cmdloop()

    def help_back(self):
        print("\t - return to the main menu")
    
    def help_list(self):
        print("\t - Lists all ebs volumes")

    def help_attach(self):
        print("\t - Attach volume to an EC2")

    def help_detach(self):
        print("\t - Detach volume to an EC2")

    def help_snapshot(self):
        print("\t - Create a snapshot of a volume")
    
    def help_create(self):
        print("\t - Create a volume out of one of your snapshots")

class S3Manager(Cmd):
    intro = "Welcome to the s3 Manager, type ? to list available commands"
    prompt = ("(s3) ")

    def do_exit(self, inp):
        exit()

    def help_exit(self):
        print("\t - Exit the Application")

    def do_list(self, inp):
        return cloud.list_buckets()

    def do_get_objects(self, inp):
        cloud.list_buckets()
        print("Enter the name of a bucket to list objects for, leave blank to cancel: ")
        bucket_name = input("bucket name: ")
        if bucket_name == "":
            return
        return cloud.get_objects(bucket_name)
    
    def do_upload(self, inp):
        print("All paths to be written relative to ", os.getcwd())
        print("Enter the name of the bucket to upload to, leave blank to cancel: ")
        bucket_name = input("bucket name: ")
        if bucket_name == "":
            return
        print("Enter the path of the object to upload, leave blank to cancel: ")
        path = input("source file: ")
        if path == "":
            return
        print("Enter the name of the object to store, leave blank to cancel: ")
        key = input("upload as: ")
        if key == "":
            return
        return cloud.upload_object(bucket_name,path,key)

    def do_download(self, inp):
        print("All paths to be written relative to ", os.getcwd())
        print("Enter the name of the bucket to download from, leave blank to cancel: ")
        cloud.list_buckets()
        bucket_name = input("bucket name: ")
        if bucket_name == "":
            return
        cloud.get_objects(bucket_name)
        print("Enter the name of the object to download, leave blank to cancel: ")
        key = input("download: ")
        if key == "":
            return
        print("Enter the target destination, leave blank to cancel: ")
        path = input("target file: ")
        if path == "":
            return
        return cloud.download_object(bucket_name,key,path)
    
    def do_delete_object(self, inp):
        print("Enter the name of the bucket to delete an object from, leave blank to cancel: ")
        cloud.list_buckets()
        bucket_name = input("bucket name: ")
        if bucket_name == "":
            return
        cloud.get_objects(bucket_name)
        print("Enter the name of the object to delete, leave blank to cancel: ")
        key = input("download: ")
        if key == "":
            return
        return cloud.delete_object(bucket_name,key)

    def do_back(self, inp):
        AWSManager().cmdloop()

    def help_back(self):
        print("\t - return to the main menu")
    
    def help_list(self):
        print("\t - Lists all s3 buckets")
    
    def help_get_objects(self):
        print("\t - Lists all objects in an s3 bucket")

    def help_upload(self):
        print("\t - Upload an object to the bucket")
    
    def help_download(self):
        print("\t - Download an object from a bucket")
    
    def help_delete_object(self):
        print("\t - Delete an object from a bucket")

class CloudwatchManager(Cmd):
    intro = "Welcome to the Cloudwatch Manager, type ? to list available commands"
    prompt = ("(cloudwatch) ")

    def do_exit(self, inp):
        exit()

    def help_exit(self):
        print("\t - Exit the Application")

    def do_show_stats(self, inp):
        cloud.list_ec2s("")
        instance_id = gather_instance_id()
        if instance_id == "":
            return
        return cloud.cloudwatch.get_metrics(instance_id)

    def do_create_cpu_alarm(self, inp):
        cloud.list_ec2s("")
        instance_id = gather_instance_id()
        if instance_id == "":
            return
        print("Enter an email to send alerts to, leave blank  to cancel:")
        email = input("email: ")
        if email == "":
            return
        return cloud.create_alarm(instance_id, email)

    def do_back(self, inp):
        AWSManager().cmdloop()

    def help_back(self):
        print("\t - return to the main menu")

    def help_show_stats(self):
        print("\t - Show the Average CPU % and CPU Credit Balance for the last 10 minutes")
    
    def help_create_cpu_alarm(self, inp):
        print("\t - Creates an email alert when an EC2 cpu usage is below 28%")

class AutoscalingManager(Cmd):
    intro = "Welcome to the Autoscaling Manager, type ? to list available commands"
    prompt = ("(autoscaling) ")

    def do_exit(self, inp):
        exit()

    def help_exit(self):
        print("\t - Exit the Application")

    def do_back(self, inp):
        AWSManager().cmdloop()

    def help_back(self):
        print("\t - return to the main menu")

    def do_create(self, inp):
        print("Enter the name for your autoscaling group: ")
        name = input("name:")
        cloud.list_ec2s("")
        instance_id = gather_instance_id()
        print("Enter the required number of instances: ")
        required = int(input("required:"))
        print("Enter the minimum number of instances: ")
        minimum = int(input("minimum:"))
        print("Enter the maximum number of instances: ")
        maximum = int(input("maximum:"))

        return cloud.create_asg_group(name, instance_id, required, minimum, maximum)

    def do_attach(self, inp):
        print("Enter the name of the autoscaling group: ")
        cloud.list_asgs()
        asg_name = input("name:")
        print("Enter a comma separated list of instances to attach: ")
        cloud.list_ec2s("")
        instances_list = input("instance ids:")
        instances = instances_list.split(",") # create a list of strings out of the comma separated string containing ids
        return cloud.attach_instances(asg_name, instances)

    def do_detach(self, inp):
        print("Enter the name of the autoscaling group: ")
        cloud.list_asgs()
        asg_name = input("name:")
        print("Enter a comma separated list of instances to detach: ")
        cloud.list_ec2s("")
        instances_list = input("instance ids:")
        instances = instances_list.split(",") # create a list of strings out of the comma separated string containing ids
        return cloud.detach_instances(asg_name, instances)

    def do_refresh(self, inp):
        print("Enter the name of the autoscaling group to refresh: ")
        cloud.list_asgs()
        asg_name = input("name:")
        return cloud.refresh_instances(asg_name)

    def help_refresh(self, inp):
        print("\t - Refresh all instances in an ASG")

    def help_detach(self, inp):
        print("\t - Detach an instance from an ASG. Will not allow lowering beyond the minimum configured value.")

    def help_attach(self, inp):
        print("\t - Attach an instance to an ASG. Will not allow raising beyond the maximum configured value.")

    def help_create(self, inp):
        print("\t - Create an ASG based on a running instance.")

class AWSManager(Cmd):
    intro = "Welcome to the AWS Manager, type ? to list available commands"
    prompt = ("(aws) ")

    def do_ec2(self, inp):
        EC2Manager().cmdloop()

    def do_ebs(self, inp):
        EBSManager().cmdloop()

    def do_s3(self, inp):
        S3Manager().cmdloop()

    def do_cloudwatch(self, inp):
        CloudwatchManager().cmdloop()

    def do_autoscaling(self, inp):
        AutoscalingManager().cmdloop()

    def do_exit(self, inp):
        exit()
    
    def help_ec2(self):
        print("\t - Manage EC2 instances")

    def help_ebs(self):
        print("\t - Manage EBS volumes")

    def help_s3(self):
        print("\t - Manage s3 buckets and objects")

    def help_cloudwatch(self):
        print("\t - Cloudwatch Statistics manager")

    def help_autoscaling(self):
        print("\t - Manage Autoscaling groups")
    
    def help_exit(self):
        print("\t - Exit the Application")

def credentials_prompt():
    print("Please enter a username:")
    username = input("username:")
    print("Please enter a password:")
    password = getpass.getpass(prompt='Password: ', stream=None) 
    validated = authenticator.authenticate(username, password)
    if(validated == False):
        print("Login Unsuccessful.\n\n")
        credentials_prompt()
    else:
        config = { 
            "key_id": validated.access_key,
            "secret_key": validated.secret,
            "region": "eu-west-1" # we assume the region for all scenarios
        }
        global cloud # make the cloud variable available in global scope
        cloud = aws.AWS(boto3, config) # not ideal method of handling this, should be passed to a constructor

        AWSManager().cmdloop()

credentials_prompt()