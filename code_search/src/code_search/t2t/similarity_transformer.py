"""Using Transformer Networks for String similarities."""
from tensor2tensor.data_generators import problem
from tensor2tensor.layers import common_layers
from tensor2tensor.models import transformer
from tensor2tensor.utils import registry
from tensor2tensor.utils import t2t_model
import tensorflow as tf

MODEL_NAME = 'cs_similarity_transformer'

# We don't use the default name because there is already an older version
# included as part of the T2T library with the default name.
@registry.register_model(MODEL_NAME)
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

    if self.hparams.mode != tf.estimator.ModeKeys.PREDICT:
      # In training mode we need to embed both the queries and the code
      # using the inputs and targets respectively.
      with tf.variable_scope('string_embedding'):
        string_embedding = self.encode(features, 'inputs')

      with tf.variable_scope('code_embedding'):
        code_embedding = self.encode(features, 'targets')

      p = tf.nn.sigmoid(tf.matmul(string_embedding, code_embedding,
                                  transpose_b=True))

      labels = tf.eye(tf.shape(p)[0], dtype=tf.int32)
      labels = tf.reshape(labels, [-1])

      p = tf.reshape(p, [-1, 1])
      logits = tf.concat([1.0 - p, p], axis=1)
      labels = tf.one_hot(labels, 2)

      loss = tf.nn.sigmoid_cross_entropy_with_logits(labels=labels,
                                                     logits=logits)

      result = string_embedding
      return result, {'training': loss}

    else:
      # In predict mode we conditionally embed either the string query
      # or the code based on the embed_code feature. In both cases the
      # input will be in the inputs feature but the variable scope will
      # be different
      # Define predicates to be used with tf.cond
      def embed_string():
        with tf.variable_scope('string_embedding'):
          string_embedding = self.encode(features, 'inputs')
        return string_embedding

      def embed_code():
        with tf.variable_scope('code_embedding'):
          code_embedding = self.encode(features, 'inputs')
        return code_embedding

      embed_code_feature = features.get('embed_code')

      # embed_code_feature will be a tensor because inputs will be a batch
      # of inputs. We need to reduce that down to a single value for use
      # with tf.cond; so we simply take the max of all the elements.
      # This implicitly assume all inputs have the same value.
      is_embed_code = tf.reduce_max(embed_code_feature)
      result = tf.cond(is_embed_code > 0, embed_code, embed_string)

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

    predictions, _ = self(features)
    return predictions
