#FROM nvidia/cuda:9.0-cudnn7-runtime-ubuntu18.04
#FROM tensorflow/tensorflow:devel-gpu
FROM python:3.6.8

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
ENV PATH=/root/miniconda3/bin:${PATH}

#RUN pip install tensorflow-gpu==1.5
RUN pip install tensorflow==1.5
RUN pip install keras==2.0.8
RUN pip install h5py==2.7.1
RUN pip install boto3

ADD 01_input.py input.py
ADD 02_train.py train.py
ADD 03_output.py output.py
