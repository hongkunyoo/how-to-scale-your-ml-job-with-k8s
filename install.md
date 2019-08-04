```bash
sudo apt-get update && \
    sudo apt-get install -y jq apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common \
&& wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    /bin/bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3 && \
    rm Miniconda3-latest-Linux-x86_64.sh && \
    echo 'export PATH=$HOME/miniconda3/bin:$PATH' >> $HOME/.bashrc && \
    $HOME/miniconda3/bin/pip install awscli && \
    source $HOME/.bashrc \
&& curl --location "https://github.com/weaveworks/eksctl/releases/download/latest_release/eksctl_$(uname -s)_amd64.tar.gz" | \
    tar xz -C /tmp && \
    sudo mv /tmp/eksctl /usr/local/bin /
&& curl -o aws-iam-authenticator https://amazon-eks.s3-us-west-2.amazonaws.com/1.11.5/2018-12-06/bin/linux/amd64/aws-iam-authenticator && \
    chmod +x ./aws-iam-authenticator && \
    sudo mv aws-iam-authenticator /usr/local/bin /
&& curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add - && \
    echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list && \
    sudo apt-get update && \
    sudo apt-get install -y kubectl \
&& curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && \
    sudo add-apt-repository \
       "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
       $(lsb_release -cs) \
       stable" && \
    sudo apt-get update && \
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io && \
    sudo usermod -aG docker $USER \
&& curl https://raw.githubusercontent.com/helm/helm/master/scripts/get | bash
```
