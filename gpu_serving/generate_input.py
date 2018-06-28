import base64
import io
import json
import numpy as np
from PIL import Image
import tensorflow as tf

width = 1024
height = 768
predict_instance_json = "inputs.json"
with open(predict_instance_json, "wb") as fp:
  for image in ["image1.jpg"]:
    img = Image.open(image)
    img = img.resize((width, height), Image.ANTIALIAS)
    arr = np.array(img)
    output_str = io.BytesIO()
    img.save(output_str, "JPEG")
    fp.write(
        json.dumps({"instances": [{"inputs": arr.tolist()}]}))

