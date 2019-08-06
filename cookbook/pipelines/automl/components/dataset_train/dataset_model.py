#!/usr/bin/env python

# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This application demonstrates how to perform basic operations on model
with the Google AutoML Vision API.

For more information, the documentation at
https://cloud.google.com/vision/automl/docs.
"""

import argparse
import logging
import os
import time

from google.cloud import automl

DATASET_OP = 'dataset'
MODEL_OP = 'model'


def create_dataset(project_id, compute_region, dataset_name, multilabel=False):
    """Create a dataset."""

    client = automl.AutoMlClient()

    # A resource that represents Google Cloud Platform location.
    project_location = client.location_path(project_id, compute_region)

    # Classification type is assigned based on multilabel value.
    classification_type = "MULTICLASS"
    if multilabel:
        classification_type = "MULTILABEL"

    # Specify the image classification type for the dataset.
    dataset_metadata = {"classification_type": classification_type}
    # Set dataset name and metadata of the dataset.
    my_dataset = {
        "display_name": dataset_name,
        "image_classification_dataset_metadata": dataset_metadata,
    }

    # Create a dataset with the dataset metadata in the region.
    dataset = client.create_dataset(project_location, my_dataset) # TODO: what error-checking needed?
    dataset_id = dataset.name.split("/")[-1]

    # Display the dataset information.
    print("Dataset name: {}".format(dataset.name))
    print("Dataset id: {}".format(dataset_id))
    print("Dataset display name: {}".format(dataset.display_name))
    print("Image classification dataset metadata:")
    print("\t{}".format(dataset.image_classification_dataset_metadata))
    print("Dataset example count: {}".format(dataset.example_count))
    print("Dataset create time:")
    print("\tseconds: {}".format(dataset.create_time.seconds))
    print("\tnanos: {}".format(dataset.create_time.nanos))

    return dataset_id


def import_data(project_id, compute_region, dataset_id, csv_path):
    """Import labeled images."""
    # csv_path = 'gs://path/to/file.csv'

    client = automl.AutoMlClient()

    # Get the full path of the dataset.
    dataset_full_id = client.dataset_path(
        project_id, compute_region, dataset_id
    )

    # Get the multiple Google Cloud Storage URIs.
    input_uris = csv_path.split(",")
    input_config = {"gcs_source": {"input_uris": input_uris}}

    # Import data from the input URI.
    response = client.import_data(dataset_full_id, input_config)

    print("Processing import...")
    # synchronous check of operation status.
    print("Data imported. {}".format(response.result()))


def create_model(
    project_id, compute_region, dataset_id, model_name, train_budget=24
):
    """Create a model."""

    client = automl.AutoMlClient()

    # A resource that represents Google Cloud Platform location.
    project_location = client.location_path(project_id, compute_region)

    # Set model name and model metadata for the image dataset.
    my_model = {
        "display_name": model_name,
        "dataset_id": dataset_id,
        "image_classification_model_metadata": {"train_budget": train_budget}
        if train_budget
        else {},
    }

    # Create a model with the model metadata in the region.
    operation = client.create_model(project_location, my_model)
    opname = operation.operation.name
    print("Training operation name: {}".format(opname))
    print("Training started, waiting for result...")
    result = operation.result()  # do synchronous wait in this case. TODO: Are there timeouts/deadlines?
    print('result:')
    print(result)
    return opname, result


def main(argv=None):
  parser = argparse.ArgumentParser(description='AutoML')
  parser.add_argument(
      '--operation', type=str,  # 'dataset' or 'model'
      help='...',
      required=True)
  parser.add_argument(
      '--project_id', type=str,
      help='...',
      required=True)
  parser.add_argument(
      '--compute_region', type=str,
      help='...',
      required=True)
  parser.add_argument(
      '--dataset_name', type=str,
      help='...',
      # required=True
      )
  parser.add_argument(
      '--dataset_id', type=str,
      help='...',
      )
  parser.add_argument(
      '--csv_path', type=str,
      help='gs://path/to/file.csv',
      )
  parser.add_argument(
      '--model_name', type=str,
      help='...',
      )
  parser.add_argument(
      '--train_budget', type=int,
      default=1,
      help='...',
      )

  args = parser.parse_args()
  logging.getLogger().setLevel(logging.INFO)


  try:
    print('args.operation: %s' % args.operation)
    if args.operation == DATASET_OP:
      # create the dataset and import data.
      # required args: project_id, compute_region, dataset_name, csv_path
      # output: dataset_id
      if not args.dataset_name:
        logging.error('error: dataset name not provided.')
        raise Exception('error: dataset name not provided.')
      if not args.csv_path:
        logging.error('error: path to csv file not provided.')
        raise Exception('error: path to csv file not provided.')
      dataset_id = create_dataset(args.project_id, args.compute_region, args.dataset_name)
      logging.info("using dataset_id %s", dataset_id)
      import_data(args.project_id, args.compute_region, dataset_id, args.csv_path)
      # write dataset_id and csv path as outputs of the pipeline step
      with open('/dataset_id.txt', 'w') as f:
        f.write(dataset_id)
      with open('/csv_path.txt', 'w') as f:
        f.write(args.csv_path)

    elif args.operation == MODEL_OP:
      # train a model given the dataset_id
      # required args: project_id, compute_region, dataset_id, model_name
      if not args.dataset_id:
        logging.error('error: dataset id not provided.')
        raise Exception('error: dataset id not provided.')
      if not args.model_name:
        logging.error('error: model name not provided.')
        raise Exception('error: model name not provided.')

      logging.info("using train budget: %s", args.train_budget)
      logging.info("starting model training...")
      opname, result = create_model(args.project_id, args.compute_region, args.dataset_id,
          args.model_name, train_budget=args.train_budget)
      logging.info("model training complete.")
      model_realname = result.name
      model_realname = model_realname.split('/')[-1] # grab just the model id
      logging.info("model 'real' name: %s", model_realname)


    else:
      logging.error('error: unknown operation %s' % args.operation)
      raise Exception('error: unknown operation')
  except Exception as e:
    logging.warn(e)



if __name__== "__main__":
  main()


# ===========
# The following aren't required for this simple pipeline example, but show how some
# other parts of the AutoML API can be used.  Okay to delete in your own copy.


# def get_operation_status(operation_full_id):
#     """Get operation status."""
#     # TODO(developer): Uncomment and set the following variables
#     # operation_full_id =
#     #   'projects/<projectId>/locations/<region>/operations/<operationId>'

#     client = automl.AutoMlClient()

#     # Get the latest state of a long-running operation.
#     response = client.transport._operations_client.get_operation(
#         operation_full_id
#     )
#     print(response)
#     return response


# def list_models(project_id, compute_region, filter_):
#     """List all models."""

#     from google.cloud.automl import enums

#     client = automl.AutoMlClient()

#     # A resource that represents Google Cloud Platform location.
#     project_location = client.location_path(project_id, compute_region)

#     # List all the models available in the region by applying filter.
#     response = client.list_models(project_location, filter_)

#     print("List of models:")
#     for model in response:
#         # Retrieve deployment state.
#         if model.deployment_state == enums.Model.DeploymentState.DEPLOYED:
#             deployment_state = "deployed"
#         else:
#             deployment_state = "undeployed"

#         # Display the model information.
#         print("Model name: {}".format(model.name))
#         print("Model id: {}".format(model.name.split("/")[-1]))
#         print("Model display name: {}".format(model.display_name))
#         print("Image classification model metadata:")
#         print(
#             "Training budget: {}".format(
#                 model.image_classification_model_metadata.train_budget
#             )
#         )
#         print(
#             "Training cost: {}".format(
#                 model.image_classification_model_metadata.train_cost
#             )
#         )
#         print(
#             "Stop reason: {}".format(
#                 model.image_classification_model_metadata.stop_reason
#             )
#         )
#         print(
#             "Base model id: {}".format(
#                 model.image_classification_model_metadata.base_model_id
#             )
#         )
#         print("Model create time:")
#         print("\tseconds: {}".format(model.create_time.seconds))
#         print("\tnanos: {}".format(model.create_time.nanos))
#         print("Model deployment state: {}".format(deployment_state))



# def get_model(project_id, compute_region, model_id):
#     """Get model details."""

#     from google.cloud.automl import enums

#     client = automl.AutoMlClient()

#     # Get the full path of the model.
#     model_full_id = client.model_path(project_id, compute_region, model_id)

#     # Get complete detail of the model.
#     model = client.get_model(model_full_id)

#     # Retrieve deployment state.
#     if model.deployment_state == enums.Model.DeploymentState.DEPLOYED:
#         deployment_state = "deployed"
#     else:
#         deployment_state = "undeployed"

#     # Display the model information.
#     print("Model name: {}".format(model.name))
#     print("Model id: {}".format(model.name.split("/")[-1]))
#     print("Model display name: {}".format(model.display_name))
#     print("Image classification model metadata:")
#     print(
#         "Training budget: {}".format(
#             model.image_classification_model_metadata.train_budget
#         )
#     )
#     print(
#         "Training cost: {}".format(
#             model.image_classification_model_metadata.train_cost
#         )
#     )
#     print(
#         "Stop reason: {}".format(
#             model.image_classification_model_metadata.stop_reason
#         )
#     )
#     print(
#         "Base model id: {}".format(
#             model.image_classification_model_metadata.base_model_id
#         )
#     )
#     print("Model create time:")
#     print("\tseconds: {}".format(model.create_time.seconds))
#     print("\tnanos: {}".format(model.create_time.nanos))
#     print("Model deployment state: {}".format(deployment_state))


# def list_model_evaluations(project_id, compute_region, model_id, filter_):
#     """List model evaluations."""

#     client = automl.AutoMlClient()

#     # Get the full path of the model.
#     model_full_id = client.model_path(project_id, compute_region, model_id)

#     # List all the model evaluations in the model by applying filter.
#     response = client.list_model_evaluations(model_full_id, filter_)

#     print("List of model evaluations:")
#     for element in response:
#         print(element)

#     # [END automl_vision_list_model_evaluations]


# def get_model_evaluation(
#     project_id, compute_region, model_id, model_evaluation_id
# ):
#     """Get model evaluation."""

#     client = automl.AutoMlClient()

#     # Get the full path of the model evaluation.
#     model_evaluation_full_id = client.model_evaluation_path(
#         project_id, compute_region, model_id, model_evaluation_id
#     )

#     # Get complete detail of the model evaluation.
#     response = client.get_model_evaluation(model_evaluation_full_id)

#     print(response)


# def display_evaluation(project_id, compute_region, model_id, filter_):
#     """Display evaluation."""

#     client = automl.AutoMlClient()

#     # Get the full path of the model.
#     model_full_id = client.model_path(project_id, compute_region, model_id)

#     # List all the model evaluations in the model by applying filter.
#     response = client.list_model_evaluations(model_full_id, filter_)

#     # Iterate through the results.
#     for element in response:
#         # There is evaluation for each class in a model and for overall model.
#         # Get only the evaluation of overall model.
#         if not element.annotation_spec_id:
#             model_evaluation_id = element.name.split("/")[-1]

#     # Resource name for the model evaluation.
#     model_evaluation_full_id = client.model_evaluation_path(
#         project_id, compute_region, model_id, model_evaluation_id
#     )

#     # Get a model evaluation.
#     model_evaluation = client.get_model_evaluation(model_evaluation_full_id)

#     class_metrics = model_evaluation.classification_evaluation_metrics
#     confidence_metrics_entries = class_metrics.confidence_metrics_entry

#     # Showing model score based on threshold of 0.5
#     for confidence_metrics_entry in confidence_metrics_entries:
#         if confidence_metrics_entry.confidence_threshold == 0.5:
#             print("Precision and recall are based on a score threshold of 0.5")
#             print(
#                 "Model Precision: {}%".format(
#                     round(confidence_metrics_entry.precision * 100, 2)
#                 )
#             )
#             print(
#                 "Model Recall: {}%".format(
#                     round(confidence_metrics_entry.recall * 100, 2)
#                 )
#             )
#             print(
#                 "Model F1 score: {}%".format(
#                     round(confidence_metrics_entry.f1_score * 100, 2)
#                 )
#             )
#             print(
#                 "Model Precision@1: {}%".format(
#                     round(confidence_metrics_entry.precision_at1 * 100, 2)
#                 )
#             )
#             print(
#                 "Model Recall@1: {}%".format(
#                     round(confidence_metrics_entry.recall_at1 * 100, 2)
#                 )
#             )
#             print(
#                 "Model F1 score@1: {}%".format(
#                     round(confidence_metrics_entry.f1_score_at1 * 100, 2)
#                 )
#             )



# def delete_model(project_id, compute_region, model_id):
#     """Delete a model."""

#     client = automl.AutoMlClient()

#     # Get the full path of the model.
#     model_full_id = client.model_path(project_id, compute_region, model_id)

#     # Delete a model.
#     response = client.delete_model(model_full_id)

#     # synchronous check of operation status.
#     print("Model deleted. {}".format(response.result()))
