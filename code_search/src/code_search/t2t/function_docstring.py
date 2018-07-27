"""Github function/text similatrity problems."""
from cStringIO import StringIO
import csv
import os
from tensor2tensor.data_generators import generator_utils
from tensor2tensor.data_generators import translate
from tensor2tensor.utils import metrics
from tensor2tensor.utils import registry
import tensorflow as tf


@registry.register_problem
class GithubFunctionDocstring(translate.TranslateProblem):
  """Function and Docstring similarity Problem.

  This problem contains the data consisting of function
  and docstring pairs as CSV files.
  """

  @property
  def is_generate_per_split(self):
    return False

  @property
  def approx_vocab_size(self):
    return 2**13

  def _get_csv_files(self, data_dir, tmp_dir, dataset_split, limit=None):
    """Get a list of CSV files.

    This routine gets the list of CSV files in data_dir. If
    the files don't exist on a local path, they are downloaded
    into the temporary directory. Optionally, one can limit the
    number of CSV files to process.

    FIXME(sanyamkapoor): `limit` exists to handle memory explosion.
    TODO(sanyamkapoor): separate train/eval data set.

    Args:
      data_dir: A string representing the data directory.
      tmp_dir: A string representing the temporary directory and is
              used to download files if not already available.
      dataset_split: Unused.
      limit: Limit the number of CSV files returned.

    Returns:
      A list of strings representing the CSV file paths on local filesystem.
    """
    glob_string = '{}/*.csv'.format(data_dir)
    csv_files = tf.gfile.Glob(glob_string)
    if limit:
      csv_files = csv_files[:limit]

    if os.path.isdir(data_dir):
      return csv_files

    return [
        generator_utils.maybe_download(tmp_dir, os.path.basename(uri), uri)
        for uri in csv_files
    ]

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

    csv_files = self._get_csv_files(data_dir, tmp_dir, dataset_split, limit=1000)

    if not csv_files:
      tf.logging.fatal('No CSV files found or downloaded!')

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
