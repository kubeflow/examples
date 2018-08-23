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

  def body(self, features):

    def embed_string():
      with tf.variable_scope('string_embedding'):
        string_embedding = self.encode(features, 'inputs')
      return string_embedding

    def embed_code():
      with tf.variable_scope('code_embedding'):
        code_embedding = self.encode(features, 'targets')
      return code_embedding

    if 'embed_code' not in features:
      features['embed_code'] = tf.constant(False, dtype=tf.bool)

    if self.trainable:
      string_embedding = embed_string()
      code_embedding = embed_code()

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

      result = tf.cond(features.get('embed_code'),
                       lambda: code_embedding, lambda: string_embedding)
      return result, {'training': loss}

    result = tf.cond(features.get('embed_code'),
                     embed_code, embed_string)
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
