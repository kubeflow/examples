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

@dsl.pipeline(
  name='Github issue summarization',
  description='Demonstrate Tensor2Tensor-based training and TF-Serving'
)
def gh_summ(
  github_token: dsl.PipelineParam = dsl.PipelineParam(
      name='github-token', value='YOUR_GITHUB_TOKEN_HERE'),
  ):


  serve = dsl.ContainerOp(
      name='serve',
      image='gcr.io/google-samples/ml-pipeline-kubeflow-tfserve',
      arguments=["--model_name", 'ghsumm-%s' % ('{{workflow.name}}',),
          "--model_path",
          'gs://aju-dev-demos-codelabs/kubecon/example_t2t_model/model_output/export'
          ]
      )

  webapp = dsl.ContainerOp(
      name='webapp',
      image='gcr.io/google-samples/ml-pipeline-webapp-launcher',
      arguments=["--model_name", 'ghsumm-%s' % ('{{workflow.name}}',),
          "--github_token", github_token]

      )
  webapp.after(serve)


if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(gh_summ, __file__ + '.tar.gz')
