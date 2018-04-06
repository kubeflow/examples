#!/usr/bin/env python2.7

import os
import random
import numpy

from PIL import Image

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2

from grpc.beta import implementations

from mnist import MNIST # pylint: disable=no-name-in-module

TF_MODEL_SERVER_HOST = os.getenv("TF_MODEL_SERVER_HOST", "127.0.0.1")
TF_MODEL_SERVER_PORT = int(os.getenv("TF_MODEL_SERVER_PORT", 9000))
TF_DATA_DIR = os.getenv("TF_DATA_DIR", "/tmp/data/")
TF_MNIST_IMAGE_PATH = os.getenv("TF_MNIST_IMAGE_PATH", None)
TF_MNIST_TEST_IMAGE_NUMBER = int(os.getenv("TF_MNIST_TEST_IMAGE_NUMBER", -1))

if TF_MNIST_IMAGE_PATH != None:
  raw_image = Image.open(TF_MNIST_IMAGE_PATH)
  int_image = numpy.array(raw_image)
  image = numpy.reshape(int_image, 784).astype(numpy.float32)
elif TF_MNIST_TEST_IMAGE_NUMBER > -1:
  test_data_set = input_data.read_data_sets(TF_DATA_DIR, one_hot=True).test
  image = test_data_set.images[TF_MNIST_TEST_IMAGE_NUMBER]
else:
  test_data_set = input_data.read_data_sets(TF_DATA_DIR, one_hot=True).test
  image = random.choice(test_data_set.images)

channel = implementations.insecure_channel(
    TF_MODEL_SERVER_HOST, TF_MODEL_SERVER_PORT)
stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

request = predict_pb2.PredictRequest()
request.model_spec.name = "mnist"
request.model_spec.signature_name = "serving_default"
request.inputs['x'].CopyFrom(
    tf.contrib.util.make_tensor_proto(image, shape=[1, 28, 28]))

result = stub.Predict(request, 10.0)  # 10 secs timeout

print(result)
print(MNIST.display(image, threshold=0))
print("Your model says the above number is... %d!" %
      result.outputs["classes"].int_val[0])
