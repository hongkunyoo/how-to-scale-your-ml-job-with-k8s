# 1. Run a basic job


1. `train.py`: 인터넷에서 mnist 데이터를 가져와서 Fully-Connected NN를 학습시키는 간단한 코드입니다.
2. `Dockerfile`: `train.py`를 도커 이미지로 변환 시킵니다.
3. `job.yaml`: Kubernetes Job을 새롭게 하나 생성합니다. 이때 `nodeSelector`를 `train-cpu`로 설정해줍니다.

```bash
# docker build
docker build . -t $IMAGE_NAME
# docker push
docker push $IMAGE_NAME
# job 실행
kubectl apply -f job.yaml
```

### 확인사항

#### 1. 어느 노드에서 돌고 있는지
```bash
# 어느 노드에서 실행이 되는가 확인
kubectl get node -L role
kubectl get pod -o wide
```

#### 2. 학습 로그 이상유무 확인
```bash
# 학습 log 확인
kubectl logs -f $POD_NAME
```
