from grpc.beta import implementations
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
import numpy as np

from .. import preprocess

# create input from request date
train_test_ratio = 0.8
request_date = "2014-08-12"
tickers = ['snp', 'nyse', 'djia', 'nikkei', 'hangseng', 'ftse', 'dax', 'aord']
closing_data = preprocess.load_data(tickers)
index = closing_data.index.get_loc("2014-08-12") - 7 # because first 7 days are not accounted in the time series
training_test_data = preprocess.preprocess_data(closing_data)
input = np.expand_dims(training_test_data[training_test_data.columns[2:]].values[index], axis=0).astype(np.float32)

# server settings
server_host = '127.0.0.1'
server_port = 9000
server_name = "tf-serving"
timeout = 10.0

print("connecting to:%s:%i" % (server_host, server_port))

# initialize to server connection
channel = implementations.insecure_channel(server_host, server_port)
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel._channel)

# build request
request = predict_pb2.PredictRequest()
request.model_spec.name = server_name
request.model_spec.signature_name = 'serving_default'
request.inputs['predictors'].CopyFrom(
  tf.contrib.util.make_tensor_proto(input, shape=input.shape))

# retrieve results
result = stub.Predict(request, timeout)
resultVal = result.outputs['prediction'].int64_val
version = result.outputs['model-version'].string_val
print("Prediction : " + str(resultVal[0]))
print("Version of model : " + str(version[0]))


