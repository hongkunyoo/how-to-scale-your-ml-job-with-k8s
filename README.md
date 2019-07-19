# Open Infra & Cloud Native Days Korea 2019 Track 7

*Hands-on session*

How to scale your ML job with Kubernetes (커피고래 유홍근)

* 내용: 데이터과학자, 분석가 입장에서 조금 더 편리하게 기계학습을 실험해 보고 여러 서버에 걸쳐서 손쉽게 기계학습 잡을 확장시키는 방법에 대해서 알아보도록 하겠습니다.
* 워크샵 소요시간: 2시간~2시간30분
* 준비 사항: AWS or GCP 계정
* 난이도: 중
* 대상 청중
    - 쿠버네티스를 활용하여 ML job 실행에 관심 있으신 분
    - Kubernetes 기본 지식(pod, job 등)
    - Job, Argo workflow  등을 실습할 예정입니다.
    - 이미 kubeflow 등 쿠버네티스를 이용한 ML툴을 사용해 보신 분들한테는 쉬울 수 있습니다.

## 워크샵 순서
1. [Why Kubernetes? (간략 소개)](#1-why-kubernetes)
2. Provisioning K8S (핸즈온)
    - [on AWS](#on-aws)
    - [on GPC](#on-gcp)
3. [How to scale your ML job (핸즈온)](#3-how-to-scale-your-ml-job-with-k8s)
    - Run a Basic Job
    - Save a model file to model storage
    - Exception handling
    - Training with hyper-parameters
    - Run multiple jobs
    - Using GPUs
    - Hello workflow
    - DAG workflow
    - Building ML Pipeline
    - Launch Jupyter notebook
    - Kubeflow tutorials

## 1. Why Kubernetes?

2019 AWS summit Seoul에서 발표한 "Amazon EKS를 활용하여 기계학습 서버 확장하기"를 토대로 워크샵을 진행합니다.
- [slide](https://www.slideshare.net/awskorea/amazon-eks-lg-aws-summit-seoul-2019)
- [video](https://www.youtube.com/watch?v=egv2TlfLL1Y&list=PLORxAVAC5fUXSZaun-15IvzUhO3YmvtdV)

[워크샵 발표 내용](res/whyk8s.pdf)
![](res/intro.png)

## 2. Provisioning K8S

Production 환경에서 제대로 클러스터를 구축한다면 private k8s 구축 및 도메인 네임 설정 & Ingress 설정을 해야하지만 본 워크샵에서는 생략하도록 하겠습니다.

### On AWS

사용할 리소스
- EKS: k8s 마스터
- EC2: kubectl 명령 서버, worker 노드
- ELB: Ingress
- ECR: ML scripts
- EFS: 모델 저장소
- S3: 학습 데이터
- VPC: default VPC

![](res/k8s-ml-aws.png)

#### 설치 목록

##### eksctl
[eksctl](https://github.com/weaveworks/eksctl)은 weaveworks에서 개발한 Amazon EKS CLI 툴입니다. 재밌는 것은 이것은 AWS에서 만든 것이 아니라 Kubernetes Network Provider중 하나인 weavenetwork를 만든 회사(Weaveworks)라는 회사에서 개발했다는 점입니다. 오늘 AWS 플랫폼 위에서는 eksctl을 이용하여 k8s 클러스터를 구축할 예정입니다.

##### aws-iam-authenticator
[aws-iam-authenticator](https://github.com/kubernetes-sigs/aws-iam-authenticator)도 마찬가지로 재밌는 사실은 원래는 heptio라는 회사에서 개발한 IAM 권한 획득 툴입니다. 현재는 kubernetes-sigs(special interest group)에서 관리합니다.
EKS는 기본적으로 AWS IAM을 이용하여 k8s RBAC과 연동합니다. 이때 필요한 것이 aws-iam-authenticator라는 녀석입니다.  
![](https://docs.aws.amazon.com/eks/latest/userguide/images/eks-iam.png)

##### kubectl
[kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)은 쿠버네티스 마스터와 대화할 수 있는 CLI툴입니다.

##### helm
[helm](https://helm.sh/)이란 쿠버네티스 package manager입니다. 해당 툴을 이용하여 필요한 모듈들을 쿠버네티스에 설치할 수 있습니다. apt, yum, pip 툴들과 비슷한 녀석이라고 생각하시면 됩니다.
오늘 helm을 통해서 Distributed ML job에 필요한 패키지들을 설치해볼 예정입니다.

##### helm chart
helm chart는 helm을 통해 설치하는 패키지 레포지토리를 말합니다. 오늘은 다음 chart들을 설치해볼 예정입니다.
- argo workflow: Data pipeline & ML workflow를 실행 시켜줄 wf engine입니다.
- nfs-client-provisioner: NAS 서버(EFS)와 연결 시켜주는 Storage Provisioner입니다.
- minio: NAS 서버를 웹으로 통해 볼 수 있게 minio UI를 사용합니다.
- cluster-autoscaler: 요청한 자원 만큼 서버 리소스를 늘려주는 k8s autoscaler입니다.
- metrics-server: 서버의 리소스 사용량을 확인하는 패키지입니다. (kubectl top node)

<details>
  <summary><b>상세 설정 방법</b></summary>

#### IAM User 생성 및 권한 부여
1. EKS Admin policy 생성

- *IAM 접속 - Policies - Create policy - JSON*
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
          "ecr:*",
          "ec2:*",
          "eks:*",
          "iam:*",
          "s3:*",
          "elasticfilesystem:*",
          "autoscaling:*",
          "cloudformation:*"
      ],
      "Resource": "*"
    }
  ]
}
```
**매우 강력한 권한이니 워크샵이 끝난 이후 삭제 바랍니다.**

- *Review policy*
- *Name*: EKS-admin

2. User 생성

- *User name*: k8s-ml
- *Access type*: Programmatic access
- *Next Permissions*
- *Attach existing policies directly*: EKS-admin 검색
- *Next Tags* - *Next Review* - *Create user*
- Access key, Secret key 저장

#### Setup

가장 먼저 EKS 마스터에 명령을 전달할 EC2 서버 하나를 생성합니다. 본인의 PC에서 직접 작업을 진행하셔도 무방합니다.
본 워크샵은 Ubuntu 18.04 위에서 정상적으로 동작하도록 구성이 되어 있습니다.
먼저 kubectl 명령 서버를 하나 만들겠습니다.
http://console.aws.amazon.com

```bash
# git clone
git clone https://github.com/hongkunyoo/how-to-scale-your-ml-job-with-k8s.git && cd how-to-scale-your-ml-job-with-k8s

# install jq
sudo apt-get update && \
    sudo apt-get install -y jq apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common 


# install awscli
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    /bin/bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3 && \
    rm Miniconda3-latest-Linux-x86_64.sh && \
    echo 'export PATH=$HOME/miniconda3/bin:$PATH' >> $HOME/.bashrc && \
    $HOME/miniconda3/bin/pip install awscli && \
    source $HOME/.bashrc

# AWS user configure
aws configure
# access key: XXX
# secret key: XXX
# region: ap-northeast-2

# 클러스터 이름과 리전을 설정합니다.
CLUSTER_NAME=k8s-ml

# installing eksctl
curl --location "https://github.com/weaveworks/eksctl/releases/download/latest_release/eksctl_$(uname -s)_amd64.tar.gz" | \
    tar xz -C /tmp && \
    sudo mv /tmp/eksctl /usr/local/bin

# installing heptio-authenticator
curl -o aws-iam-authenticator https://amazon-eks.s3-us-west-2.amazonaws.com/1.11.5/2018-12-06/bin/linux/amd64/aws-iam-authenticator && \
    chmod +x ./aws-iam-authenticator && \
    sudo mv aws-iam-authenticator /usr/local/bin

# installing kubectl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add - && \
    echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list && \
    sudo apt-get update && \
    sudo apt-get install -y kubectl

# install docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && \
    sudo add-apt-repository \
       "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
       $(lsb_release -cs) \
       stable" && \
    sudo apt-get update && \
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io && \
    sudo usermod -aG docker $USER


# Create k8s cluster
eksctl create cluster --name $CLUSTER_NAME --without-nodegroup

# default worker node 구성
eksctl create nodegroup --cluster $CLUSTER_NAME --name default --nodes-min 1 --nodes-max 1 --nodes 1 --node-labels "role=default" --node-type m5.xlarge --asg-access

# CPU worker node 구성
eksctl create nodegroup --cluster $CLUSTER_NAME --name train-cpu --nodes-min 1 --nodes-max 8 --nodes 2 --node-labels "role=train-cpu" --node-type c5.xlarge --asg-access

# MEM worker node 구성
eksctl create nodegroup --cluster $CLUSTER_NAME --name train-cpu --nodes-min 1 --nodes-max 2 --nodes 1 --node-labels "role=train-mem" --node-type r5.xlarge  --asg-access

# 클러스터 확인
kubectl get node -L role

# Create EFS filesystem
FS_ID=$(aws efs create-file-system --creation-token $CLUSTER_NAME | jq -r .FileSystemId)

# Manage file system access
# AWS console

# installing helm client
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get | bash

# RBAC setting
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

# installing helm
helm init --service-account default
```

```bash
# before installing helm chart, change values
vi charts/nfs-client-provisioner/values.yaml
```

```yaml
# line 14
nfs:
  server: !(FS_ID).efs.ap-northeast-2.amazonaws.com
  path: /
```

```bash
vi charts/minio/values.yaml
```

```yaml
# line 45
nfsServer: !(FS_ID).efs.ap-northeast-2.amazonaws.com
nfsServerPath: /
```

```bash
# install helm charts
helm install charts/nfs-client-provisioner --namespace kube-system
helm install charts/minio --namespace kube-system
helm install charts/metrics-server --namespace kube-system

# check all chart is running
kubectl get pod -n kube-system

echo "This is your ECR repository: "$(aws sts get-caller-identity | jq -r .Account).dkr.ecr.ap-northeast-2.amazonaws.com/\$IMAGE_NAME
aws ecr create-repository --repository-name k8s-ml
$(aws ecr get-login --no-include-email)
```

</details>


---

### On GCP

![](res/gcp.png)

사용할 리소스
- GKE: k8s 마스터
- GCE: worker 노드
- CLB: Ingress
- GCR: ML scripts
- FileStore: 모델 저장소
- GCS: 학습 데이터
- VPC: default VPC

![](res/k8s-ml-gcp.png)

#### 설치 목록

GCP에서는 Cloud Console이라는 훌륭한 콘솔이 기본적으로 제공되고 대부분 이미 설치가 되어 있기 때문에 필요한 helm chart만 바로 설치하면 됩니다.
##### helm chart
- argo workflow: Data pipeline & ML workflow를 실행 시켜줄 wf engine입니다.
- nfs-client-provisioner: NAS 서버(EFS)와 연결 시켜주는 Storage Provisioner입니다.
- minio: NAS 서버를 웹으로 통해 볼 수 있게 minio UI를 사용합니다.
- ~~cluster-autoscaler~~: GCP 자체적으로 autoscale을 지원합니다. 단점은 세부적인 option 설정이 불가능합니다.
- ~~metrics-server~~: GKE를 생성할때 metrics-server 설치 옵션을 넣으주면 자동으로 설치되어서 나옵니다.


https://console.cloud.google.com 접속

<details>
  <summary><b>상세 설정 방법</b></summary>

```bash
git clone https://github.com/hongkunyoo/how-to-scale-your-ml-job-with-k8s.git && cd how-to-scale-your-ml-job-with-k8s

gcloud components update

gcloud config set compute/zone us-central1-a

CLUSTER_NAME=k8s-ml

gcloud container clusters create $CLUSTER_NAME \
    --num-nodes=1 \
    --node-labels=role=default \
    --machine-type=n1-standard-4 \
    --node-locations=us-central1-a


gcloud container node-pools create train-cpu \
    --cluster $CLUSTER_NAME \
    --node-labels=role=train-cpu \
    --enable-autoscaling \
    --min-nodes=1 \
    --num-nodes=2 \
    --max-nodes=8 \
    --machine-type=n1-highcpu-8


gcloud container node-pools create train-mem \
    --cluster $CLUSTER_NAME \
    --node-labels=role=train-mem \
    --enable-autoscaling \
    --min-nodes=1 \
    --num-nodes=1 \
    --max-nodes=2 \
    --machine-type=n1-highmem-8

# 클러스터 확인
kubectl get node -L role

# RBAC setting
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

# installing helm
helm init --service-account default

# Create Cloud FileStore
gcloud filestore instances create nfs-storage \
    --project=$DEVSHELL_PROJECT_ID \
    --file-share=name="vol",capacity=1TB \
    --zone=us-central1-a \
    --network=name="default",reserved-ip-range="10.0.0.0/29"
```

```bash
vi charts/nfs-client-provisioner/values.yaml
```

```yaml
# line 14
nfs:
  server: 10.0.0.2
  path: /vol
```

```bash
vi charts/minio/values.yaml
```

```yaml
# line 45
nfsServer: 10.0.0.2
nfsServerPath: /vol
```

```bash
# install helm charts
helm install charts/nfs-client-provisioner --namespace kube-system
helm install charts/minio --namespace kube-system

kubectl get pod -n kube-system

echo "This is your GCR repository: "gcr.io/$(gcloud config get-value project)/IMAGE
```

</details>


## 3. How to scale your ML job with k8s

### [1. Run a basic job](hands-on/01-run-job)
몸풀기! 간단한 `train.py` 코드를 이용하여 도커 이미지를 만들고 Job을 이용하여 학습을 시켜보겠습니다.

### [2. Save a model file to model storage](hands-on/02-save-model)
기계학습을 통해 얻어진 모델을 한곳에서 관리하고 싶을 때는 어떻게할 할수 있을까요?
매번 S3로 모델을 업로드하는 것이 귀찮으신가요?
NFS storage 타입 PVC를 이용하여 filesystem에 저장하는 것 만으로 모델을 한곳에 모아서 관리할 수 있게 구성해 봅시다.

### [3. Exception handling](hands-on/03-exception)
간혹 한개의 문제가 되는 학습 job 때문에 서버 전체에 장애가 발생하는 경우가 있습니다.
쿠버네티스를 이용한다면 문제가 되는 job 하나만을 종료되게끔 만들 수 있습니다.
인위적으로 Out of Memory 상황을 발생 시켜 쿠버네티스가 어떻게 handling하는지 확인해 보도록 하겠습니다.

### [4. Training with hyper-parameters](hands-on/04-train-hp)
여러가지 종류의 하이퍼파라미터들을 실험해 보고 싶을때는 어떻게 하면 좋을까요?
단순히 프로세스 파라미터 전달 방법 외에 다른 방법이 있을까요?
`ConfigMap`을 이용하여 파일 기반의 모델 파라미터를 전달해 봅시다.

### [5. Run multiple jobs](hands-on/05-run-multi)
복수의 기계학습 job을 동시에 실행 시켜봅니다. 다음과 같은 것을 확인해볼 예정입니다.
- 스케줄링
- Job 진행 상황
- 모니터링
- 에러처리
- Autoscaling

### [6. Using GPUs](hands-on/06-using-gpu/)
쿠버네티스에서 GPU 자원을 사용하는 방법에 대해서 알아보도록 하겠습니다.
특히나 GPU 자원은 비용이 비싸기 때문에 서버의 개수가 0개부터 시작하여 autoscaling이 되도록 설정해보겠습니다.

### [7. Hello workflow](hands-on/07-hello-wf/)
간단하게 Argo workflow에 대해서 알아보도록 하겠습니다.
Argo workflow란 쿠버네티스 job끼리 서로 dependency를 가실 수 있게 만들어주는 프레임워크입니다.
오늘 저희는 argo workflow를 이용하여 Data Pipeline을 만들어 볼 예정입니다.

### [8. DAG workflow](hands-on/08-wf-dag/)
Argo workflow를 이용하여 DAG (Directed acyclic graph)를 만드는 법을 살펴보겠습니다.
조금 복잡할 수도 있어서 따로 구분하여 hands-on을 준비하였습니다.

### [9. Building ML Pipeline](hands-on/09-ml-pipeline/)
Argo workflow를 이용하여 최종적으로 Data Pipeline을 만들어 보도록 하겠습니다.
S3에서 데이터를 가져와서 병렬로 분산하여 기계학습을 실행하여 NAS storage에 학습된 모델을 저장하고 최종적으로 slack으로 알람이 가게끔 만들어 보겠습니다.

### [10. Launch Jupyter notebook](hands-on/10-jupyter/)
JupyterHub를 이용하여 쿠버네티스 상에서 분석할 수 있는 환경을 구축해 보겠습니다.

### [11. Kubeflow tutorials](hands-on/11-kubeflow/) (Advanced - GCP only)
Kubernetes + tensorflow 조합으로 탄생한 kubeflow에 대해서 간단히 알아보고  
codelab 튜토리얼에 대해서 소개해 드립니다.

