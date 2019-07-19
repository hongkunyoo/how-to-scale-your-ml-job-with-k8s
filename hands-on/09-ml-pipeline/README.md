# 9. Building ML Pipeline

지금까지 실습해본 과정들을 하나로 조합하여 Machine Learning Pipeline을 만들어 보겠습니다.
먼저 원천 데이터저장소(s3)에 있는 파일을 다운 받아 임시디렉토리 (wf-storage)에 저장을 하고(input.py)
train.py에서 각각 주어진 모델 파라미터를 이용하여 학습을 하고 그 결과를 model-storage에 저장하여 모델파일을 한 곳으로 모으고
output.py에서 학습된 모델들을 다시 s3로 업로드하고 최종적으로 SLACK 알람을 보내도록 하겠습니다.

#### AWS
```bash
# Create S3 bucket
BUCKET_NAME=k8s-ml-$(echo $(curl -s "https://helloacm.com/api/random/?n=5&x=2")| tr -d \")
aws s3 mb s3://$BUCKET_NAME

# console.aws.amazon.com에 들어가셔서 IAM User Access key를 발급 받습니다.
```

#### GCS
```bash
# Create GCS bucket
BUCKET_NAME=k8s-ml-$(echo $(curl -s "https://helloacm.com/api/random/?n=5&x=2")| tr -d \")
gsutil mb gs://$BUCKET_NAME

# console.cloud.google.com에 들어가서 GCS Interoperability를 Enable 시키고 Access key를 발급 받습니다.
```

![](img_pipeline.png)

### Script Test

```bash
pip install -r requirements.txt

# Download
ACCESS_KEY=$ACCESS_KEY SECRET_KEY=$SECRET_KEY python 01_input.py $BUCKET_NAME, $OBJECT_KEY $DOWNLOAD_FULL_PATH

# Train
python 02_train.py $EPOCHS $ACTIVATE $DROPOUT $TRAIN_PATH_NAME

# Upload
ACCESS_KEY=$ACCESS_KEY SECRET_KEY=$SECRET_KEY python 03_output.py $BUCKET_NAME, $UPLOAD_FULL_PATH
```

### pipeline.yaml 설명

#### Volumes
- wf-storage: workflow 실행 시점에서 dynamic하게 생성되는 임시 저장소(학습 데이터 저장)
- model-storage: 학습한 모델 저장소

#### Templates
- alarm-slack: workflow 종료시 slack으로 알람을 보내는 template
- input: s3에서 데이터를 받아오는 template
- train: 학습 template
- output: 학습된 모델파일을 s3로 업로드하는 template


```bash
# ml pipeline 실행
kubectl apply -f pipeline.yaml
```


### Do it more
#### 동적으로 pipeline 제작 하기

지금까지는 미리 workflow YAML 파일을 만들어서 워크플로우를 호출하였습니다. 이번에는 파이썬 스크립트를 이용하여 필요한 인자 및 모델 실험 개수를 원하는대로 늘릴 수 있게 만들어 봅시다.

1. template (pipeline-template.yaml)을 python jinja2를 이용하여 불러옵니다.
2. 학습에 필요한 인자들을 원하는 만큼 입력합니다.
3. template rendering을 합니다 --> 완성된 argo workflow 생성
4. 완성된 yaml 파일을 쿠버네티스 마스터에 전달합니다.

