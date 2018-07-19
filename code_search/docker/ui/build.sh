#!/usr/bin/env bash

##
# This script builds and pushes a Docker image containing
# the Code Search UI to Google Container Registry. It automatically tags
# a unique image for every run.
#

set -ex

BUILD_IMAGE_UUID=$(python3 -c 'import uuid; print(uuid.uuid4().hex[:7]);')
BUILD_IMAGE_TAG="code-search-ui:v$(date +%Y%m%d)-${BUILD_IMAGE_UUID}"

# Directory of this script used for path references
_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pushd "${_SCRIPT_DIR}"

docker build -f "${_SCRIPT_DIR}/Dockerfile" -t ${BUILD_IMAGE_TAG} "${_SCRIPT_DIR}/../.."

# Push image to GCR PROJECT available
PROJECT=${PROJECT:-}
if [[ ! -z "${PROJECT}" ]]; then
  docker tag ${BUILD_IMAGE_TAG} gcr.io/${PROJECT}/${BUILD_IMAGE_TAG}
  docker push gcr.io/${PROJECT}/${BUILD_IMAGE_TAG}
fi

popd
