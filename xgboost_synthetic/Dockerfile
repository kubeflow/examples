# Create docker image for the demo
#
# This docker image is based on existing notebook image
# It also includes the dependencies required for training and deploying
# this way we can use it as the base image
FROM gcr.io/kubeflow-images-public/tensorflow-1.12.0-notebook-cpu:v0.5.0

USER root

COPY requirements.txt .
RUN pip3 --no-cache-dir install -r requirements.txt

RUN apt-get update -y
RUN apt-get install -y emacs

RUN pip3 install https://storage.googleapis.com/ml-pipeline/release/0.1.20/kfp.tar.gz

# Checkout kubeflow/testing because we use some of its utilities
RUN mkdir -p /src/kubeflow && \
    cd /src/kubeflow && \
    git clone https://github.com/kubeflow/testing.git testing

# Install the hub CLI for git
RUN cd /tmp && \
    curl -LO  https://github.com/github/hub/releases/download/v2.11.2/hub-linux-amd64-2.11.2.tgz && \
    tar -xvf hub-linux-amd64-2.11.2.tgz && \
    mv hub-linux-amd64-2.11.2 /usr/local && \
    ln -sf /usr/local/hub-linux-amd64-2.11.2/bin/hub /usr/local/bin/hub

# Bake a copy of update_model.py into the image
# Used for testing the code with one of jobs.
COPY update_model.py .
RUN mkdir -p /src/jlewi/kubecon-demo && \
    mv update_model.py /src/jlewi/kubecon-demo

USER jovyan