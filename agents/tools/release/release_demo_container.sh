#!/usr/bin/env bash
#
# Copyright 2017 The Kubeflow Examples Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Build and release demo container

RELEASE_VERSION=0.0.1
APP_TAG=agents-demo

RELEASE_TYPE=${RELEASE_TYPE:-dirty}

if [ -z ${RELEASE_REGISTRY+x} ]; then
  echo "Please specify a target registry for the release by setting RELEASE_REGISTRY."
  exit 1
fi

IMAGE_TAG=${RELEASE_REGISTRY}/${APP_TAG}:${RELEASE_VERSION}

if [ ${RELEASE_TYPE} == 'dirty' ]; then
  echo "Building dirty release."
  SALT=`python -c 'import datetime; import uuid; now=datetime.datetime.now(); print(now.strftime("%m%d-%H%M") + "-" + uuid.uuid4().hex[0:4])'`
  IMAGE_TAG=${IMAGE_TAG}-${SALT}
fi

echo "Building release with tag: ${IMAGE_TAG}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR=${SCRIPT_DIR}/../../
cd ${APP_DIR}

docker build -t ${IMAGE_TAG} -f doc/Dockerfile .

gcloud docker -- push ${IMAGE_TAG}
#docker push ${IMAGE_TAG}

