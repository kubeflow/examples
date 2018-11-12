#!/usr/bin/env bash

set -ex

kubectl config set-cluster kubeflow --server=https://kubernetes.default --certificate-authority=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
kubectl config set-credentials pipeline --token "$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)"
kubectl config set-context kubeflow --cluster kubeflow --user pipeline
kubectl config use-context kubeflow

# Update Ksonnet to point to the Kubernetes Cluster
ks env add code-search --context $(kubectl config current-context)

# Update Ksonnet to use the namespace where kubeflow is deployed. By default it's 'kubeflow'
ks env set code-search --namespace=kubeflow

# Update the Working Directory of the application
sed -i'' "s,gs://example/prefix,${WORKING_DIR}," components/params.libsonnet


#
#
#echo environment
#env | sort
#WORKER_ID=$(echo ${TF_CONFIG} | jq ".task.index")
#WORKER_TYPE=$(echo ${TF_CONFIG} | jq -r ".task.type")
#MASTER_INSTANCE=$(echo ${TF_CONFIG} | jq -r ".cluster.${WORKER_TYPE}[${WORKER_ID}]")
#"$@" \
#  --master=grpc://${MASTER_INSTANCE} \
#  --worker_id=${WORKER_ID} \
#
## Sleep to give fluentd time to capture logs
#sleep 120
