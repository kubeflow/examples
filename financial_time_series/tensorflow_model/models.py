"""
Module that contains tensorflow models
"""
import tensorflow as tf


class FlatModel():
  """ Model that contains only single layer"""

  def __init__(self, nr_predictors, nr_classes):
    """

    Args:
        nr_predictors (int): amount of predictors
        nr_classes (int): amount of classes
    """
    self._nr_predictors = nr_predictors
    self._nr_classes = nr_classes

  @property
  def nr_predictors(self):
    """ amount of predictors property """
    return self._nr_predictors

  @property
  def nr_classes(self):
    """ amount of classes property """
    return self._nr_classes

  def build_model(self, feature_data):
    """

    Args:
        feature_data (tf. tensors): feature tensors

    Returns:
        model: tensorflow model

    """
    weights = tf.Variable(tf.truncated_normal([self._nr_predictors, self._nr_classes],
                                              stddev=0.0001))
    biases = tf.Variable(tf.ones([self._nr_classes]))

    model = tf.nn.softmax(tf.matmul(feature_data, weights) + biases)

    return model


class DeepModel():
  """ Model that contains several layers """

  def __init__(self, nr_predictors, nr_classes, dim_hidden1=50, dim_hidden2=25):
    """

    Args:
        nr_predictors (int): amount of predictors
        nr_classes (int): amount of classes
        dim_hidden1 (int): amount of neurons in first hidden layer
        dim_hidden2 (int): amount of neurons in second hidden layer
    """
    self._nr_predictors = nr_predictors
    self._nr_classes = nr_classes
    self.dim_hidden1 = dim_hidden1
    self.dim_hidden2 = dim_hidden2

  @property
  def nr_predictors(self):
    """ amount of predictors property """
    return self._nr_predictors

  @property
  def nr_classes(self):
    """ amount of classes property """
    return self._nr_classes

  def build_model(self, feature_data):
    """

    Args:
        feature_data (tf. tensors): feature tensors

    Returns:
        model: tensorflow model

    """
    weights1 = tf.Variable(tf.truncated_normal([self._nr_predictors, self.dim_hidden1],
                                               stddev=0.0001))
    biases1 = tf.Variable(tf.ones([self.dim_hidden1]))

    weights2 = tf.Variable(tf.truncated_normal([self.dim_hidden1, self.dim_hidden2],
                                               stddev=0.0001))
    biases2 = tf.Variable(tf.ones([self.dim_hidden2]))

    weights3 = tf.Variable(tf.truncated_normal([self.dim_hidden2, self.nr_classes],
                                               stddev=0.0001))
    biases3 = tf.Variable(tf.ones([self._nr_classes]))

    hidden_layer_1 = tf.nn.relu(tf.matmul(feature_data, weights1) + biases1)
    hidden_layer_2 = tf.nn.relu(tf.matmul(hidden_layer_1, weights2) + biases2)
    model = tf.nn.softmax(tf.matmul(hidden_layer_2, weights3) + biases3)

    return model
