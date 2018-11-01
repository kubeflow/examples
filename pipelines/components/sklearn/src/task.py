# ==============================================================================
#  Copyright 2018 Google LLC. All Rights Reserved.
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

import time
import pickle
import os.path
import argparse
import yaml
import pandas as pd
import tensorflow as tf
from sklearn import svm
from sklearn import tree
from sklearn import ensemble
from sklearn import neighbors
from sklearn import naive_bayes
from sklearn import linear_model
from sklearn import neural_network
from sklearn import gaussian_process


ESTIMATORS = {
  'AdaBoostClassifier': ensemble.AdaBoostClassifier,
  'BaggingClassifier': ensemble.BaggingClassifier,
  'DecisionTreeClassifier': tree.DecisionTreeClassifier,
  'ExtraTreesClassifier': ensemble.ExtraTreesClassifier,
  'GaussianNB': naive_bayes.GaussianNB,
  'GaussianProcessClassifier': gaussian_process.GaussianProcessClassifier,
  'GradientBoostingClassifier': ensemble.GradientBoostingClassifier,
  'GradientBoostingRegressor': ensemble.GradientBoostingRegressor,
  'KDTree': neighbors.KDTree,
  'KNeighborsClassifier': neighbors.KNeighborsClassifier,
  'KNeighborsRegressor': neighbors.KNeighborsRegressor,
  'Lasso': linear_model.Lasso,
  'LinearRegression': linear_model.LinearRegression,
  'LogisticRegression': linear_model.LogisticRegression,
  'MLPClassifier': neural_network.MLPClassifier,
  'RandomForestClassifier': ensemble.RandomForestClassifier,
  'Ridge': linear_model.Ridge,
  'SGDRegressor': linear_model.SGDRegressor,
  'SVC': svm.SVC,
  'SVR': svm.SVR,
}


def get_value(value):
  try:
    f_value = float(value)
    return int(f_value) if int(f_value) == f_value else f_value
  except ValueError:
    pass
  return value


def read_csv(data_path, header):
  with tf.gfile.Open(data_path, 'r') as f:
    dataframe = pd.read_csv(f, header=header)
    first_column = dataframe.columns[0]
    target = dataframe[first_column]
    del dataframe[first_column]
  return dataframe, target


def write_to_file(content, out_director, filename):
  with tf.gfile.Open(os.path.join(out_director, filename), 'w') as f:
    if isinstance(content, (str, int, float)):
      f.write(str(content))
    elif isinstance(content, dict):
      yaml.dump(content, f, default_flow_style=False)
    else:
      pickle.dump(content, f)


def get_estimator(estimator_name, hyperparameters):
  if estimator_name in ESTIMATORS:
    return ESTIMATORS[estimator_name](**hyperparameters)
  raise Exception("'{estimator_name}' is not supported".format(estimator_name=estimator_name))


def train(estimator_name, training_data_path, test_data_path, header, output_dir, hyperparameters):
  """
  Train and save a classification or regression model using sklearn
  :param estimator_name: The name of the sklearn estimator class
  :param training_data_path: The full path to the local (or GCS) training file
  :param test_data_path: The full path to the local (or GCS) test file
  :param output_dir: The output directory where the trained model is stored
  :param hyperparameters: a dictionary of hyperparameters to be passed to the estimator
  """
  estimator = get_estimator(estimator_name, hyperparameters)
  training_features, training_target = read_csv(training_data_path, header)

  report = {'training_samples': len(training_target),
            'hyperparameters': hyperparameters,
            'training_data_path': training_data_path}

  training_start_time = time.time()
  estimator.fit(training_features, training_target)
  training_end_time = time.time()
  training_time = training_end_time - training_start_time
  report['training_time'] = training_time

  now = time.strftime('%Y%m%d%H%M%S')
  model_name = '{}_{}.pkl'.format(estimator_name, now)
  report_name = '{}_{}_report.yaml'.format(estimator_name, now)
  report['model_name'] = model_name

  write_to_file(estimator, output_dir, model_name)

  if test_data_path is not None:
    test_features, test_target = read_csv(test_data_path, header)
    score = estimator.score(test_features, test_target)
    report['test_samples'] = len(test_target)
    report['test_score'] = float(score)
    report['test_data_path'] = test_data_path

  write_to_file(report, output_dir, report_name)
  print('Report: {}'.format(report_name))


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  estimators = ', '.join(sorted(ESTIMATORS.keys()))

  parser.add_argument(
    '--estimator_name',
    help='The name of the estimator to be used. Available estimators are: {}'.format(estimators),
    required=True)

  parser.add_argument(
    '--training_data_path',
    help='The path where the training data is stored.\n' +
         'It can be the path to a local file, or a file in a GCS bucket.\n' +
         'The expected input is a csv file where the target is the first column',
    required=True)

  parser.add_argument(
    '--test_data_path',
    help='The path where the tests data is stored.\n' +
        'It can be the path to a local file, or a file in a GCS bucket.\n' +
         'The expected input is a csv file with no header, ' +
         'and features have the same order as the training data')

  parser.add_argument(
    '--output_dir',
    help='The path where the training related file will be stored.',
    required=True)

  parser.add_argument('--with-header',
    help='Indicates that the train and test datasets have headers.\n' +
    'By default, it is assumed that the input files have no headers.'
    dest='header',
    action='store_true')

  arguments, hp_pairs = parser.parse_known_args()

  _training_data_path = arguments.training_data_path
  _test_data_path = arguments.test_data_path
  _output_dir = arguments.output_dir
  _est_name = arguments.estimator_name
  _header = 0 if arguments.header else None
  _hyperparams = {hp_pairs[i][2:]: get_value(hp_pairs[i + 1]) for i in range(0, len(hp_pairs), 2)}

  train(_est_name, _training_data_path, _test_data_path, _header, _output_dir, _hyperparams)
