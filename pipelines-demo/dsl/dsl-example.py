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

def inference():
  return dsl.ContainerOp(
    name='inference',
    image='bash:5.1',
    command=['sh', '-c'],
    arguments=['echo $(( $RANDOM % 10 + 1 ))']
  )

@func_to_container_op
def training() -> str:
  import random
  result = random.choice(['pass', 'fail'])
  return result


@func_to_container_op
def print_op(message: str):
  print(message)


@dsl.pipeline(
  name='Kubeflow pipeline example',
  description='Demonstrate the flow control of Kubeflow pipeline'
)
def dsl_example(stage: dsl.PipelineParam):
  with dsl.Condition(stage == 'training'):
    train_op = training()
    with dsl.Condition(train_op.output == 'pass'):
      print_op('Training pass. Do inference')
      infer_op = inference()
    with dsl.Condition(train_op.output == 'fail'):
      print_op('Training fail. Stop')

  # inference stage
  with dsl.Condition(stage != 'training'):
    infer_op = inference()

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(dsl_example, __file__ + '.yaml')
