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
APP=${1:-NULLAPP}

# TODO: Use single python script to manage both base and app builds.

if [[ $APP == "NULLAPP" ]]; then
  echo "Please specify an app to build by build_app.sh [app_name] with app_name"
  echo "referring to an app at dir path apps/[app_name] containing a Dockerfile"
  exit 1
fi

PROJECT_ID=$(get_project_id)
SALT=`python -c 'import datetime; import uuid; now=datetime.datetime.now(); print(now.strftime("%m%d-%H%M") + "-" + uuid.uuid4().hex[0:4])'`

VERSION_TAG=${APP}-${SALT}
IMAGE_TAG=`echo gcr.io/${PROJECT_ID}/${APP}:${VERSION_TAG} | tr '_' '-'`

# TODO: In python implementation verify that ${APP_PATH} exists.
APP_PATH=${WORKSPACE_ROOT}/apps/$APP
cd ${APP_PATH}

docker build -t ${IMAGE_TAG} .
gcloud docker -- push ${IMAGE_TAG}
