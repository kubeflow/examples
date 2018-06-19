#!/usr/bin/env bash

set -e

PROJECT=${PROJECT:-}
BUILD_IMAGE_TAG=${BUILD_IMAGE_TAG:-nmslib:devel}

# Directory of this script used as docker context
_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pushd "$_SCRIPT_DIR"

docker build -t ${BUILD_IMAGE_TAG} .

# Push image to GCR if PROJECT available
if [[ ! -z "${PROJECT}" ]]; then
    docker tag ${BUILD_IMAGE_TAG} gcr.io/${PROJECT}/${BUILD_IMAGE_TAG}
    docker push gcr.io/${PROJECT}/${BUILD_IMAGE_TAG}
fi

popd
