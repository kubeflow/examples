"""Using Transformer Networks for String similarities."""
from tensor2tensor.data_generators import problem
from tensor2tensor.layers import common_layers
from tensor2tensor.models import transformer
from tensor2tensor.utils import registry
from tensor2tensor.utils import t2t_model
import tensorflow as tf


@registry.register_model('cs_similarity_transformer')
class SimilarityTransformer(t2t_model.T2TModel):
  """Transformer Model for Similarity between two strings.

  This model defines the architecture using two transformer
  networks, each of which embed a string and the loss is
  calculated as a Binary Cross-Entropy loss. Normalized
  Dot Product is used as the distance measure between two
  string embeddings.
  """
  def top(self, body_output, _):  # pylint: disable=no-self-use
    return body_output

  def body(self, features):
    with tf.variable_scope('string_embedding'):
      string_embedding = self.encode(features, 'inputs')

    with tf.variable_scope('code_embedding'):
      code_embedding = self.encode(features, 'targets')

    result = tf.concat([string_embedding, code_embedding], 1)

    if self.hparams.mode != tf.estimator.ModeKeys.PREDICT:
      # string_embedding_norm = tf.nn.l2_normalize(string_embedding, axis=1)
      # code_embedding_norm = tf.nn.l2_normalize(code_embedding, axis=1)

      p = tf.nn.sigmoid(tf.matmul(string_embedding, code_embedding,
                                         transpose_b=True))

      labels = tf.eye(tf.shape(p)[0], dtype=tf.int32)
      labels = tf.reshape(labels, [-1])

      p = tf.reshape(p, [-1, 1])
      logits = tf.concat([1.0 - p, p], axis=1)
      labels = tf.one_hot(labels, 2)

      loss = tf.nn.sigmoid_cross_entropy_with_logits(labels=labels,
                                                     logits=logits)

      return result, {'training': loss}

    return result

  def encode(self, features, input_key):
    hparams = self._hparams
    inputs = common_layers.flatten4d3d(features[input_key])

    (encoder_input, encoder_self_attention_bias, _) = (
        transformer.transformer_prepare_encoder(inputs, problem.SpaceID.EN_TOK,
                                                hparams))

    encoder_input = tf.nn.dropout(encoder_input,
                                  1.0 - hparams.layer_prepostprocess_dropout)
    encoder_output = transformer.transformer_encoder(
        encoder_input,
        encoder_self_attention_bias,
        hparams,
        nonpadding=transformer.features_to_nonpadding(features, input_key))

    encoder_output = tf.reduce_mean(encoder_output, axis=1)

    return encoder_output

  def infer(self, features=None, **kwargs):
    del kwargs

    if 'targets' not in features:
      features['targets'] = tf.placeholder(tf.int64, shape=(None, None, 1, 1))

    predictions, _ = self(features)
    return predictions
