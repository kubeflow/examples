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
from typing import NamedTuple


@func_to_container_op
def calculate_op(a: float, b: float) -> NamedTuple(
  'MyOutputs',
  [
    ('sum', float),
    ('product', float)
  ]):
  return (a + b, a * b)


def echo_func(sum: float, product: float):
  cop = dsl.ContainerOp(
    name='echo_func',
    image='bash:5.1',
    command=['sh', '-c'],
    arguments=['echo sum %s product %s | tee /out.txt' % (sum, product)],
	file_outputs={'out': '/out.txt'},
  )
  cop.container.set_image_pull_policy('IfNotPresent')
  return cop


@dsl.pipeline(
  name='Kubeflow data passing example',
  description='Demonstrate the data passing between Kubeflow funcs'
)
def data_passing(
    a: dsl.PipelineParam(name='a', value=2), 
    b: dsl.PipelineParam(name='b', value=3)
  ):
  result = calculate_op(a, b)
  echo_func(result.outputs['sum'], result.outputs['product'])


if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(data_passing, __file__ + '.yaml')
