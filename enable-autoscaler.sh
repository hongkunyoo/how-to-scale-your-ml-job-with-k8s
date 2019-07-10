if ! which aws &> /dev/null; then
    echo "aws command not found"
    echo "aws cli should be installed"
    exit 1
fi

CLUSTER_NAME=eks-ml


echo '########################################'
echo '>>>>>>>> Get AutoScaleGroup ID >>>>>>>>>'
echo '########################################'
NG_ID=$(eksctl get nodegroup --cluster $CLUSTER_NAME | cut -d ' ' -f1 | sed 1d | cut -f2)
NG_STACK=eksctl-$CLUSTER_NAME-nodegroup-$NG_ID
ASG_ID=$(aws cloudformation describe-stack-resource --stack-name $NG_STACK --logical-resource-id NodeGroup --query StackResourceDetail.PhysicalResourceId --output text)
REGION=$(aws configure get region)


echo '#################################################'
echo '>>>>>>>> Tag cluster-autoscaler/enabled >>>>>>>>>'
echo '#################################################'
aws autoscaling create-or-update-tags --tags ResourceId=$ASG_ID,ResourceType=auto-scaling-group,Key=k8s.io/cluster-autoscaler/enabled,Value=,PropagateAtLaunch=true
aws autoscaling create-or-update-tags --tags ResourceId=$ASG_ID,ResourceType=auto-scaling-group,Key=k8s.io/cluster-autoscaler/$CLUSTER_NAME,Value=,PropagateAtLaunch=true

NODE_ROLE=$(aws cloudformation describe-stack-resource --stack-name $NG_STACK --logical-resource-id NodeInstanceRole --query StackResourceDetail.PhysicalResourceId --output text)
aws iam put-role-policy --role-name $NODE_ROLE --policy-name autoscale --policy-document '{ "Version": "2012-10-17", "Statement": [ { "Effect": "Allow",  "Action": [ "autoscaling:*" ], "Resource": "*" } ] }'


echo '################################################'
echo '>>>>>>>> Installing cluster-autoscaler >>>>>>>>>'
echo '################################################'
cat <<EOF | kubectl create -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: kube-system-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: default
  namespace: kube-system
EOF

helm install stable/cluster-autoscaler --name autoscale --namespace kube-system --set autoDiscovery.clusterName=$CLUSTER_NAME,awsRegion=$REGION,sslCertPath=/etc/kubernetes/pki/ca.crt

echo '################################'
echo '>>>>>>>>>>>>> done >>>>>>>>>>>>>'
echo '################################'

