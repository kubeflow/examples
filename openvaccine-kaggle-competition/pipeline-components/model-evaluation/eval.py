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

train_df = pd.read_json("data/train.json", lines=True)
test_df = pd.read_json("data/test.json", lines=True)


symbols = "().ACGUBEHIMSX"
feat_cols = ["sequence", "structure", "predicted_loop_type"]
target_cols = ["reactivity", "deg_Mg_pH10", "deg_Mg_50C", "deg_pH10", "deg_50C"]
error_cols = ["reactivity_error", "deg_error_Mg_pH10", "deg_error_Mg_50C", "deg_error_pH10", "deg_error_50C"]

tokenizer = Tokenizer(char_level=True, filters="")
tokenizer.fit_on_texts(symbols)

# get the number of elements in the vocabulary
vocab_size = len(tokenizer.word_index) + 1

myfile = open("/data/myfile.txt","a")#append mode
print("writing file ..", vocab_size)
myfile.write(str(vocab_size))
myfile.close()

def process_features(example):
    sequence_sentences = example[0]
    structure_sentences = example[1]
    loop_sentences = example[2]
    
    # transform character sequences into number sequences
    sequence_tokens = np.array(
        tokenizer.texts_to_sequences(sequence_sentences)
    )
    structure_tokens = np.array(
        tokenizer.texts_to_sequences(structure_sentences)
    )
    loop_tokens = np.array(
        tokenizer.texts_to_sequences(loop_sentences)
    )
    
    # concatenate the tokenized sequences
    sequences = np.stack(
        (sequence_tokens, structure_tokens, loop_tokens),
        axis=1
    )
    sequences = np.transpose(sequences, (2, 0, 1))
    
    prepared = sequences.tolist()
    
    return prepared[0]

def process_labels(df):
    df = df.copy()
    
    labels = np.array(df[target_cols].values.tolist())
    labels = np.transpose(labels, (0, 2, 1))
    
    return labels

public_test_df = test_df.query("seq_length == 107")
private_test_df = test_df.query("seq_length == 130")

x_train = [process_features(row.tolist()) for _, row in train_df[feat_cols].iterrows()]
y_train = process_labels(train_df)

unprocessed_x_public_test = [row.tolist() for _, row in public_test_df[feat_cols].iterrows()]
unprocessed_x_private_test = [row.tolist() for _, row in private_test_df[feat_cols].iterrows()]



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

model_public = build_model(vocab_size, seq_length=107, pred_len=107)
model_private = build_model(vocab_size, seq_length=130, pred_len=130)


model_public.set_weights(model.get_weights())
model_private.set_weights(model.get_weights())

public_preds = model_public.predict(np.array([process_features(x) for x in unprocessed_x_public_test]))
private_preds = model_private.predict(np.array([process_features(x) for x in unprocessed_x_private_test]))

