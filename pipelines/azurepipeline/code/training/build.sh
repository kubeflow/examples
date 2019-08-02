#!/bin/bash
IMAGE=<your_registry>.azurecr.io/kubeflow/training
docker build -t $IMAGE . && docker run -it $IMAGE
