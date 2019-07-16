# 5. Run multiple jobs

여러개의 기계학습 Job을 동시에 실행시켜 보겠습니다.
쿠버네티스를 이용하여 기계학습을 한다면 다음과 같은 장점을 얻을 수 있습니다. 

- 스케줄링이 편리해집니다: 사람이 직접 스케줄링하던 기계학습 훈련을 쿠버네티스에게 맡깁니다. 학습 서버가 증가할수록 그 효과는 커집니다.
- 확장성: 리소스가 부족하여 서버를 추가해야 할때 확장이 용이해 집니다.
- Job 관리가 편리해 집니다: 현재 어떤 잡이 실행되고 있는지, 어떤 잡이 끝났는지, 장애 발생여부 등 
- 모니터링이 편리해 집니다: 리소스 사용량, 기계학습 로그 모니터링
- 배포가 쉬워집니다: 라이브러리, 소스코드
- 장애에 견고해집니다: 장애발생시, 쉽게 대응할 수 있고 견고해집니다.

실행하기에 앞서 먼저 cluster-autoscaler를 설치하겠습니다.

### AWS

```bash
helm install charts/cluster-autoscaler --namespace kube-system
```

### GCP
GCP에서는 따로 cluster-autoscaler 패키지를 설치할 필요없이 플랫폼 차원에서 지원하는데요. (생성할때 `--enable-autoscaling) 
단점으로는 autoscaling의 로그를 볼 수 없다는 점과 세밀한 옵션값을 전달할수 없습니다.


- `experiments.yaml`: 사용자정의 학습 스크립트 및 모델 파라미터
- `run-multi.py`: template을 두고 사용자가 정의한 정보들을 순차적으로 접어 넣어 job을 완성시킵니다. 



```bash
# PyYaml 설치
pip install -r requirements.txt

# multi job 실행
python run-multi.py

# 쿠버네티스 스케줄링 확인
kubectl get pod -owide

# 서버 리소스 사용량 확인
kubectl top node

# Job 리소스 사용량 확인
kubectl top pod

# 각 기계학습 Job 로그 확인
kubectl logs -f $POD_NAME
```
