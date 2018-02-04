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

# Tensorflow 1.4.1, CPU, agents@14669421f6a1699b9100cc42071a79c4dca2f1c3
#FROM gcr.io/kubeflow-rl/base-agents:tf1.4.1-0202-0829-a186

# Tensorflow 1.4.1, CPU, agents@459c4f88ece996eac3489e6e97a6ee0b30bdd6b3
FROM gcr.io/kubeflow-rl/base-agents:tf1.4.1-0204-0938-c870

ADD trainer /app/trainer/

ADD demo.ipynb /app/demo/
ADD render.mp4 /app/demo/

WORKDIR /app/

ENTRYPOINT ["python", "-m", "trainer.task"]
