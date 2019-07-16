# 5. Run multiple jobs

### AWS

```bash
helm install charts/cluster-autoscaler --namespace kube-system
```

### GCP
GCP에서는 따로 cluster-autoscaler 패키지를 설치할 필요없이 플랫폼 차원에서 지원하는데요. (생성할때 `--enable-autoscaling) 
단점으로는 autoscaling의 로그를 볼 수 없다는 점과 세밀한 옵션값을 전달할수 없습니다.
