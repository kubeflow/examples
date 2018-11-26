#!/bin/bash
# This script is a wrapper script for calling search index creator ksonnet component
# and creates a kubernetes job to compute search index.
# For more details about search index ksonnet component, check
# https://github.com/kubeflow/examples/blob/master/code_search/kubeflow/components/search-index-creator.jsonnet

set -ex

# Providing negative value to kubeflow wait would wait for a week
timeout="-1s"
# Ksonnet Environment name. Always use pipeline
ksEnvName="pipeline"
# Search index creator ksonnet component name
component="search-index-creator"

usage() {
	echo "Usage: deploy.sh --workingDir=<working dir> --workflowId=<workflow id invoking the container>
	--dataDir=<data dir> --timeout=<timeout>  --namespace=<kubernetes namespace>  --cluster=<cluster to deploy job to> "
}

# List of required parameters
names=(workingDir workflowId dataDir namespace cluster)

source "./parse_arguments.sh"

# Configure kubectl to use the underlying cluster
kubectl config set-cluster "${cluster}" --server=https://kubernetes.default --certificate-authority=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
kubectl config set-credentials pipeline --token "$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)"
kubectl config set-context kubeflow --cluster "${cluster}" --user pipeline
kubectl config use-context kubeflow
ks env set "${ksEnvName}" --namespace="${namespace}"

# Apply parameters
ks param set ${component} dataDir ${dataDir} --env ${ksEnvName}
ks param set ${component} jobNameSuffix ${workflowId} --env ${ksEnvName}
ks param set ${component} lookupFile ${workingDir}/code-embeddings-index/${workflowId}/embedding-to-info.csv --env ${ksEnvName}
ks param set ${component} indexFile ${workingDir}/code-embeddings-index/${workflowId}/embeddings.index --env ${ksEnvName}

echo "running ks apply pipeline -c ${component}"
ks apply ${ksEnvName} -c "${component}"

JOB_NAME="pipeline-create-search-index-${workflowId}"
echo "wait for ${JOB_NAME} to finish"

kubectl wait --timeout="${timeout}" --for=condition=complete job/${JOB_NAME} -n "${namespace}"
# If the wait above failed, then the script will fail fast and following command won't run.
# TODO complete doesn't mean it's successful. Check the job succeeded.
echo "${JOB_NAME} is succeeded"
