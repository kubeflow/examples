#!/usr/bin/env bash

set -ex

# Default namespace to deploy the ksonnet component to
NAMESPACE="kubeflow"
# Providing negative value to kubeflow wait would wait for a week
TIMEOUT="-1s"

usage()
{
    echo "usage: deploy.sh
    [--working_dir The base GCS bucket ]
    [--component What ksonnet component to run. Available components: search-index-creator ]
    [--timeout How long to wait for the job to finish. e.g. 30m, 1h ]
    [--namespace Namespace to deploy the ksonnet component to ]
    [-h help]"
}

while [ "$1" != "" ]; do
    case $1 in
      --working_dir )
        shift
        WORKING_DIR=$1
        ;;
      --component )
        shift
        COMPONENT=$1
        ;;
      --timeout )
        shift
        TIMEOUT=$1
        ;;
      --namespace )
        shift
        NAMESPACE=$1
        ;;
      -h | --help )
        usage
        exit
        ;;
      * )
        usage
        exit 1
    esac
    shift
done

KUBECTL_CLUSTER_NAME="kubeflow"
KUBECTL_CONTEXT_NAME="kubeflow"
# Configure kubectl to use the underlying cluster
kubectl config set-cluster "${KUBECTL_CLUSTER_NAME}" --server=https://kubernetes.default --certificate-authority=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
kubectl config set-credentials pipeline --token "$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)"
kubectl config set-context "${KUBECTL_CONTEXT_NAME}" --cluster "${KUBECTL_CLUSTER_NAME}" --user pipeline
kubectl config use-context "${KUBECTL_CONTEXT_NAME}"

KS_ENV_NAME="code-search"
# Update Ksonnet to point to the Kubernetes Cluster
ks env add "${KS_ENV_NAME}" --context $(kubectl config current-context)
# Update Ksonnet to use the namespace where kubeflow is deployed. By default it's 'kubeflow'
ks env set "${KS_ENV_NAME}" --namespace="${NAMESPACE}"
# Update the Working Directory of the application
sed -i'' "s,gs://example/prefix,${WORKING_DIR}," components/params.libsonnet

echo "running ks apply ${KS_ENV_NAME} -c ${COMPONENT}"
ks apply "${KS_ENV_NAME}" -c "${COMPONENT}"

echo "wait for ${COMPONENT} to finish"

if [ "${COMPONENT}" = "search-index-creator" ]; then
  kubectl wait --timeout="${TIMEOUT}" --for=condition=complete job/search-index-creator -n "${NAMESPACE}"
  # If the wait above failed, then the script will fail fast and following command won't run.
  # TODO complete doesn't mean it's successful. Check the job succeeded.
  echo "search-index-creator is succeeded"
fi