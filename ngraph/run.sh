#!/usr/bin/env bash

KUBEFLOW_DIR=$1
TAG=$2
GCLOUD_PROJECT=$3

echo 'Deploying kubeflow...'
$KUBEFLOW_DIR/scripts/kfctl.sh init ngraph --platform none
cd ngraph
$KUBEFLOW_DIR/scripts/kfctl.sh generate all
cd ks_app/
ks pkg install kubeflow/jobs
ks generate single-job mnist
ks param set mnist jobName mnist
ks param set mnist jobImage gcr.io/${GCLOUD_PROJECT}/kubeflow-train:$TAG
kubectl create ns kubeflow
ks env add default --namespace kubeflow
ks apply default -c mnist
echo 'run kubectl port-forward <mnist-pod> 6006'
echo 'open browser to url http://localhost:6006'
