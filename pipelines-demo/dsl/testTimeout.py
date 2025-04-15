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
from kfp.components import func_to_container_op

def training(t: int):
  cop = dsl.ContainerOp(
    name='inference',
    image='bash:5.1',
    command=['sh', '-c'],
    arguments=['sleep %s;' % (t)]
  )
  cop.container.set_image_pull_policy('IfNotPresent')
  return cop


@dsl.pipeline(
  name='Kubeflow test timeout',
  description='Demonstrate the setting of timeout for pipeline'
)
def test_timeout(a: int = 5):
  op1 = training(a).set_timeout(20)
  dsl.get_pipeline_conf().set_timeout(30)


if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(test_timeout, 'testTimeout.yaml')
