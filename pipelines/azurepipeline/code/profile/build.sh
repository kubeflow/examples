#!/bin/bash
IMAGE=<your_registry>.azurecr.io/kubeflow/profile
docker build -t $IMAGE . && docker run -it $IMAGE
