"""Using Transformer Networks for String similarities."""
from tensor2tensor.data_generators import problem
from tensor2tensor.layers import common_layers
from tensor2tensor.models import transformer
from tensor2tensor.utils import registry
from tensor2tensor.utils import t2t_model
import tensorflow as tf


@registry.register_model
class SimilarityTransformer(t2t_model.T2TModel):
  # pylint: disable=abstract-method

  """
  This class defines the model to compute similarity scores between functions
  and docstrings
  """

  def top(self, body_output, features):  # pylint: disable=no-self-use,unused-argument
    return body_output

  def body(self, features):
    """Body of the Similarity Transformer Network."""

    with tf.variable_scope('string_embedding'):
      string_embedding = self.encode(features, 'inputs')

    if 'targets' in features:
      with tf.variable_scope('code_embedding'):
        code_embedding = self.encode(features, 'targets')

      string_embedding_norm = tf.nn.l2_normalize(string_embedding, axis=1)
      code_embedding_norm = tf.nn.l2_normalize(code_embedding, axis=1)

      # All-vs-All cosine distance matrix, reshaped as row-major.
      cosine_dist = 1.0 - tf.matmul(string_embedding_norm, code_embedding_norm,
                                    transpose_b=True)
      cosine_dist_flat = tf.reshape(cosine_dist, [-1, 1])

      # Positive samples on the diagonal, reshaped as row-major.
      label_matrix = tf.eye(tf.shape(cosine_dist)[0], dtype=tf.int32)
      label_matrix_flat = tf.reshape(label_matrix, [-1])

      logits = tf.concat([1.0 - cosine_dist_flat, cosine_dist_flat], axis=1)
      labels = tf.one_hot(label_matrix_flat, 2)

      loss = tf.nn.sigmoid_cross_entropy_with_logits(labels=labels,
                                                     logits=logits)

      return string_embedding, {'training': loss}

    return string_embedding

  def encode(self, features, input_key):
    hparams = self._hparams
    inputs = common_layers.flatten4d3d(features[input_key])

    (encoder_input, encoder_self_attention_bias, _) = (
        transformer.transformer_prepare_encoder(inputs, problem.SpaceID.EN_TOK,
                                                self._hparams))

    encoder_input = tf.nn.dropout(encoder_input,
                                  1.0 - hparams.layer_prepostprocess_dropout)
    encoder_output = transformer.transformer_encoder(
        encoder_input,
        encoder_self_attention_bias,
        self._hparams,
        nonpadding=transformer.features_to_nonpadding(features, input_key))
    encoder_output = tf.expand_dims(encoder_output, 2)

    encoder_output = tf.reduce_mean(tf.squeeze(encoder_output, axis=2), axis=1)

    return encoder_output

  def infer(self, features=None, **kwargs):  # pylint: disable=no-self-use,unused-argument
    predictions, _ = self(features)
    return predictions
