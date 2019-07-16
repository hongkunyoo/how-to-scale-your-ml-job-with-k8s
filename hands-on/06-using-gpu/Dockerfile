FROM FROM nvidia/cuda:9.2-cudnn7-runtime-ubuntu18.04

RUN apt-get update \
        && apt-get install -y --no-install-recommends \
               curl \
               locales \
               vim-tiny \
               wget \
               build-essential \
               unzip \
               ca-certificates

RUN curl -LO https://repo.continuum.io/miniconda/Miniconda3-4.4.10-Linux-x86_64.sh
RUN bash Miniconda3-4.4.10-Linux-x86_64.sh -p $HOME/miniconda3 -b
RUN rm Miniconda3-4.4.10-Linux-x86_64.sh
ENV PATH=$HOME/miniconda3/bin:${PATH}

RUN pip install tensorflow-gpu==1.5
RUN pip install keras==2.0.8
RUN pip install h5py==2.7.1

ADD train.py .
