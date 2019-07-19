# 7. Hello Workflow

[Argo](https://argoproj.github.io/argo/)는 쿠버네티스 workflow 프레임워크입니다. 쿠버네티스에는 아직 Job끼리의 선후관계를 나타내는 workflow를 설정하는 기능이 없습니다. 그렇기 때문에 Custom Resource Definition을 쿠버네티스를 확장시킨 Argo workflow에 대해 알아보겠습니다.  
아래의 예제를 참고하시면 여러 종류의 workflow를 제작해 보실 수 있습니다.  
[Argo workflow 예제](https://github.com/argoproj/argo/blob/master/examples/README.md)

Argo를 사용하기 위해 먼저 아래에 준비된 helm chart를 설치해 주시기 바랍니다.
```bash
helm install charts/argo-workflow --namespace kube-system

# Get LoadBalancer external IP
kubectl get services -nkube-system
```

Argo는 아래와 같이 예쁜 workflow UI를 제공해 줍니다. 해당 UI를 접속해 보기 위해 argo-ui `service`의 external IP를 확인해 주세요.
![](https://miro.medium.com/max/1400/1*ZKFG3dbNO3S646rM1BFkrw.png)

### 1. hello whalesay
가장 간단한 wf입니다. 사실상 Job으로 대체를 해도 될만큼 간단합니다. 조금 다른점이 있다면 template에 파라미터를 전달할 수 있다는 점입니다. 
처음으로 workflow를 제작해보고 argo-ui를 통해 눈으로 직접 확인해 봅시다.

```bash
cat << EOF | kubectl create -f -
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: handson-07-hello-wf
spec:
  # invoke the whalesay template with
  # "hello world" as the argument
  # to the message parameter
  entrypoint: whalesay
  arguments:
    parameters:
    - name: message
      value: hello world

  templates:
  - name: whalesay
    inputs:
      parameters:
      - name: message       # parameter declaration
    container:
      # run cowsay with that message input parameter as args
      image: docker/whalesay
      command: [cowsay]
      args: ["{{inputs.parameters.message}}"]
EOF
```

### 2. Steps

Job들을 한 step씩 차례대로 혹은 병렬로 호출하는 예제입니다.

```bash
cat << EOF | kubectl create -f -
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: handson-07-steps
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
            value: "hello"
    - - name: hello2a           # double dash => run after previous step
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "world"
      - name: hello2b           # single dash => run in parallel with previous step
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "other world"

  # This is the same template as from the previous example
  - name: whalesay
    inputs:
      parameters:
      - name: message
    container:
      image: docker/whalesay
      command: [cowsay]
      args: ["{{inputs.parameters.message}}"]
EOF
```

### 3. Exit Handler

종료시 호출되는 exit-handler에 대해서 확인해 봅시다.

```bash
cat << EOF | kubectl create -f -
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: handson-07-exit-handler
spec:
  entrypoint: hello-hello-hello
  onExit: good-bye

  # This spec contains two templates: hello-hello-hello and whalesay
  templates:
  ##########################################
  # onExit
  - name: good-bye
    container:
      image: docker/whalesay
      command: [cowsay]
      args:
      - "Good bye!"
  ##########################################


  - name: hello-hello-hello
    # Instead of just running a container
    # This template has a sequence of steps
    steps:
    - - name: hello1            # hello1 is run before the following steps
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "hello"
    - - name: hello2a           # double dash => run after previous step
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "world"
      - name: hello2b           # single dash => run in parallel with previous step
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "other world"

  # This is the same template as from the previous example
  - name: whalesay
    inputs:
      parameters:
      - name: message
    container:
      image: docker/whalesay
      command: [cowsay]
      args: ["{{inputs.parameters.message}}"]
EOF
```

### Do it more

#### 1. workfow의 결과를 Exit Handler가 받아서 메세지로 출력해 봅시다.

[참고 자료](https://github.com/argoproj/argo/blob/master/examples/README.md#exit-handlers)

#### 2. 아래와 같은 workflow를 제작해 봅시다.

![](../08-wf-dag/dag.png)
