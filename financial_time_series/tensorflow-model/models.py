import tensorflow as tf


class FlatModel(object):

    def __init__(self, nr_predictors, nr_classes):
        self.nr_predictors = nr_predictors
        self.nr_classes = nr_classes

    def build_model(self, feature_data):
        weights = tf.Variable(tf.truncated_normal([self.nr_predictors, self.nr_classes], stddev=0.0001))
        biases = tf.Variable(tf.ones([self.nr_classes]))

        model = tf.nn.softmax(tf.matmul(feature_data, weights) + biases)

        return model


class DeepModel(object):

    def __init__(self, nr_predictors, nr_classes, dim_hidden1=50, dim_hidden2=25):
        self.nr_predictors = nr_predictors
        self.nr_classes = nr_classes
        self.dim_hidden1 = dim_hidden1
        self.dim_hidden2 = dim_hidden2

    def build_model(self, feature_data):
        weights1 = tf.Variable(tf.truncated_normal([self.nr_predictors, self.dim_hidden1], stddev=0.0001))
        biases1 = tf.Variable(tf.ones([self.dim_hidden1]))

        weights2 = tf.Variable(tf.truncated_normal([self.dim_hidden1, self.dim_hidden2], stddev=0.0001))
        biases2 = tf.Variable(tf.ones([self.dim_hidden2]))

        weights3 = tf.Variable(tf.truncated_normal([self.dim_hidden2, self.nr_classes], stddev=0.0001))
        biases3 = tf.Variable(tf.ones([self.nr_classes]))

        hidden_layer_1 = tf.nn.relu(tf.matmul(feature_data, weights1) + biases1)
        hidden_layer_2 = tf.nn.relu(tf.matmul(hidden_layer_1, weights2) + biases2)
        model = tf.nn.softmax(tf.matmul(hidden_layer_2, weights3) + biases3)

        return model
