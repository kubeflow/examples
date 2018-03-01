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

FROM gcr.io/kubeflow/tensorflow-notebook-cpu

RUN curl https://sdk.cloud.google.com | bash
RUN mkdir -p ${HOME}/bin && mkdir -p ${HOME}/lib && cd ${HOME}/lib && curl -L -o ${HOME}/lib/ks.tgz "https://github.com/ksonnet/ksonnet/releases/download/v0.8.0/ks_0.8.0_linux_amd64.tar.gz" && tar -xzvf ${HOME}/lib/ks.tgz && rm ${HOME}/lib/ks.tgz && ln -s ${HOME}/lib/ks_0.8.0_linux_amd64/ks ${HOME}/bin/ks

RUN curl -sSL -o /home/jovyan/bin/argo https://github.com/argoproj/argo/releases/download/v2.0.0/argo-linux-amd64
RUN chmod +x /home/jovyan/bin/argo

RUN mkdir -p /home/jovyan/kubeflow-examples/agents/
ADD . /home/jovyan/kubeflow-examples/agents/

USER root

RUN mkdir -p /usr/lib/golang && cd /usr/lib/golang && \
  wget https://dl.google.com/go/go1.10.linux-amd64.tar.gz && \
  tar -xzf go1.10.linux-amd64.tar.gz && mv go /usr/local/

RUN apt-get install -y make gcc git pkg-config

USER jovyan

RUN echo "export PATH=\$PATH:/usr/local/go/bin" >> $HOME/.bash_profile
RUN echo "export GOROOT=/usr/local/go" >> $HOME/.bash_profile
RUN echo "export GOPATH=\$HOME/go" >> $HOME/.bash_profile
RUN echo "export PATH=\$PATH:\$GOROOT/bin" >> $HOME/.bash_profile
RUN source $HOME/.bash_profile

RUN mkdir -p $GOPATH/src/github.com/opencontainers
RUN cd $GOPATH/src/github.com/opencontainers && \
    git clone https://github.com/AkihiroSuda/runc.git && cd runc && \
    git checkout unshare-m-r && make BUILDTAGS=""

RUN go get github.com/jessfraz/img

RUN unshare -m -U --map-root-user
RUN echo "FROM ubuntu" >> Dockerfile && img build -t something .

USER root

RUN cd runc && make && make install

RUN chown -R jovyan /home/jovyan/kubeflow-examples

# Needed for rendering and uploading renders
#RUN apt-get update
#RUN apt-get install -y libav-tools ffmpeg git

#RUN curl https://get.docker.com | bash
#RUN usermod -aG docker jovyan

#RUN pip install -r /home/jovyan/kubeflow-examples/agents/requirements.txt
