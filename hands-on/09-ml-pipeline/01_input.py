import os, sys
import boto3


bucket_name, object_name, file_name = sys.argv[1:]
s3 = boto3.client('s3')
print('downloading %s' % object_name)
s3.download_file(bucket_name, object_name, file_name)
print('download done')
