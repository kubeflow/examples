# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

FROM gcr.io/kubeflow-images-public/tensorflow-1.8.0-notebook-cpu

ENV KS_VER ks_0.12.0-rc1_linux_amd64

RUN cd /tmp && \
    wget --quiet https://github.com/ksonnet/ksonnet/releases/download/v0.12.0-rc1/$KS_VER.tar.gz && \
    tar -xvf $KS_VER.tar.gz && \
    rm $KS_VER.tar.gz

ENV PATH $PATH:/tmp/$KS_VER

RUN pip install --no-cache-dir annoy ktext nltk Pillow pydot
