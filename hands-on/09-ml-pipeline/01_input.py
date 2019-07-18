import os, sys
import boto3
from boto3.session import Session
from botocore.client import Config
from botocore.handlers import set_list_objects_encoding_type_url


bucket_name, object_name, download_path = sys.argv[1:]

ACCESS_KEY = os.environ['ACCESS_KEY']
SECRET_KEY = os.environ['SECRET_KEY']

s3 = None
session = Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

if ACCESS_KEY.startswith('GOOG'):
    session.events.unregister('before-parameter-build.s3.ListObjects',set_list_objects_encoding_type_url)
    s3 = session.client('s3', endpoint_url='https://storage.googleapis.com',config=Config(signature_version='s3v4'))
else:
    s3 = session.client('s3')

#s3 = boto3.client('s3')
print('downloading %s' % object_name)
s3.download_file(bucket_name, object_name, os.path.join(download_path, object_name))
print('download done')
