#!/usr/bin/env bash

set -e

# Script Variables
IMAGE_TAG=${IMAGE_TAG:-semantic-code-search:devel}
DOCKER_ENTRYPOINT=${DOCKER_ENTRYPOINT:-}

MOUNT_DATA_DIR=${MOUNT_DATA_DIR:-}
MOUNT_OUTPUT_DIR=${MOUNT_OUTPUT_DIR:-}

DATA_DIR=${DATA_DIR:-/data}
OUTPUT_DIR=${OUTPUT_DIR:-/output}

# Internal Variables
_DOCKER_RUN_OPTS="-it --rm --entrypoint=${DOCKER_ENTRYPOINT}"
_DOCKER_CMD="${@} --t2t_usr_dir=/t2t_problems --tmp_dir=/tmp --data_dir=${DATA_DIR} --output_dir=${OUTPUT_DIR}"

if [[ -z ${DOCKER_ENTRYPOINT} ]]; then
    echo "ERROR: Missing DOCKER_ENTRYPOINT environment variable! Use 't2t-datagen' or 't2t-trainer'"
    exit 1
fi

# Mount local directories (if specified)
if [[ ! -z ${MOUNT_DATA_DIR} ]]; then
    _DOCKER_RUN_OPTS="${_DOCKER_RUN_OPTS} -v ${MOUNT_DATA_DIR}:${DATA_DIR}:rw"
fi

if [[ ! -z ${MOUNT_OUTPUT_DIR} ]]; then
    _DOCKER_RUN_OPTS="${_DOCKER_RUN_OPTS} -v ${MOUNT_OUTPUT_DIR}:${OUTPUT_DIR}:rw"
fi

_FINAL_CMD="docker run ${_DOCKER_RUN_OPTS} ${IMAGE_TAG} ${_DOCKER_CMD}"

echo "${_FINAL_CMD}"
eval "${_FINAL_CMD}"
