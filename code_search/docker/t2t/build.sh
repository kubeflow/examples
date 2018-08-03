#!/usr/bin/env bash

##
# This script builds and pushes a Docker image containing
# the T2T problem to Google Container Registry. It automatically tags
# a unique image for every run.
#

set -ex

BUILD_IMAGE_UUID=$(python3 -c 'import uuid; print(uuid.uuid4().hex[:7]);')
BUILD_IMAGE_TAG="code-search:v$(date +%Y%m%d)-${BUILD_IMAGE_UUID}"

# Directory of this script used for path references
_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pushd "${_SCRIPT_DIR}"

# Build CPU image
docker build -f "${_SCRIPT_DIR}/Dockerfile" \
             -t ${BUILD_IMAGE_TAG} \
             --build-arg BASE_IMAGE_TAG=1.8.0 \
             "${_SCRIPT_DIR}/../.."

# Build GPU image
docker build -f "${_SCRIPT_DIR}/Dockerfile" \
             -t ${BUILD_IMAGE_TAG}-gpu \
             --build-arg BASE_IMAGE_TAG=1.8.0-gpu \
             "${_SCRIPT_DIR}/../.."

# Push images to GCR Project if available
PROJECT=${PROJECT:-}
if [[ ! -z "${PROJECT}" ]]; then
  # Tag and push CPU image
  docker tag ${BUILD_IMAGE_TAG} gcr.io/${PROJECT}/${BUILD_IMAGE_TAG}
  docker push gcr.io/${PROJECT}/${BUILD_IMAGE_TAG}

  # Tag and push GPU image
  docker tag ${BUILD_IMAGE_TAG}-gpu gcr.io/${PROJECT}/${BUILD_IMAGE_TAG}-gpu
  docker push gcr.io/${PROJECT}/${BUILD_IMAGE_TAG}-gpu
fi

popd
