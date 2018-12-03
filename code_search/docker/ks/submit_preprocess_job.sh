#!/bin/bash
# This script is a wrapper script for calling submit code embedding job ksonnet component
# and creates a kubernetes job to submit dataflow job to compute code function embedding
# For more details about search index ksonnet component, check
# https://github.com/kubeflow/examples/blob/master/code_search/kubeflow/components/submit-code-embeddings-job.libsonnet

set -ex

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"

# Providing negative value to kubeflow wait would wait for a week
timeout="-1s"
# Ksonnet Environment name. Always use pipeline
ksEnvName="pipeline"
# submit code embeddings job ksonnet component name
component="submit-preprocess-job"
# default number of dataflow workers
numWorkers=5
# default dataflow worker machine type
workerMachineType=n1-highcpu-32

usage() {
	echo "Usage: submit_preprocess_job.sh
	--cluster=<cluster to deploy job to>
	--dataDir=<data dir>
    --namespace=<kubernetes namespace>
	--numWorkers=<num of workers>
	--project=<project>
	--timeout=<timeout>
	--tokenPairsBQTable=<input token pairs BQ table>
	--workerMachineType=<worker machine type>
	--workflowId=<workflow id invoking the container>
	--workingDir=<working dir>"
}

# List of required parameters
names=(cluster dataDir namespace project tokenPairsBQTable workflowId workingDir)

source "${DIR}/parse_arguments.sh"
source "${DIR}/initialize_kubectl.sh"

# Apply parameters
ks param set ${component} dataDir ${dataDir} --env ${ksEnvName}
ks param set ${component} jobNameSuffix ${workflowId} --env ${ksEnvName}
ks param set ${component} numWorkers ${numWorkers} --env ${ksEnvName}
ks param set ${component} project ${project} --env ${ksEnvName}
ks param set ${component} tokenPairsBQTable ${tokenPairsBQTable} --env ${ksEnvName}
ks param set ${component} workerMachineType ${workerMachineType} --env ${ksEnvName}
ks param set ${component} workingDir ${workingDir} --env ${ksEnvName}

ks show ${ksEnvName} -c "${component}"
ks apply ${ksEnvName} -c "${component}"

JOB_NAME="pipeline-preprocess-${workflowId}"
echo "wait for ${JOB_NAME} to finish"

kubectl wait --timeout="${timeout}" --for=condition=complete job/${JOB_NAME} -n "${namespace}"
# If the wait above failed, then the script will fail fast and following command won't run.
# TODO complete doesn't mean it's successful. Check the job succeeded.
echo "${JOB_NAME} is succeeded"
