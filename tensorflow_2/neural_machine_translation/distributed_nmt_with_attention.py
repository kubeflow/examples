#!/usr/bin/env python
#coding: utf-8

#Neural Machine Translation with Attention
#This machine translation tutorial trains an [encoder-decoder architecture with attention](https://github.com/tensorflow/nmt) on a [Spanish-English dataset](http://www.manythings.org/anki/).

import re
import os
import io
import time
import argparse
import numpy as np
import unicodedata

import tensorflow as tf
from sklearn.model_selection import train_test_split


class Encoder(tf.keras.Model):
	def __init__(self, vocab_size, embedding_dim, enc_units, batch_sz):
		super(Encoder, self).__init__()
		self.batch_sz = batch_sz
		self.enc_units = enc_units
		self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
		self.gru = tf.keras.layers.GRU(self.enc_units,
		                               return_sequences=True,
		                               return_state=True,
		                               recurrent_initializer='glorot_uniform')

	def call(self, x, hidden):
		x = self.embedding(x)
		output, state = self.gru(x, initial_state = hidden)
		return output, state

	def initialize_hidden_state(self):
		return tf.zeros((self.batch_sz, self.enc_units))


class BahdanauAttention(tf.keras.layers.Layer):
	def __init__(self, units):
		super(BahdanauAttention, self).__init__()
		self.W1 = tf.keras.layers.Dense(units)
		self.W2 = tf.keras.layers.Dense(units)
		self.V = tf.keras.layers.Dense(1)

	def call(self, query, values):
		# query hidden state shape == (batch_size, hidden size)
		# query_with_time_axis shape == (batch_size, 1, hidden size)
		# values shape == (batch_size, max_len, hidden size)
		# we are doing this to broadcast addition along the time axis to calculate the score
		query_with_time_axis = tf.expand_dims(query, 1)

		# score shape == (batch_size, max_length, 1)
		# we get 1 at the last axis because we are applying score to self.V
		# the shape of the tensor before applying self.V is (batch_size, max_length, units)
		score = self.V(tf.nn.tanh(
		    self.W1(query_with_time_axis) + self.W2(values)))

		# attention_weights shape == (batch_size, max_length, 1)
		attention_weights = tf.nn.softmax(score, axis=1)

		# context_vector shape after sum == (batch_size, hidden_size)
		context_vector = attention_weights * values
		context_vector = tf.reduce_sum(context_vector, axis=1)
		return context_vector, attention_weights


class Decoder(tf.keras.Model):
	def __init__(self, vocab_size, embedding_dim, dec_units, batch_sz):
		super(Decoder, self).__init__()
		self.batch_sz = batch_sz
		self.dec_units = dec_units
		self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
		self.gru = tf.keras.layers.GRU(self.dec_units,
		                               return_sequences=True,
		                               return_state=True,
		                               recurrent_initializer='glorot_uniform')
		self.fc = tf.keras.layers.Dense(vocab_size)

		# used for attention
		self.attention = BahdanauAttention(self.dec_units)

	def call(self, x, hidden, enc_output):
		# enc_output shape == (batch_size, max_length, hidden_size)
		context_vector, attention_weights = self.attention(hidden, enc_output)

		# x shape after passing through embedding == (batch_size, 1, embedding_dim)
		x = self.embedding(x)

		# x shape after concatenation == (batch_size, 1, embedding_dim + hidden_size)
		x = tf.concat([tf.expand_dims(context_vector, 1), x], axis=-1)

		# passing the concatenated vector to the GRU
		output, state = self.gru(x)

		# output shape == (batch_size * 1, hidden_size)
		output = tf.reshape(output, (-1, output.shape[2]))

		# output shape == (batch_size, vocab)
		x = self.fc(output)
		return x, state, attention_weights


# Converts the unicode file to ascii
def unicode_to_ascii(s):
	return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def preprocess_sentence(w):
	w = unicode_to_ascii(w.lower().strip())

	# creating a space between a word and the punctuation following it
	# eg: "he is a boy." => "he is a boy ."
	# Reference:- https://stackoverflow.com/questions/3645931/python-padding-punctuation-with-white-spaces-keeping-punctuation
	w = re.sub(r"([?.!,¿])", r" \1 ", w)
	w = re.sub(r'[" "]+', " ", w)

	# replacing everything with space except (a-z, A-Z, ".", "?", "!", ",")
	w = re.sub(r"[^a-zA-Z?.!,¿]+", " ", w)
	w = w.strip()

	# adding a start and an end token to the sentence
	# so that the model know when to start and stop predicting.
	w = '<start> ' + w + ' <end>'
	return w


# 1. Remove the accents
# 2. Clean the sentences
# 3. Return word pairs in the format: [ENGLISH, SPANISH]
def create_dataset(path, num_examples):
	lines = io.open(path, encoding='UTF-8').read().strip().split('\n')
	word_pairs = [[preprocess_sentence(w) for w in l.split('\t')]  for l in lines[:num_examples]]
	return zip(*word_pairs)


def tokenize(lang):
	lang_tokenizer = tf.keras.preprocessing.text.Tokenizer(filters='')
	lang_tokenizer.fit_on_texts(lang)
	tensor = lang_tokenizer.texts_to_sequences(lang)
	tensor = tf.keras.preprocessing.sequence.pad_sequences(tensor, padding='post')
	return tensor, lang_tokenizer


def load_dataset(path, num_examples=None):
	# creating cleaned input, output pairs
	targ_lang, inp_lang = create_dataset(path, num_examples)
	input_tensor, inp_lang_tokenizer = tokenize(inp_lang)
	target_tensor, targ_lang_tokenizer = tokenize(targ_lang)
	return input_tensor, target_tensor, inp_lang_tokenizer, targ_lang_tokenizer


def data_loader(hyperparams):
	# Download the file
	data_dir = os.path.join(os.getcwd(), 'dataset')
	data_url = 'http://storage.googleapis.com/download.tensorflow.org/data/spa-eng.zip'
	path_to_zip = tf.keras.utils.get_file(os.path.join(data_dir, 'spa-eng.zip'), origin=data_url, extract=True)
	path_to_file = os.path.join(os.path.dirname(path_to_zip), "spa-eng", "spa.txt")
	print("Path to stored file: {}".format(path_to_file))


	num_examples = hyperparams['NUM_EXAMPLES']
	batch_size = hyperparams['BATCH_SIZE']

	input_tensor, target_tensor, inp_lang, targ_lang = load_dataset(path_to_file, num_examples)
	max_length_targ, max_length_inp = target_tensor.shape[1], input_tensor.shape[1]

	(input_tensor_train, input_tensor_val, 
		target_tensor_train, target_tensor_val) = train_test_split(input_tensor, target_tensor, test_size=hyperparams['TEST_SIZE'])

	buffer_size = len(input_tensor_train)
	steps_per_epoch = len(input_tensor_train)//batch_size
	vocab_inp_size = len(inp_lang.word_index)+1
	vocab_tar_size = len(targ_lang.word_index)+1

	dataset = tf.data.Dataset.from_tensor_slices((input_tensor_train, target_tensor_train)).shuffle(buffer_size)
	dataset = dataset.batch(batch_size, drop_remainder=True)

	return dataset, vocab_inp_size, vocab_tar_size, max_length_inp, max_length_targ, steps_per_epoch, targ_lang


def define_model(hyperparams, vocab_inp_size, vocab_tar_size):
	embedding_dim = 255
	units = 1024
	strategy = tf.distribute.MirroredStrategy()
	with strategy.scope():
		encoder = Encoder(vocab_inp_size, embedding_dim, units, hyperparams['BATCH_SIZE'])
		attention_layer = BahdanauAttention(10)
		decoder = Decoder(vocab_tar_size, embedding_dim, units, hyperparams['BATCH_SIZE'])
	return encoder, attention_layer, decoder


def loss_function(real, pred):
	loss_object = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True, reduction='none')
	mask = tf.math.logical_not(tf.math.equal(real, 0))
	loss_ = loss_object(real, pred)
	mask = tf.cast(mask, dtype=loss_.dtype)
	loss_ *= mask
	return tf.reduce_mean(loss_)

@tf.function
def train_step(inp, targ, enc_hidden, optimizer, encoder, decoder, attention_layer, targ_lang, hyperparams):
	loss = 0

	with tf.GradientTape() as tape:
		enc_output, enc_hidden = encoder(inp, enc_hidden)
		dec_hidden = enc_hidden
		dec_input = tf.expand_dims([targ_lang.word_index['<start>']] * hyperparams['BATCH_SIZE'], 1)
		
		# Teacher forcing - feeding the target as the next input
		for t in range(1, targ.shape[1]):
			# passing enc_output to the decoder
			predictions, dec_hidden, _ = decoder(dec_input, dec_hidden, enc_output)
			loss += loss_function(targ[:, t], predictions)
			# using teacher forcing
			dec_input = tf.expand_dims(targ[:, t], 1)
	
	batch_loss = (loss / int(targ.shape[1]))
	variables = encoder.trainable_variables + decoder.trainable_variables
	gradients = tape.gradient(loss, variables)
	optimizer.apply_gradients(zip(gradients, variables))
	return batch_loss

class NeuralMachineTranslation(object):

	def __init__(self, learning_rate=0.01, batch_size=64, epochs=2, num_examples=3000, test_size=0.2):
		self.hyperparams = {'BATCH_SIZE': batch_size, 'NUM_EXAMPLES': num_examples, 'TEST_SIZE': test_size}
		self.model_file = "lstm_trained"
		self.learning_rate = learning_rate
		self.epochs = epochs
		(self.dataset, self.vocab_inp_size, self.vocab_tar_size, self.max_length_inp, 
			self.max_length_targ, self.steps_per_epoch, self.targ_lang) = data_loader(self.hyperparams)
		self.encoder, self.attention_layer, self.decoder = define_model(self.hyperparams, self.vocab_inp_size, self.vocab_tar_size)


	def train(self):
		optimizer = tf.keras.optimizers.Adam()
		checkpoint_dir = './training_checkpoints'
		checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
		checkpoint = tf.train.Checkpoint(optimizer=optimizer,
										 encoder=self.encoder,
										 decoder=self.decoder)

		for epoch in range(self.epochs):
			enc_hidden = self.encoder.initialize_hidden_state()
			total_loss = 0
			
			for (batch, (inp, targ)) in enumerate(self.dataset.take(self.steps_per_epoch)):
				batch_loss = train_step(inp, targ, enc_hidden, optimizer, self.encoder, 
					self.decoder, self.attention_layer, self.targ_lang, self.hyperparams)
				total_loss += batch_loss
			
			# saving (checkpoint) the model every 2 epochs
			if (epoch + 1) % 2 == 0:
				checkpoint.save(file_prefix = checkpoint_prefix)
			print("epoch {}:\nloss={:.2f}\n".format(epoch + 1, total_loss / self.steps_per_epoch))

	def translate(sentence):
		max_length_inp, max_length_targ = self.max_length_inp, self.max_length_targ
		sentence = preprocess_sentence(sentence)
		inputs = [inp_lang.word_index[i] for i in sentence.split(' ')]
		inputs = tf.keras.preprocessing.sequence.pad_sequences([inputs],
		                                                     maxlen=max_length_inp,
		                                                     padding='post')
		inputs = tf.convert_to_tensor(inputs)
		result = ''
		hidden = [tf.zeros((1, units))]
		enc_out, enc_hidden = self.encoder(inputs, hidden)
		dec_hidden = enc_hidden
		dec_input = tf.expand_dims([targ_lang.word_index['<start>']], 0)

		for t in range(max_length_targ):
			predictions, dec_hidden, attention_weights = self.decoder(dec_input,
			                                                     dec_hidden,
			                                                     enc_out)
			
			predicted_id = tf.argmax(predictions[0]).numpy()
			result += targ_lang.index_word[predicted_id] + ' '

			if targ_lang.index_word[predicted_id] == '<end>':
				return result, sentence, attention_plot
			# the predicted ID is fed back into the model
			dec_input = tf.expand_dims([predicted_id], 0)

		return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-lr", "--learning_rate", default="1e-4", help="Learning rate for the Keras optimizer")
    parser.add_argument("-bsz", "--batch_size", default="64", help="Batch size for each step of learning")
    parser.add_argument("-e", "--epochs", default="2", help="Number of epochs in each trial")
    parser.add_argument("-ne", "--num_examples", default="3000", help="Number of examples to train on")
    args = parser.parse_args()
    learning_rate = float(args.learning_rate)
    batch_size = int(args.batch_size)
    epochs = int(args.epochs)
    num_examples = int(args.num_examples)
    model = NeuralMachineTranslation(learning_rate, batch_size, epochs, num_examples)
    model.train()