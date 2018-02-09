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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR=${SCRIPT_DIR}/../
SALT=`python -c 'import datetime; import uuid; now=datetime.datetime.now(); print(now.strftime("%m%d-%H%M") + "-" + uuid.uuid4().hex[0:4])'`
VERSION_TAG=0.1-$SALT
IMAGE_TAG=gcr.io/kubeflow-rl/agents-demo:${VERSION_TAG}

cd ${APP_DIR}

docker build -t ${IMAGE_TAG} -f ${SCRIPT_DIR}/Dockerfile .

gcloud docker -- push ${IMAGE_TAG}
