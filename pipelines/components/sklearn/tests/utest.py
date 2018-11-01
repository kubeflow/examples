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

from __future__ import print_function
import os
import os.path
import pickle
import shutil
import unittest
import tempfile
import subprocess
import yaml
import pandas as pd
import sklearn.datasets


class TestSKLearnRunner(unittest.TestCase):
  def setUp(self):
    print("setUp")
    self.test_directory = os.path.abspath(tempfile.mkdtemp(dir='.'))
    n_samples = 5000
    n_features = 10
    train_test_ratio = 0.8
    train_size = int(n_samples * train_test_ratio)
    features, target = sklearn.datasets.make_regression(n_samples=n_samples,
                                                        n_features=n_features, noise=20)
    df = pd.concat([pd.DataFrame(target), pd.DataFrame(features)], axis=1)
    self.train_file = os.path.abspath(os.path.join(self.test_directory, 'temp_train.csv'))
    self.test_file = os.path.abspath(os.path.join(self.test_directory, 'temp_test.csv'))
    df.iloc[:train_size].to_csv(self.train_file, header=None, index=False)
    df.iloc[train_size:].to_csv(self.test_file, header=None, index=False)

  def tearDown(self):
    print("tearDown")
    shutil.rmtree(self.test_directory)


  def test_end_to_end(self):
    assert os.path.exists(self.train_file)
    assert os.path.exists(self.test_file)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    command = [
      'python',
      os.path.join(dir_path, '../src/task.py'),
      '--estimator_name',
      'Lasso',
      '--training_data_path',
      self.train_file,
      '--test_data_path',
      self.test_file,
      '--output_dir',
      self.test_directory,
      '--alpha',
      '0.7',
    ]

    output = str(subprocess.check_output(command).strip())
    report_name = output[output.find(' '):].strip(" '")
    report_file = os.path.join(self.test_directory, report_name)

    assert os.path.exists(report_file)
    with open(report_file, 'r') as rf:
      report = yaml.load(rf)
      model_name = report['model_name']
      model_file = os.path.join(self.test_directory, model_name)
      assert os.path.exists(model_file)
      with open(model_file, 'rb') as mf:
        model = pickle.load(mf)
        test_df = pd.read_csv(self.test_file, header=None)
        del test_df[0]
        assert len(test_df) == len(model.predict(test_df))
