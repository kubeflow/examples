import json
import numpy as np
import requests
from retrying import retry

@retry(wait_exponential_multiplier=1000, wait_exponential_max=5000,
       stop_max_delay=2*60*1000)
def predict_nparray(url, data, feature_names=None):
    pdata={
        "data": {
            "names":feature_names,
            "tensor": {
                "shape": np.asarray(data.shape).tolist(),
                "values": data.flatten().tolist(),
            },
        }
    }
    serialized_data = json.dumps(pdata)
    r = requests.post(url, data={'json':serialized_data}, timeout=5)
    return r
