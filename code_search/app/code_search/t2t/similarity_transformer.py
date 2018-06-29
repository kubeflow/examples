import os
import tensorflow as tf
from tensor2tensor.utils import t2t_model
from tensor2tensor.utils import registry
from tensor2tensor.data_generators import text_problems
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

    self.code_transformer = transformer.TransformerEncoder(*args, **kwargs)
    self.docstring_transformer = transformer.TransformerEncoder(*args, **kwargs)

  def body(self, features):
    """The body of this model takes in features
    of code and docstring pairs, embeds & computes a
    similarity probability and computes the loss as
    standard cross entropy loss
    """
    string_embedding = self.code_transformer(features['inputs'])

    loss = None
    if 'targets' in features:
      code_embedding = self.docstring_transformer(features['targets'])
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


@registry.register_problem
class GithubFunctionDocstring(text_problems.Text2TextProblem):
  # pylint: disable=abstract-method

  """This class defines the problem of finding similarity between Python function
   and docstring"""

  @property
  def is_generate_per_split(self):
    return False

  def generate_samples(self, data_dir, _tmp_dir, dataset_split):  #pylint: disable=no-self-use
    """This method returns the generator to return {"inputs": [text], "targets": [text]} dict"""

    docstrings_file_path = os.path.join(data_dir, '{}.docstring'.format(dataset_split))
    functions_file_path = os.path.join(data_dir, '{}.function'.format(dataset_split))

    return text_problems.text2text_txt_iterator(docstrings_file_path, functions_file_path)
