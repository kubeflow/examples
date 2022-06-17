
from tensorflow.keras.models import load_model
import autokeras as ak
import pickle5 as pkl

### Load model 
loaded_model = load_model("/data/model", custom_objects=ak.CUSTOM_OBJECTS)


with open("/data/train.pkl", "rb") as f:
    X_train, y_train = pkl.load(f)

with open("/data/test.pkl", "rb") as f:
    X_test, y_test = pkl.load(f)


loaded_model.evaluate(X_test, y_test)
