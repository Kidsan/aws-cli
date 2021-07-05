import datetime

class CloudWatchController:
    def __init__(self, cloud_watch):   
        self.cw = cloud_watch

    def print_bucket(self, index, bucket):
        print("\t",index,": Name:",bucket.name)
    
    def print_object(self, index, bucket_object):
        print("\t",index,": Key:", bucket_object.key, "- size:", bucket_object.size, "bytes - Last Modified:", bucket_object.last_modified)

    def get_metrics(self, instance_id):
        # Create a list of metrics we are gathering
        metrics = [
            self.cw.get_metric_statistics(Namespace='AWS/EC2',Statistics=['Average'],Period=60,MetricName='CPUUtilization',Dimensions=[{'Name': 'InstanceId','Value': instance_id}],  StartTime=datetime.datetime.now() - datetime.timedelta(minutes=10),EndTime=datetime.datetime.now()),
            self.cw.get_metric_statistics(Namespace='AWS/EC2',Statistics=['Average'],Period=60,MetricName='CPUCreditBalance',Dimensions=[{'Name': 'InstanceId','Value': instance_id}],  StartTime=datetime.datetime.now() - datetime.timedelta(minutes=10),EndTime=datetime.datetime.now())
        ]
        print("Monitoring on instance:", instance_id)
        for index, metric in enumerate(metrics):
            print("\t",index,": Metric:",metric["Label"], " Average - Value:", metric["Datapoints"][0]['Average'],metric["Datapoints"][0]['Unit'] )
    
    def create_cpu_alarm(self, instance_id, topic_arn):
        self.cw.put_metric_alarm(
            AlarmName=str(instance_id) + ' CPU Usage Below 28%',
            EvaluationPeriods=1,
            MetricName='CPUUtilization',
            Namespace='AWS/EC2',
            ComparisonOperator="LessThanThreshold",
            Period=300,
            Statistic='Average',
            Threshold=28.0,
            ActionsEnabled=True,
            AlarmActions=[
                topic_arn
            ],
            AlarmDescription='Alarm when CPU below 28%',
            Dimensions=[
                {
                'Name': 'InstanceId',
                'Value': instance_id
                },
            ],
            Unit='Percent'
        )
