import os, sys
import boto3

bucket_name, path = sys.argv[1:]
s3_client = boto3.client('s3')

for file_name in os.listdir(path):
    response = s3_client.upload_file(os.path.join(path, file_name), bucket_name, file_name)
