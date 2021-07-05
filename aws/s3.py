class S3Controller:
    def __init__(self, s3res):   
        self.s3 = s3res

    def print_bucket(self, index, bucket):
        print("\t",index,": Name:",bucket.name)
    
    def print_object(self, index, bucket_object):
        print("\t",index,": Key:", bucket_object.key, "- size:", bucket_object.size, "bytes - Last Modified:", bucket_object.last_modified)

    def list_buckets(self):
        buckets = self.s3.buckets.all()
        print("Current AWS S3 Buckets:")
        for index, bucket in enumerate(buckets):
            self.print_bucket(index, bucket)

    def list_objects(self, bucket_name):
        objects = self.s3.Bucket(bucket_name).objects.all()
        print("Objects in", bucket_name,":")
        for index, bucket_object in enumerate(objects):
            self.print_object(index, bucket_object)
    
    def upload_object(self, bucket_name, file_path, key):
        self.s3.Bucket(bucket_name).upload_file(file_path, key)

    def download_object(self, bucket_name, object_name, output_name):
        self.s3.Object(bucket_name, object_name).download_file(output_name)

    def delete_object(self, bucket_name, object_name):
        self.s3.Object(bucket_name, object_name).delete()