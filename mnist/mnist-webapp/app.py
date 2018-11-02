# taken from https://community.canvaslms.com/thread/2595

import os
from flask import Flask, render_template,url_for, request, jsonify
import numpy as np
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2
from grpc.beta import implementations

from PIL import Image
import re
import io
import base64

app = Flask(__name__)

TF_MODEL_SERVER_HOST = os.getenv("TF_MODEL_SERVER_HOST", "10.0.175.4")
TF_MODEL_SERVER_PORT = int(os.getenv("TF_MODEL_SERVER_PORT", 9000))

@app.route('/', methods=['GET','POST'])
def get_image():
    guess = 0
    if request.method== 'POST':
        #requests image from url
        img_size = 28, 28
        image_url = request.values['imageBase64']
        image_string = re.search(r'base64,(.*)', image_url).group(1)
        image_bytes = io.BytesIO(base64.b64decode(image_string))
        image = Image.open(image_bytes)
        image = image.resize(img_size, Image.LANCZOS)
        image = image.convert('1')
        int_image = np.array(image)
        image = np.reshape(int_image, 784).astype(np.float32)
        # image = image.convert('1')
        # image = np.asarray(image)
        # image = image.flatten()

        channel = implementations.insecure_channel(
            TF_MODEL_SERVER_HOST, TF_MODEL_SERVER_PORT)
        stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

        prequest = predict_pb2.PredictRequest()
        prequest.model_spec.name = "mnist"
        prequest.model_spec.signature_name = "serving_default"
        prequest.inputs['x'].CopyFrom(
            tf.contrib.util.make_tensor_proto(image, shape=[1, 28, 28]))

        result = stub.Predict(prequest, 10.0)  # 10 secs timeout

        guess = result.outputs["classes"].int_val[0]
        return jsonify(guess = guess)

    return render_template('index.html', guess = guess)


if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0")
