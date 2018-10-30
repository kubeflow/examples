#!/bin/bash
#
# A simple script for starting TFServing locally in a docker container.
# This allows us to test sending predictions to the model.
set -ex
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
MODEL_DIR=${DIR}/test_data/model/export
MODEL_NAME=cs_similarity_transformer
docker run  -t --rm --name=cs_serving_test -p 8500:8500 -p 8501:8501 \
   -v "${MODEL_DIR}:/models/${MODEL_NAME}" \
   -e MODEL_NAME="${MODEL_NAME}" \
   tensorflow/serving &
