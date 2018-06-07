import os
from tensor2tensor.utils import registry
from tensor2tensor.data_generators import text_problems


@registry.register_problem
class GithubFunctionSummarizer(text_problems.Text2TextProblem):
  # pylint: disable=abstract-method

  """This class defines the problem of converting Python function code to docstring"""

  @property
  def is_generate_per_split(self):
    return False

  def generate_samples(self, data_dir, _tmp_dir, dataset_split):  #pylint: disable=no-self-use
    """This method returns the generator to return {"inputs": [text], "targets": [text]} dict"""

    # TODO(sanyamkapoor): Merge with validation set file "valid.{function|docstring}"
    functions_file_path = os.path.join(data_dir, '{}.function'.format(dataset_split))
    docstrings_file_path = os.path.join(data_dir, '{}.docstring'.format(dataset_split))

    return text_problems.text2text_txt_iterator(functions_file_path, docstrings_file_path)
