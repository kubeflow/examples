import os
from tensor2tensor.utils import registry
from tensor2tensor.data_generators import text_problems
from tensor2tensor.models import transformer


@registry.register_problem
class GithubDocstringLanguageModel(text_problems.Text2SelfProblem):
  """This class defines the Language Modeling problem for Github docstrings"""

  @property
  def is_generate_per_split(self):
    return False

  def generate_samples(self, data_dir, tmp_dir, dataset_split):
    docstrings_file_path = os.path.join(data_dir, '{}.docstring'.format(dataset_split))

    return text_problems.text2self_txt_iterator(docstrings_file_path)

@registry.register_hparams
def transformer_gh_lm():
  hparams = transformer.transformer_base()
  # TODO(sanyamkapoor): change language model embedding size
  return hparams
