"""Github function/text similatrity problems."""
import csv
import glob
import os
from tensor2tensor.data_generators import text_problems
from tensor2tensor.utils import metrics
from tensor2tensor.utils import registry


@registry.register_problem
class GithubFunctionDocstring(text_problems.Text2TextProblem):
  # pylint: disable=abstract-method

  """This class defines the problem of finding similarity between Python
  function and docstring"""

  @property
  def is_generate_per_split(self):
    return False

  @property
  def approx_vocab_size(self):
    return 2**13

  def generate_samples(self, data_dir, tmp_dir, dataset_split):  # pylint: disable=no-self-use,unused-argument
    """Returns a generator to return {"inputs": [text], "targets": [text]}."""

    # TODO(sanyamkapoor): separate train/eval data set.
    pair_files_glob = os.path.join(data_dir, 'pairs-*.csv')
    for pairs_file_path in glob.glob(pair_files_glob):
      with open(pairs_file_path, 'r') as csv_file:
        pairs_reader = csv.reader(csv_file)
        for row in pairs_reader:
          function_tokens, docstring_tokens = row[-2:]
          yield {'inputs': docstring_tokens, 'targets': function_tokens}

  def eval_metrics(self):  # pylint: disable=no-self-use
    return [
        metrics.Metrics.ACC
    ]
