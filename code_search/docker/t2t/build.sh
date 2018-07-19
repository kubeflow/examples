#!/usr/bin/env bash

##
# This script builds and pushes a Docker image containing
# the T2T problem to Google Container Registry. It automatically tags
# a unique image for every run.
#

set -ex

GPU=${GPU:-0}
BASE_IMAGE_TAG=$([[ "${GPU}" = "1" ]] && echo "1.8.0-gpu-py3" || echo "1.8.0-py3")
BUILD_IMAGE_UUID=$(python3 -c 'import uuid; print(uuid.uuid4().hex[:7]);')
BUILD_IMAGE_TAG="code-search:v$(date +%Y%m%d)$([[ ${GPU} = "1" ]] && echo '-gpu' || echo '')-${BUILD_IMAGE_UUID}"

# Directory of this script used for path references
_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pushd "${_SCRIPT_DIR}"

docker build -f "${_SCRIPT_DIR}/Dockerfile" -t ${BUILD_IMAGE_TAG} --build-arg BASE_IMAGE_TAG=${BASE_IMAGE_TAG} "${_SCRIPT_DIR}/../.."

# Push image to GCR PROJECT available
PROJECT=${PROJECT:-}
if [[ ! -z "${PROJECT}" ]]; then
  docker tag ${BUILD_IMAGE_TAG} gcr.io/${PROJECT}/${BUILD_IMAGE_TAG}
  docker push gcr.io/${PROJECT}/${BUILD_IMAGE_TAG}
fi

popd
