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

RUN mkdir -p ${HOME}/bin && mkdir -p ${HOME}/lib && cd ${HOME}/lib && curl -L -o ${HOME}/lib/ks.tgz "https://github.com/ksonnet/ksonnet/releases/download/v0.8.0/ks_0.8.0_linux_amd64.tar.gz" && tar -xzvf ${HOME}/lib/ks.tgz && rm ${HOME}/lib/ks.tgz && ln -s ${HOME}/lib/ks_0.8.0_linux_amd64/ks ${HOME}/bin/ks

#TODO: Best method to put ks on path...?

RUN curl https://sdk.cloud.google.com | bash

RUN mkdir -p /home/jovyan/kubeflow-examples/agents

ADD . /home/jovyan/kubeflow-examples/agents/

USER root

RUN chown -R jovyan /home/jovyan/kubeflow-examples

USER jovyan
