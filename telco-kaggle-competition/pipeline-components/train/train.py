import tensorflow as tf
from tensorflow import keras as ks
import pickle5 as pkl

with open("/data/train.pkl", "rb") as f:
    X_train, y_train = pkl.load(f)

with open("/data/test.pkl", "rb") as f:
    X_test, y_test = pkl.load(f)

model = ks.Sequential(
    [
        ks.layers.Dense(25,input_shape=(19,), activation="relu"),
        ks.layers.Dense(20, activation="relu"),
        ks.layers.Dense(15, activation="relu"),
        ks.layers.Dense(1, activation="sigmoid"),
    ]
)

model.compile(
    optimizer="adam",
    loss="binary_crossentropy", # I'm looking for 0 and 1 response
    metrics=["accuracy"]
)

model.fit(X_train, y_train, epochs = 10)


# my_model = model.export_model()
model.save('/data/model', save_format="tf")