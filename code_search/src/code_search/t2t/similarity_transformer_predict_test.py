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
TODO: Currently this test assumes data_dir is /mnt/nfs-east1-d/data

code_search must be a top level Python package.
python -m code_searcch.t2t.similarity_transformer_export_test

Requirements:
 requires host machine has tensorflow_model_server executable available
"""

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

import grpc
import tensorflow as tf

from tensor2tensor.utils import registry
from tensor2tensor.serving import serving_utils
from tensor2tensor.serving import export
from tensor2tensor.utils import decoding
from tensor2tensor.utils import usr_dir
from tensor2tensor.bin import t2t_trainer
from tensor2tensor.utils import trainer_lib

from code_search.t2t  import similarity_transformer

FLAGS = tf.flags.FLAGS


def encode(input_str, output_str=None, encoders=None):
  """Input str to features dict, ready for inference"""
  inputs = encoders["inputs"].encode(input_str) + [1]  # add EOS id
  batch_inputs = tf.reshape(inputs, [1, -1, 1])  # Make it 3D.
  return {"inputs": batch_inputs}


def _get_t2t_usr_dir():
  """Get the path to the t2t usr dir."""
  return os.path.join(os.path.realpath(__file__), "../")


# ---
# various things copied from
# https://github.com/tensorflow/serving/blob/master/tensorflow_serving/model_servers/tensorflow_model_server_test.py
# b/c doesn't look like it's importable form tensorflow_serving


def PickUnusedPort():
  s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
  s.bind(('', 0))
  port = s.getsockname()[1]
  s.close()
  return port


def WaitForServerReady(port):
  """Waits for a server on the localhost to become ready."""

  # HACK
  sleep(5)

  """
  # TODO: I don't know why these imports don't work. They are can be imported
  # in tensor2tensor.serving.serving_utils so why not here? ...
  from tensorflow_serving.apis import predict_pb2
  #from tensorflow_serving.apis import prediction_service_pb2_grpc
  for _ in range(0, WAIT_FOR_SERVER_READY_INT_SECS):
    time.sleep(1)
    request = predict_pb2.PredictRequest()
    request.model_spec.name = 'intentionally_missing_model'
    try:
      # Send empty request to missing model
      channel = grpc.insecure_channel('localhost:{}'.format(port))
      stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
      stub.Predict(request, RPC_TIMEOUT)
    except grpc.RpcError as error:
      # Missing model error will have details containing 'Servable'
      if 'Servable' in error.details():
        print('Server is ready')
        break
  """

class TensorflowModelServer(object):

  @staticmethod
  def __TestSrcDirPath(relative_path=''):

    base = "/tmp"

    if 'TEST_SRCDIR' in os.environ:
      base = os.environ['TEST_SRCDIR']

    path = os.path.join(base,
                        'test-modelserver',
                        relative_path)
    tf.gfile.MakeDirs(path)
    return path

  @staticmethod
  def RunServer(model_name,
                model_path,
                model_config_file=None,
                monitoring_config_file=None,
                batching_parameters_file=None,
                grpc_channel_arguments='',
                wait_for_server_ready=True,
                pipe=None):
    """Run tensorflow_model_server using test config.
    A unique instance of server is started for each set of arguments.
    If called with same arguments, handle to an existing server is
    returned.
    Args:
      model_name: Name of model.
      model_path: Path to model.
      model_config_file: Path to model config file.
    Returns:
      3-tuple (<Popen object>, <grpc host:port>, <rest host:port>).
    Raises:
      ValueError: when both model_path and config_file is empty.
    """

    port = PickUnusedPort()

    rest_api_port = PickUnusedPort()

    print('Starting test server on port: {} for model_name: '
          '{}/model_config_file: {}'.format(port, model_name,
                                            model_config_file))
    command = os.path.join(
        TensorflowModelServer.__TestSrcDirPath('model_servers'),
        'tensorflow_model_server')

    command += ' --port=' + str(port)

    if model_config_file:
      command += ' --model_config_file=' + model_config_file
    elif model_path:
      command += ' --model_name=' + model_name
      command += ' --model_base_path=' + model_path
    else:
      raise ValueError('Both model_config_file and model_path cannot be empty!')

    print(command)
    proc = subprocess.Popen(shlex.split(command), stderr=pipe)
    atexit.register(proc.kill)
    print('Server started')
    if wait_for_server_ready:
      WaitForServerReady(port)

    hostports = (
        proc,
        'localhost:' + str(port),
        'localhost:' + str(rest_api_port),
    )

    return hostports


class TestSimilarityTransformerExport(tf.test.TestCase):

  def test_e2e_export_and_query(self):
    """Test that we can export and query the model via tf.serving."""

    test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
    # If we set t2t_usr_dir t2t_train.main will end up importing that
    # directory which causes an error because the model ends up being registered
    # twice.
    # FLAGS.t2t_usr_dir = _get_t2t_usr_dir()
    FLAGS.problem = "github_function_docstring"
    FLAGS.data_dir = test_data_dir
    FLAGS.tmp_dir = tempfile.mkdtemp()
    logging.info("Using data_dir %s", FLAGS.data_dir)
    logging.info("Using tmp_dir %s", FLAGS.tmp_dir)

    FLAGS.output_dir = tempfile.mkdtemp()
    logging.info("Using output_dir %s", FLAGS.output_dir)

    #FLAGS.export_dir = os.path.join(FLAGS.output_dir, "export")
    FLAGS.model = similarity_transformer.MODEL_NAME
    FLAGS.hparams_set = "transformer_tiny"
    FLAGS.train_steps = 1
    FLAGS.schedule = "train"

    timeout_secs = 10

    # TODO(jlewi): Not sure why @cwbeitel's prototype was calling usr_dir.
    # This ends up causing the model to be registered twice which causes
    # an error.
    # usr_dir.import_usr_dir(FLAGS.t2t_usr_dir)

    t2t_trainer.main(None)

    export.main(None)

    # ----
    # Start model server

    # Will start a tf model server on an un-used port and
    # kill process on exit.
    _, server, _ = TensorflowModelServer().RunServer(
        FLAGS.model,
        FLAGS.output_dir
    )

    # ----
    # Query the server

    doc_query = [1,2,3] # Dummy encoded doc query
    code_query = [1,2,3] # Dummy encoded code query

    # Alternatively for query, without going through query.main()
    # TODO: Is servable_name the same as model name?
    request_fn = serving_utils.make_grpc_request_fn(
        servable_name=FLAGS.model,
        server=server,
        timeout_secs=timeout_secs)

    # Compute embeddings
    # TODO: May need to customize how these queries are fed in, potentially
    #       side-stepping serving_utils.predict.
    encoded_string = serving_utils.predict([doc_query], problem_object, request_fn)
    encoded_code = serving_utils.predict([code_query], problem_object, request_fn)

    # TODO: Make an assertion about the result.

if __name__ == "__main__":
  logging.getLogger().setLevel(logging.INFO)
  tf.test.main()