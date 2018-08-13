#!/usr/bin/env bash

export DATA_DIR="/data"

# Download the github-issues.zip training data to /mnt/github-issues-data
wget --directory-prefix=${DATA_DIR} https://storage.googleapis.com/kubeflow-examples/github-issue-summarization-data/github-issues.zip

# Unzip the file into /mnt/github-issues-data directory
unzip ${DATA_DIR}/github-issues.zip -d ${DATA_DIR}
