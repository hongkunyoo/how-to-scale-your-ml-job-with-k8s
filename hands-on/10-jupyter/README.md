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
