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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TMPDIR=$(mktemp -d)
cd ${TMPDIR}
ks init app

cd app

ks registry add kubeflow github.com/kubeflow/kubeflow/tree/master/kubeflow
ks pkg install kubeflow/tf-job

cp -r environments ${SCRIPT_DIR}/
cp -r vendor ${SCRIPT_DIR}/
cp -r .ksonnet ${SCRIPT_DIR}/

cd ${SCRIPT_DIR} && rm -r ${TMPDIR}
