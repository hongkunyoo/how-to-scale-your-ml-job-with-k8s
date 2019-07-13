## Open Infrastructure & Cloud Native Days Korea 2019 Track 7

*Hands-on session*

How to scale your ML job with Kubernetes

### Prequisition
- AWS 계정 or GCP 계정
- Kubernetes 기본 지식
  - Deployments
  - Services
  - Jobs
  - Ingress

#### 워크샵 순서
1. Why Kubernetes? (발표)
2. Provisioning K8S on AWS / GCP  (핸즈온)
3. Data pipeline 구축 & Distributed ML 학습하기 (핸즈온)

### 1. Why Kubernetes?

2019 AWS summit Seoul에서 발표한 "Amazon EKS를 활용하여 기계학습 서버 확장하기"를 토대로 워크샵을 진행합니다.
- [slide](https://www.slideshare.net/awskorea/amazon-eks-lg-aws-summit-seoul-2019)
- [video](https://www.youtube.com/watch?v=egv2TlfLL1Y&list=PLORxAVAC5fUXSZaun-15IvzUhO3YmvtdV)

[워크샵 발표 내용](whyk8s.pdf) (사내 검토 중)

### 2. Provisioning K8S

#### On AWS

사용할 리소스
- EKS: k8s 마스터
- EC2: bastion 서버, worker 노드
- ELB: Ingress
- ECR: ML scripts
- EFS: 모델 저장소
- S3: 학습 데이터

---

##### eksctl
[eksctl](https://github.com/weaveworks/eksctl)은 weaveworks에서 개발한 Amazon EKS CLI 툴입니다. 재밌는 것은 이것은 AWS에서 만든 것이 아니라 Kubernetes Network Provider중 하나인 weavenetwork를 만든 회사(Weaveworks)라는 회사에서 개발했다는 점입니다. 오늘 AWS 플랫폼 위에서는 eksctl을 이용하여 k8s 클러스터를 구축할 예정입니다.

##### aws-iam-authenticator
[aws-iam-authenticator](https://github.com/kubernetes-sigs/aws-iam-authenticator)도 마찬가지로 재밌는 사실은 원래는 heptio라는 회사에서 개발한 IAM 권한 획득 툴입니다. 현재는 kubernetes-sigs(special interest group)에서 관리합니다.
EKS는 기본적으로 AWS IAM을 이용하여 k8s RBAC과 연동합니다. 이때 필요한 것이 aws-iam-authenticator라는 녀석입니다.  
![](https://docs.aws.amazon.com/eks/latest/userguide/images/eks-iam.png)

##### kubectl

##### helm

##### helm chart
- metrics-server
- cluster-autoscaler
- minio
- efs-provisioner
- prometheus
- grafana
- nginx-ingress
- argo workflow

```bash
CLUSTER_NAME=openinfra
REGSION=ap-northeast-2

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
eksctl create cluster --name $CLUSTER_NAME --region $REGION --node-type m5.large --nodes-min=1 --nodes-max=3

# installing metric server
cat <<EOF | kubectl create -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: default-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: default
  namespace: kube-system
EOF

helm init --service-account default

NG_ID=$(eksctl get nodegroup --cluster $CLUSTER_NAME | cut -d ' ' -f1 | sed 1d | cut -f2)
NG_STACK=eksctl-$CLUSTER_NAME-nodegroup-$NG_ID
ASG_ID=$(aws cloudformation describe-stack-resource --stack-name $NG_STACK --logical-resource-id NodeGroup --query StackResourceDetail.PhysicalResourceId --output text)
REGION=$(aws configure get region)

aws autoscaling create-or-update-tags --tags ResourceId=$ASG_ID,ResourceType=auto-scaling-group,Key=k8s.io/cluster-autoscaler/enabled,Value=,PropagateAtLaunch=true
aws autoscaling create-or-update-tags --tags ResourceId=$ASG_ID,ResourceType=auto-scaling-group,Key=k8s.io/cluster-autoscaler/$CLUSTER_NAME,Value=,PropagateAtLaunch=true

NODE_ROLE=$(aws cloudformation describe-stack-resource --stack-name $NG_STACK --logical-resource-id NodeInstanceRole --query StackResourceDetail.PhysicalResourceId --output text)
aws iam put-role-policy --role-name $NODE_ROLE --policy-name autoscale --policy-document '{ "Version": "2012-10-17", "Statement": [ { "Effect": "Allow",  "Action": [ "autoscaling:*" ], "Resource": "*" } ] }'

```
#### On GCP

사용할 리소스
- GKE: k8s 마스터
- GCE: bastion 서버, worker 노드
- CLB: Ingress
- GCR: ML scripts
- FileStore: 모델 저장소
- GCS: 학습 데이터

https://console.cloud.google.com 접속
```bash
gcloud config set compute/zone asia-northeast2-a

CLUSTER_NAME=openinfra

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

#### Enable GPU

```bash
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.11/nvidia-device-plugin.yml
```

#### Install helm packages

```bash
helm install stable/metrics-server --name stats --namespace kube-system --set 'args={--logtostderr,--metric-resolution=2s}'
helm install stable/cluster-autoscaler --name autoscale --namespace kube-system --set autoDiscovery.clusterName=$CLUSTER_NAME,awsRegion=$REGION,sslCertPath=/etc/kubernetes/pki/ca.crt
```
#### Run ML jobs

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

#### Build Data Pipeline

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
