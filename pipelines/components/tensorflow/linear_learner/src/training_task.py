# Copyright 2018 Google LLC. All Rights Reserved.
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
# ==============================================================================

"""Main task that starts Classification training."""

import json
import logging
import os
import data_utils
import model
import tensorflow as tf

# This controls the evaluation frequency for local runs. But for cloud
# runs it throttles the evaluations.
THROTTLE_SECS = 1
# The directory where the exported model resides (created by tensorflow).
EXPORT_DIR_NAME = 'export'


def _get_session_config_from_env_var():
  """Returns a tf.ConfigProto instance that has appropriate device_filters set.
  """
  tf_config = json.loads(os.environ.get('TF_CONFIG', '{}'))

  if (tf_config and 'task' in tf_config and 'type' in tf_config['task'] and
      'index' in tf_config['task']):
    # Master should only communicate with itself and ps
    if tf_config['task']['type'] == 'master':
      return tf.ConfigProto(device_filters=['/job:ps', '/job:master'])
    # Worker should only communicate with itself and ps
    elif tf_config['task']['type'] == 'worker':
      return tf.ConfigProto(device_filters=[
          '/job:ps',
          '/job:worker/task:%d' % tf_config['task']['index']
      ])
  return None


def run_training(args):
  """Main function that initializes a Linear Learner and starts training.

  Args:
    args: Dictionary of command line arguments for training. In the form of
      attributes instead of keys.
  """
  # Prepare data input for training and evaluations
  data_utils_obj = data_utils.DataUtils(
      file_type=args.input_type,
      is_classification=(args.model_type == 'classification'),
      export_dir_name=EXPORT_DIR_NAME)

  # For training we need to repeat the dataset forever.
  input_fn_train = data_utils_obj.get_input_fn(
      file_pattern=args.training_data_path,
      batch_size=args.batch_size,
      repeat=True,
      shuffle=True)
  # Evaluation input_fn
  if args.validation_data_path:
    input_fn_eval = data_utils_obj.get_input_fn(
        file_pattern=args.validation_data_path, batch_size=args.batch_size)
  else:
    input_fn_eval = data_utils_obj.get_input_fn(
        file_pattern=args.training_data_path, batch_size=args.batch_size)

  # Get feature_columns
  feature_columns = data_utils_obj.get_feature_columns()

  # Input functions for training and evaluation specs.
  train_spec = tf.estimator.TrainSpec(
      input_fn=input_fn_train, max_steps=args.max_steps)
  # Throttle seconds is set to 1, which is the lowest possible value.
  eval_spec = tf.estimator.EvalSpec(
      input_fn=input_fn_eval,
      exporters=[data_utils_obj.get_exporter('csv')],
      steps=args.eval_steps,
      name='validation',
      throttle_secs=THROTTLE_SECS,
      start_delay_secs=0)

  # Prepare estimator.
  linear_estimator = model.get_estimator(
      params=args,
      feature_columns=feature_columns,
      session_config=_get_session_config_from_env_var())

  tf.estimator.train_and_evaluate(linear_estimator, train_spec, eval_spec)

  # Only allow master to perform evaluation and export the
  # deployment_config.yaml file
  if tf.estimator.RunConfig().task_type == 'master':
    # Run a final evaluation to export metrics
    # Select the data_path to perform evaluation on, based on user input.
    data_path = (
        args.test_data_path or args.validation_data_path or
        args.train_data_path)

    eval_results = linear_estimator.evaluate(
        input_fn=data_utils_obj.get_input_fn(
            file_pattern=data_path, batch_size=args.batch_size),
        steps=None,
        name='final_evaluation')

    logging.info('Final evaluation results : %s', eval_results)

    # Export deployment_config.yaml file
    data_utils_obj.export_deployment_config_file(args.output_dir, eval_results)