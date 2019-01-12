"""Test mnist_client.

This file tests that we can send predictions to the model.

It is an integration test as it depends on having access to
a deployed model.

Python Path Requirements:
  kubeflow/testing/py - https://github.com/kubeflow/testing/tree/master/py
     * Provides utilities for testing

Manually running the test
 1. Configure your KUBECONFIG file to point to the desired cluster
 2. Use kubectl port-forward to forward a local port
    to the gRPC port of TFServing.
"""

import json
import logging
import os

import mnist_client

from py import test_runner

from kubeflow.testing import test_util
from kubeflow.testing import util

class MnistClientTest(test_util.TestCase):
  def __init__(self, args):
    self.args = args
    super(MnistClientTest, self).__init__(class_name="MnistClientTest",
                                          name="MnistClientTest")

  def test_predict(self):
    this_dir = os.path.dirname(__file__)
    data_dir = os.path.join(this_dir, "..", "data")
    img_path = os.path.abspath(data_dir)

    x, y, _ = mnist_client.random_mnist(img_path)

    server_host = "localhost"
    server_port = 9000
    model_name = "mnist"
    # get prediction from TensorFlow server
    pred, scores, ver = mnist_client.get_prediction(
      x, server_host=server_host, server_port=server_port,
      server_name=model_name, timeout=10)

    # TODO(jlewi): Should we do any additional validation?

if __name__ == "__main__":
  test_runner.main(module=__name__)
