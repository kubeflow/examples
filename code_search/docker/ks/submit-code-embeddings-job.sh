#!/bin/bash
# This script is a wrapper script for calling submit code embedding job ksonnet component
# and creates a kubernetes job to submit dataflow job to compute code function embedding
# For more details about search index ksonnet component, check
# https://github.com/kubeflow/examples/blob/master/code_search/kubeflow/components/submit-code-embeddings-job.libsonnet

set -ex

# Providing negative value to kubeflow wait would wait for a week
timeout="-1s"
# Ksonnet Environment name. Always use pipeline
ksEnvName="pipeline"
# submit code embeddings job ksonnet component name
component="submit-code-embeddings-job"
# default number of dataflow workers
numWorkers=5
# default dataflow worker machine type
workerMachineType=n1-highcpu-32

usage() {
	echo "Usage: submit-code-embeddings-job.sh --workflowId=<workflow id invoking the container> --modelDir=<directory contains the model>
	--dataDir=<data dir> --numWorkers=<num of workers> --project=<project> --targetDataset=<target BQ dataset>
	--workerMachineType=<worker machine type> --workingDir=<working dir>"
}

# List of required parameters
names=(dataDir modelDir targetDataset workingDir workflowId)

source "./parse_arguments.sh"
source "./initialize_kubectl.sh"

# get project id

# Apply parameters
ks param set ${component} jobNameSuffix "-"+${workflowId} --env ${ksEnvName}
ks param set ${component} dataDir ${dataDir} --env ${ksEnvName}
ks param set ${component} modelDir ${modelDir} --env ${ksEnvName}
ks param set ${component} project ${project} --env ${ksEnvName}
ks param set ${component} targetDataset ${targetDataset} --env ${ksEnvName}
ks param set ${component} workingDir ${workingDir}/${workflowId} --env ${ksEnvName}
ks param set ${component} numWorkers ${numWorkers} --env ${ksEnvName}
ks param set ${component} workerMachineType ${workerMachineType} --env ${ksEnvName}

ks apply ${ksEnvName} -c "${component}"

JOB_NAME="submit-code-embeddings-job-${workflowId}"
echo "wait for ${JOB_NAME} to finish"

kubectl wait --timeout="${timeout}" --for=condition=complete job/${JOB_NAME} -n "${namespace}"
# If the wait above failed, then the script will fail fast and following command won't run.
# TODO complete doesn't mean it's successful. Check the job succeeded.
echo "${JOB_NAME} is succeeded"
