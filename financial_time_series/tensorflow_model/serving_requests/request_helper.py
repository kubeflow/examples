""" Module that builds the request and processes the response from the tf-server.

Uses GRPC protocol to send a request to the tf-server and processes it.
"""

from grpc.beta import implementations
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc


def send_request(input_tensor):
  """Send a request to the TF-server to obtain a prediction.

  Args:
    input_tensor (np.ndarray): input tensor for which we want a prediction

  Returns:
    int: prediction
    str: version of the ML model

  """

  # server settings
  server_host = '127.0.0.1'
  server_port = 9000
  server_name = "tf-serving"
  timeout = 10.0

  print("connecting to:%s:%i" % (server_host, server_port))

  # initialize to server connection
  channel = implementations.insecure_channel(server_host, server_port)
  stub = prediction_service_pb2_grpc.PredictionServiceStub(channel._channel) # pylint: disable=protected-access

  # build request
  request = predict_pb2.PredictRequest()
  request.model_spec.name = server_name                   # pylint: disable=no-member
  request.model_spec.signature_name = 'serving_default'   # pylint: disable=no-member
  request.inputs['predictors'].CopyFrom(                  # pylint: disable=no-member
      tf.contrib.util.make_tensor_proto(input_tensor, shape=input_tensor.shape))

  # retrieve results
  result = stub.Predict(request, timeout)
  resultval = result.outputs['prediction'].int64_val
  version = result.outputs['model-version'].string_val
  return resultval[0], version[0]
