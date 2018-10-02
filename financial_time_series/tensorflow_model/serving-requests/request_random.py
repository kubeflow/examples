"""
Module that sends a random request to the tf-server
"""

import numpy as np

from . import request_helper   #pylint: disable=relative-beyond-top-level


def send_random_request():
  """ function that send random request"""
  # create random input
  input_tensor = np.random.rand(1, 24).astype(np.float32)
  # send request
  value, version = request_helper.send_request(input_tensor)
  # print response
  print("Prediction : " + str(value))
  print("Version of model : " + str(version))


send_random_request()
