"""Github function/text similatrity problems."""
from cStringIO import StringIO
import csv
from tensor2tensor.data_generators import generator_utils
from tensor2tensor.data_generators import translate
from tensor2tensor.utils import metrics
from tensor2tensor.utils import registry
import tensorflow as tf


@registry.register_problem
class GithubFunctionDocstring(translate.TranslateProblem):
  """Function and Docstring similarity Problem.

  This problem contains the data consisting of function
  and docstring pairs as CSV files. The files are structured
  such that they contain two columns without headers containing
  the docstring tokens and function tokens. The delimiter is
  ",".
  """

  FILES_BASE_URL = 'gs://kubeflow-examples/t2t-code-search/raw_data'

  GITHUB_FUNC_DOC_PAIR_FILES = [
    'func-doc-pairs-000{:02}-of-00100.csv'.format(i)
    for i in range(100)
  ]

  @property
  def is_generate_per_split(self):
    return False

  @property
  def approx_vocab_size(self):
    return 2**13

  def source_data_files(self, _):
    # TODO(sanyamkapoor): Manually separate train/eval data set.
    return self.GITHUB_FUNC_DOC_PAIR_FILES

  @property
  def max_samples_for_vocab(self):
    # FIXME(sanyamkapoor): This exists to handle memory explosion.
    return int(3.5e5)

  def generate_samples(self, data_dir, tmp_dir, dataset_split):
    """A generator to return data samples.Returns the data generator to return .


    Args:
      data_dir: A string representing the data directory.
      tmp_dir: A string representing the temporary directory and is
              used to download files if not already available.
      dataset_split: Train, Test or Eval.

    Yields:
      Each element yielded is of a Python dict of the form
        {"inputs": "STRING", "targets": "STRING"}
    """

    csv_file_names = self.source_data_files(dataset_split)
    download_dir = tmp_dir if data_dir.startswith('gs://') else data_dir
    csv_files = [
        generator_utils.maybe_download(download_dir, filename,
                                       '{}/{}'.format(self.FILES_BASE_URL,
                                                      filename))
        for filename in csv_file_names
    ]

    for pairs_file in csv_files:
      tf.logging.debug('Reading {}'.format(pairs_file))
      with open(pairs_file, 'r') as csv_file:
        for line in csv_file:
          reader = csv.reader(StringIO(line))
          docstring_tokens, function_tokens = next(reader)
          yield {'inputs': docstring_tokens, 'targets': function_tokens}

  def eval_metrics(self):  # pylint: disable=no-self-use
    return [
        metrics.Metrics.ACC
    ]
