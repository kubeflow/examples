#!/usr/bin/env bash

set -e

BASE_IMAGE_TAG=${BASE_IMAGE_TAG:-1.8.0-py3} # 1.8.0-gpu-py3 for GPU-based image
BUILD_IMAGE_TAG=${BUILD_IMAGE_TAG:-semantic-code-search:devel}

# Directory of this script used as docker context
_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pushd "$_SCRIPT_DIR"

docker build -t ${BUILD_IMAGE_TAG} --build-arg BASE_IMAGE_TAG=${BASE_IMAGE_TAG} .

popd
