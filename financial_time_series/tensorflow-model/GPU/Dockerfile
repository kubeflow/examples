FROM tensorflow/tensorflow:1.8.0-devel-gpu-py3
MAINTAINER Sven Degroote "sven.degroote@ml6.eu"

RUN apt-get update -y && \
    apt-get install -y build-essential python-numpy python-dev python3-pip python3 wget

RUN pip3 install --upgrade pip setuptools

# Install packages
COPY requirements.txt .
RUN pip3 install  -r requirements.txt
RUN pip3 uninstall protobuf -y
RUN pip3 install tensorflow-gpu==1.8.0
RUN pip3 install --upgrade google-cloud-bigquery

# Verify that tensorflow is installed
RUN pip3 show tensorflow

COPY . /opt/workdir
WORKDIR /opt/workdir

