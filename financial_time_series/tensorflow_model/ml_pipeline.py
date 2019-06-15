#!/usr/bin/env python3
# Copyright 2018 Google LLC
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

import kfp.dsl as dsl


class Preprocess(dsl.ContainerOp):

  def __init__(self, name, bucket, cutoff_year):
    super(Preprocess, self).__init__(
      name=name,
      # image needs to be a compile-time string
      image='gcr.io/<project>/<image-name>/cpu:v1',
      command=['python3', 'run_preprocess.py'],
      arguments=[
        '--bucket', bucket,
        '--cutoff_year', cutoff_year,
        '--kfp'
      ],
      file_outputs={'blob-path': '/blob_path.txt'}
    )

class Train(dsl.ContainerOp):

  def __init__(self, name, blob_path, version, bucket, model):
    super(Train, self).__init__(
      name=name,
      # image needs to be a compile-time string
      image='gcr.io/<project>/<image-name>/cpu:v1',
      command=['python3', 'run_train.py'],
      arguments=[
        '--version', version,
        '--blob_path', blob_path,
        '--bucket', bucket,
        '--model', model
      ]
    )


@dsl.pipeline(
  name='financial time series',
  description='Train Financial Time Series'
)
def train_and_deploy(
        bucket=dsl.PipelineParam('bucket', value='<bucket>'),
        cutoff_year=dsl.PipelineParam('cutoff-year', value='2010'),
        version=dsl.PipelineParam('version', value='4'),
        model=dsl.PipelineParam('model', value='DeepModel')
):
  """Pipeline to train financial time series model"""
  preprocess_op = Preprocess('preprocess', bucket, cutoff_year)
  #pylint: disable=unused-variable
  train_op = Train('train and deploy', preprocess_op.output, version, bucket, model)


if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(train_and_deploy, __file__ + '.tar.gz')
