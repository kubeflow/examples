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

get_project_id() {
  local project="${DEVSHELL_PROJECT_ID:-}"
  if [[ -z "$project" ]]; then
    project=$(gcloud config get-value project 2> /dev/null)
  fi
  if [[ -z "$project" ]]; then
    >&2 echo "No default project was found."
    >&2 echo "Please set a project by typing:"
    >&2 echo "gcloud config set project YOUR-PROJECT-NAME"
  fi
  echo "$project"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

IMAGE_BASE_NAME=agents
TENSORFLOW_IMAGE_TAG=1.4.1
PROJECT_ID=$(get_project_id)
SALT=`python -c 'import datetime; import uuid; now=datetime.datetime.now(); print(now.strftime("%m%d-%H%M") + "-" + uuid.uuid4().hex[0:4])'`

VERSION_TAG=tf${TENSORFLOW_IMAGE_TAG}-${SALT}
IMAGE_TAG=gcr.io/${PROJECT_ID}/${IMAGE_BASE_NAME}:${VERSION_TAG}
echo ${IMAGE_TAG}

sed s/{tensorflow_image_tag}/${TENSORFLOW_IMAGE_TAG}/g Dockerfile > \
  Dockerfile.temp

cd ${SCRIPT_DIR}

docker build -t ${IMAGE_TAG} -f Dockerfile.temp .

gcloud docker -- push ${IMAGE_TAG}

rm Dockerfile.temp
