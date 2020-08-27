#!/usr/bin/env python
#coding: utf-8

#Text classification with an RNN
#This text classification tutorial trains a [recurrent neural network](https://developers.google.com/machine-learning/glossary/#recurrent_neural_network) on the [IMDB large movie review dataset](http://ai.stanford.edu/~amaas/data/sentiment/) for sentiment analysis.

import importlib
import argparse
import tensorflow as tf
import tensorflow_datasets as tfds
import os

def data_loader(hyperparams, local_data_dir):
    dataset, info = tfds.load('imdb_reviews/subwords8k', 
                              data_dir=local_data_dir,
                              with_info=True,
                              as_supervised=True)
    train_dataset, test_dataset = dataset['train'], dataset['test']
    encoder = info.features['text'].encoder
    train_dataset = train_dataset.shuffle(hyperparams['BUFFER_SIZE'])
    train_dataset = train_dataset.padded_batch(hyperparams['BATCH_SIZE'], padded_shapes=None)
    test_dataset = test_dataset.padded_batch(hyperparams['BATCH_SIZE'], padded_shapes=None)
    return train_dataset, test_dataset, encoder

def define_model(encoder, learning_rate):
    strategy = tf.distribute.MirroredStrategy()
    with strategy.scope():
        model = tf.keras.Sequential([
            tf.keras.layers.Embedding(encoder.vocab_size, 64),
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        model.compile(loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                          optimizer=tf.keras.optimizers.Adam(learning_rate),
                          metrics=['accuracy'])
    return model

class MovieReviewClassification(object):
    def __init__(self, learning_rate=0.01, batch_size=64, epochs=2, local_data_dir='/app/tensorflow_datasets'):
        hyperparams = {'BUFFER_SIZE': 10000, 'BATCH_SIZE': batch_size}
        self.model_file = "lstm_trained"
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.train_dataset, self.test_dataset, self.encoder = data_loader(hyperparams, local_data_dir)
        
    def train(self):
        model = define_model(self.encoder, self.learning_rate)
        #steps per epoch are reduced here to train on limited resources
        #you are free to remove this argument
        history = model.fit(self.train_dataset, 
                            epochs=self.epochs,
                            shuffle=True,
                            steps_per_epoch=30,
                            validation_data=self.test_dataset,
                            validation_steps=30,
                            verbose=0)
        model.save(self.model_file)
        val_losses = history.history['val_loss']
        val_accuracies = history.history['val_accuracy']
        for epoch, val_loss, val_accuracy in zip(range(self.epochs), val_losses, val_accuracies):
          print("epoch {}:\nval_loss={:.2f}\nval_accuracy={:.2f}\n".format(epoch + 1, val_loss, val_accuracy))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-lr", "--learning_rate", default="1e-4", help="Learning rate for the Keras optimizer")
    parser.add_argument("-bsz", "--batch_size", default="64", help="Batch size for each step of learning")
    parser.add_argument("-e", "--epochs", default="2", help="Number of epochs in each trial")
    args = parser.parse_args()
    learning_rate = float(args.learning_rate)
    batch_size = int(args.batch_size)
    epochs = int(args.epochs)
    model = MovieReviewClassification(learning_rate, batch_size, epochs, local_data_dir="/app/tensorflow_datasets")
    model.train()