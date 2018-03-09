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

FROM docker:17.10

RUN apk update

RUN apk add --no-cache curl python bash

RUN curl https://sdk.cloud.google.com | bash

RUN ln -s /root/google-cloud-sdk/bin/gsutil /usr/bin/gsutil
RUN ln -s /root/google-cloud-sdk/bin/gcloud /usr/bin/gcloud
