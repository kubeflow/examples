# Copyright 2019 Google LLC
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
import kfp.gcp as gcp

DATASET_OP = 'dataset'
MODEL_OP = 'model'

@dsl.pipeline(
  name='automl1',
  description='Create AutoML dataset and train model'
)
def automl1(  #pylint: disable=unused-argument
  project_id='YOUR_PROJECT_HERE',
  compute_region='YOUR_REGION_HERE',
  dataset_name='YOUR_DATASETNAME_HERE',
  model_name='YOUR_MODELNAME_HERE',
  csv_path='YOUR_DATASET_PATH'
  ):


  dataset = dsl.ContainerOp(
      name='dataset',
      image='gcr.io/google-samples/automl-pipeline',
      arguments=["--project_id", project_id, "--operation", DATASET_OP,
          "--compute_region", compute_region,
          "--dataset_name", dataset_name,
          "--csv_path", csv_path],
      file_outputs={'dataset_id': '/dataset_id.txt', 'csv_path': '/csv_path.txt'}

      ).apply(gcp.use_gcp_secret('user-gcp-sa'))

  model = dsl.ContainerOp(
      name='model',
      image='gcr.io/google-samples/automl-pipeline',
      arguments=["--project_id", project_id, "--operation", MODEL_OP,
          "--compute_region", compute_region,
          "--model_name", model_name,
          "--csv_path", dataset.outputs['csv_path'],
          "--dataset_id", dataset.outputs['dataset_id']]
      ).apply(gcp.use_gcp_secret('user-gcp-sa'))

  model.after(dataset)



if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(automl1, __file__ + '.tar.gz')
