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

# List any changed  files. We only include files in the notebooks directory.
# because that is the code in the docker image.
# In particular we exclude changes to the ksonnet configs.
CHANGED_FILES := $(shell git diff-files --relative=github_issue_summarization/tensor2tensor/github)

ifeq ($(strip $(CHANGED_FILES)),)
# Changed files is empty; not dirty
# Don't include --dirty because it could be dirty if files outside the ones we care
# about changed.
TAG := $(shell date +v%Y%m%d)-$(shell git describe --tags --always)
else
TAG := $(shell date +v%Y%m%d)-$(shell git describe --tags --always --dirty)-$(shell git diff | shasum -a256 | cut -c -6)
endif

DIR := $(shell pwd)

# You can override this on the command line as
# make PROJECT=kubeflow-examples <target>
PROJECT := kubeflow-examples

IMG := gcr.io/$(PROJECT)/issue-summarization-t2t-trainer
CPU_IMG := $(IMG)-cpu

CPU_BASE_IMG := gcr.io/kubeflow-images-public/tensorflow-1.7.0-notebook-cpu:v20180419-0ad94c4e

echo:
	@echo changed files $(CHANGED_FILES)
	@echo tag $(TAG)		

push-cpu: build-cpu
	gcloud docker -- push $(CPU_IMG):$(TAG)

set-image: push-cpu
	# Set the image to use
	cd ../../ks-kubeflow && ks param set tensor2tensor cpuImage $(CPU_IMG):$(TAG)

# To build without the cache set the environment variable
# export DOCKER_BUILD_OPTS=--no-cache
build-cpu:
	docker build ${DOCKER_BUILD_OPTS} --build-arg BASE_IMAGE=$(CPU_BASE_IMG) -f Dockerfile -t $(CPU_IMG):$(TAG) ./
	@echo Built $(CPU_IMG):$(TAG)