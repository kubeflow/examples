"""Module for running the training of the machine learning model.

Scripts that performs all the steps to train the ML model.
"""
import logging
import os
import argparse
import time
from google.cloud import storage
import tensorflow as tf

import models
import preprocess
import metrics


def get_preprocessed_data():
  """Obtain the preprocessed data."""
  tickers = ['snp', 'nyse', 'djia', 'nikkei', 'hangseng', 'ftse', 'dax', 'aord']
  closing_data = preprocess.load_data(tickers)
  time_series = preprocess.preprocess_data(closing_data)
  training_test_data = preprocess.train_test_split(time_series, train_test_ratio=0.8)
  return training_test_data


def upload_to_storage(bucket, export_path):
  """Upload files from export path to Google Cloud Storage.

  Args:
    bucket (str): Google Cloud Storage bucket
    export_path (str): export path

  Returns:

  """
  client = storage.Client()
  bucket = client.get_bucket(bucket)
  if bucket:
    for root, _, files in os.walk(export_path):
      for file in files:
        path = os.path.join(root, file)
        blob = bucket.blob(path)
        blob.upload_from_filename(path)


def run_training(args):
  """Runs the ML model training script.

  Args:
    args: args that are passed when submitting the training

  Returns:

  """
  # parse args
  logging.info('parsing args...')
  model = getattr(models, args.model)(nr_predictors=24, nr_classes=2)

  # get the data
  logging.info('getting the data...')
  training_test_data = get_preprocessed_data()

  # define training objective
  logging.info('defining the training objective...')
  sess = tf.Session()
  feature_data = tf.placeholder("float", [None, 24])
  actual_classes = tf.placeholder("float", [None, 2])

  model = model.build_model(feature_data)
  cost = -tf.reduce_sum(actual_classes * tf.log(model))
  train_opt = tf.train.AdamOptimizer(learning_rate=0.0001).minimize(cost)
  init = tf.global_variables_initializer()
  sess.run(init)

  # train model
  correct_prediction = tf.equal(tf.argmax(model, 1), tf.argmax(actual_classes, 1))
  accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))

  logging.info('training the model...')
  time_dct = {}
  time_dct['start'] = time.time()
  for i in range(1, args.epochs):
    sess.run(
        train_opt,
        feed_dict={
            feature_data: training_test_data['training_predictors_tf'].values,
            actual_classes: training_test_data['training_classes_tf'].values.reshape(
                len(training_test_data['training_classes_tf'].values), 2)
        }
    )
    if i % 5000 == 0:
      print(i, sess.run(
          accuracy,
          feed_dict={
              feature_data: training_test_data['training_predictors_tf'].values,
              actual_classes: training_test_data['training_classes_tf'].values.reshape(
                  len(training_test_data['training_classes_tf'].values), 2)
          }
      ))
  time_dct['end'] = time.time()
  logging.info('training took {0:.2f} sec'.format(time_dct['end'] - time_dct['start']))

  # print results of confusion matrix
  logging.info('validating model on test set...')
  feed_dict = {
      feature_data: training_test_data['test_predictors_tf'].values,
      actual_classes: training_test_data['test_classes_tf'].values.reshape(
          len(training_test_data['test_classes_tf'].values), 2)
  }
  metrics.tf_confusion_matrix(model, actual_classes, sess, feed_dict)

  # create signature for TensorFlow Serving
  logging.info('Exporting model for tensorflow-serving...')

  export_path = args.version
  tf.saved_model.simple_save(
      sess,
      export_path,
      inputs={'predictors': feature_data},
      outputs={'prediction': tf.argmax(model, 1),
               'model-version': tf.constant([str(args.version)])}
  )

  # save model on GCS
  logging.info("uploading to " + args.bucket + "/" + export_path)
  upload_to_storage(args.bucket, export_path)


def main():
  parser = argparse.ArgumentParser(description='Training')

  parser.add_argument('--model',
                      type=str,
                      help='model to be used for training',
                      default='DeepModel',
                      choices=['FlatModel', 'DeepModel'])

  parser.add_argument('--epochs',
                      type=int,
                      help='number of epochs to train',
                      default=30001)

  parser.add_argument('--version',
                      type=str,
                      help='version (stored for serving)',
                      default='1')

  parser.add_argument('--bucket',
                      type=str,
                      help='GCS bucket where model is saved',
                      default='<your-bucket-name>')

  args = parser.parse_args()
  run_training(args)


if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)
  main()
