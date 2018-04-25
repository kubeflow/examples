# Copyright 2017 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Requirements:
#   https://github.com/mattrobenolt/jinja2-cli
#   pip install jinja2-clie
# Update the Airflow deployment

TAG := $(shell date +v%Y%m%d)-$(shell git describe --tags --always --dirty)-$(shell git diff | sha256sum | cut -c -6)
DIR := ${CURDIR}

# You can override this on the command line as
# make PROJECT=kubeflow-examples <target>
PROJECT := kubeflow-examples

# TPU uses the same docker image as CPU .
IMG := gcr.io/$(PROJECT)/tf-job-issue-summarization

push: build
	gcloud docker -- push $(IMG):$(TAG)

set-image: push
	# Set the image to use
	cd ../ks-kubeflow && ks param set tfjob-pvc image $(IMG):$(TAG)

# To build without the cache set the environment variable
# export DOCKER_BUILD_OPTS=--no-cache
build:
	docker build ${DOCKER_BUILD_OPTS} -f Dockerfile -t $(IMG):$(TAG) ./
	@echo Built $(IMG):$(TAG)