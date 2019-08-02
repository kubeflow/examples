#!/bin/bash
IMAGE=<your_registry>.azurecr.io/kubeflow/deploy
docker build -t $IMAGE . && docker run -it $IMAGE
