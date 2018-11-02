#  Copyright 2016 The TensorFlow Authors. All Rights Reserved.
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
"""This showcases how simple it is to build image classification networks.

It follows description from this TensorFlow tutorial:
    https://www.tensorflow.org/versions/master/tutorials/mnist/pros/index.html#deep-mnist-for-experts
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import numpy as np
import tensorflow as tf

# Configure model options
TF_DATA_DIR = os.getenv("TF_DATA_DIR", "/tmp/data/")
TF_MODEL_DIR = os.getenv("TF_MODEL_DIR", None)
TF_EXPORT_DIR = os.getenv("TF_EXPORT_DIR", "mnist/")
TF_MODEL_TYPE = os.getenv("TF_MODEL_TYPE", "CNN")
TF_TRAIN_STEPS = int(os.getenv("TF_TRAIN_STEPS", 200))
TF_BATCH_SIZE = int(os.getenv("TF_BATCH_SIZE", 100))
TF_LEARNING_RATE = float(os.getenv("TF_LEARNING_RATE", 0.01))

N_DIGITS = 10  # Number of digits.
X_FEATURE = 'x'  # Name of the input feature.


def conv_model(features, labels, mode):
  """2-layer convolution model."""
  # Reshape feature to 4d tensor with 2nd and 3rd dimensions being
  # image width and height final dimension being the number of color channels.
  feature = tf.reshape(features[X_FEATURE], [-1, 28, 28, 1])

  # First conv layer will compute 32 features for each 5x5 patch
  with tf.variable_scope('conv_layer1'):
    h_conv1 = tf.layers.conv2d(
        feature,
        filters=32,
        kernel_size=[5, 5],
        padding='same',
        activation=tf.nn.relu)
    h_pool1 = tf.layers.max_pooling2d(
        h_conv1, pool_size=2, strides=2, padding='same')

  # Second conv layer will compute 64 features for each 5x5 patch.
  with tf.variable_scope('conv_layer2'):
    h_conv2 = tf.layers.conv2d(
        h_pool1,
        filters=64,
        kernel_size=[5, 5],
        padding='same',
        activation=tf.nn.relu)
    h_pool2 = tf.layers.max_pooling2d(
        h_conv2, pool_size=2, strides=2, padding='same')
    # reshape tensor into a batch of vectors
    h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])

  # Densely connected layer with 1024 neurons.
  h_fc1 = tf.layers.dense(h_pool2_flat, 1024, activation=tf.nn.relu)
  h_fc1 = tf.layers.dropout(
      h_fc1,
      rate=0.5,
      training=(mode == tf.estimator.ModeKeys.TRAIN))

  # Compute logits (1 per class) and compute loss.
  logits = tf.layers.dense(h_fc1, N_DIGITS, activation=None)
  predict = tf.nn.softmax(logits)
  classes = tf.cast(tf.argmax(predict, 1), tf.uint8)

  # Compute predictions.
  predicted_classes = tf.argmax(logits, 1)
  if mode == tf.estimator.ModeKeys.PREDICT:
    predictions = {
        'class': predicted_classes,
        'prob': tf.nn.softmax(logits)
    }
    return tf.estimator.EstimatorSpec(mode, predictions=predictions,
        export_outputs={'classes':
                        tf.estimator.export.PredictOutput({"predictions": predict,
                                                           "classes": classes})})

  # Compute loss.
  loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

  # Create training op.
  if mode == tf.estimator.ModeKeys.TRAIN:
    optimizer = tf.train.GradientDescentOptimizer(
        learning_rate=TF_LEARNING_RATE)
    train_op = optimizer.minimize(loss, global_step=tf.train.get_global_step())
    return tf.estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)

  # Compute evaluation metrics.
  eval_metric_ops = {
      'accuracy': tf.metrics.accuracy(
          labels=labels, predictions=predicted_classes)
  }
  return tf.estimator.EstimatorSpec(
      mode, loss=loss, eval_metric_ops=eval_metric_ops)


def cnn_serving_input_receiver_fn():
  inputs = {X_FEATURE: tf.placeholder(tf.float32, [None, 28, 28])}
  return tf.estimator.export.ServingInputReceiver(inputs, inputs)


def linear_serving_input_receiver_fn():
  inputs = {X_FEATURE: tf.placeholder(tf.float32, (784,))}
  return tf.estimator.export.ServingInputReceiver(inputs, inputs)


def main(_):
  tf.logging.set_verbosity(tf.logging.INFO)

  # Download and load MNIST dataset.
  mnist = tf.contrib.learn.datasets.DATASETS['mnist'](TF_DATA_DIR)
  train_input_fn = tf.estimator.inputs.numpy_input_fn(
      x={X_FEATURE: mnist.train.images},
      y=mnist.train.labels.astype(np.int32),
      batch_size=TF_BATCH_SIZE,
      num_epochs=None,
      shuffle=True)
  test_input_fn = tf.estimator.inputs.numpy_input_fn(
      x={X_FEATURE: mnist.train.images},
      y=mnist.train.labels.astype(np.int32),
      num_epochs=1,
      shuffle=False)

  training_config = tf.estimator.RunConfig(
      model_dir=TF_MODEL_DIR, save_summary_steps=100, save_checkpoints_steps=1000)

  if TF_MODEL_TYPE == "LINEAR":
    # Linear classifier.
    feature_columns = [
        tf.feature_column.numeric_column(
            X_FEATURE, shape=mnist.train.images.shape[1:])]
    classifier = tf.estimator.LinearClassifier(
        feature_columns=feature_columns, n_classes=N_DIGITS,
        model_dir=TF_MODEL_DIR, config=training_config)
    export_final = tf.estimator.FinalExporter(
        TF_EXPORT_DIR, serving_input_receiver_fn=cnn_serving_input_receiver_fn)

  elif TF_MODEL_TYPE == "CNN":
    # Convolutional network
    classifier = tf.estimator.Estimator(
        model_fn=conv_model, model_dir=TF_MODEL_DIR, config=training_config)
    export_final = tf.estimator.FinalExporter(
        TF_EXPORT_DIR, serving_input_receiver_fn=cnn_serving_input_receiver_fn)
  else:
    print("No such model type: %s" % TF_MODEL_TYPE)
    sys.exit(1)

  train_spec = tf.estimator.TrainSpec(
        input_fn=train_input_fn, max_steps=TF_TRAIN_STEPS)
  eval_spec = tf.estimator.EvalSpec(input_fn=test_input_fn,
                                      steps=1,
                                      exporters=export_final,
                                      throttle_secs=1,
                                      start_delay_secs=1)
  tf.estimator.train_and_evaluate(classifier, train_spec, eval_spec)

if __name__ == '__main__':
  tf.app.run()
