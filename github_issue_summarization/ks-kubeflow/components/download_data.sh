#!/bin/bash
#
# Script to download the data
set -ex

DATA_DIR=/data

mkdir -p ${DATA_DIR}

wget --directory-prefix=${DATA_DIR} \
	https://storage.googleapis.com/kubeflow-examples/github-issue-summarization-data/github-issues.zip

unzip -d ${DATA_DIR} ${DATA_DIR}/github-issues.zip
