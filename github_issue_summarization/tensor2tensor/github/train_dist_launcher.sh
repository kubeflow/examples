#!/bin/bash
# TODO(ankushagarwal): Convert this to a python launcher script
set -x
PS_REPLICAS="${1}"
WORKER_REPLICAS="${2}"
WORKER_GPU="${3}"
TRAIN_STEPS="${4}"
WORKER_JOB="${5}"
SYNC="${6}"
export TF_CONFIG=$(echo ${TF_CONFIG} | sed 's/"worker"/"master"/g')
echo "TF_CONFIG = ${TF_CONFIG}"
OUTDIR=./out
DATA_DIR=gs://kubeflow-examples/tensor2tensor/data
TMP_DIR=./tmp
PROBLEM=github_issue_summarization_problem
USR_DIR=./github
HPARAMS_SET=transformer_github_issues
WORKER_ID=$(echo ${TF_CONFIG} | jq ".task.index")
WORKER_TYPE=$(echo ${TF_CONFIG} | jq -r ".task.type")
MASTER_INSTANCE=$(echo ${TF_CONFIG} | jq -r ".cluster.${WORKER_TYPE}[${WORKER_ID}]")
rm -rf "${OUTDIR}" "${TMP_DIR}"
mkdir -p "${OUTDIR}"
mkdir -p "${TMP_DIR}"
t2t-trainer \
  --data_dir=${DATA_DIR} \
  --t2t_usr_dir=${USR_DIR} \
  --problems=${PROBLEM} \
  --model=transformer \
  --hparams_set=${HPARAMS_SET} \
  --output_dir=$OUTDIR --job-dir=$OUTDIR --train_steps=${TRAIN_STEPS} \
  --master=grpc://${MASTER_INSTANCE} \
  --ps_replicas=${PS_REPLICAS} \
  --worker_replicas=${WORKER_REPLICAS} \
  --worker_gpu=${WORKER_GPU} \
  --worker_id=${WORKER_ID} \
  --worker_job=${WORKER_JOB} \
  --ps_gpu=0 \
  --schedule=train \
  --sync=${SYNC}
