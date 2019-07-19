# Using GPUs

특정 ML job은 GPU 위에서 실행시키는 것이 엄청난 효율을 가져옵니다. (Deep Learning 계열) 하지만 GPU는 다른 리소스에 비해 비용이 많이 발생합니다. 
그렇기 때문에 다른 서버와는 다르게 GPU서버는 정말 필요할 때만 생성하고 사용하지 않을때에는 삭제하도록 하겠습니다. 만약에 직접 서버를 관리하였더라면 매번 서버를 실행하여 필요한 패키지를 설치하고 
Deep Learning 코드를 다운 받아서 실행시켜줬어야 합니다. 쿠버네티스를 이용한다면 이 모든 것을 한방에 해결하실 수 있습니다.



### AWS - GPU worker node 구성
```bash
# GPU worker node 생성
CLUSTER_NAME=k8s-ml
eksctl create nodegroup --cluster $CLUSTER_NAME --name train-gpu --nodes-min 0 --nodes-max 1 --nodes 0 --node-labels "role=train-gpu" --node-type p3.2xlarge --asg-access

# 생성 확인
eksctl get nodegroup --cluster $CLUSTER_NAME

# k8s.io/cluster-autoscaler/node-template/label/role 라벨 부여
NG_STACK=eksctl-$CLUSTER_NAME-nodegroup-train-gpu
ASG_ID=$(aws cloudformation describe-stack-resource --stack-name $NG_STACK --logical-resource-id NodeGroup --query StackResourceDetail.PhysicalResourceId --output text)
REGION=$(aws configure get region)

aws autoscaling create-or-update-tags --tags ResourceId=$ASG_ID,ResourceType=auto-scaling-group,Key=k8s.io/cluster-autoscaler/node-template/label/role,Value=train-gpu,PropagateAtLaunch=true

# GPU plugin 설치 
# - Expose the number of GPUs on each nodes of your cluster
# - Keep track of the health of your GPUs
# - Run GPU enabled containers in your Kubernetes cluster.
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.11/nvidia-device-plugin.yml
```

### GCP - GPU worker node 구성

```bash
gcloud container node-pools create train-gpu \
    --cluster $CLUSTER_NAME \
    --node-labels=role=train-gpu \
    --enable-autoscaling \
    --min-nodes=0 \
    --num-nodes=0 \
    --max-nodes=1 \
    --accelerator type=nvidia-tesla-k80,count=1 \
    --machine-type=n1-standard-4

kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/stable/nvidia-driver-installer/cos/daemonset-preloaded.yaml
```

---

### AWS - Run GPU job

GPU 노드를 선택할 수 있도록 `nodeSelector`를 수정해 줍니다.

```yaml
    nodeSelector:
      role: train-gpu
```

### GCP - Run GPU job

GCP에서는 한 클러스터에서 non-GPU node pool과 GPU node pool을 동시에 사용하면 GPU node pool에 다음과 같은 `taint`를 삽입한다고 합니다. 그렇기 때문에 아래의 `taint`에 대한 적절한 `tolerations` 설정을 해줘야 합니다.
[참고자료](https://cloud.google.com/kubernetes-engine/docs/how-to/gpus#create)

```yaml
    nodeSelector:
      role: train-gpu
    tolerations:
    - key: nvidia.com/gpu
      value: present
      effect: NoSchedule
```

### Do it more (AWS only)

cluster autoscaler에 직접 들어가서 어떤 옵션들을 수정할 수 있는지 알아봅시다.
