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

"""LinearModel class that helps initializes an estimator."""

import tensorflow as tf


def get_estimator(params, feature_columns, session_config):
  """Initializes a LinearRegressor or a LinearClassifier estimator.

  Args:
    params: Dictionary of parameters necessary to create tf.Estimator
    feature_columns : List of tf.feature_column that describes the features.
    session_config : A tf.ConfigProto type which will be passed to RunConfig()

  Returns:
    A tf.estimtator instance.
  """

  optimizer = _initialize_optimizer(params)

  # Eval frequency is assumed to be co-incident with ckpt frequency.
  config = tf.estimator.RunConfig(
    save_checkpoints_secs=params.eval_frequency_secs,
    session_config=session_config)

  if params.model_type == 'classification':
    return tf.estimator.LinearClassifier(
      feature_columns=feature_columns,
      optimizer=optimizer,
      n_classes=params.num_classes,
      model_dir=params.job_dir,
      loss_reduction=tf.losses.Reduction.MEAN,
      config=config)

  if params.model_type == 'regression':
    return tf.estimator.LinearRegressor(
        feature_columns=feature_columns,
        optimizer=optimizer,
        model_dir=params.job_dir,
        loss_reduction=tf.losses.Reduction.MEAN,
        config=config)


def _initialize_optimizer(params):
  """Initializes an optimizer with given learning rate and optimizer type.

  Args:
    params: Dictionary of parameters necessary to create tf optimizer

  Returns:
    A tf optimizer that could be used with a tf Estimator.
  """

  # Initialize optimizer instance.
  if params.optimizer_type == 'ftrl':
    return tf.train.FtrlOptimizer(
      learning_rate=params.learning_rate,
      l1_regularization_strength=params.l1_reg_strength,
      l2_regularization_strength=params.l2_reg_strength,
      l2_shrinkage_regularization_strength=params.l2_shrinkage_reg_strength)
  elif params.optimizer_type == 'adam':
    return tf.train.AdamOptimizer(
      learning_rate=params.learning_rate,
      beta1=params.beta_1,
      beta2=params.beta_2)

  elif params.optimizer_type == 'sgd':
    return tf.train.GradientDescentOptimizer(learning_rate=params.learning_rate)

  elif params.optimizer_type == 'rmse':
    return tf.train.RMSPropOptimizer(learning_rate=params.learning_rate)