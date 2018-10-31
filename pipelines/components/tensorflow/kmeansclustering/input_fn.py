import tensorflow as tf
import numpy as np


def make_input_fn(npy_uri):
    def input_fn():
        with tf.gfile.Open(npy_uri) as f:
            features = np.load(f)

        features = tf.convert_to_tensor(features, dtype=tf.float32)
        features = tf.train.limit_epochs(features, num_epochs=1)

        return features

    return input_fn
