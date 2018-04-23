#!/bin/bash
# TODO(ankushagarwal): Convert this to a python launcher script
set -x
export TF_CONFIG=${TF_CONFIG}
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
  --output_dir=$OUTDIR --job-dir=$OUTDIR --train_steps=1000 \
  --master=grpc://${MASTER_INSTANCE} \
  --schedule=run_std_server
