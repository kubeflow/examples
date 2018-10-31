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

"""Test embedding query using TFServing.

This is a manual/E2E test that assumes TFServing is running externally
(e.g. Docker container or K8s pod).

The script start_test_server.sh can be used to start a Docker container
when running locally.

To run TFServing we need a model. start_test_server.sh will use a model
in ../../t2t/test_data/model

code_search must be a top level Python package.

 requires host machine has tensorflow_model_server executable available
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

from code_search.nmslib.cli  import start_search_server

FLAGS = tf.flags.FLAGS


#def encode(input_str, output_str=None, encoders=None):
  #"""Input str to features dict, ready for inference"""
  #inputs = encoders["inputs"].encode(input_str) + [1]  # add EOS id
  #batch_inputs = tf.reshape(inputs, [1, -1, 1])  # Make it 3D.
  #return {"inputs": batch_inputs}


#def _get_t2t_usr_dir():
  #"""Get the path to the t2t usr dir."""
  #return os.path.join(os.path.realpath(__file__), "../")


# ---
# various things copied from
# https://github.com/tensorflow/serving/blob/master/tensorflow_serving/model_servers/tensorflow_model_server_test.py
# b/c doesn't look like it's importable form tensorflow_serving


#def PickUnusedPort():
  #s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
  #s.bind(('', 0))
  #port = s.getsockname()[1]
  #s.close()
  #return port


#def WaitForServerReady(port):
  #"""Waits for a server on the localhost to become ready."""

  ## HACK
  #sleep(5)

  #"""
  ## TODO: I don't know why these imports don't work. They are can be imported
  ## in tensor2tensor.serving.serving_utils so why not here? ...
  #from tensorflow_serving.apis import predict_pb2
  ##from tensorflow_serving.apis import prediction_service_pb2_grpc
  #for _ in range(0, WAIT_FOR_SERVER_READY_INT_SECS):
    #time.sleep(1)
    #request = predict_pb2.PredictRequest()
    #request.model_spec.name = 'intentionally_missing_model'
    #try:
      ## Send empty request to missing model
      #channel = grpc.insecure_channel('localhost:{}'.format(port))
      #stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
      #stub.Predict(request, RPC_TIMEOUT)
    #except grpc.RpcError as error:
      ## Missing model error will have details containing 'Servable'
      #if 'Servable' in error.details():
        #print('Server is ready')
        #break
  #"""

#class TensorflowModelServer(object):

  #@staticmethod
  #def __TestSrcDirPath(relative_path=''):

    #base = "/tmp"

    #if 'TEST_SRCDIR' in os.environ:
      #base = os.environ['TEST_SRCDIR']

    #path = os.path.join(base,
                        #'test-modelserver',
                        #relative_path)
    #tf.gfile.MakeDirs(path)
    #return path

  #@staticmethod
  #def RunServer(model_name,
                #model_path,
                #model_config_file=None,
                #monitoring_config_file=None,
                #batching_parameters_file=None,
                #grpc_channel_arguments='',
                #wait_for_server_ready=True,
                #pipe=None):
    #"""Run tensorflow_model_server using test config.
    #A unique instance of server is started for each set of arguments.
    #If called with same arguments, handle to an existing server is
    #returned.
    #Args:
      #model_name: Name of model.
      #model_path: Path to model.
      #model_config_file: Path to model config file.
    #Returns:
      #3-tuple (<Popen object>, <grpc host:port>, <rest host:port>).
    #Raises:
      #ValueError: when both model_path and config_file is empty.
    #"""

    #port = PickUnusedPort()

    #rest_api_port = PickUnusedPort()

    #logging.info('Starting test server on port: %s for model_name: '
                 #'%s/model_config_file: %s'.format(port, model_name,
                                                   #model_config_file))
    #command = os.path.join(
        #TensorflowModelServer.__TestSrcDirPath('model_servers'),
        #'tensorflow_model_server')

    #command += ' --port=' + str(port)

    #if model_config_file:
      #command += ' --model_config_file=' + model_config_file
    #elif model_path:
      #command += ' --model_name=' + model_name
      #command += ' --model_base_path=' + model_path
    #else:
      #raise ValueError('Both model_config_file and model_path cannot be empty!')

    #logging.info(command)
    #proc = subprocess.Popen(shlex.split(command), stderr=pipe)
    #atexit.register(proc.kill)
    #logging.info('Server started')
    #if wait_for_server_ready:
      #WaitForServerReady(port)

    #hostports = (
        #proc,
        #'localhost:' + str(port),
        #'localhost:' + str(rest_api_port),
    #)

    #return hostports

PROBLEM_NAME = "kf_github_function_docstring"

class TestEmbedQuery(unittest.TestCase):

  def test_embed(self):
    """Test that we can embed the search query string via tf.serving.

    This test assumes the model is running as an external process in TensorFlow
    serving.

    The external process can be started a variety of ways e.g. subprocess,
    kubernetes, or docker container.

    The script start_test_server.sh can be used to start TFServing in
    docker container.
    """
    # Directory containing the vocabulary.
    test_data_dir = os.path.abspath(
      os.path.join(os.path.dirname(__file__), "..", "..", "t2t", "test_data"))
    # 8501 should be REST port
    server = os.getenv("TEST_SERVER", "localhost:8501")

    # Model name matches the subdirectory in TF Serving's model Directory
    # containing models.
    model_name = "test_model_20181030"
    serving_url = "http://{0}/v1/models/{1}:predict".format(server, model_name)
    query = "Write to GCS"
    encoder = start_search_server.build_query_encoder(PROBLEM_NAME,
                                                      test_data_dir)
    start_search_server.embed_query(encoder, serving_url, query)

if __name__ == "__main__":
  logging.getLogger().setLevel(logging.INFO)
  # DO NOT SUBMIT; hack so that debugger will break on error
  test = TestEmbedQuery()
  test.test_embed()
  # unittest.main()