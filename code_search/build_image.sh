#!/usr/bin/env bash

##
# This script builds and pushes a Docker image containing
# "app" to Google Container Registry. It automatically tags
# a unique image for every run.
#

set -ex

PROJECT=${PROJECT:-}

if [[ -z "${PROJECT}" ]]; then
  echo "PROJECT environment variable missing!"
  exit 1
fi

GPU=${GPU:-0}

BASE_IMAGE_TAG=$([[ "${GPU}" = "1" ]] && echo "1.8.0-gpu-py3" || echo "1.8.0-py3")
BUILD_IMAGE_TAG="code-search:v$(date +%Y%m%d)$([[ ${GPU} = "1" ]] && echo '-gpu' || echo '')-$(python3 -c 'import uuid; print(uuid.uuid4().hex[:7]);')"

# Directory of this script used as docker context
_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pushd "${_SCRIPT_DIR}/app"

docker build -t ${BUILD_IMAGE_TAG} --build-arg BASE_IMAGE_TAG=${BASE_IMAGE_TAG} .

# Push image to GCR PROJECT available
docker tag ${BUILD_IMAGE_TAG} gcr.io/${PROJECT}/${BUILD_IMAGE_TAG}
docker push gcr.io/${PROJECT}/${BUILD_IMAGE_TAG}

popd
