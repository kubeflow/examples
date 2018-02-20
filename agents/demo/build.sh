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

# Configurable variables
# You can configure this script by running sh build-demo-gcp.s
VERSION=${VERSION:-0.1}
APP_NAME=${APP_NAME:-agents}
TENSORFLOW_IMAGE_TAG=${TENSORFLOW_IMAGE_TAG:-1.4.1}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR=${SCRIPT_DIR}/../
SALT=`python -c 'import datetime; import uuid; now=datetime.datetime.now(); print(now.strftime("%m%d-%H%M") + "-" + uuid.uuid4().hex[0:4])'`
VERSION_TAG=${VERSION}-$SALT
PROJECT_ID=$(get_project_id)
IMAGE_TAG=gcr.io/${PROJECT_ID}/${APP_NAME}-demo:${VERSION_TAG}

cd ${APP_DIR}

docker build -t ${IMAGE_TAG} -f ${SCRIPT_DIR}/Dockerfile .

echo "Ready to rock! 🎉"
echo "Just push the following tag to your registry of choice then provide that "
echo "to JupyterHub to launch the demo:"
echo ${IMAGE_TAG}
