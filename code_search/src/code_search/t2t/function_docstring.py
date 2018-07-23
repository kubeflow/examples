"""Github function/text similatrity problems."""
import csv
import os
from cStringIO import StringIO
from tensor2tensor.data_generators import generator_utils
from tensor2tensor.data_generators import translate
from tensor2tensor.utils import metrics
from tensor2tensor.utils import registry


##
# These URLs are only for fallback purposes in case the specified
# `data_dir` does not contain the data. However, note that the data
# files must have the same naming pattern.
# TODO: The memory is exploding, need to fix this.
#
_DATA_BASE_URL = 'gs://kubeflow-examples/t2t-code-search/data'
_GITHUB_FUNCTION_DOCSTRING_FILES = [
    'pairs-0000{}-of-00010.csv'.format(i)
    for i in range(1)
]


@registry.register_problem
class GithubFunctionDocstring(translate.TranslateProblem):
  # pylint: disable=abstract-method

  """This class defines the problem of finding similarity between Python
  function and docstring"""

  @property
  def is_generate_per_split(self):
    return False

  @property
  def approx_vocab_size(self):
    return 2**13

  def source_data_files(self, dataset_split):  # pylint: disable=no-self-use,unused-argument
    # TODO(sanyamkapoor): separate train/eval data set.
    return _GITHUB_FUNCTION_DOCSTRING_FILES

  def generate_samples(self, data_dir, tmp_dir, dataset_split):  # pylint: disable=no-self-use,unused-argument
    """Returns a generator to return {"inputs": [text], "targets": [text]}.

    If the `data_dir` is a GCS path, all data is downloaded to the
    `tmp_dir`.
    """

    download_dir = tmp_dir if data_dir.startswith('gs://') else data_dir
    uri_base = data_dir if data_dir.startswith('gs://') else _DATA_BASE_URL
    pair_csv_files = [
        generator_utils.maybe_download(download_dir, filename, os.path.join(uri_base, filename))
        for filename in self.source_data_files(dataset_split)
    ]

    for pairs_file in pair_csv_files:
      with open(pairs_file, 'r') as csv_file:
        for line in csv_file:
          reader = csv.reader(StringIO(line), delimiter=',')
          function_tokens, docstring_tokens = next(reader)[-2:]  # pylint: disable=stop-iteration-return
          yield {'inputs': docstring_tokens, 'targets': function_tokens}

  def eval_metrics(self):  # pylint: disable=no-self-use
    return [
        metrics.Metrics.ACC
    ]
