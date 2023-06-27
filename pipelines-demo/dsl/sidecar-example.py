#  Copyright 2023 kbthu. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import kfp
from kfp import dsl

@dsl.pipeline(
    name='metric-test',
    description='query metrics from promehteus')
def exec_pipeline():
  op = dsl.ContainerOp(name='metrics-test',
                      image='kbthu/metrics-example:1.0.1',
                      command=['metrics'],
                      arguments=['pq', '-q', 'count(prometheus_target_interval_length_seconds)'],
  )
  op.container.set_image_pull_policy('IfNotPresent')
  op.add_sidecar(dsl.Sidecar('prometheus', 'bitnami/prometheus:2.44.0', command='ls')
    .set_image_pull_policy('IfNotPresent'))

if __name__ == '__main__':
    kfp.compiler.Compiler().compile(exec_pipeline, __file__ + '.yaml')
