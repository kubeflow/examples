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

FROM gcr.io/kubeflow/tensorflow-notebook-gpu

USER jovyan
RUN mkdir -p ${HOME}/bin && curl -L -o ${HOME}/bin/ks "https://github.com/ksonnet/ksonnet/releases/download/v0.8.0/ks-linux-amd64" && chmod a+rx ${HOME}/bin/ks

RUN curl https://sdk.cloud.google.com | bash

RUN mkdir -p /home/jovyan/kubeflow-examples/agents

ADD . /home/jovyan/kubeflow-examples/agents/

USER jovyan
