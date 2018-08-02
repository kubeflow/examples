#!/usr/bin/env bash

set -e

T2T_USR_DIR=${T2T_USR_DIR:-}
TARGET_BIN="${1}"
TARGET_BIN_OPTS="--tmp_dir=/tmp"

# Add T2T user directory for new problems
if [[ ! -z "${T2T_USR_DIR}" ]]; then
    TARGET_BIN_OPTS="${TARGET_BIN_OPTS} --t2t_usr_dir=${T2T_USR_DIR}"
fi

# Process TF_CONFIG to pass parameters distributed training parameters to `t2t-trainer`
TF_CONFIG=${TF_CONFIG:-}
if [[ ! -z "${TF_CONFIG}" ]]; then
    WORKER_ID=$(echo "${TF_CONFIG}" | jq ".task.index")
    WORKER_TYPE=$(echo "${TF_CONFIG}" | jq -r ".task.type")
    MASTER_INSTANCE=$(echo "${TF_CONFIG}" | jq -r ".cluster.${WORKER_TYPE}[${WORKER_ID}]")

    # FIXME(sanyamkapoor): Distributed training hangs. See kubeflow/examples#208.
    # if [[ "${TARGET_BIN}" = "t2t-trainer" ]]; then
    #   TARGET_BIN_OPTS="${TARGET_BIN_OPTS} --master=grpc://${MASTER_INSTANCE} --worker_id=${WORKER_ID}"
    # fi
    unset TF_CONFIG
fi

EVAL_CMD="${TARGET_BIN} ${TARGET_BIN_OPTS} ${@:2}"

echo "Running command: '${EVAL_CMD}'"
eval "${EVAL_CMD}"
