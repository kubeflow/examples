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

# For now, just assume we're building a cpu image

get_project_id() {
  # From
  # Find the project ID first by DEVSHELL_PROJECT_ID (in Cloud Shell)
  # and then by querying the gcloud default project.
  local project="${DEVSHELL_PROJECT_ID:-}"
  if [[ -z "$project" ]]; then
    project=$(gcloud config get-value project 2> /dev/null)
  fi
  if [[ -z "$project" ]]; then
    >&2 echo "No default project was found, and DEVSHELL_PROJECT_ID is not set."
    >&2 echo "Please use the Cloud Shell or set your default project by typing:"
    >&2 echo "gcloud config set project YOUR-PROJECT-NAME"
  fi
  echo "$project"
}

upsearch () {
  test / == "$PWD" && return || \
      test -e "$1" && echo "$PWD" && return || \
      cd .. && upsearch "$1"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT=$(upsearch WORKSPACE)
BASE=${1:-NULLBASE}

if [[ $BASE == "NULLBASE" ]]; then
  echo "Please specify a base to build by build.sh [base_tag] with base_tag"
  echo "referring to a Dockerfile with the pattern Dockerfile.[base_tag] in"
  echo "tools/base/"
  exit 1
fi

IMAGE_BASE_NAME=base-${BASE}
TENSORFLOW_IMAGE_TAG=1.4.1

PROJECT_ID=$(get_project_id)
SALT=`python -c 'import datetime; import uuid; now=datetime.datetime.now(); print(now.strftime("%m%d-%H%M") + "-" + uuid.uuid4().hex[0:4])'`

VERSION_TAG=tf${TENSORFLOW_IMAGE_TAG}-${SALT} # probably want git hash of agents not kubeflow-rl
IMAGE_TAG=gcr.io/${PROJECT_ID}/${IMAGE_BASE_NAME}:${VERSION_TAG}

cd ${WORKSPACE_ROOT}

sed s/{tensorflow_image_tag}/${TENSORFLOW_IMAGE_TAG}/g tools/base/Dockerfile.${BASE} > \
  tools/base/Dockerfile.temp

docker build -t ${IMAGE_TAG} -f tools/base/Dockerfile.temp .

gcloud docker -- push ${IMAGE_TAG}

rm tools/base/Dockerfile.temp
