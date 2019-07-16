- AWS: kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.11/nvidia-device-plugin.yml
- GCP: kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/stable/nvidia-driver-installer/cos/daemonset-preloaded.yaml


# GPU worker node 구성
eksctl create nodegroup --cluster $CLUSTER_NAME --name train-gpu --nodes-min 0 --nodes-max 1 --nodes 0 --node-labels "role=train-gpu" --node-type p3.2xlarge --asg-access

NG_STACK=eksctl-$CLUSTER_NAME-nodegroup-train-gpu
ASG_ID=$(aws cloudformation describe-stack-resource --stack-name $NG_STACK --logical-resource-id NodeGroup --query StackResourceDetail.PhysicalResourceId --output text)
REGION=$(aws configure get region)

aws autoscaling create-or-update-tags --tags ResourceId=$ASG_ID,ResourceType=auto-scaling-group,Key=k8s.io/cluster-autoscaler/node-template/label/role,Value=train-gpu,PropagateAtLaunch=true


gcloud container node-pools create train-gpu \
    --cluster $CLUSTER_NAME \
    --node-labels=role=train-gpu \
    --enable-autoscaling \
    --min-nodes=0 \
    --num-nodes=0 \
    --max-nodes=1 \
    --accelerator type=nvidia-tesla-k80,count=1 \
    --machine-type=n1-standard-4

