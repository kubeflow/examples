# Copyright 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Use an official Ubuntu 18.04 as parent image
FROM ubuntu:18.04

# Install python 2.7.
FROM python:2.7

RUN apt-get update
RUN apt-get install -y git make g++

# Download the training set and code.
COPY ames_dataset/ ./ames_dataset
COPY housing.py ./housing.py

# Install Kubeflow seldon_serve component.
COPY seldon_serve/ ./seldon_serve
RUN pip install -r seldon_serve/requirements.txt

# Build XGBoost.
RUN git clone --recursive https://github.com/dmlc/xgboost && \
    cd xgboost && \
    make -j4 && \
    cd python-package; python setup.py install

ENTRYPOINT ["python", "housing.py"]
