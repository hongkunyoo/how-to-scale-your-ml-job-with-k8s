# 1. Run a basic job


1. `train.py`: 인터넷에서 mnist 데이터를 가져와서 Fully-Connected NN를 학습시키는 간단한 코드입니다.
2. `Dockerfile`: `train.py`를 도커 이미지로 변환 시킵니다.
3. `job.yaml`: Kubernetes Job을 새롭게 하나 생성합니다. 이때 `nodeSelector`를 `train-cpu`로 설정해줍니다.
4. `kubectl apply -f job.yaml`
5. `kubectl get pod`
6. `kubectl logs -f $POD_NAME`
