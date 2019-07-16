# 7. Hello Workflow

[Argo](https://argoproj.github.io/argo/)는 쿠버네티스 workflow 프레임워크입니다. 쿠버네티스에는 아직 Job끼리의 선후관계를 나타내는 workflow를 설정하는 기능이 없습니다. 그렇기 때문에 Custom Resource Definition을 쿠버네티스를 확장시킨 Argo workflow에 대해 알아보겠습니다.  
아래의 예제를 참고하시면 여러 종류의 workflow를 제작해 보실 수 있습니다.
[Argo workflow 예제](https://argoproj.github.io/docs/argo/examples/README.html)

Argo를 사용하기 위해 먼저 아래에 준비된 helm chart를 설치해 주시기 바랍니다.
```bash
helm install charts/argo-workflow --namespace kube-system

# Get LoadBalancer external IP
kubectl get services -nkube-system
```

Argo는 아래와 같이 예쁜 workflow UI를 제공해 줍니다. 해당 UI를 접속해 보기 위해 argo-ui `service`의 external IP를 확인해 주세요.
![](https://miro.medium.com/max/1400/1*ZKFG3dbNO3S646rM1BFkrw.png)

### 1. hello whalesay
가장 간단한 wf입니다. 사실상 Job으로 대체를 해도 될만큼 간단합니다. 처음으로 workflow를 구성해보고 argo-ui를 통해 눈으로 직접 확인해 봅시다.

`kubectl apply -f 01-hello-wf.yaml`

