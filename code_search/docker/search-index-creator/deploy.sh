#!/usr/bin/env bash

set -ex

# The name of the cluster where the pipeline runs
KUBECTL_CLUSTER_NAME="kubeflow"
# Default namespace to deploy the ksonnet component to
NAMESPACE="kubeflow"
# Providing negative value to kubeflow wait would wait for a week
TIMEOUT="-1s"
# Ksonnet Environment name. Always use pipeline
KS_ENV_NAME="pipeline"
# Search index creator ksonnet component name
COMPONENT="search-index-creator"

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
      --workflow_id )
        shift
        WORKFLOW_ID=$1
        ;;
      --data_dir )
        shift
        DATA_DIR=$1
        ;;
      --timeout )
        shift
        TIMEOUT=$1
        ;;
      --namespace )
        shift
        NAMESPACE=$1
        ;;
      --cluster )
        shift
        KUBECTL_CLUSTER_NAME=$1
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

KUBECTL_CONTEXT_NAME="kubeflow"
# Configure kubectl to use the underlying cluster
kubectl config set-cluster "${KUBECTL_CLUSTER_NAME}" --server=https://kubernetes.default --certificate-authority=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
kubectl config set-credentials pipeline --token "$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)"
kubectl config set-context "${KUBECTL_CONTEXT_NAME}" --cluster "${KUBECTL_CLUSTER_NAME}" --user pipeline
kubectl config use-context "${KUBECTL_CONTEXT_NAME}"
ks env set "${KS_ENV_NAME}" --namespace="${NAMESPACE}"

# Apply parameters
ks param set ${COMPONENT} dataDir ${DATA_DIR} --env ${KS_ENV_NAME}
ks param set ${COMPONENT} jobNameSuffix ${WORKFLOW_ID} --env ${KS_ENV_NAME}
ks param set ${COMPONENT} lookupFile ${WORKING_DIR}/code-embeddings-index/${WORKFLOW_ID}/embedding-to-info.csv --env ${KS_ENV_NAME}
ks param set ${COMPONENT} indexFile ${WORKING_DIR}/code-embeddings-index/${WORKFLOW_ID}/embeddings.index --env ${KS_ENV_NAME}

echo "running ks apply pipeline -c ${COMPONENT}"
ks apply ${KS_ENV_NAME} -c "${COMPONENT}"

JOB_NAME="pipeline-create-search-index-${WORKFLOW_ID}"
echo "wait for ${JOB_NAME} to finish"

kubectl wait --timeout="${TIMEOUT}" --for=condition=complete job/${JOB_NAME} -n "${NAMESPACE}"
# If the wait above failed, then the script will fail fast and following command won't run.
# TODO complete doesn't mean it's successful. Check the job succeeded.
echo "${JOB_NAME} is succeeded"
