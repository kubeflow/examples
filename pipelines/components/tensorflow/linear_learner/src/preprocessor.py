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

"""Preprocessing job."""

from collections import defaultdict

import json
import numpy as np
import pandas as pd

try:
    xrange          # Python 2
except NameError:
    xrange = range  # Python 3


class InvalidSplit(Exception):
  """An exception that sum of validation split and test split is larger
  than 50%.
  """
  pass


class EmptyDataFrame(Exception):
  """An exception that a DataFrame is empty.
  """
  pass


class UnknownModelType(Exception):
  """An exception that an unknown model type is passed into the preprocessor.
  """
  pass


class PreProcessor(object):
  """Pre-processing module.

  This module provides a list of functions that can perform a series of
  preprocessing tasks on one or more given pandas DataFrames. Example usage:

  prep = PreProcessor()
  data_frame = prep.read_data('path/to/training.csv')
  data_frame = prep.shuffle_data(data_frame)
  data_frame = prep.remove_rows(data_frame)
  data_frame = prep.impute_missing_values(data_frame)
  data_frame = prep.encode_target_column(data_frame)
  data_frame = prep.encode_categorical_data(data_frame)
  [training_data_frame, validation_data_frame, test_data_frame] =
               prep.split_dataset(data_frame)
  prep.write_data(training_data_frame, 'path/to/processed_train.csv')
  """

  def __init__(self,
               max_missing_column_percent=0.1,
               min_training_split_percent=0.6,
               default_validation_split_percent=0.2,
               default_test_split_percent=0.2,
               random_seed=None):
    """Constructor for PreProcessor.

    Set some preprocessing specs. Currently these specs are related to imputing
    missing values and splitting the dataset. We are currently setting all the
    values as default.

    Args:
      max_missing_column_percent: if more than <_max_missing_column_percent> is
        missing, deletes the rows.
      min_training_split_percent: the minimum percentage of training data.
      default_validation_split_percent: default validation split percentage if
        not specified by the user.
      default_test_split_percent: default test split percentage if not
        specified by the user.
      random_seed: random seed to shuffle the dataset.
    """
    self._max_missing_column_percent = max_missing_column_percent
    self._min_training_split_percent = min_training_split_percent
    self._default_validation_split_percent = default_validation_split_percent
    self._default_test_split_percent = default_test_split_percent
    self._random_seed = random_seed

    # Record the mean of each numerical column. The key will be the column
    # index and the value will be the mean of that column.
    self._mean = {}

    # Record the categories of each non-numeirc column. The key will be the
    # the column index and the value will be the categories mapping of onehot
    # encoding.
    self._categories = {}

    # Record the class mapping of each class if it is a classification job.
    # The key will be the numerical mapping and the value will be the
    # corresponding class name.
    self.target_classes = None

    # Number of rows in training data frame.
    self.num_of_training_rows = 0

  def _concatenate_data_frames(self, *data_frames):
    """Concatenate multiple DataFrames into a single DataFrame.

    Args:
      *data_frames: one or more DataFrames.

    Returns:
      concatenated_data_frame: a concatenated DataFrame.
      df_breakpoint: a list of numbers indicating the splitting position on
                     the concatenated_data_frame.
    """
    df_breakpoint = [len(df) for df in data_frames]
    for i in xrange(1, len(df_breakpoint)):
      df_breakpoint[i] += df_breakpoint[i - 1]
    concatenated_data_frame = pd.concat(list(data_frames))
    return concatenated_data_frame, df_breakpoint

  def _split_data_frame(self, data_frame, df_breakpoint):
    """Split a single DataFrame into multiple.

    Args:
      data_frame: a single DataFrame to be split.
      df_breakpoint: a list of numbers indicating the splitting position on
                     the concatenated_data_frame.

    Returns:
      A list of DataFrames split from the single DataFrame.
    """
    data_frames = []
    last_bp = 0
    for bp in df_breakpoint:
      if bp <= last_bp:
        data_frames.append(pd.DataFrame())
      else:
        data_frames.append(data_frame.iloc[last_bp:bp, :])
      last_bp = bp
    return data_frames

  def read_data(self, data_path):
    """Reads a csv file from local path.

    Args:
      data_path: full file path of the dataset to be read.

    Returns:
      A pandas DataFrame.
    """
    # Currently we do not allow headers in the input data.
    return pd.read_csv(data_path, header=None)

  def shuffle_data(self, *data_frames):
    """Shuffles the data.

    Args:
      *data_frames: one or more pandas DataFrames.

    Returns:
      A list of shuffled pandas DataFrames.

    Raises:
      EmptyDataFrame: if an empty DataFrame is encountered.
    """
    processed_df = []
    for data_frame in data_frames:
      if data_frame.empty:
        raise EmptyDataFrame('Please check your data file to make sure it is '
                             'not empty.')
      data_frame = data_frame.sample(frac=1, random_state=self._random_seed)
      processed_df.append(data_frame)
    return processed_df

  def remove_rows(self, *data_frames):
    """Removes some rows of given DataFrames.

    Removes the entire row if there are more than
    <self._max_missing_column_percent> of attributes missing.

    Args:
      *data_frames: one or more pandas DataFrames.

    Returns:
      A list of pandas DataFrames with useless rows removed.

    Raises:
      EmptyDataFrame: if an empty DataFrame is encountered.
    """
    processed_df = []
    for data_frame in data_frames:
      if data_frame.empty:
        raise EmptyDataFrame('Please check your data file to make sure it is '
                             'not empty.')
      num_min_not_missing = \
        int(data_frame.shape[1] * (1 - self._max_missing_column_percent))
      data_frame.dropna(axis=0, thresh=num_min_not_missing,
                        inplace=True)
      processed_df.append(data_frame)
    return processed_df

  def impute_missing_values(self, *data_frames):
    """Imputes missing values for numeric columns.

    Numeric: imputes with mean value.
    Categorical: leaves it intact and sets nan to all zeros while encoding.
    TODO(hlzheng): figure out a better way to impute missing categorical value.
                   (imputes with the most frequent one?)
    Args:
      *data_frames: one or more pandas DataFrames.

    Returns:
      A list of pandas DataFrames with missing values imputed.

    Raises:
      EmptyDataFrame: if an empty DataFrame is encountered.
    """
    concatenated_data_frame, df_breakpoint = \
      self._concatenate_data_frames(*data_frames)

    # Starts from the second column since first column is treated as
    # label/regression value.
    for column in concatenated_data_frame.columns[1:]:
      # If the current column is numeric, imputes by mean.
      if np.issubdtype(concatenated_data_frame[column].dtype, np.number):
        if column not in self._mean:
          self._mean[column] = concatenated_data_frame[column].mean()
        # Proceeds if there is missing value in the current column.
        if concatenated_data_frame[column].isnull().values.any():
          concatenated_data_frame[column].fillna(self._mean[column],
                                                 inplace=True)

    return self._split_data_frame(concatenated_data_frame, df_breakpoint)

  def _onehot_encoding(self, data_frame):
    """Onehot encodes non-numeric columns in a pandas DataFrame.

    nan will be encoded as all zeros, which is taken care of by the get_dummies
    function.

    Args:
      data_frame: a pandas DataFrame.

    Returns:
      A pandas DataFrame after onehot encoding.
    """
    # A placeholder to hold all the processed columns. Starts with the
    # label/regression value column.
    processed_columns = [data_frame.iloc[:, 0]]

    for column in data_frame.columns[1:]:
      # Do not encode numeric columns.
      if np.issubdtype(data_frame[column].dtype, np.number):
        processed_columns.append(data_frame[column])
      else:
        if column not in self._categories:
          self._categories[column] = \
            data_frame[column].astype('category').cat.categories
        categorical_column = \
          data_frame[column].astype('category',
                                    categories=self._categories[column])
        encoded_columns = pd.get_dummies(categorical_column)
        for idx in encoded_columns:
          processed_columns.append(encoded_columns[idx])

    return pd.concat(processed_columns, axis=1)

  def _label_encoding(self, data_frame):
    pass

  def encode_categorical_data(self, *data_frames):
    """Encodes non-numeric columns in pandas DataFrames.

    Currently we are supporting in-place onehot encoding. More encoding methods
    to be added.

    Args:
      *data_frames: one or more pandas DataFrames.

    Returns:
      A list of pandas DataFrames with target column encoded.
    """
    concatenated_data_frame, df_breakpoint = \
      self._concatenate_data_frames(*data_frames)

    encoded_data_frame = self._onehot_encoding(concatenated_data_frame)

    return self._split_data_frame(encoded_data_frame, df_breakpoint)

  def encode_target_column(self, *data_frames):
    """Encodes the target columns in pandas DataFrames.

    Args:
      *data_frames: one or more pandas DataFrames.

    Returns:
      A list of pandas DataFrames with target column encoded.
    """
    concatenated_data_frame, df_breakpoint = \
      self._concatenate_data_frames(*data_frames)

    target_column = concatenated_data_frame.columns[0]
    concatenated_data_frame[target_column], self.target_classes = \
      pd.factorize(concatenated_data_frame[target_column])

    return self._split_data_frame(concatenated_data_frame, df_breakpoint)

  def split_dataset(self,
                    data_frame,
                    model_type,
                    validation_split=None,
                    test_split=None):
    """Splits a DataFrame into three DataFrames.

    If it is a classification job, splits different classes evenly among three
    DataFrames. Otherwise just performs a simple split according to the split
    percentage.

    Args:
      data_frame: a pandas DataFrame.
      model_type: classification or regression.
      validation_split: percentage of the validation data.
      test_split: percentage of the test data.

    Returns:
      A list of three pandas DataFrames.
      [train_dataframe, validation_dataframe, test_dataframe].

    Raises:
      InvalidSplit: if the sum of validation_split and test_split is larger than
                    a preset threshold.
      UnknownModelType: if the model_type is neither classification nor
                        regression.
    """
    validation_split = (
      validation_split or self._default_validation_split_percent)
    test_split = test_split or self._default_test_split_percent

    if validation_split + test_split > 1 - self._min_training_split_percent:
      raise InvalidSplit('Sum of validation_split and test_split is more than '
                         '%f' % (1 - self._min_training_split_percent))

    processed_df = []
    end_train_split = 1 - validation_split - test_split
    end_validation_split = 1 - test_split
    if model_type == 'classification':
      # Groups by the first column, which is the class label.
      grouped_df = data_frame.groupby(data_frame.columns[0])
      classes = sorted(grouped_df.groups.keys())

      train_dataframe = pd.DataFrame()
      validation_dataframe = pd.DataFrame()
      test_dataframe = pd.DataFrame()
      for class_label in classes:
        indices = grouped_df.groups[class_label]
        end_train_idx = int(len(indices) * end_train_split)
        end_validation_idx = int(len(indices) * end_validation_split)
        # If there is no room for validation, assign one instance to it.
        if end_train_idx == end_validation_idx:
          end_train_idx -= 1

        train_indices = indices[:end_train_idx]
        validation_indices = indices[end_train_idx:end_validation_idx]
        test_indices = indices[end_validation_idx:]

        train_dataframe = pd.concat([train_dataframe,
                                     data_frame.loc[train_indices]])
        validation_dataframe = pd.concat([validation_dataframe,
                                          data_frame.loc[validation_indices]])
        test_dataframe = pd.concat([test_dataframe,
                                    data_frame.loc[test_indices]])

      # Needs to shuffle again to mix all the classes.
      processed_df = self.shuffle_data(train_dataframe,
                                       validation_dataframe,
                                       test_dataframe)
    elif model_type == 'linear':
      end_train_idx = int(len(data_frame) * end_train_split)
      end_validation_idx = int(len(data_frame) * end_validation_split)

      processed_df = [data_frame.iloc[:end_train_idx],
                      data_frame.iloc[end_train_idx:end_validation_idx],
                      data_frame.iloc[end_validation_idx:]]
    else:
      raise UnknownModelType('Unknown model type.')

    return processed_df

  def write_data(self, data_frame, output_dir):
    """Writes the data frame to local output directory.

    Args:
      data_frame: a pandas DataFrame to be saved as a csv file.
      output_dir: targeted output path.
    """
    data_frame.to_csv(output_dir, header=None, index=None)

  def run_preprocessing(self,
                        input_data_paths,
                        output_data_paths,
                        model_type,
                        validation_split=None,
                        test_split=None):
    """Starts a pre-processing pipeline.

    At the end of pre-processing it outputs files according to
    <output_data_paths>.

    Args:
      input_data_paths: Path to input csv files to be used for pre-processing.
      output_data_paths: Path to output csv pre-processed files.
      model_type: classification or regression.
      validation_split: percentage of the validation data.
      test_split: percentage of the test data.

    Raises:
      ValueError: If length of input_data_paths and output_data_paths are not
      equal, or
      If length of input_data_paths=1 and output_data_paths!=3, or
      If input_data_paths is empty.
    """
    # Check for empty data path.
    if not input_data_paths or not output_data_paths:
      raise ValueError('The input_data_paths or output_data_paths cannot be'
                       ' empty')
    # Check if only one input data path is specified. Then output should have 3
    # data paths.
    if len(input_data_paths) == 1:
      if len(output_data_paths) != 3:
        raise ValueError('The length of output_data_paths must be 3 when there'
                         ' is only one input_data_path.')
    # Check that the length of input_data_paths and output_data_paths are equal.
    elif len(input_data_paths) != len(output_data_paths):
      raise ValueError('The length of input_data_paths and output_data_paths'
                       ' are not equal.')

    data_frames = []
    for input_data_path in input_data_paths:
      data_frames.append(self.read_data(input_data_path))

    data_frames = self.remove_rows(*data_frames)
    data_frames = self.impute_missing_values(*data_frames)
    data_frames = self.encode_categorical_data(*data_frames)

    if model_type == 'classification':
      data_frames = self.encode_target_column(*data_frames)

    if len(data_frames) == 1:
      data_frames = self.split_dataset(data_frames[0], model_type,
                                       validation_split, test_split)
    else:
      # Only do shuffling if dataset is not being split.
      data_frames = self.shuffle_data(*data_frames)

    # Write pre-processed data, based on the input argument.
    for i, output_data_path in enumerate(output_data_paths):
      self.write_data(data_frames[i], output_data_path)

    self.num_of_training_rows = len(data_frames[0].index)

  def _prepare_feature_mapping(self):
    """Prepares the feature mapping dictionary.

    Returns:
      feature_mapping: a dictionary contains the feature mapping.
    """
    feature_mapping = defaultdict(dict)
    if self._mean:
      for column in self._mean:
        feature_mapping[column]['type'] = 'numerical'
        feature_mapping[column]['statistics'] = {}
        feature_mapping[column]['statistics']['mean'] = self._mean[column]

    if self._categories:
      for column in self._categories:
        category = self._categories[column]
        feature_mapping[column]['type'] = 'categorical'
        feature_mapping[column]['num_category'] = len(category)
        feature_mapping[column]['mapping'] = {}
        for idx, cat in enumerate(category):
          feature_mapping[column]['mapping'][cat] = idx

    return feature_mapping if feature_mapping else None

  def _prepare_target_mapping(self):
    """Prepares the target column mapping dictionary.

    Returns:
      target_mapping: a dictionary contains the target mapping.
    """
    if self.target_classes is None:
      return None
    target_mapping = {}
    for idx, class_name in enumerate(self.target_classes):
      target_mapping[idx] = class_name

    return target_mapping

  def export_mapping(self, mapping_path):
    """Exports the feature mapping and target column mapping as a JSON file.

    Args:
      mapping_path: a directory to store the JSON mapping file.
    """
    target_mapping = self._prepare_target_mapping()
    feature_mapping = self._prepare_feature_mapping()
    mapping = {'target_column': target_mapping,
               'feature_columns': feature_mapping}
    with open(mapping_path, 'w') as file_handler:
      json.dump(mapping, file_handler, sort_keys=True, indent=2)
