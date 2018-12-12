#!/usr/bin/env bash

KUBEFLOW_DIR=$1

if [[ -d ngraph ]]; then
  pushd ngraph
  ${KUBEFLOW_DIR}/scripts/kfctl.sh delete all 
  popd
  rm -rf ngraph
fi
