class SNSController:
    def __init__(self, sns_resource):   
        self.sns = sns_resource

    def create_topic(self, name):
        return self.sns.create_topic(Name=name)

    def create_email_subscription(self, topic_arn, email):
        topic = self.sns.Topic(topic_arn)
        topic.subscribe(Protocol='email',Endpoint=email)