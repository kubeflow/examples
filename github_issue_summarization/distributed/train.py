import argparse
import json
import logging
import os
import sys
import time

import numpy as np
import dill as dpickle
import pandas as pd
import tensorflow as tf
from tensorflow.keras.callbacks import CSVLogger, ModelCheckpoint

#import recurrent
from ktext.preprocess import processor
from sklearn.model_selection import train_test_split

from seq2seq_utils import load_decoder_inputs, load_encoder_inputs, load_text_processor

class Trainer(object):
  def __init__(self, args):
    self.args = args

    if not args.data_dir:
      raise ValueError("--data_dir must be set.")

    if not args.model_dir:
      raise ValueError("--model_dir must be set.")

    # TODO(jlewi): We should make this a command line flag
    self.use_sample_data = False

    self.data_dir = args.data_dir
    self.model_dir = args.model_dir
    self.data_file = args.data_file

    # TODO(jlewi): We should refactor this code.
    # On PS we should just return or not invoke this code
    # at all. Build model probably isn't where we should
    # start the PS.
    self.tf_config = os.environ.get('TF_CONFIG', '{}')
    self.tf_config_json = json.loads(self.tf_config)

    self.cluster = self.tf_config_json.get('cluster')
    self.job_name = self.tf_config_json.get('task', {}).get('type')
    self.task_index = self.tf_config_json.get('task', {}).get('index')

  def preprocess(self):
    # We preprocess the data if we are the master or chief.
    # Or if we aren't running distributed.
    if self.job_name and self.job_name.lower() not in ["master", "chief"]:
      return

    # TODO(jlewi): The test data isn't being used for anything. How can
    # we configure evaluation?
    if self.use_sample_data:
      training_data_size = 2000
      traindf, _ = train_test_split(pd.read_csv(self.data_file).sample(n=training_data_size),
      test_size=.10)
    else:
      traindf, _ = train_test_split(pd.read_csv(self.data_file), test_size=.10)

    train_body_raw = traindf.body.tolist()
    train_title_raw = traindf.issue_title.tolist()

    body_pp = processor(keep_n=8000, padding_maxlen=70)
    train_body_vecs = body_pp.fit_transform(train_body_raw)

    logging.info('\noriginal string:\n', train_body_raw[0], '\n')
    logging.info('after pre-processing:\n', train_body_vecs[0], '\n')

    title_pp = processor(append_indicators=True, keep_n=4500,
      padding_maxlen=12, padding='post')

    # process the title data
    train_title_vecs = title_pp.fit_transform(train_title_raw)

    logging.info('\noriginal string:\n', train_title_raw[0])
    logging.info('after pre-processing:\n', train_title_vecs[0])

    # Save the preprocessor
    with open(self.data_dir + 'body_pp.dpkl', 'wb') as f:
      dpickle.dump(body_pp, f)

    with open(self.data_dir + 'title_pp.dpkl', 'wb') as f:
      dpickle.dump(title_pp, f)

    # Save the processed data
    np.save(self.data_dir + 'train_title_vecs.npy', train_title_vecs)
    np.save(self.data_dir + 'train_body_vecs.npy', train_body_vecs)

  def build_model(self):
    """Build a keras model."""
    logging.info("starting")

    if self.job_name and self.job_name.lower() in ["ps"]:
      logging.info("ps doesn't build model")
      return

    # TODO(jlewi): Why do we need to block waiting for the file?
    # I think this is because only the master produces the npy
    # files so the other workers need to wait for the files to arrive.
    # It might be better to make preprocessing a separate job.
    while True:
      if os.path.isfile(self.data_dir + 'train_body_vecs.npy'):
        break
      logging.info("Waiting for dataset")
      time.sleep(2)
    self.encoder_input_data, doc_length = load_encoder_inputs(
      self.data_dir + 'train_body_vecs.npy')
    self.decoder_input_data, self.decoder_target_data = load_decoder_inputs(
      self.data_dir + 'train_title_vecs.npy')

    num_encoder_tokens, body_pp = load_text_processor(
      self.data_dir + 'body_pp.dpkl')
    num_decoder_tokens, title_pp = load_text_processor(
      self.data_dir + 'title_pp.dpkl')

    #arbitrarly set latent dimension for embedding and hidden units
    latent_dim = 300

    ##### Define Model Architecture ######

    ########################
    #### Encoder Model ####
    encoder_inputs = tf.keras.layers.Input(shape=(doc_length,), name='Encoder-Input')

    # Word embeding for encoder (ex: Issue Body)
    x = tf.keras.layers.Embedding(
          num_encoder_tokens, latent_dim, name='Body-Word-Embedding', mask_zero=False)(encoder_inputs)
    x = tf.keras.layers.BatchNormalization(name='Encoder-Batchnorm-1')(x)

    # We do not need the `encoder_output` just the hidden state.
    _, state_h = tf.keras.layers.GRU(latent_dim, return_state=True, name='Encoder-Last-GRU')(x)

    # Encapsulate the encoder as a separate entity so we can just
    #  encode without decoding if we want to.

    encoder_model = tf.keras.Model(inputs=encoder_inputs, outputs=state_h, name='Encoder-Model')
    seq2seq_encoder_out = encoder_model(encoder_inputs)

    ########################
    #### Decoder Model ####
    decoder_inputs = tf.keras.layers.Input(shape=(None,), name='Decoder-Input')  # for teacher forcing

    # Word Embedding For Decoder (ex: Issue Titles)
    dec_emb = tf.keras.layers.Embedding(
                num_decoder_tokens,
                latent_dim, name='Decoder-Word-Embedding',
                mask_zero=False)(decoder_inputs)
    dec_bn = tf.keras.layers.BatchNormalization(name='Decoder-Batchnorm-1')(dec_emb)

    # Set up the decoder, using `decoder_state_input` as _state.
    # TODO(jlewi): Once https://github.com/keras-team/keras/issues/9761 is
    # fixed remove this hack.
    if True:
      decoder_gru = tf.keras.layers.GRU(
        latent_dim, return_state=True, return_sequences=True, name='Decoder-GRU')
    else:
      decoder_gru = recurrent.GRU(
        latent_dim, return_state=True, return_sequences=True, name='Decoder-GRU')

    # TODO: seems to be running into this https://github.com/keras-team/keras/issues/9761
    # TODO: jlewi@ changed the function call to match the new syntax in the issue
    # This is now giving error:
    # ValueError: An `initial_state` was passed that is not compatible with `cell.state_size`. Received `state_spec`=[InputSpec(shape=(None, 300), ndim=2), InputSpec(shape=(None, 300), ndim=2)]; however `cell.state_size` is [300]
    decoder_gru_output, _ = decoder_gru(dec_bn, initial_state=[seq2seq_encoder_out])
    x = tf.keras.layers.BatchNormalization(name='Decoder-Batchnorm-2')(decoder_gru_output)

    # Dense layer for prediction
    decoder_dense = tf.keras.layers.Dense(
                      num_decoder_tokens, activation='softmax', name='Final-Output-Dense')
    decoder_outputs = decoder_dense(x)

    ########################
    #### Seq2Seq Model ####

    self.seq2seq_Model = tf.keras.Model([encoder_inputs, decoder_inputs], decoder_outputs)

    self.seq2seq_Model.compile(
      optimizer=tf.keras.optimizers.Nadam(lr=0.001),
      loss='sparse_categorical_crossentropy',
      metrics=['accuracy'])

  def train_keras(self, base_name='tutorial_seq2seq',batch_size=1200, epochs=7):
    """Train using Keras.

    This is an alternative to using the TF.Estimator API.

    TODO(jlewi): The reason we added support for using Keras
    was to debug whether we were hitting issue:
    https://github.com/keras-team/keras/issues/9761 only with TF.Estimator.
    """
    logging.info("Using base name: %s", base_name)
    csv_logger = CSVLogger('{:}.log'.format(base_name))
    model_checkpoint = ModelCheckpoint(
      '{:}.epoch{{epoch:02d}}-val{{val_loss:.5f}}.hdf5'.format(
        base_name), save_best_only=True)

    history = self.seq2seq_Model.fit(
      [self.encoder_input_data, self.decoder_input_data],
      np.expand_dims(self.decoder_target_data, -1),
              batch_size=batch_size,
              epochs=epochs,
              validation_split=0.12, callbacks=[csv_logger, model_checkpoint])


  def train_estimator(self):
    """Train the model using the TF.Estimator API."""
    if self.job_name:
      cluster_spec = tf.train.ClusterSpec(cluster)
    if self.job_name == "ps":
      server = tf.train.Server(cluster_spec, job_name=self.job_name,
                               task_index=self.task_index)

      server.join()
      sys.exit(0)

    cfg = tf.estimator.RunConfig(session_config=tf.ConfigProto(log_device_placement=False))

    estimator = tf.keras.estimator.model_to_estimator(
                  keras_model=self.seq2seq_Model, model_dir=self.model_dir,
                  config=cfg)

    expanded = np.expand_dims(self.decoder_target_data, -1)
    input_fn = tf.estimator.inputs.numpy_input_fn(
                 x={'Encoder-Input': self.encoder_input_data,
                    'Decoder-Input': self.decoder_input_data},
                 y=expanded,
                 shuffle=False)

    train_spec = tf.estimator.TrainSpec(input_fn=input_fn,
                                        max_steps=self.args.max_steps)
    eval_spec = tf.estimator.EvalSpec(input_fn=input_fn, throttle_secs=10,
                                      steps=self.args.eval_steps)

    tf.estimator.train_and_evaluate(estimator, train_spec, eval_spec)

def main(args):
  logging.basicConfig(
    level=logging.INFO,
    format=('%(levelname)s|%(asctime)s'
            '|%(pathname)s|%(lineno)d| %(message)s'),
    datefmt='%Y-%m-%dT%H:%M:%S',
  )
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)

  parser = argparse.ArgumentParser()

  parser.add_argument(
    "--data_file",
    type=str,
    default="",
    help="The path for the data file. Should be  .csv file")

  parser.add_argument(
    "--data_dir",
    type=str,
    default="",
    help="The directory for the data. "
         "This directory is used to store the preprocessors. "
         "It needs to be a shared directory among all the workers.")

  parser.add_argument(
    "--model_dir",
    type=str,
    default="Location to save the model.")

  parser.add_argument("--max_steps", type=int, default=2000000)
  parser.add_argument("--eval_steps", type=int, default=1000)

  args = parser.parse_args()

  trainer = Trainer(args)
  trainer.preprocess()
  trainer.build_model()

  # TODO(jlewi): Estimator isn't working so we
  # we should probably train using Keras.
  trainer.train_estimator()

if __name__ == '__main__':
  main()
