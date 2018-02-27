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

FROM tensorflow/tensorflow:1.4.1

# Needed for rendering and uploading renders
RUN apt-get update
RUN apt-get install -y libav-tools ffmpeg git

ADD requirements.txt /app/
RUN pip install -r /app/requirements.txt

ADD trainer /app/trainer/

WORKDIR /app/

ENTRYPOINT ["python", "-m", "trainer.task"]
