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

import csv
import os
import tensorflow as tf


from tensorflow.python.lib.io import file_io


try:
    xrange
except NameError:
    xrange = range


class DataUtils(object):
  """Main class that handles data utilities.

  First column of csv file is assumed to be the target.
  0. is the default value for missing values.
  All the data values in column are parsed as floats except target in case of
  classification job.
  """

  def __init__(self, file_type, is_classification, export_dir_name='export'):
    self._column_header = None
    self._file_type = file_type
    self._is_classification = is_classification
    self._export_dir_name = export_dir_name

  def _make_input_parser(self, with_target=True):
    """Returns a parser func according to file_type, task_type and target.

    Need to set record_default for 1st column to integer instead of float in
    case of classification tasks.

    Args:
      with_target: Whether target will be there ot not. We don't need the target
        when doing prediction.

    Returns:
      It returns a parser for different file type,task type and target presence.
    """

    def parse_csv(rows_string_tensor):
      """Takes the string input tensor and parses it to feature dict and target.

      All the columns except the first one are treated as feature column. The
      first column is expected to be the target.
      Only returns target for if with_target is True.

      Args:
        rows_string_tensor: csv rows in tensor format.
      Returns:
        features: A dictionary of features with key as "column_names" from
          self._column_header.
        target: tensor of target values which is the first column of the file.
          This will only be returned if with_target==True.
      """
      column_header = (
        self._column_header if with_target else self._column_header[1:])

      record_default = [[0.] for _ in xrange(len(column_header))]

      # Set target's default value to integer in case of classification.
      record_default[0][0] = 0 if self._is_classification else record_default[
        0][0]

      columns = tf.decode_csv(
        rows_string_tensor, record_defaults=record_default)
      features = dict(zip(column_header, columns))
      # We don't expect target to be there in input.
      target = features.pop(column_header[0]) if with_target else None
      return features, target

    if self._file_type == 'csv':
      return parse_csv

  def _initialize_column_header(self, filename):
    """Build column headers from the CSV file or file containing TF-Examples.

    Each column header will be the column position for csv and column key for
    TF-Example.

    Args:
      filename: Training input file path.
    """
    if self._file_type == 'csv':
      with file_io.FileIO(filename, 'r') as f:
        num_columns = len(next(csv.reader(f, delimiter=',')))

      self._column_header = [str(i) for i in xrange(num_columns)]

  def get_input_fn(self, file_pattern, batch_size, repeat=False, shuffle=False):
    """Returns a function that will return a (features, target) tuple.

    Args:
      file_pattern: Glob file pattern for input.
      batch_size: Number of data examples in a batch for a step.
      repeat: Whether to infinitely repeat the dataset or not. It is used when
        we don't want input_fn() to throw OutOfRangeError. Defaults to False.
      shuffle: Whether to shuffle dataset. Should be True for training.

    Returns:
      A input_fn function that can directly be fed to a TrainSpec or EvalSpec.

    Raises:
      ValueError : If the file_pattern doesn't match with any files.
    """
    filenames = file_io.get_matching_files(file_pattern)
    if not filenames:
      raise ValueError(
        'File pattern : {} doesn\'t match any files'.format(file_pattern))

    if not self._column_header:
      # Column header can be generated from any of the files.
      # Note: Column Header generated is a list of column_numbers.
      self._initialize_column_header(filenames[0])

    def input_fn():
      """Creates a input_fn to be fed to TrainSpec or EvalSpec.

      Returns:
        A (features(dict), target) tuple which is a dataset iterator object.
      """
      if self._file_type == 'csv':
        read_fn = tf.data.TextLineDataset

      if len(filenames) > 1:
        files_dataset = tf.data.Dataset.list_files(filenames)

        if shuffle:
          files_dataset = files_dataset.shuffle(len(filenames))

        dataset = files_dataset.interleave(
          lambda filename: read_fn(filename).map(
            self._make_input_parser(with_target=True)),
          cycle_length=len(filenames))

      else:
        dataset = tf.data.TextLineDataset(filenames)
        if shuffle:
          dataset = dataset.shuffle(buffer_size=batch_size * 10)
        dataset = dataset.map(self._make_input_parser(with_target=True))

      if repeat:
        dataset = dataset.repeat()

      dataset = dataset.batch(batch_size)

      # Make iterator.
      iterator = dataset.make_one_shot_iterator()
      features, target = iterator.get_next()

      return features, target

    return input_fn

  def get_feature_columns(self):
    """Returns feature_columns to be used for an Estimator.

    Returns:
      A list of numeric_columns for all the columns in _column_header except
      target.
    """
    return [
      tf.feature_column.numeric_column(header)
      for header in self._column_header[1:]
      ]

  def get_exporter(self, exporter_type):
    """Get an exporter for estimator.

    Args:
      exporter_type: Only supporting csv export type for now.

    Returns:
      An export of exporter_type that can be directly fed to an estimator.
    """
    serving_input_fn = None
    if exporter_type == 'csv':
      serving_input_fn = self._csv_serving_input_fn

    return tf.estimator.FinalExporter(self._export_dir_name, serving_input_fn)

  def _csv_serving_input_fn(self):
    """Build the serving inputs."""
    csv_row = tf.placeholder(shape=[None], dtype=tf.string)
    features, _ = self._make_input_parser(with_target=False)(csv_row)
    return tf.estimator.export.ServingInputReceiver(features,
                                                    {'csv_row': csv_row})

  def _get_full_model_export_path(self, output_dir):
    """Get the latest model export path using _export_dir_name and timestamps.

    Args:
      output_dir: GCS path where the model has been trained.

    Returns:
      A full GCS path that points to the latest exported model dir
      <output_dir>/export/<_export_dir_name>/<latest_timestamp>/

    Raises:
      IOError: If no exported model is found in the directory.
    """
    timestamp_dir_path = os.path.join(output_dir, 'export',
                                      self._export_dir_name)
    try:
      timestamped_dir_list = file_io.list_directory(timestamp_dir_path)
    except tf.errors.NotFoundError:
      timestamped_dir_list = None

    if not timestamped_dir_list:
      raise IOError('No exported model was found in the directory',
                    timestamp_dir_path)

    # Convert string timestamps to long so that it can be sorted.
    # When doing list_files in a GCS directory it outputs directories name as
    # '12345678/'. Hence we need to check for that case.
    timestamped_dir_list = [
      long(timestamp.strip('/')) for timestamp in timestamped_dir_list
      ]
    latest_model_path = os.path.join(timestamp_dir_path,
                                     str(sorted(timestamped_dir_list)[-1]))

    return latest_model_path
