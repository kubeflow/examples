# Docker image to train a model using T2T
#
# For GPU use gcr.io/kubeflow-images-public/tensorflow-1.7.0-notebook-gpu:latest
# For CPU use gcr.io/kubeflow-images-public/tensorflow-1.7.0-notebook-cpu:latest
ARG BASE_IMAGE=gcr.io/kubeflow-images-public/tensorflow-1.7.0-notebook-gpu:latest
FROM $BASE_IMAGE

# Install pip packages as user jovyan
RUN pip install tensor2tensor==1.6.6 h5py

USER root

RUN apt-get install -y jq

COPY __init__.py github/__init__.py
COPY github_problem.py github/github_problem.py
COPY t2t_launcher.sh github/t2t_launcher.sh
RUN chmod a+rx github/t2t_launcher.sh

RUN chown -R jovyan:users /home/jovyan/github

USER jovyan
