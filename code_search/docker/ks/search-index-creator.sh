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
	echo "Usage: search-index-creator.sh --workingDir=<working dir> --workflowId=<workflow id invoking the container>
	--dataDir=<data dir> --timeout=<timeout>  --namespace=<kubernetes namespace>  --cluster=<cluster to deploy job to> "
}

# List of required parameters
names=(workingDir workflowId dataDir namespace cluster)

source "./parse_arguments.sh"
source "./initialize_kubectl.sh"

# Apply parameters
ks param set ${component} dataDir ${dataDir} --env ${ksEnvName}
ks param set ${component} jobNameSuffix "-"+${workflowId} --env ${ksEnvName}
ks param set ${component} lookupFile ${workingDir}/${workflowId}/code-embeddings-index/embedding-to-info.csv --env ${ksEnvName}
ks param set ${component} indexFile ${workingDir}/${workflowId}/code-embeddings-index/embeddings.index --env ${ksEnvName}

ks apply ${ksEnvName} -c "${component}"

JOB_NAME="pipeline-create-search-index-${workflowId}"
echo "wait for ${JOB_NAME} to finish"

kubectl wait --timeout="${timeout}" --for=condition=complete job/${JOB_NAME} -n "${namespace}"
# If the wait above failed, then the script will fail fast and following command won't run.
# TODO complete doesn't mean it's successful. Check the job succeeded.
echo "${JOB_NAME} is succeeded"
