FROM tensorflow/tensorflow:1.13.2-gpu-py3

RUN pip install keras==2.0.8
RUN pip install h5py==2.7.1
RUN pip install boto3

ADD 01_input.py input.py
ADD 02_train.py train.py
ADD 03_output.py output.py
