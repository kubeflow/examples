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

  def body(self, features):
    """Body of the Similarity Transformer Network."""

    with tf.variable_scope('string_embedding'):
      string_embedding = self.encode(features, 'inputs')

    loss = None
    if 'targets' in features:
      with tf.variable_scope('code_embedding'):
        code_embedding = self.encode(features, 'targets')

      cosine_dist = tf.losses.cosine_distance(
          tf.nn.l2_normalize(string_embedding, axis=1),
          tf.nn.l2_normalize(code_embedding, axis=1),
          axis=1, reduction=tf.losses.Reduction.NONE)

      # TODO(sanyamkapoor): need negative sampling, won't be all ones anymore.
      labels = tf.one_hot(tf.ones(
          tf.shape(features['targets'])[0], tf.int32), 2)
      logits = tf.concat([cosine_dist, 1 - cosine_dist], axis=1)

      loss = tf.nn.sigmoid_cross_entropy_with_logits(labels=labels,
                                                     logits=logits)

    if loss is not None:
      return string_embedding, loss

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
