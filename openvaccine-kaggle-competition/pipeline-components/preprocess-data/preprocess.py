import json
import numpy as np
import pandas as pd
import tensorflow as tf
import argparse
import os
import pickle5 as pkl

from tensorflow.keras.preprocessing.text import Tokenizer

print('v5')
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

# print('x_train', x_train)
# print('y_train', y_train)



#to save it
with open("/data/train.pkl", "wb") as f:
    pkl.dump([x_train, y_train], f)

