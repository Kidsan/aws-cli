class EBSController:
    def __init__(self, ec2Resource):   
        self.ebs = ec2Resource.volumes
        self.ec2 = ec2Resource

    def print_volume(self, index, volume):
        print("\t",index,": ID:",volume.id, "- AZ:", volume.availability_zone, "- Created:", volume.create_time, "- Size:", volume.size, "GiB - State:", volume.state)
    
    def list_volumes(self):
        volumes = self.ebs.all()
        print("EBS Volumes: ")
        for index, volume in enumerate(volumes):
            self.print_volume(index, volume)

    def detach_volume(self, volume_id, instance_id):
        return self.ec2.Volume(volume_id).detach_from_instance(InstanceId=instance_id)

    def attach_volume(self, volume_id, instance_id, device):
        return self.ec2.Volume(volume_id).attach_to_instance(Device=device,InstanceId=instance_id)

    def create_snapshot(self, volume_id, description):
        return self.ec2.Volume(volume_id).create_snapshot(Description=description)

    def create_volume(self, snapshot_id):
        return self.ec2.create_volume(SnapshotId=snapshot_id, AvailabilityZone="eu-west-1a")

    def list_snapshots(self):
        # We have to filter down to "our" snapshots to remove the public ones
        snapshots = self.ec2.snapshots.filter(OwnerIds=['self'])
        print("Available snapshots: ")
        for index, snapshot in enumerate(snapshots):
            print("\t",index,": ID:",snapshot.id)

