# 9. Building ML Pipeline


# Create S3 bucket
BUCKET_NAME=k8s-ml-$(echo $(curl -s "https://helloacm.com/api/random/?n=5&x=2")| tr -d \")
aws s3 mb s3://$BUCKET_NAME


# Create GCS bucket
BUCKET_NAME=k8s-ml-$(echo $(curl -s "https://helloacm.com/api/random/?n=5&x=2")| tr -d \")
gsutil mb gs://$BUCKET_NAME

