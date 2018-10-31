# Copyright 2018 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""
Model Training
"""

# Keras's Neural Network components
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten

# Kera's Convoluntional Neural Network components
from keras.layers import Conv2D, MaxPooling2D

import numpy as np
from keras.utils import np_utils

def construct_model_grayscale(input_shape=(28,28,1), n_classes=62):
  """ Construct basic CNN for classifying grayscale images of size 28 x 28
  """
  # Add missing number of channels (1) if not specified in input_shape
  if len(input_shape) == 2:
    input_shape = (input_shape[0], input_shape[1], 1)

  # Constructing a Feed Forward Neural Network
  model = Sequential()

  model.add(Conv2D(filters=32, kernel_size=3, padding='same', activation='relu', input_shape=input_shape))
  model.add(Conv2D(filters=64, kernel_size=3, padding='same', activation='relu'))
  model.add(MaxPooling2D(pool_size=2))
  model.add(Flatten())
  model.add(Dense(128, activation='relu'))
  model.add(Dropout(0.5))
  model.add(Dense(64, activation='relu'))
  model.add(Dense(n_classes, activation='softmax'))
  model.compile(loss='categorical_crossentropy',  optimizer='adam', metrics=['accuracy'])
  return model

def train_model_grayscale(x, y, x_test=None, y_test=None, input_shape=(28,28,1), n_classes=62, epochs=10, batch_size=32, percent=0.2, verbose=False, seed=113):
  """ Train CNN for classifying grayscale images of size 28 x 28
  """
  model = construct_model_grayscale(input_shape, n_classes)
  accuracy = train(model, x, y, x_test, y_test, epochs, batch_size, percent, verbose, seed)
  return model, accuracy

def construct_model_color(input_shape=(100, 100, 3), n_classes=81):
  """ Construct basic CNN for classifying color images of size 100 x 100
  """
  # Add missing number of channels (3) if not specified in input_shape
  if len(input_shape) == 2:
    input_shape = (input_shape[0], input_shape[1], 3)

  # Constructing a Feed Forward Neural Network
  model = Sequential()

  model.add(Conv2D(filters=16, kernel_size=3, padding='same', activation='relu', input_shape=input_shape))
  model.add(Conv2D(filters=32, kernel_size=3, padding='same', activation='relu'))
  model.add(Conv2D(filters=64, kernel_size=3, padding='same', activation='relu'))
  model.add(Conv2D(filters=128, kernel_size=3, padding='same', activation='relu'))
  model.add(MaxPooling2D(pool_size=2))
  model.add(Flatten())
  model.add(Dense(1024, activation='relu'))
  model.add(Dropout(0.25))
  model.add(Dense(256, activation='relu'))
  model.add(Dense(n_classes, activation='softmax'))
  model.compile(loss='categorical_crossentropy',  optimizer='adam', metrics=['accuracy'])
  return model

def train_model_color(x, y, x_test=None, y_test=None, input_shape=(100, 100, 3), n_classes=81, epochs=10, batch_size=32, percent=0.2, verbose=False, seed=113):
  """ Train CNN for classifying color images of size 100 x 100
  """
  model = construct_model_color(input_shape, n_classes)
  accuracy = train(model, x, y, x_test, y_test, epochs, batch_size, percent, verbose, seed)
  return model, accuracy

def train(model, x, y, x_test=None, y_test=None, epochs=10, batch_size=32, percent=0.2, verbose=False, seed=113):
    """ Train the model
    Args:
        model     : (model) The CNN model.
        x         : (numpy.ndarray) The x portion (preprocessed image data) of the dataset.
        y         : (numpy.ndarray) The y portion (labels) of the dataset.
        x_test    : (numpy.ndarray) The x_test (if pre-split) portion of the dataset.
        y_test    : (numpy.ndarray) The y_test (if pre-split) portion of the dataset.
        epochs    : (int) The number of times to feed the entire dataset for training.
        batch_size: (int) The mini-batch size.
        percent   : (float) The percent of the dataset to use for test.
        verbose   : (bool) Display (console) progress status.
        seed      : (int) Seed for random shuffle before splitting.
        learning_rate: (float) The learning rate.

    Returns:
        The model accuracy after training and evaluation.

    Raises:
        None
    """

    # one hot encode the labels
    y = np_utils.to_categorical(y)
    if y_test is not None:
        y_test = np_utils.to_categorical(y_test)


    # Images are grayscale. Keras expects shape to be (rows, height, width, channels) vs. (rows, height, width)
    if len(x.shape) == 3:
        x = x.reshape(x.shape[0], x.shape[1], x.shape[2], 1)
        if x_test is not None:
            x_test = x_test.reshape(x_test.shape[0], x_test.shape[1], x_test.shape[2], 1)

    # Ignore percent if data is already split
    if x_test is not None:
        percent = 0


    # Calculate the number of elements which will be used as training data
    train_size = int((1-percent) * len(x))
    if verbose: print("Training Size:", train_size)

    # Dataset is combined
    if x_test is None:
        # Randomly shuffle the data before splitting
        np.random.seed(seed)
        np.random.shuffle(x)
        np.random.seed(seed)
        np.random.shuffle(y)

        # split the data into Train and Test
        X_train = x[:train_size]
        Y_train = y[:train_size]
        X_test  = x[train_size:]
        Y_test  = y[train_size:]
    # Dataset is presplit
    else:
        X_train = x
        Y_train = y
        X_test  = x_test
        Y_test  = y_test

    if verbose: verbose = 2

    # Train the model with the training data
    model.fit(X_train, Y_train, validation_data=(X_test, Y_test), epochs=epochs, batch_size=batch_size, shuffle=True, verbose=verbose)

    # Run the model with the test (evaluation) data
    accuracy = model.evaluate(X_test, Y_test, verbose=0)

    return accuracy
