import json
import numpy as np
import pandas as pd
import tensorflow as tf
import argparse
import os
import pickle5 as pkl

from tensorflow.keras.preprocessing.text import Tokenizer

parser = argparse.ArgumentParser()
parser.add_argument('--LR')
parser.add_argument('--EPOCHS')
parser.add_argument('--BATCH_SIZE')
parser.add_argument('--EMBED_DIM', type=int)
parser.add_argument('--HIDDEN_DIM', type=int)
parser.add_argument('--DROPOUT', type=float)
parser.add_argument('--SP_DROPOUT', type=float)
parser.add_argument('--TRAIN_SEQUENCE_LENGTH', type=int)

args = vars(parser.parse_args())

lr = args['LR']
epochs = args['EPOCHS']
batchsize = args['BATCH_SIZE']
embeddim = args['EMBED_DIM']
hiddendim = args['HIDDEN_DIM']
dropout = args['DROPOUT']
spdropout = args['SP_DROPOUT']
trainsequencelength = args['TRAIN_SEQUENCE_LENGTH']

LR=lr
EPOCHS=epochs
BATCH_SIZE=batchsize
EMBED_DIM=embeddim
HIDDEN_DIM=hiddendim
DROPOUT=dropout
SP_DROPOUT=spdropout
TRAIN_SEQUENCE_LENGTH=trainsequencelength

with open("/data/train.pkl", "rb") as f:
    x_train, y_train = pkl.load(f)

def gru_layer(hidden_dim, dropout):
    return tf.keras.layers.Bidirectional(
         tf.keras.layers.GRU(hidden_dim, dropout=dropout, return_sequences=True, kernel_initializer = 'orthogonal')
    )

def lstm_layer(hidden_dim, dropout):
    return tf.keras.layers.Bidirectional(
        tf.keras.layers.LSTM(hidden_dim, dropout=dropout, return_sequences=True, kernel_initializer = 'orthogonal')
    )

def build_model(vocab_size, seq_length=TRAIN_SEQUENCE_LENGTH, pred_len=68,
                embed_dim=EMBED_DIM,
                hidden_dim=HIDDEN_DIM, dropout=DROPOUT, sp_dropout=SP_DROPOUT):
    inputs = tf.keras.layers.Input(shape=(seq_length, 3))

    embed_dim_int=int(embed_dim)
    print('embed_dim_int' , embed_dim_int)
    embed = tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=embed_dim_int)(inputs)
    
    reshaped = tf.reshape(
        embed, shape=(-1, embed.shape[1],  embed.shape[2] * embed.shape[3])
    )
    
    hidden = tf.keras.layers.SpatialDropout1D(sp_dropout)(reshaped)
    
    hidden = gru_layer(hidden_dim, dropout)(hidden)
    hidden = lstm_layer(hidden_dim, dropout)(hidden)
    
    truncated = hidden[:, :pred_len]
    
    out = tf.keras.layers.Dense(5, activation="linear")(truncated)
    
    model = tf.keras.Model(inputs=inputs, outputs=out)
    
    return model



with open('/data/myfile.txt') as fp:
    for line in fp:
        vocab_size=int(line)
print("reading file ..", vocab_size)

model = build_model(vocab_size)
model.summary()

class MeanColumnwiseRMSE(tf.keras.losses.Loss):
    def __init__(self, name='MeanColumnwiseRMSE'):
        super().__init__(name=name)

    def call(self, y_true, y_pred):
        colwise_mse = tf.reduce_mean(tf.square(y_true - y_pred), axis=1)
        return tf.reduce_mean(tf.sqrt(colwise_mse), axis=1)

model.compile(tf.optimizers.Adam(learning_rate=float(LR)), loss=MeanColumnwiseRMSE())
history = model.fit(np.array(x_train), np.array(y_train), 
                    validation_split=.1, batch_size=int(BATCH_SIZE), epochs=int(EPOCHS))

validation_loss = history.history.get("val_loss")[0]

