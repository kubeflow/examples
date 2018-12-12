#!/usr/bin/env bash

KUBEFLOW_DIR=$1
TAG=$2
GCLOUD_PROJECT=$3
PID=''

cleanup() {
  if [[ -n $PID ]]; then
    echo killing $PID
    kill -9 $PID
  fi
}
trap cleanup EXIT

portforward() {
  local pod=$1 namespace=$2 from_port=$3 to_port=$4 cmd
  kubectl port-forward $pod ${from_port}:${to_port} --namespace=$namespace 2>&1>/dev/null &
  PID=$!
  echo 'PID='$PID
}

waitforpod() {
  local cmd="kubectl get pods --no-headers -oname --selector=job-name --field-selector=status.phase=Running --namespace=kubeflow-admin" found=$(eval "$cmd") finished
  while [[ -z $found ]]; do
    sleep 1
    found=$(eval "$cmd")
  done
  found=${found#*/}
  cmd="kubectl logs $found | grep '^TensorBoard 1.12.0')"
  finished=$(eval "$cmd")
  while [[ -z $finished ]]; do
    sleep 1
    finished=$(eval "$cmd")
  done
  echo $found
}

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
echo "Waiting for training to complete and tensorboard to run... (1-2min)"
pod=$(waitforpod)
echo "Pod $pod has completed training and tensorboard is up. Setting up port-forward"
portforward $pod $namespace $port $port
echo "Opening browser to view tensorboard"
open browser http://localhost:6006
