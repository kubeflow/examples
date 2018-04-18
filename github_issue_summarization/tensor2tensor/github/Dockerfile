FROM gcr.io/kubeflow-images-staging/tensorflow-1.7.0-notebook-gpu:latest

USER root

RUN pip install tensor2tensor && \
      apt-get install -y jq

COPY __init__.py github/__init__.py
COPY github_problem.py github/github_problem.py
COPY ps_dist_launcher.sh github/ps_dist_launcher.sh
COPY train_dist_launcher.sh github/train_dist_launcher.sh

RUN chown -R jovyan:users /home/jovyan/github

USER jovyan
