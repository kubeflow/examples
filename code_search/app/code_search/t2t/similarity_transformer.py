import os
import csv
import tensorflow as tf
from tensor2tensor.utils import t2t_model
from tensor2tensor.utils import registry
from tensor2tensor.data_generators import problem
from tensor2tensor.data_generators import text_problems
from tensor2tensor.layers import common_layers
from tensor2tensor.models import transformer


@registry.register_model
class SimilarityTransformer(t2t_model.T2TModel):
  # pylint: disable=abstract-method

  """
  This class defines the model to compute similarity scores between functions and
  docstrings
  """
  def __init__(self, *args, **kwargs):
    super(SimilarityTransformer, self).__init__(*args, **kwargs)

  def body(self, features):
    """The body of this model takes in features
    of code and docstring pairs, embeds & computes a
    similarity probability and computes the loss as
    standard cross entropy loss
    """
    with tf.variable_scope("string_embedding"):
      string_embedding = self.encode(features, 'inputs')

    loss = None
    if 'targets' in features:
      with tf.variable_scope("code_embedding"):
        code_embedding = self.encode(features, 'targets')

      cosine_dist = tf.losses.cosine_distance(tf.nn.l2_normalize(string_embedding, axis=1),
                                              tf.nn.l2_normalize(code_embedding, axis=1),
                                              axis=1, reduction=tf.losses.Reduction.NONE)

      # TODO: need to do negative sampling, so this won't be all ones anymore
      labels = tf.one_hot(tf.ones(features['targets'].shape[0], tf.int32), 2)
      logits = tf.concat([cosine_dist, 1 - cosine_dist], axis=1)

      loss = tf.nn.sigmoid_cross_entropy_with_logits(labels=labels, logits=logits)

    if loss:
      return string_embedding, loss

    return string_embedding

  def encode(self, features, input_key):
    inputs = common_layers.flatten4d3d(features[input_key])

    (encoder_input, encoder_self_attention_bias, _) = (
        transformer.transformer_prepare_encoder(inputs, problem.SpaceID.EN_TOK, self._hparams))

    encoder_input = tf.nn.dropout(encoder_input,
                                  1.0 - self._hparams.layer_prepostprocess_dropout)
    encoder_output = transformer.transformer_encoder(
        encoder_input,
        encoder_self_attention_bias,
        self._hparams,
        nonpadding=transformer.features_to_nonpadding(features, input_key))
    encoder_output = tf.expand_dims(encoder_output, 2)

    # TODO: compute embedding from a sequence of embedding vectors

    return encoder_output


@registry.register_problem
class GithubFunctionDocstring(text_problems.Text2TextProblem):
  # pylint: disable=abstract-method

  """This class defines the problem of finding similarity between Python function
   and docstring"""

  @property
  def is_generate_per_split(self):
    return False

  @property
  def approx_vocab_size(self):
    return 2**13

  def generate_samples(self, data_dir, _tmp_dir, dataset_split):  #pylint: disable=no-self-use
    """This method returns the generator to return {"inputs": [text], "targets": [text]} dict"""

    # TODO: separate train/eval data set
    pairs_file_path= os.path.join(data_dir, 'pairs.csv')

    with open(pairs_file_path, 'r') as csv_file:
      pairs_reader = csv.reader(csv_file)
      for i, row in enumerate(pairs_reader):
        function_tokens, docstring_tokens = row[-2:]
        yield {"inputs": docstring_tokens, "targets": function_tokens}
