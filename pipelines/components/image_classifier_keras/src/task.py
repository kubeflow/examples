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
"""
ML Pipeline driver for Image Classification using Keras
"""

import os
import argparse
import subprocess
import zipfile
try:
  from . import openCV
except:
  import openCV

try:
  from . import model
except:
  import model

try:
  from . import hdf5
except:
  import hdf5


def emnist(training_data_path, test_data_path, num_epochs, batch_size, verbosity=False):
  """ Example ML Pipeline for processing the EMNIST dataset
  Args:
    training_data_path : (str) directory root of training data
    test_data_path     : (str) directory root of test data
    num_epochs         : (int) number of epochs
    batch_size         : (int) (mini) batch size
    verbosity          : (bool) progress reporting level

  Returns:
    trained model

  Raises:
    N/A
  """
  return pipeline('emnist', arguments.training_data_path, None, openCV.GRAYSCALE, (28,28), arguments.num_epochs, arguments.batch_size, verbose)


def fruits360(training_data_path, test_data_path, num_epochs, batch_size, verbosity=False):
  """ Example ML Pipeline for processing the Fruits360 dataset
  Args:
    training_data_path : (str) directory root of training data
    test_data_path     : (str) directory root of test data
    num_epochs         : (int) number of epochs
    batch_size         : (int) (mini) batch size
    verbosity          : (bool) progress reporting level

  Returns:
    trained model

  Raises:
    N/A
  """
  return pipeline('fruits360', arguments.training_data_path, arguments.test_data_path, openCV.COLOR, (100, 100), arguments.num_epochs, arguments.batch_size, verbose)


def pipeline(name, training_data_path, test_data_path, colorspace, resize, num_epochs, batch_size, verbosity):
  """ Pipeline for processing the image dataset
  Args:
    name               : (str) name of model (for saving on disk)
    training_data_path : (str) directory root of training data
    test_data_path     : (str) directory root of test data
    colorspace         : (int) colorspace to train images in (COLOR or GRAYSCALE)
    resize             : (tuple(int,int)) (height, width) to resize images for training
    num_epochs         : (int) number of epochs
    batch_size         : (int) (mini) batch size
    verbosity          : (bool) progress reporting level

  Returns:
    trained model

  Raises:
    N/A
  """
  try:
    dataset_train = openCV.load_directory(training_data_path,
                                 colorspace=colorspace,
                                 resize=resize,
                                 flatten=False,
                                 concurrent=4,
                                 verbose=verbosity)

    # if test data path not specified, then the data specified by
    # training_data_path is used for train and test
    if test_data_path:
      dataset_test = openCV.load_directory(test_data_path,
                                 colorspace=colorspace,
                                 resize=resize,
                                 flatten=False,
                                 concurrent=4,
                                 verbose=verbosity)
  except Exception as e:
    print("ERROR while preprocessing the data", e)
    return

  if verbosity:
    # Dataset should be 81 collections (fruits and there varieties).
    # Each collection should consist of a set of three entries: data, labels, and errors.
    print( "Number of collections:", len(dataset_train) )
    print( "Number of sets in a collection:", len(dataset_train[0]))

  try:
    # Store the training machine learning ready data to HDF5
    hdf5.store_dataset(name + '-train', dataset_train, verbose=verbosity)
    if test_data_path:
      hdf5.store_dataset(name + '-test',  dataset_test, verbose=verbosity)
  except Exception as e:
    print("ERROR while storing preprocessed data:", e)

  if verbosity:
    print("HDF5 train file size:", int( os.path.getsize(name + '-train.h5') / (1024 * 1024) ), "MB")
    if test_data_path:
      print("HDF5 test  file size:", int( os.path.getsize(name + '-test.h5') / (1024 * 1024) ), "MB")

  try:
    # load the dataset back into memory
    X_train, Y_train, classes = hdf5.load_dataset(name + '-train')
    if test_data_path:
      X_test,  Y_test,  classes = hdf5.load_dataset(name + '-test')
    else:
      X_test, Y_test = None, None
  except Exception as e:
    print("ERROR while loading preprocessed data:", e)

  try:
    if colorspace == openCV.COLOR:
      _model, accuracy = model.train_model_color(X_train, Y_train, X_test, Y_test, input_shape=resize, n_classes=len(classes), epochs=num_epochs, batch_size=batch_size, verbose=verbosity)
    else:
      _model, accuracy = model.train_model_grayscale(X_train, Y_train, X_test, Y_test, input_shape=resize, n_classes=len(classes), epochs=num_epochs, batch_size=batch_size, verbose=verbosity)
  except Exception as e:
    print("ERROR while training the model:", e)

  _model.save( name + '.model.h5')
  return _model, name + '.model.5'

def download_compressed_dataset_from_gcs(gcs_zip_file, dataset_path):
  """Download compressed dataset and uncompress.

  Args:
    gcs_zip_file: GCS path to the compressed dataset
    dataset_path:

  Returns:
    A list to the local data paths where the data is downloaded.
  """

  # Copy raw files from GCS into local path.
  local_zip_file = './tmp/dataset.zip'
  subprocess.check_call(
      ['gsutil', 'cp', gcs_zip_file, local_zip_file])

  zip_ref = zipfile.ZipFile(local_zip_file)
  zip_ref.extractall(dataset_path)
  zip_ref.close()
  os.remove(local_zip_file)

  return local_zip_file

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
    '--name',
    type=str,
    required=True,
    help='Dataset name (for storing the model or precanned model)')
  parser.add_argument(
    '--training_data_path',
    type=str,
    required=True,
    help='Dataset as a directory, where subfolders are the classes')
  parser.add_argument(
    '--test_data_path',
    type=str,
    help='Dataset as a directory, where subfolders are the classes')
  parser.add_argument(
    '--gcs',
    type=str,
    help='Compressed dataset on GCS storage')
  parser.add_argument(
    '--local',
    type=str,
    help='The local directory to uncompress a dataset (e.g., from GCS) to.')
  parser.add_argument(
    '--num_epochs',
    type=int,
    default=10,
    help='number of times to go through the data, default=10')
  parser.add_argument(
    '--batch_size',
    type=int,
    default=128,
    help='number of records to read during each training step, default=128')
  parser.add_argument(
    '--learning_rate',
    type=float,
    default=.001,
    help='learning rate for gradient descent, default=.001')
  parser.add_argument(
    '--colorspace',
    type=str,
    required=False,
    choices=['GRAYSCALE', 'COLOR'],
    default='COLOR',
    help='Colorspace for image preprocessing, default=COLOR')
  parser.add_argument(
    '--resize',
    type=str,
    required=False,
    default='(224,224)',
    help='Resize for image preprocessing, default=(224, 224)')
  parser.add_argument(
    '--verbosity',
    choices=['DEBUG', 'ERROR', 'FATAL', 'INFO', 'WARN', 'SILENT'],
    default='INFO',
    help='Progress reporting level'
    )

  arguments, hp_pairs = parser.parse_known_args()

  if arguments.verbosity == 'SILENT':
    verbose = False
  else:
    verbose = True

  if arguments.gcs is not None:
    download_compressed_dataset_from_gcs(arguments.gcs, arguments.local)

  if arguments.name == 'emnist':
    emnist(arguments.training_data_path, arguments.test_data_path, arguments.num_epochs, arguments.batch_size, verbose)
  elif arguments.name == 'fruits360':
    fruits360(arguments.training_data_path, arguments.test_data_path, arguments.num_epochs, arguments.batch_size, verbose)
  else:
    if arguments.colorspace == 'COLOR':
      colorspace = openCV.COLOR
    else:
      colorspace = openCV.GRAYSCALE

    toks = arguments.resize[1:-1].split(',')
    resize = ( int(toks[0]), int(toks[1]) )

    pipeline(arguments.name, arguments.training_data_path, arguments.test_data_path, colorspace, resize, arguments.num_epochs, arguments.batch_size, verbose)
