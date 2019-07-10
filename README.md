## Open Infrastructure & Cloud Native Days Korea 2019 Track 7

*Hands on session*
How to scale your ML job with Kubernetes

### Prequisition
- AWS 계정
- GCP 계정
- Kubernetes 기본 지식
  - Deployments
  - Services
  - Jobs
  - Configmaps

### Provisioning

#### On AWS

```bash
CLUSTER_NAME=openinfra

# installing eksctl
curl --location "https://github.com/weaveworks/eksctl/releases/download/latest_release/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
mv /tmp/eksctl /usr/local/bin

# installing heptio-authenticator
curl -o aws-iam-authenticator https://amazon-eks.s3-us-west-2.amazonaws.com/1.11.5/2018-12-06/bin/linux/amd64/aws-iam-authenticator
chmod +x ./aws-iam-authenticator
mv aws-iam-authenticator /usr/local/bin

# installing kubectl
apt-get update && apt-get install -y apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list
apt-get update
apt-get install -y kubectl

# installing helm client
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get | bash

# k8s cluster
eksctl create cluster --name $CLUSTER_NAME --node-type m5.large --nodes-min=4 --nodes-max=8

# installing metric server
cat <<EOF | kubectl create -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: tiller
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: tiller
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: tiller
  namespace: kube-system
EOF

helm init --service-account tiller
sleep 20
chown $SUDO_UID:$SUDO_GID $HOME/.kube/config
chown -R $SUDO_UID:$SUDO_GID $HOME/.helm

NG_ID=$(eksctl get nodegroup --cluster $CLUSTER_NAME | cut -d ' ' -f1 | sed 1d | cut -f2)
NG_STACK=eksctl-$CLUSTER_NAME-nodegroup-$NG_ID
ASG_ID=$(aws cloudformation describe-stack-resource --stack-name $NG_STACK --logical-resource-id NodeGroup --query StackResourceDetail.PhysicalResourceId --output text)
REGION=$(aws configure get region)

aws autoscaling create-or-update-tags --tags ResourceId=$ASG_ID,ResourceType=auto-scaling-group,Key=k8s.io/cluster-autoscaler/enabled,Value=,PropagateAtLaunch=true
aws autoscaling create-or-update-tags --tags ResourceId=$ASG_ID,ResourceType=auto-scaling-group,Key=k8s.io/cluster-autoscaler/$CLUSTER_NAME,Value=,PropagateAtLaunch=true

NODE_ROLE=$(aws cloudformation describe-stack-resource --stack-name $NG_STACK --logical-resource-id NodeInstanceRole --query StackResourceDetail.PhysicalResourceId --output text)
aws iam put-role-policy --role-name $NODE_ROLE --policy-name autoscale --policy-document '{ "Version": "2012-10-17", "Statement": [ { "Effect": "Allow",  "Action": [ "autoscaling:*" ], "Resource": "*" } ] }'

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


```
#### On GCP

https://console.cloud.google.com 접속
```bash
gcloud config set compute/zone asia-northeast2-a

CLUSTER_NAME=openinfra2

gcloud container clusters create $CLUSTER_NAME \
    --cluster-version=1.13.7-gke.8 \
    --num-nodes=1 \
    --node-labels=role=default \
    --machine-type=n1-standard-4 \
    --node-locations=asia-northeast2-a,asia-northeast2-b


gcloud container node-pools create train-cpu \
    --cluster $CLUSTER_NAME \
    --node-labels=role=train-cpu \
    --enable-autoscaling \
    --min-nodes=1 \
    --num-nodes=2 \
    --max-nodes=3 \
    --machine-type=n1-highcpu-8

gcloud container node-pools create train-gpu \
    --cluster $CLUSTER_NAME \
    --node-labels=role=train-gpu \
    --enable-autoscaling \
    --min-nodes=0 \
    --num-nodes=0 \
    --max-nodes=1 \
    --machine-type=n1-highmem-2
```

### Install helm packages

```bash
helm install stable/metrics-server --name stats --namespace kube-system --set 'args={--logtostderr,--metric-resolution=2s}'
helm install stable/cluster-autoscaler --name autoscale --namespace kube-system --set autoDiscovery.clusterName=$CLUSTER_NAME,awsRegion=$REGION,sslCertPath=/etc/kubernetes/pki/ca.crt
helm install stable/cluster-autoscaler --name autoscale --namespace kube-system --set autoDiscovery.clusterName=$CLUSTER_NAME,awsRegion=$REGION,sslCertPath=/etc/kubernetes/pki/ca.crt
```
### Run ML jobs

1. Basic Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: exp01-example
spec:
  template:
    spec:
      containers:
      - name: ml
        image: hongkunyoo/eks-ml:example
        imagePullPolicy: Always
        command: ["python", "train.py"]
        args: ['5', 'softmax', '0.5']
        resources:
          requests:
            cpu: "0.5"
            memory: "3Gi"
          limits:
            cpu: "1"
            memory: "5Gi"
      restartPolicy: Never
  backoffLimit: 0
```

### Build Data Pipeline

1. Workflow hello world

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow                  # new type of k8s spec
metadata:
  generateName: hello-world-    # name of the workflow spec
spec:
  entrypoint: whalesay          # invoke the whalesay template
  templates:
  - name: whalesay              # name of the template
    container:
      image: docker/whalesay
      command: [cowsay]
      args: ["hello world"]
      resources:                # limit the resources
        limits:
          memory: 32Mi
          cpu: 100m
```

2. Multi step Data Pipeline

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: steps-
spec:
  entrypoint: hello-hello-hello

  # This spec contains two templates: hello-hello-hello and whalesay
  templates:
  - name: hello-hello-hello
    # Instead of just running a container
    # This template has a sequence of steps
    steps:
    - - name: hello1            # hello1 is run before the following steps
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "hello1"
    - - name: hello2a           # double dash => run after previous step
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "hello2a"
      - name: hello2b           # single dash => run in parallel with previous step
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "hello2b"

  # This is the same template as from the previous example
  - name: whalesay
    inputs:
      parameters:
      - name: message
    container:
      image: docker/whalesay
      command: [cowsay]
      args: ["{{inputs.parameters.message}}"]
```
