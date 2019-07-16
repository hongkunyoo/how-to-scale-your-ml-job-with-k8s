# 10. Launch Jupyter notebook

Jupyter notebook은 분석환경에서 많이 사용하는 툴입니다. JupyterHub는 여러 사람들이 여러 notebook을 사용할 수 있게 만든 플랫폼입니다. 쿠버네티스 위에 JupyterHub를 구축하여 여러 사람들이 여러 서버에서 notebook을 이용할 수 있게 구축해 봅시다.

```bash
openssl rand -hex 32

vim config.yaml
```

```yaml
proxy:
  secretToken: "<RANDOM_HEX>"
```

```bash
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update

RELEASE=jhub
NAMESPACE=jhub

kubectl create ns $NAMESPACE

helm upgrade --install $RELEASE jupyterhub/jupyterhub \
  --namespace $NAMESPACE  \
  --version=0.8.2 \
  --values config.yaml
```
