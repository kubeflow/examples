# coding=utf-8
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

"""Tests of modified similarity transformer model.

code_search must be a top level Python package.
python -m code_searcch.t2t.similarity_transformer_export_test
"""

# TODO(jlewi): Starting the test seems very slow. I wonder if this is because
# tensor2tensor is loading a bunch of models and if maybe we can skip that.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import os
import shutil
import atexit
import subprocess
import socket
import shlex
import tempfile
import unittest

import grpc
import tensorflow as tf

import datetime

start = datetime.datetime.now()

from tensor2tensor.utils import registry
from tensor2tensor.serving import serving_utils
from tensor2tensor.serving import export
from tensor2tensor.utils import decoding
from tensor2tensor.utils import usr_dir
from tensor2tensor.bin import t2t_trainer
from tensor2tensor.utils import trainer_lib

from code_search.t2t  import similarity_transformer

FLAGS = tf.flags.FLAGS

PROBLEM_NAME = "github_function_docstring"

class TestSimilarityTransformer(unittest.TestCase):

  def test_train_and_export(self):
    """Test that we can train and export the model."""

    test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
    # If we set t2t_usr_dir t2t_train.main will end up importing that
    # directory which causes an error because the model ends up being registered
    # twice.
    FLAGS.problem = "kf_github_function_docstring"
    FLAGS.data_dir = test_data_dir
    FLAGS.tmp_dir = tempfile.mkdtemp()
    logging.info("Using data_dir %s", FLAGS.data_dir)
    logging.info("Using tmp_dir %s", FLAGS.tmp_dir)

    FLAGS.output_dir = tempfile.mkdtemp()
    logging.info("Using output_dir %s", FLAGS.output_dir)

    FLAGS.model = similarity_transformer.MODEL_NAME
    FLAGS.hparams_set = "transformer_tiny"
    FLAGS.train_steps = 1

    # We want to trigger eval.
    FLAGS.local_eval_frequency = 1
    FLAGS.schedule = "continuous_train_and_eval"

    timeout_secs = 10

    # Calling generate data will generate data if no data exists.
    # TODO(jlewi): We only test datageneration if the files don't exist.
    # We should see about running it regularly. The problem I ran into
    # was that it downloads the entire dataset which is quite large.
    t2t_trainer.generate_data()
    t2t_trainer.main(None)

    export.main(None)

if __name__ == "__main__":
  logging.getLogger().setLevel(logging.INFO)
  unittest.main()