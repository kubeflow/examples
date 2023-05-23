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

def mnist_train():
  cop = dsl.ContainerOp(
    name='mnist_train',
    image='kbthu/tf-mnist-example:1.0.1',
    command=['python3'],
    arguments=['/mnist/mnist-train.py'],
    file_outputs={'output': '/model/model.keras'},
  )
  cop.container.set_image_pull_policy('IfNotPresent')
  cop.add_pvolumes({'/model': dsl.PipelineVolume(pvc='mnist-model')})
  return cop


def mnist_test(model):
  cop = dsl.ContainerOp(
    name='mnist_test',
    image='kbthu/tf-mnist-example:1.0.1',
    command=['python3'],
    arguments=['/mnist/mnist-test.py'],
  )
  cop.container.set_image_pull_policy('IfNotPresent')
  cop.add_pvolumes({'/model': dsl.PipelineVolume(pvc='mnist-model')})
  return cop


@dsl.pipeline(
  name='Kubeflow pipeline example',
  description='Demonstrate the Kubeflow pipeline with Mnist training'
)
def kfp_example():
  _train_op = mnist_train()
  
  mnist_test(
    dsl.InputArgumentPath(_train_op.outputs['output'])
  ).after(_train_op)


if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(kfp_example, __file__ + '.yaml')
