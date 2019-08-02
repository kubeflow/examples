#!/bin/bash
IMAGE=<your_registry>.azurecr.io/kubeflow/preprocess
docker build -t $IMAGE . && docker run -it $IMAGE
