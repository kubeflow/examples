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

"""Controller of Linear Learner algorithm, runs preprocessor and then training.

This module does the following:
1) Download all files from GCS to local VM path (WORKING_DIR/TEMP_DIR).
2) If preprocessing is mentioned, then it calls pre_processor library to do
pre-processing and saves the processed data in PROCESSED_DATA_DIR.
3) If preprocessing is not mentioned, then we just load the training_data and
count the num_of_training_rows and number_classes if it's a 'classification'
job.
4) Then we change a few flags:
input_data flags to point to local VM paths. These are where the trainer will
read the data from.
Set max_steps according to the DEFAULT_EPOCHS and num_of_training_rows
Set number_classes if its a classification job.
5) Start running training.
6) If user specified preprocessing then upload the PROCESSED_DATA_DIR and the
EXPORT_DIR to user's GCS bucket path.
"""

import argparse
import logging
import math
import os
import subprocess
import sys

import preprocessor
import training_task

# Minimum classes for classification.
MIN_CLASSES = 2
# If max_steps is not provide, then use this to calculate max_steps
DEFAULT_EPOCHS = 10
# local and GCS data folder where the processed data would be stored.
PROCESSED_DATA_DIR = 'processed/'
# Directory in GCS where the model should be saved.
GCS_MODEL_DIR = 'model/'
# Current working directory.
WORKING_DIR = os.getcwd()
# Temporary directory inside
TEMP_DIR = 'tmp/'
# Directory which will contain the model artifcats to be exported.
EXPORT_DIR = 'export/'
# List of file names where processed files will be written to.
TRAINING_FILE_NAME = 'training.csv'
VALIDATION_FILE_NAME = 'validation.csv'
TEST_FILE_NAME = 'test.csv'


def check_num_classes(num_classes):
  """Verifies number of classes argument is integer from Argument parser.

  Args:
    num_classes: An `int` with the number of classes defined in argparse.

  Returns:
    An `int` with the number of classes.

  Raises:
     ArgumentTypeError: Minimum classes is 2.
  """
  if isinstance(num_classes, int):
    if num_classes < MIN_CLASSES:
      raise argparse.ArgumentTypeError(
          'Argument "num_classes" should have a minimum value of 2')
    return num_classes
  else:
    raise argparse.ArgumentTypeError(
        'Argument "num_classes" should be an integer with a minimum value of 2"'
    )


def get_args():
  """Argument parser.

  Returns:
    Dictionary of arguments.
  """
  parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter)

  parser.add_argument(
    '--preprocess',
    help='Whether pre-processing is needed.',
    action='store_true')

  parser.add_argument(
    '--validation_split',
    type=float,
    default=0.2,
    help='Split percentage to use for validation dataset.')

  parser.add_argument(
    '--test_split',
    type=float,
    default=0.2,
    help='Split percentage to use for test dataset.')

  parser.add_argument(
    '--training_data_path',
    help=('The GCS path where the training data is stored.\n'
          'Also accepts Glob file pattern.'
          'Glob file pattern is based on wildcard matching.\n'
          'There are three types of wilcard characters : \n.'
          '1) * : Matches zero or more characters.\n'
          'Example: The pattern \'train_data/input*.csv\' will match : \n'
          'train_data/input_1.csv \n'
          'train_data/input_2.csv \n'
          'train_data/input_3.csv \n'
          'train_data/input_4.csv \n'
          '..\n'
          '..\n'
          '..\n'
          'train_data/input_99.csv \n'
          'train_data/input_100.csv \n'
          '2) ? : Matches a single character.\n'
          'Example: The pattern \'train_data/input_?.csv\' will match : \n'
          'train_data/input_1.csv \n'
          'train_data/input_2.csv \n'
          'train_data/input_3.csv \n'
          'train_data/input_4.csv \n'
          '..\n'
          '..\n'
          'train_data/input_8.csv \n'
          'train_data/input_9.csv \n'
          '3) [] : To specify a character range.\n'
          'Example: The pattern \'train_data/*[1-5]*.csv\' will match : \n'
          'train_data/input_1.csv \n'
          'train_data/input_2.csv \n'
          'train_data/input_3.csv \n'
          'train_data/input_4.csv \n'
          'train_data/input_5.csv \n'),
    required=True)

  parser.add_argument(
    '--validation_data_path',
    help=('The GCS path where the validation data is stored.\n'
          'Must be specified if not doing pre-processing\n.'
          'Also accepts Glob file pattern. See help for flag : '
          '\'training_data_path\' for more details.'))

  parser.add_argument(
    '--test_data_path',
    help=('The GCS path where the test data is stored.\n'
          'Also accepts Glob file pattern. See help for flag : '
          '\'training_data_path\' for more details.'))

  parser.add_argument(
    '--job_dir',
    help='The GCS path where the training related file will be stored.',
    required=True)

  parser.add_argument(
    '--num_classes',
    help='Number of output classes (only needed for classification).',
    default=2,
    type=check_num_classes)

  # Only accepting csv for now
  parser.add_argument(
    '--input_type',
    help=('Input data format, either \'csv\' or \'tfrecord\'.\n'
          'If csv is mentioned then the first column is treated as target.'
          'The csv files should not have a column header.'),
    choices=['csv'],
    default='csv')

  # Model parameters
  parser.add_argument(
    '--model_type',
    help='Model to use for training (regression or classification).',
    choices=['classification', 'regression'],
    required=True)

  # Add training related arguments
  parser.add_argument(
    '--max_steps',
    help='Number of steps (batches) to run the trainer for.',
    type=int,
    default=400)

  parser.add_argument(
    '--eval_steps',
    help=('Number of steps (batches) to run evaluation for.\n'
          'If not specified, it means run evaluation on the whole validation '
          'data-set. This value must be >= 1.'
          ),
    type=int)

  parser.add_argument(
    '--batch_size', help='Batch Size for training.', default=100, type=int)

  parser.add_argument(
    '--eval_frequency_secs',
    help='Frequency at which evaluation and checkpointing will take place.',
    type=int,
    default=600)

  # Hyper-parameters
  parser.add_argument(
    '--learning_rate',
    help='Learning rate for training.',
    required=True,
    type=float)

  parser.add_argument(
    '--optimizer_type',
    help=('Type of optimizer to use. Choices :-\n'
          '1) \'adam\' : Adam Optimizer.\n'
          '2) \'ftrl\' : FTRL Optimizer.\n'
          '3) \'sgd\' : Gradient Descent Optimizer.\n'
          '4) \'rmse\': Root Mean Square Error.\n'),
    choices=['adam', 'ftrl', 'sgd', 'rmse'],
    default='ftrl')

  parser.add_argument(
    '--l1_reg_strength',
    help='L1 regularization strength for optimizer_type=\'ftrl\'.',
    default=0.,
    type=float)

  parser.add_argument(
    '--l2_reg_strength',
    help='L2 regularization strength for optimizer_type=\'ftrl\'.',
    default=0.,
    type=float)

  parser.add_argument(
    '--l2_shrinkage_reg_strength',
    help='L2 shrinkage regularization strength for optimizer_type=\'ftrl\'.',
    default=0.,
    type=float)

  parser.add_argument(
    '--beta_1',
    help='Beta 1 value for optimizer_type=\'adam\'.',
    default=0.9,
    type=float)

  parser.add_argument(
    '--beta_2',
    help='Beta 2 value for optimizer_type=\'adam\'.',
    default=0.999,
    type=float)

  return parser.parse_args()


def check_args(args):
  """Checks if the arguments specified are valid.

  Args:
    args: Command line arguments by the user.

  Raises:
   ValueError: If the arguments are not valid.
  """
  if args.test_data_path and not args.validation_data_path:
    raise ValueError('Validation data must be specified if test data path is.')
  if not args.preprocess and not args.validation_data_path:
    raise ValueError('Validation data must be specified if not preprocessing.')


def download_files_from_gcs(training_data_path,
                            validation_data_path=None,
                            test_data_path=None):
  """Download files from GCS to a WORKING_DIR/.

  Args:
    training_data_path: GCS path to the training data
    validation_data_path: GCS path to the validation data.
    test_data_path: GCS path to the test data.

  Returns:
    A list to the local data paths where the data is downloaded.
  """
  local_file_names = [TRAINING_FILE_NAME]
  gcs_input_paths = [training_data_path]
  if validation_data_path:
    local_file_names.append(VALIDATION_FILE_NAME)
    gcs_input_paths.append(validation_data_path)
  if test_data_path:
    local_file_names.append(TEST_FILE_NAME)
    gcs_input_paths.append(test_data_path)

  # Copy raw files from GCS into local path.
  raw_local_files_data_paths = [
    os.path.join(WORKING_DIR, TEMP_DIR, local_file_name)
    for local_file_name in local_file_names
    ]
  for i, gcs_input_path in enumerate(gcs_input_paths):
    if gcs_input_path:
      subprocess.check_call(
        ['gsutil', 'cp', gcs_input_path, raw_local_files_data_paths[i]])

  return raw_local_files_data_paths


def upload_files_to_gcs(gcs_output_dir):
  """Uploads training artifacts to gcs_output_dir.

  Sepcifically writes files in these folders: PROCESSED_DATA_DIR, EXPORT_DIR
  Args:
    gcs_output_dir: GCS path where the data should be uploaded to.
  """
  # Uploads processed data to the processed data dir to GCS
  if gcs_output_dir.startswith('gs://'):
    subprocess.check_call([
      'gsutil', 'cp', '-r',
      os.path.join(WORKING_DIR, PROCESSED_DATA_DIR, '*'),
      os.path.join(gcs_output_dir, PROCESSED_DATA_DIR)
    ])
    # Uploads export data to the model dir to GCS
    subprocess.check_call([
      'gsutil', 'cp', '-r',
      os.path.join(WORKING_DIR, EXPORT_DIR, '*'),
      os.path.join(gcs_output_dir, GCS_MODEL_DIR)
    ])


def _setup_logging():
  """Sets up logging."""
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)

  # Set tf logging to avoid duplicate logging. If the handlers are not removed,
  # then we will have duplicate logging :
  # From tf loggging written to stderr stream, and
  # From python logger written to stdout stream.
  tf_logger = logging.getLogger('tensorflow')
  while tf_logger.handlers:
    tf_logger.removeHandler(tf_logger.handlers[0])

  # Redirect INFO logs to stdout
  stdout_handler = logging.StreamHandler(sys.stdout)
  stdout_handler.setLevel(logging.INFO)
  logger.addHandler(stdout_handler)

  # Suppress C++ level warnings.
  os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def main():
  args = get_args()
  check_args(args)

  _setup_logging()

  logging.info('Downloading data')
  raw_local_files_data_paths = download_files_from_gcs(
    args.training_data_path, args.validation_data_path, args.test_data_path)

  preprocessor_obj = preprocessor.PreProcessor()
  if args.preprocess:
    logging.info('Processing data')
    # Create a data path where processed files will be written to.
    processed_local_files_data_paths = [
      os.path.join(WORKING_DIR, PROCESSED_DATA_DIR, file_name) for file_name
      in [TRAINING_FILE_NAME, VALIDATION_FILE_NAME, TEST_FILE_NAME]
      ]
    # If the input only training and validation data then the
    # processed_local_files_data_paths should match that.
    if len(raw_local_files_data_paths) == 2:
      processed_local_files_data_paths = processed_local_files_data_paths[:2]

    # Run pre-processing and save the processed data inside 'processed_data' dir
    preprocessor_obj.run_preprocessing(
      raw_local_files_data_paths, processed_local_files_data_paths,
      args.model_type, args.validation_split, args.test_split)

    # Upload output artifacts to GCS path.
    logging.info('Uploading pre-processing artifacts.')
    upload_files_to_gcs(args.job_dir)

    args.training_data_path = processed_local_files_data_paths[0]
    args.validation_data_path = processed_local_files_data_paths[1]
    args.test_data_path = None
    if len(processed_local_files_data_paths) > 2:
      args.test_data_path = processed_local_files_data_paths[2]
  else:
    # Re-write datasets paths to local paths.
    args.training_data_path = raw_local_files_data_paths[0]
    args.validation_data_path = raw_local_files_data_paths[1]
    args.test_data_path = None
    if len(raw_local_files_data_paths) > 2:
      args.test_data_path = raw_local_files_data_paths[2]

    # Read the training data to get information like num_rows and num_classes.
    if args.max_steps is None or args.model_type == 'classification':
      train_df = preprocessor_obj.read_data(raw_local_files_data_paths[0])
  # Set num_classes.
  if args.model_type == 'classification':
    if args.preprocess:
      args.num_classes = len(preprocessor_obj.target_classes)
    else:
      args.num_classes = len(train_df[0].astype('category').cat.categories)
      print(args.num_classes)
  # If max_steps is not set, then set it using DEFAULT_EPOCHS.
  if args.max_steps is None:
    num_of_training_rows = preprocessor_obj.num_of_training_rows or len(
      train_df.index)
    args.max_steps = DEFAULT_EPOCHS * math.ceil(
      num_of_training_rows / args.batch_size)

  logging.info('Running Linear Learner training with the following args :')
  logging.info(args)
  training_task.run_training(args)
  logging.info('Linear learning finished.')


if __name__ == '__main__':
  main()
