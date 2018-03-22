import argparse
import glob
import pandas as pd
from sklearn.model_selection import train_test_split
from ktext.preprocess import processor
from seq2seq_utils import load_decoder_inputs, load_encoder_inputs, load_text_processor
from seq2seq_utils import viz_model_architecture
import numpy as np
from keras.callbacks import CSVLogger, ModelCheckpoint
from keras.layers import Input, LSTM, GRU, Dense, Embedding, Bidirectional, BatchNormalization
from keras.models import Model
from keras import optimizers
import dill as dpickle
import zipfile
from google.cloud import storage

# Parsing flags.
parser = argparse.ArgumentParser()
parser.add_argument("--sample_size", type=int, default=2000000)
parser.add_argument("--learning_rate", default="0.001")

parser.add_argument("--input_data_gcs_bucket", type=str, default="kubeflow-examples")
parser.add_argument("--input_data_gcs_path", type=str, default="github-issue-summarization-data/github-issues.zip")

parser.add_argument("--output_model_gcs_bucket", type=str, default="kubeflow-examples")
parser.add_argument("--output_model_gcs_path", type=str, default="github-issue-summarization-data/output_model.h5")

parser.add_argument("--output_body_preprocessor_dpkl", type=str, default="body_preprocessor.dpkl")
parser.add_argument("--output_title_preprocessor_dpkl", type=str, default="title_preprocessor.dpkl")
parser.add_argument("--output_train_title_vecs_npy", type=str, default="train_title_vecs.npy")
parser.add_argument("--output_train_body_vecs_npy", type=str, default="train_body_vecs.npy")
parser.add_argument("--output_model_h5", type=str, default="output_model.h5")

args = parser.parse_args()
print(args)

learning_rate=float(args.learning_rate)

pd.set_option('display.max_colwidth', 500)


bucket = storage.Bucket(storage.Client(), args.input_data_gcs_bucket)
storage.Blob(args.input_data_gcs_path, bucket).download_to_filename('github-issues.zip')

zip_ref = zipfile.ZipFile('github-issues.zip', 'r')
zip_ref.extractall('.')
zip_ref.close()

# Read in data sample 2M rows (for speed of tutorial)
traindf, testdf = train_test_split(pd.read_csv('github_issues.csv').sample(n=args.sample_size),
                                   test_size=.10)

# Print stats about the shape of the data.
print(f'Train: {traindf.shape[0]:,} rows {traindf.shape[1]:,} columns')
print(f'Test: {testdf.shape[0]:,} rows {testdf.shape[1]:,} columns')

train_body_raw = traindf.body.tolist()
train_title_raw = traindf.issue_title.tolist()

# Clean, tokenize, and apply padding / truncating such that each document
# length = 70. Also, retain only the top 8,000 words in the vocabulary and set
# the remaining words to 1 which will become common index for rare words.
body_pp = processor(keep_n=8000, padding_maxlen=70)
train_body_vecs = body_pp.fit_transform(train_body_raw)

print('Example original body:', train_body_raw[0])
print('Example body after pre-processing:', train_body_vecs[0])

# Instantiate a text processor for the titles, with some different parameters.
title_pp = processor(append_indicators=True, keep_n=4500,
                     padding_maxlen=12, padding ='post')

# process the title data
train_title_vecs = title_pp.fit_transform(train_title_raw)

print('Example original title:', train_title_raw[0])
print('Example title after pre-processing:', train_title_vecs[0])

# Save the preprocessor.
with open(args.output_body_preprocessor_dpkl, 'wb') as f:
    dpickle.dump(body_pp, f)

with open(args.output_title_preprocessor_dpkl, 'wb') as f:
    dpickle.dump(title_pp, f)

# Save the processed data.
np.save(args.output_train_title_vecs_npy, train_title_vecs)
np.save(args.output_train_body_vecs_npy, train_body_vecs)


encoder_input_data, doc_length = load_encoder_inputs(args.output_train_body_vecs_npy)
decoder_input_data, decoder_target_data = load_decoder_inputs(args.output_train_title_vecs_npy)

num_encoder_tokens, body_pp = load_text_processor(args.output_body_preprocessor_dpkl)
num_decoder_tokens, title_pp = load_text_processor(args.output_title_preprocessor_dpkl)

# Arbitrarly set latent dimension for embedding and hidden units
latent_dim = 300

###############
# Encoder Model.
###############
encoder_inputs = Input(shape=(doc_length,), name='Encoder-Input')

# Word embeding for encoder (ex: Issue Body)
x = Embedding(num_encoder_tokens, latent_dim, name='Body-Word-Embedding', mask_zero=False)(encoder_inputs)
x = BatchNormalization(name='Encoder-Batchnorm-1')(x)

# We do not need the `encoder_output` just the hidden state.
_, state_h = GRU(latent_dim, return_state=True, name='Encoder-Last-GRU')(x)

# Encapsulate the encoder as a separate entity so we can just
# encode without decoding if we want to.
encoder_model = Model(inputs=encoder_inputs, outputs=state_h, name='Encoder-Model')

seq2seq_encoder_out = encoder_model(encoder_inputs)

################
# Decoder Model.
################
decoder_inputs = Input(shape=(None,), name='Decoder-Input')  # for teacher forcing

# Word Embedding For Decoder (ex: Issue Titles)
dec_emb = Embedding(num_decoder_tokens, latent_dim, name='Decoder-Word-Embedding', mask_zero=False)(decoder_inputs)
dec_bn = BatchNormalization(name='Decoder-Batchnorm-1')(dec_emb)

# Set up the decoder, using `decoder_state_input` as initial state.
decoder_gru = GRU(latent_dim, return_state=True, return_sequences=True, name='Decoder-GRU')
decoder_gru_output, _ = decoder_gru(dec_bn, initial_state=seq2seq_encoder_out)
x = BatchNormalization(name='Decoder-Batchnorm-2')(decoder_gru_output)

# Dense layer for prediction
decoder_dense = Dense(num_decoder_tokens, activation='softmax', name='Final-Output-Dense')
decoder_outputs = decoder_dense(x)

################
# Seq2Seq Model.
################

seq2seq_Model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

seq2seq_Model.compile(optimizer=optimizers.Nadam(lr=learning_rate), loss='sparse_categorical_crossentropy')

seq2seq_Model.summary()

script_name_base = 'tutorial_seq2seq'
csv_logger = CSVLogger('{:}.log'.format(script_name_base))
model_checkpoint = ModelCheckpoint('{:}.epoch{{epoch:02d}}-val{{val_loss:.5f}}.hdf5'.format(script_name_base),
                                   save_best_only=True)

batch_size = 1200
epochs = 7
history = seq2seq_Model.fit([encoder_input_data, decoder_input_data], np.expand_dims(decoder_target_data, -1),
          batch_size=batch_size,
          epochs=epochs,
          validation_split=0.12, callbacks=[csv_logger, model_checkpoint])

#############
# Save model.
#############
seq2seq_Model.save(args.output_model_h5)


######################
# Upload model to GCS.
######################
bucket = storage.Bucket(storage.Client(), args.output_model_gcs_bucket)
storage.Blob(args.output_model_gcs_path, bucket).upload_from_filename(args.output_model_h5)
